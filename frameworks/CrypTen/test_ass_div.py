import torch
import crypten
import crypten.mpc as mpc
import crypten.communicator as comm 
import sys
from tqdm import tqdm
import argparse

import my_print_tool



@mpc.run_multiprocess(world_size=2)
def test(x = 10, y = 3):
    x_enc = crypten.cryptensor([x], ptype=crypten.mpc.arithmetic, src=1)
    my_print_tool.my_print_or_match(x_enc.data, "input")
    y_enc = crypten.cryptensor([3], ptype=crypten.mpc.arithmetic, src=1)
    y_enc.data = torch.tensor([1])
    z_enc = x_enc / y_enc
    my_print_tool.my_print_or_match(z_enc.data, "output")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a TF Encrypted model")
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
        "--bug_dir",
        metavar="FILE",
        type=str,
        default="bugs",
    )

    args = parser.parse_args()
    my_print_tool.bug_file = args.bug_dir + "bug_in_ass_div.txt"

    my_print_tool.folder_path = f"./real-data/ass_div/s-{args.secret}"
  
    if args.no_record:
        my_print_tool.vulnerability_message_idx = args.vul_index
        my_print_tool.is_record = False
    my_print_tool.init(args.secret)
    for i in tqdm(range(args.try_times)):
        test(args.secret)
        my_print_tool.new_record()
  
        


