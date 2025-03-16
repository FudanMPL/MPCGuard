import load_data
from dataset_verify import *
from load_data import *
import config
import functionality

config.ideal_protocol_functionality = functionality.F_ass_mul
config.number_of_party = 2

secret = 1049088
# run_ideal_protocol(secret)
# views_ideal = load_data.get_views_of_corrupted_party_in_ideal_world(secret)
# output_share_of_victim_party_ideal = load_data.get_output_share_of_victim_party_in_ideal_world(secret)
# labels_ideal = [share % 2 for share in output_share_of_victim_party_ideal]
# accuracy_ideal, _ = get_ideal_accuracy(views_ideal, labels_ideal)
# logger.info(f"  accuracy_ideal: {accuracy_ideal}")



config.real_data_dir = "./real-data/ass_ltz/"
views_real = load_data.get_views_of_corrupted_party_in_real_world(secret)
output_share_of_victim_party_real = load_data.get_outputs_of_victim_party_in_real_world(secret)
labels_real = [share % 2 for share in output_share_of_victim_party_real]
accuracy_real, _ = get_real_accuracy(views_real, labels_real)
logger.info(f"  accuracy_real: {accuracy_real}")
logger.info(f"  time: {config.times['model_train_and_test']}")
