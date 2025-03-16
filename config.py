import logging


logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('DEBUG.log')
file_handler.setLevel(logging.DEBUG)


info_handler = logging.FileHandler('INFO.log')
info_handler.setLevel(logging.INFO)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
info_handler.setFormatter(formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(info_handler)


run_mode = "run"

number_of_epoch = 200
number_of_iterations_to_get_mean_acc = 1

corrupted_party = [0]
victim_party = 1
collection_data_size = 2000
ideal_collection_data_size = 2000
number_of_random_to_try = 1
accuracy_verify_gap = 0.1
number_of_party = None


real_protocol_execute_program = None
ideal_protocol_functionality = None
real_data_dir = None

bug_file = None
current_name = None


times = {}
times['model_train_and_test'] = 0
times['run_real_protocol'] = 0
times['vul_location'] = 0
times['vul_verify'] = 0