import torch
import torch.nn as nn
import numpy as np
from deap import base, creator, tools, gp, algorithms
import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import logging
import time

import xgboost as xgb
from sklearn.metrics import accuracy_score, log_loss

def train_model_and_get_accuracy_by_xgboost(train_x, train_y, test_x, test_y):
    start = time.time()

    model = xgb.XGBClassifier(
        n_estimators=100, 
        learning_rate=0.01,  
        max_depth=6,  
        subsample=0.8, 
        colsample_bytree=0.8,  
        objective='binary:logistic',  
        use_label_encoder=False  
    )
    
    model.fit(
        train_x, train_y
    )
    
    train_preds = model.predict(train_x)
    test_preds = model.predict(test_x)
    

    train_accuracy = accuracy_score(train_y, train_preds)
    test_accuracy = accuracy_score(test_y, test_preds)
    

    train_loss = log_loss(train_y, model.predict_proba(train_x))
    test_loss = log_loss(test_y, model.predict_proba(test_x))
    
    # print(f'Train set Evaluation Loss: {train_loss:.4f}, Accuracy: {train_accuracy:.4f}')
    # print(f'Test set Evaluation Loss: {test_loss:.4f}, Accuracy: {test_accuracy:.4f}')
    end = time.time()
    import tools_and_global_parameters
    tools_and_global_parameters.timer['model_train_and_test'] += end - start
    return test_accuracy, test_loss



 

class PeriodicActivation(nn.Module):
    def __init__(self):
        super(PeriodicActivation, self).__init__()

    def forward(self, x):
        return torch.sin(  np.pi * (x ))

 

class NALU(nn.Module):
    def __init__(self, input_size, output_size):
        super(NALU, self).__init__()
        self.W_hat = nn.Parameter(torch.Tensor(output_size, input_size))
        self.M_hat = nn.Parameter(torch.Tensor(output_size, input_size))
        self.G = nn.Parameter(torch.Tensor(output_size, input_size))
        self.reset_parameters()
        self.batch_norm1 = nn.BatchNorm1d(output_size)  
        self.activation = PeriodicActivation()

    def reset_parameters(self):
        nn.init.uniform_(self.W_hat, -0.1, 0.1)
        nn.init.uniform_(self.M_hat, -0.1, 0.1)
        nn.init.uniform_(self.G, -0.1, 0.1)

    def forward(self, x):
        W = torch.tanh(self.W_hat) * torch.sigmoid(self.M_hat)
        a = F.linear(x, W)
        m = torch.exp(F.linear(torch.log(torch.abs(x) + 1e-7), W))
        g = torch.sigmoid(F.linear(x, self.G))
        y = g * a + (1 - g) * m
        y = self.batch_norm1(y)
        y = self.activation(y)

        return y


class LogicGateNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LogicGateNet, self).__init__()
        self.hidden = nn.Linear(input_size, hidden_size)
        self.output = nn.Linear(hidden_size, output_size)
        self.batch_norm = nn.BatchNorm1d(output_size)

    def forward(self, x):
        x = self.hidden(x)
        x = F.relu(x)
        x = self.output(x)
        x = self.batch_norm(x)
        x = F.relu(x)
        return x

class MPCNN(nn.Module):
    def __init__(self, input_size, hidden_size=128):
        super(MPCNN, self).__init__()
        arith_input_size = input_size // 65
        logic_input_size = arith_input_size * 64

        self.nalu = NALU(input_size=arith_input_size, output_size=hidden_size)
        self.periodic_activation = PeriodicActivation()

        self.logic_net = LogicGateNet(input_size=logic_input_size, hidden_size=hidden_size, output_size=hidden_size)

        self.fusion_layer = nn.Linear(hidden_size * 2, hidden_size)

        self.output_layer = nn.Linear(hidden_size, 1)

    def forward(self, x_input):
        # Calculate the size of x_arith and x_logic
        arith_input_size = x_input.shape[1] // 65  # 1 part for x_arith and 64 parts for x_logic
        logic_input_size = arith_input_size * 64
        
        # Split x_input into x_arith and x_logic
        x_arith = x_input[:, :arith_input_size]
        x_logic = x_input[:, arith_input_size:arith_input_size + logic_input_size]
        

        y_nalu = self.nalu(x_arith)
        y_arith = self.periodic_activation(y_nalu)

        y_logic = self.logic_net(x_logic)

        y_fused = torch.cat((y_arith, y_logic), dim=1)
        y_fused = torch.relu(self.fusion_layer(y_fused))

        y_output = torch.sigmoid(self.output_layer(y_fused)).squeeze(-1)  # 去掉多余的维度
        return y_output







class BasicDNN(nn.Module):
    def __init__(self, input_size, hidden_size=160):
        super(BasicDNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.output_layer = nn.Linear(hidden_size, 1)


    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = torch.sigmoid(self.output_layer(x)).squeeze(-1)
        return x


class BasicCNN(nn.Module):
    def __init__(self, input_size, hidden_size=256):  # Further reduced hidden_size
        super(BasicCNN, self).__init__()
        
        # Convolutional layers with smaller channel sizes
        self.conv1 = nn.Conv1d(1, 6, kernel_size=3, padding=1)  # Reduced to 16
        self.conv2 = nn.Conv1d(6, 12, kernel_size=3, padding=1)  # Reduced to 32
        
        # Max pooling layer
        self.pool = nn.MaxPool1d(kernel_size=2, stride=2)
        
        # Calculate the output size after conv and pool layers
        conv_output_size = input_size // 4 * 12  # Updated to match 32 channels from conv2
        
        # Fully connected layers
        self.fc1 = nn.Linear(conv_output_size, hidden_size)  # First fully connected layer
        self.fc2 = nn.Linear(hidden_size, 1)  # Output layer for binary classification

    def forward(self, x):
        # Adjust input dimensions to (batch_size, 1, input_size)
        x = x.unsqueeze(1)
        
        # Pass through convolutional and max pooling layers
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        
        # Flatten and pass through fully connected layers
        x = torch.flatten(x, start_dim=1)
        x = F.relu(self.fc1(x))  # First fully connected layer
        x = torch.sigmoid(self.fc2(x)).squeeze(-1)  # Output layer
        return x


class BasicLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=256, num_layers=2, step_size=64):
        super(BasicLSTM, self).__init__()
        self.step_size = step_size
        self.seq_len = input_size // step_size
        
        if input_size % step_size != 0:
            self.seq_len += 1  

        self.lstm = nn.LSTM(input_size=step_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)

   
        self.fc1 = nn.Linear(hidden_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.output_layer = nn.Linear(hidden_size, 1)

    def forward(self, x):
        batch_size, input_size = x.size(0), x.size(1)
        

        if input_size % self.step_size != 0:
            padding_size = (self.seq_len * self.step_size) - input_size
            x = F.pad(x, (0, padding_size)) 


        x = x.view(batch_size, self.seq_len, self.step_size) 
        output, (hidden, cell) = self.lstm(x)  
        x = hidden[-1]  

        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))

        x = torch.sigmoid(self.output_layer(x))

        x = x.view(-1) 
        return x





