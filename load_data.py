import config
from config import *
import subprocess
import os
import numpy as np
import time



input_shares_in_ideal_world = {}
output_shares_in_ideal_world = {}
adversary_views_in_ideal_world = {}




def get_views_of_corrupted_party_in_real_world(secret, l=None):
    views = []
    for i in range(config.collection_data_size):
        adversary_view = []
        for party in config.corrupted_party:
            with open(config.real_data_dir + "/s-{}/P-{}-view-{}".format(secret, party, i), 'r') as f:
                view = []
                # read each line as an integer
                for line in f:
                    view.append(int(line))
                if l is None:
                    l = len(view)
                adversary_view = adversary_view + view[:l]
        views.append(adversary_view)
    return views


def run_ideal_protocol(secret):
    adversary_views_in_ideal_world[secret] = []
    input_shares_in_ideal_world[secret] = []
    output_shares_in_ideal_world[secret] = []
    for i in range(config.ideal_collection_data_size):
        config.ideal_protocol_functionality(secret)



def get_output_share_of_victim_party_in_ideal_world(secret):
    result = []
    for output_shares in output_shares_in_ideal_world[secret]:
        result.append(output_shares[config.victim_party])
    return result

def get_views_of_corrupted_party_in_ideal_world(secret):
    return adversary_views_in_ideal_world[secret]


def get_outputs_of_victim_party_in_real_world(secret):
    outputs = []
    for i in range(config.collection_data_size):
        with open(config.real_data_dir +"/s-{}/P-{}-output-{}".format(secret, config.victim_party, i), 'r') as f:
            output = int(f.readline())
            outputs.append(output)
    return outputs


def run_real_protocol(secret):
    if config.run_mode == 'debug':
        return
    start_time = time.time()
    subprocess.run(["rm", "-rf", config.real_data_dir +"/s-{}/".format(secret)] )
    subprocess.run(["mkdir", "-p", config.real_data_dir+"/s-{}/".format(secret)])
    logger.info("run real protocol with secret: {}".format(secret))
    commands = []
    commands.extend(config.real_protocol_execute_program)
    commands.append("--secret")
    commands.append(str(secret))
    commands.append("--try_times")
    commands.append(str(config.collection_data_size))
    commands.append("--bug_file")
    commands.append(config.bug_file)
    subprocess.run(commands, text=True)

    end_time = time.time()
    times['run_real_protocol'] += end_time - start_time


def rerun_with_print_stack_trace(secret, index):
    logger.info("rerun with print stack trace with secret: {} index: {}".format(secret, index))
    commands = []
    commands.extend(config.real_protocol_execute_program)
    commands.append("--secret")
    commands.append(str(secret))
    commands.append("--try_times")
    commands.append(str(1))
    commands.append("--vul_index")
    commands.append(str(index))
    commands.append("--bug_file")
    commands.append(config.bug_file)
    commands.append("--no-record")
    subprocess.run(commands, text=True)


def int64_to_bits(arr):
    # 获取原始数组的形状
    original_shape = arr.shape
    
    # 将数组展平成一维
    arr_flat = arr.ravel()
    
    # 定义一个空数组用于存储每个整数的 bit 表示
    bit_array = []
    
    # 遍历每个整数
    for num in arr_flat:
        # 将 np.int64 转换为 Python 的原生 int 类型
        num = int(num)
        # 将整数转换为 64 位二进制字符串
        bits = np.binary_repr(num, width=64)  # 确保使用 64 位表示
        # 将字符串转换为 list，并映射为整数
        bit_array.append([int(b) for b in bits])
    
    # 转换为 NumPy 数组
    bit_array = np.array(bit_array, dtype=np.int8)
    
    # Reshape 回到原始形状，并增加一维存储每个元素的 64 位
    bit_array = bit_array.reshape(*original_shape, 64)
    
    return bit_array



def dataset_split(views, labels, rate=0.8):
    logger.debug("dataset split")
    # Pad the views to the same length
    max_length = max([len(view) for view in views])
    for i in range(len(views)):
        views[i] = np.pad(views[i], (0, max_length - len(views[i])), 'constant', constant_values=0)
    views = np.array(views, dtype=np.int64)
    labels = np.array(labels, dtype=np.float64)
    n_samples, n_dimensions = views.shape
    features_list = []
    for i in range(n_dimensions):
        # For each dimension, perform the two operations
        # 1. Normalize it (divide by absolute max)
        dimension_values = views[:, i].astype(np.float64)
        abs_max = np.max(np.abs(dimension_values))
        log_max = np.ceil(np.log2(abs_max))
        if abs_max != 0:
            log_max = np.ceil(np.log2(abs_max))
        else:
            log_max = 0
        normalized_values = dimension_values / 2 ** log_max    
        # Add the normalized values as one feature dimension
        features_list.append(normalized_values.reshape(-1, 1))
    for i in range(n_dimensions):
        # 2. Decompose into 64 bits
        int_values = views[:, i]
        uint64_values = int_values.astype(np.uint64)
        # Get bits
        shift_amounts = np.arange(64, dtype=np.uint64)
        bit_masks = (1 << shift_amounts).astype(np.uint64)
        bits = ((uint64_values[:, None] & bit_masks) > 0).astype(np.float64)
        bits = bits[:, ::-1]  # Reverse bits to get from most significant to least significant
        features_list.append(bits)

    # Concatenate all features
    features = np.hstack(features_list)  # features of shape (n_samples, n_dimensions * 65)

    # Shuffle the data
    indices = np.arange(len(features))
    np.random.shuffle(indices)
    features = features[indices]
    labels = labels[indices]

    # Split the data
    split_index = int(rate * len(features))
    train_features = features[:split_index]
    test_features = features[split_index:]
    train_labels = labels[:split_index]
    test_labels = labels[split_index:]

    return train_features, train_labels, test_features, test_labels

                         

def print_bit_length_of_corrupted_party_view_with_rate(secret, rate):
    for party in config.corrupted_party:
        with open(config.real_data_dir +"/s-{}/P-{}-view-0".format(secret, party), 'r') as f:
            view = []
            # read each line as an integer
            for line in f:
                view.append(int(line))
            l = int(rate * len(view))
            logger.info("party {} full view  length: {} leakage index: {}".format(party, len(view), l))


def is_secret_real_data_exist(secret):
    if not os.path.exists(config.real_data_dir+"/s-{}/".format(secret)):
        return False
    return True




