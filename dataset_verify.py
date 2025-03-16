import numpy as np
from deap import base, creator, tools, gp, algorithms
import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import logging
import time

from config import logger, number_of_epoch
import config
import load_data
from my_models import *



current_model = None
current_test_features = None
current_test_labels = None


def get_real_accuracy(views, labels):
    global current_test_features, current_test_labels
    train_features, train_labels, test_features, test_labels = load_data.dataset_split(views, labels)
    current_test_features = test_features
    current_test_labels = test_labels
    # return train_model_and_get_accuracy_by_xgboost(train_features, train_labels, test_features, test_labels)
    # return train_model_and_get_accuracy_by_sr(train_features, train_labels, test_features, test_labels)
    return train_model_and_get_accuracy(Real_World_Classifier, train_features, train_labels, test_features, test_labels)



def get_ideal_accuracy(views, labels):
    global current_test_features, current_test_labels
    train_features, train_labels, test_features, test_labels = load_data.dataset_split(views, labels)
    current_test_features = test_features
    current_test_labels = test_labels
    # return train_model_and_get_accuracy_by_sr(train_features, train_labels, test_features, test_labels)
    return train_model_and_get_accuracy(Ideal_World_Classifier, train_features, train_labels, test_features, test_labels)






def accuracy_evaluate(model, criterion, X_test, y_test):
    # set the model to evaluation mode
    model.eval()
    # forward pass
    with torch.no_grad():
        y_pred = model(X_test)
        # calculate the loss
        loss = criterion(y_pred, y_test)
        # calculate the accuracy
        predicted = (y_pred > 0.5).float()  # Threshold probabilities to get binary class predictions
        correct = (predicted == y_test).sum().item()
        accuracy = correct / y_test.size(0)
    return loss.item(), accuracy





def train_model_and_get_accuracy(Classifier, train_x, train_y, test_x, test_y):

    start_time = time.time()


    # Check if GPU is available and move tensors to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Convert numpy arrays to torch tensors and move them to the selected device
    train_x = torch.tensor(train_x, dtype=torch.float32).to(device)
    train_y = torch.tensor(train_y, dtype=torch.float32).to(device)
    test_x = torch.tensor(test_x, dtype=torch.float32).to(device)
    test_y = torch.tensor(test_y, dtype=torch.float32).to(device)
    
    train_dataset = torch.utils.data.TensorDataset(train_x, train_y)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=1000, shuffle=True)

    # Define the model and move it to the device
    model = Classifier(train_x.size(1)).to(device)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total number of parameters: {total_params}")    

    # Define the criterion and optimizer
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=0.1)

    max_accuracy = 0
    # Train the model
    for epoch in range(number_of_epoch):
        for X_train, y_train in train_loader:
            # Move batch data to the device
            X_train, y_train = X_train.to(device), y_train.to(device)
            loss = train(model, optimizer, criterion, X_train, y_train)

        logger.debug(f'Epoch: {epoch + 1}')
        
        # Evaluate on training data
        loss, accuracy = accuracy_evaluate(model, criterion, train_x, train_y)
        logger.debug(f'Train set Evaluation Loss: {loss:.4f}, Accuracy: {accuracy:.4f}')
        
        # Evaluate on test data
        loss, accuracy = accuracy_evaluate(model, criterion, test_x, test_y)
        logger.debug(f'Test set Evaluation Loss: {loss:.4f}, Accuracy: {accuracy:.4f}')
        if accuracy > max_accuracy:
            max_accuracy = accuracy

    end_time = time.time()
    config.times['model_train_and_test'] += end_time - start_time

    return max_accuracy, loss


# define the train function
def train(model, optimizer, criterion, X_train, y_train):
    # set the model to train mode
    model.train()
    # zero the parameter gradients
    optimizer.zero_grad()
    # forward pass
    y_pred = model(X_train)
    # calculate the loss
    loss = criterion(y_pred, y_train)
    # backward pass
    loss.backward()
    # update the model parameters
    optimizer.step()
    return loss.item()



