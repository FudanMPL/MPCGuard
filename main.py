import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import torch.nn.functional as F
import sys
import argparse
import json
import traceback

import functionality

import detect_leakage_for_output
import detect_leakage_for_input
from config import logger
import config
import os
import time

from load_data import  *



def generate_secret_pair():
    # Here, we set a fixed secret pair for testing
    secret_paires = []
    secret_paires.append((1049088, -2**63))
    secret_paires.append((-5374770517643919356, 0))
    secret_paires.append((-1049088, 2**63-1))
    secret_paires.append((123123123, ~123123123))
    secret_paires.append((-2**63, 2**63-1))                      
    return secret_paires



if __name__ == '__main__':


    parser = argparse.ArgumentParser(description="test a mpc protocol")

    parser.add_argument(
        "--mode",
        metavar="FILE",
        type=str,
        default="run",
        help="run mode: run for whole process, debug for without collecting data",
    )
    parser.add_argument(
        "--bug_dir",
        metavar="FILE",
        type=str,
        default="bugs/",
        help="directory to store bugs",
    )
    args = parser.parse_args()
    bug_dir = args.bug_dir + "/"
    config.run_mode = args.mode
    os.makedirs('real-data', exist_ok=True)
    os.makedirs(bug_dir, exist_ok=True)

    # read programs, names, ideal_programs from ./mpcguard_config.json
    with open('mpcguard_config.json', 'r') as f:
        my_config = json.load(f)
    real_programs = my_config['real_programs']
    names = my_config['names']
    ideal_programs = my_config['ideal_programs']
    party_numbers = my_config['party_numbers']
    l = len(real_programs)

    
    for i in range(l):
        logger.info("================   test program: {}   ================".format(real_programs[i]))
        config.times['model_train_and_test'] = 0
        config.times['run_real_protocol'] = 0
        config.times['vul_location'] = 0
        config.times['vul_verify'] = 0
        total_time = 0
        start_time = time.time()
        try:
            config.real_data_dir = 'real-data/' + names[i]
            config.bug_file = bug_dir + names[i]
            config.real_protocol_execute_program = real_programs[i]
            config.current_name = names[i]
            config.number_of_party = party_numbers[i]
            # use string  ideal_programs[i] to get the real function object
            config.ideal_protocol_functionality = getattr(functionality, ideal_programs[i])

            for secret1, secret2 in generate_secret_pair():
                run_real_protocol(secret1)
                run_real_protocol(secret2)
                run_ideal_protocol(secret1)
                run_ideal_protocol(secret2)
                if detect_leakage_for_input.detect_leakage(secret1, secret2):
                    break
                if detect_leakage_for_output.detect_leakage(secret1):
                    break
                if detect_leakage_for_output.detect_leakage(secret2):
                    break

        except Exception as e:
            # print stack trace of e
            traceback.print_exc()
        
        end_time = time.time()
        total_time = end_time - start_time
        logger.info("Total time: {}".format(total_time))
        logger.info("Protocol Execution time: {}".format(config.times['run_real_protocol']))
        logger.info("Vulnerability Verification time: {}".format(config.times['vul_verify']))
        logger.info("Vulnerability Location time: {}".format(config.times['vul_location']))
        other_time = total_time - config.times['vul_verify'] - config.times['run_real_protocol'] - config.times['vul_location']
        logger.info("Other time: {}".format(other_time))
        logger.info("Additionally, Model Train and Test time: {}".format(config.times['model_train_and_test']))
