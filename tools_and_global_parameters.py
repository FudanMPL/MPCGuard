import logging
import yaml

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# file_handler = logging.FileHandler('DEBUG.log')
# file_handler.setLevel(logging.DEBUG)


info_handler = logging.FileHandler('INFO.log')
info_handler.setLevel(logging.INFO)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# file_handler.setFormatter(formatter)
info_handler.setFormatter(formatter)


logger.addHandler(console_handler)
# logger.addHandler(file_handler)
logger.addHandler(info_handler)


timer = {}
timer['model_train_and_test'] = 0
timer['run_real_protocol'] = 0
timer['vul_location'] = 0
timer['vul_verify'] = 0

my_config = {}

def load_config(file_name):
    global my_config
    with open(file_name, 'r') as f:
        temp_config = yaml.safe_load(f)
        for key in temp_config:
            my_config[key] = temp_config[key]


