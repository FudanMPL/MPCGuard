from tools_and_global_parameters import *

import load_data
from load_data import *
from dataset_verify import *
import time



def detect_leakage(secret):
    logger.info("test for output with secret: {}".format(secret))
    start_time = time.time()
    views_ideal = load_data.get_views_of_corrupted_party_in_ideal_world(secret)
    output_share_of_victim_party_ideal = load_data.get_output_share_of_victim_party_in_ideal_world(secret)
    labels_ideal = [share % 2 for share in output_share_of_victim_party_ideal]
    accuracy_ideal, _ = get_ideal_accuracy(views_ideal, labels_ideal)
    logger.info(f"  accuracy_ideal: {accuracy_ideal}")
    views_real = load_data.get_views_of_corrupted_party_in_real_world(secret)
    output_share_of_victim_party_real = load_data.get_outputs_of_victim_party_in_real_world(secret)
    labels_real = [share % 2 for share in output_share_of_victim_party_real]
    accuracy_real, _ = get_real_accuracy(views_real, labels_real)
    logger.info(f"  accuracy_real: {accuracy_real}")
    end_time = time.time()
    timer['vul_verify'] += end_time - start_time
    logger.info(f" accuracy_real: {accuracy_real} accuracy_ideal: {accuracy_ideal}")
    if accuracy_real > accuracy_ideal + my_config['accuracy_verify_gap']:
        with open(my_config['bug_file'], "a") as f:
            f.write("\n")
            logger.info(f"accuracy_ideal: {accuracy_ideal}  accuracy_real: {accuracy_real}")
            f.write(f"accuracy_ideal: {accuracy_ideal}  accuracy_real: {accuracy_real}\n")
            logger.info(f"Leakage detected for output with secret: {secret} ")
            f.write(f"Leakage detected for output with secret: {secret}\n")
        if my_config['run_mode'] == 'identify':
            return True
        start_time = time.time()
        with open(my_config['bug_file'], "a") as f:
            last_fail_length = 0
            last_succ_length = len(views_real[0])
            full_length = last_succ_length
            while last_succ_length - last_fail_length > 1:
                current_length = (last_succ_length + last_fail_length) // 2
                views_real = load_data.get_views_of_corrupted_party_in_real_world(secret, current_length)
                accuracy_real, _ = get_real_accuracy(views_real, labels_real)
                logger.info(f"  accuracy_real: {accuracy_real} length: {current_length}") 
                f.write(f"  accuracy_real: {accuracy_real} length: {current_length}\n")
                if accuracy_real > accuracy_ideal + my_config['accuracy_verify_gap']:
                    last_succ_length = current_length
                else:
                    last_fail_length = current_length
            logger.info(f"Leakage detected for output with secret: {secret} length: {last_succ_length} full length: {full_length}")
            f.write(f"Leakage detected for output with secret: {secret} length: {last_succ_length} full length: {full_length}")
        rerun_with_print_stack_trace(secret, last_succ_length)    
        end_time = time.time()
        timer['vul_location'] += end_time - start_time  
        return True
    logger.info("No leakage detected for output")      
    return False
        



