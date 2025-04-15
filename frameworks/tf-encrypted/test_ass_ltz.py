"""Example of a simple average using TF Encrypted."""
import argparse
from tqdm import tqdm
import tensorflow as tf

import tf_encrypted as tfe
from tf_encrypted.protocol import ABY3  # noqa:F403,F401
from tf_encrypted.protocol import Pond  # noqa:F403,F401
from tf_encrypted.protocol import SecureNN  # noqa:F403,F401

from tf_encrypted.tensor.fixed import my_fixed

prot = None 
secret = None



# @tfe.local_computation(name_scope="provide_input")
# def provide_input() -> tf.Tensor:
#     # pick random tensor to be averaged
#     tmp = tf.random.normal(shape=(10,))
#     return tmp

# @tfe.local_computation(player_name="result-receiver", name_scope="receive_output")
# def receive_output(average:tf.constant):
#     # simply print average
#     tf.print("Average:", average)





if __name__ == "__main__":
    import subprocess
    command = ["bash", './rss_start.sh']  
    result = subprocess.run(command, capture_output=True, text=True)

    parser = argparse.ArgumentParser(description="Train a TF Encrypted model")
    parser.add_argument(
        "--config",
        metavar="FILE",
        type=str,
        default="./rss_config.json",
        help="path to configuration file",
    )
    parser.add_argument(
        "--try_times",
        metavar="FILE",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--secret",
        metavar="FILE",
        type=int,
        default=123123,
    )
    parser.add_argument(
        "--no-record",
        dest="no_record",
        action="store_true",
    )
    parser.add_argument(
        "--vul_index",
        metavar="FILE",
        type=int,
        default=-1,
    )

    parser.add_argument(
        "--bug_file",
        metavar="FILE",
        type=str
    )
    parser.add_argument(
        "--real_view_data_dir",
        metavar="FILE",
        type=str
    )
    args = parser.parse_args()
    import my_print_tool
    my_print_tool.bug_file = args.bug_file


    my_print_tool.is_record = not args.no_record
    my_print_tool.folder_path = str(args.real_view_data_dir) + "/"
    my_print_tool.init(args.secret)
    my_print_tool.vulnerability_message_idx = args.vul_index




    # set tfe config
    if args.config != "local":
        # config file was specified
        config_file = args.config
        config = tfe.RemoteConfig.load(config_file)
        config.connect_servers()
        tfe.set_config(config)
    else:
        # Always best practice to preset all players to avoid invalid device errors
        config = tfe.LocalConfig(
            player_names=[
                "server0",
                "server1",
                "server2",
                "inputter-0",
                "result-receiver",
            ]
        )
        tfe.set_config(config)

    secret = args.secret
    # set tfe protocol
    prot = globals()['SecureNN'](fixedpoint_config=my_fixed)
    tfe.set_protocol(prot)

    @tfe.local_computation(name_scope="provide_input")
    def provide_input() -> tf.Tensor:
        # pick random tensor to be averaged
        return tf.constant(secret, dtype=tf.int64)


    def test(secret1, secret2=1):
        x = provide_input(player_name="inputter-0")
        import my_print_tool
        with tf.device(prot.server_0.device_name):
            my_print_tool.my_print_or_match(x.share0.value, "input")
        with tf.device(prot.server_1.device_name):
            my_print_tool.my_print_or_match(x.share1.value, "input")

        result = prot.is_negative(x)
        with tf.device(prot.server_0.device_name):
            my_print_tool.my_print_or_match(result.share0.value, "output")
        with tf.device(prot.server_1.device_name):
            my_print_tool.my_print_or_match(result.share0.value, "output")




    for i in tqdm(range(args.try_times)):
        test(args.secret, 1)
        my_print_tool.new_record()


