
from tools_and_global_parameters import *
import load_data
from load_data import  *
from dataset_verify import *
import time







def detect_leakage(secret1, secret2):
    logger.info("test for input with secret: {} {}".format(secret1, secret2))

    
    views_real1 = load_data.get_views_of_corrupted_party_in_real_world(secret1) 
    views_real2 = load_data.get_views_of_corrupted_party_in_real_world(secret2)

    start_time = time.time()
    views_real = views_real1 + views_real2
    labels_real = [0] * len(views_real1) + [1] * len(views_real2)
    accuracy_real, loss_real = get_real_accuracy(views_real, labels_real)
    views_ideal1 = load_data.get_views_of_corrupted_party_in_ideal_world(secret1)
    views_ideal2 = load_data.get_views_of_corrupted_party_in_ideal_world(secret2)
    views_ideal = views_ideal1 + views_ideal2
    labels_ideal = [0] * len(views_ideal1) + [1] * len(views_ideal2)
    accuracy_ideal, loss_ideal = get_ideal_accuracy(views_ideal, labels_ideal)
    logger.info(f"  accuracy_real: {accuracy_real} loss_real: {loss_real}")
    logger.info(f"  accuracy_ideal: {accuracy_ideal} loss_ideal: {loss_ideal}")
    end_time = time.time()
    timer['vul_verify'] += end_time - start_time

    if accuracy_real > accuracy_ideal + my_config['accuracy_verify_gap']:
        with open(my_config['bug_file'], "a") as f:
            f.write("\n")
            logger.info(f"accuracy_ideal: {accuracy_ideal}  accuracy_real: {accuracy_real}")
            f.write(f"accuracy_ideal: {accuracy_ideal}  accuracy_real: {accuracy_real}\n")
            logger.info(f"Leakage detected for input with secret1: {secret1} secret2: {secret2}")
            f.write(f"Leakage detected for input with secret1: {secret1} secret2: {secret2}\n")
        if my_config['run_mode'] == 'identify':
            return True
        start_time = time.time()
        with open(my_config['bug_file'], "a") as f:
            last_fail_length = 0
            last_succ_length = len(views_real1[0])
            full_length = len(views_real1[0])
            while last_succ_length - last_fail_length > 1:
                current_length = (last_succ_length + last_fail_length) // 2
                views_real1 = load_data.get_views_of_corrupted_party_in_real_world(secret1, current_length)
                views_real2 = load_data.get_views_of_corrupted_party_in_real_world(secret2, current_length)
                views_real = views_real1 + views_real2
                accuracy_real, _ = get_real_accuracy(views_real, labels_real)
                logger.info(f"  accuracy_real: {accuracy_real} length: {current_length}") 
                f.write(f"  accuracy_real: {accuracy_real} length: {current_length}\n")
                if accuracy_real > accuracy_ideal + my_config['accuracy_verify_gap']:
                    last_succ_length = current_length
                else:
                    last_fail_length = current_length
            logger.info(f"Leakage detected for input with secret1: {secret1} secret2: {secret2} length: {last_succ_length} full length: {full_length}")
            f.write(f"Leakage detected for input with secret1: {secret1} secret2: {secret2} length: {last_succ_length} full length: {full_length}")
        rerun_with_print_stack_trace(secret1, last_succ_length)
        end_time = time.time()
        timer['vul_location'] += end_time - start_time
        return True
    logger.info("No leakage detected for input")
    return False
        


        