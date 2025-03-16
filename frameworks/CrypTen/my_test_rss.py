import torch
import crypten
import crypten.mpc as mpc
import crypten.communicator as comm 
import sys
from tqdm import tqdm

import my_print_tool


@mpc.run_multiprocess(world_size=3)
def test_linear(x = 10, y = 3):
    a = 1
    b = 2
    c = 30
    x_enc = crypten.cryptensor([x], ptype=crypten.mpc.arithmetic, src=1)
    my_print_tool.my_print_or_match(x_enc.data, "input")
    y_enc = crypten.cryptensor([3], ptype=crypten.mpc.arithmetic, src=1)
    y_enc.data = torch.tensor([1])
    z_enc = a * x_enc + b * y_enc + c
    from crypten.mpc.primitives.replicated import replicate_shares
    z_rss_share = replicate_shares([z_enc.share])
    my_print_tool.my_print_or_match(z_enc.data, "output")


@mpc.run_multiprocess(world_size=3)
def test_mul(x = 10, y = 3):
    x_enc = crypten.cryptensor([x], ptype=crypten.mpc.arithmetic, src=1)
    my_print_tool.my_print_or_match(x_enc.data, "input")
    y_enc = crypten.cryptensor([3], ptype=crypten.mpc.arithmetic, src=1)
    y_enc.data = torch.tensor([1])
    z_enc = x_enc * y_enc
    from crypten.mpc.primitives.replicated import replicate_shares
    z_rss_share = replicate_shares([z_enc.share])
    my_print_tool.my_print_or_match(z_enc.data, "output")



@mpc.run_multiprocess(world_size=3)
def test_truncp(x = 1100000):
    x_enc = crypten.cryptensor([x], ptype=crypten.mpc.arithmetic, src=1)
    my_print_tool.my_print_or_match(x_enc.data, "input")
    z_enc = x_enc.div(2 ** 10) 
    from crypten.mpc.primitives.replicated import replicate_shares
    z_rss_share = replicate_shares([z_enc.share])
    my_print_tool.my_print_or_match(z_enc.data, "output")
  

@mpc.run_multiprocess(world_size=3)
def test_ltz(x = 1100000):
    x_enc = crypten.cryptensor([x], ptype=crypten.mpc.arithmetic, src=1)
    my_print_tool.my_print_or_match(x_enc.data, "input")
    z_enc = x_enc < 0
    my_print_tool.my_print_or_match(z_enc.data, "output")



@mpc.run_multiprocess(world_size=3)
def test_share(x = 1100000):
    x_enc = crypten.cryptensor([x], ptype=crypten.mpc.arithmetic, src=1)
    my_print_tool.my_print_or_match(x_enc.data, "input")


@mpc.run_multiprocess(world_size=3)
def test_reconstruct(x = 1100000):
    x_enc = crypten.cryptensor([x], ptype=crypten.mpc.arithmetic, src=1)
    x = x_enc.get_plain_text()





if __name__ == "__main__":
    from crypten.config import cfg
    cfg.mpc.protocol = "replicated"
    secret = int(sys.argv[1])
    try_times = int(sys.argv[2])
    if len(sys.argv) > 3:
        my_print_tool.vulnerability_message_idx = int(sys.argv[3])
        my_print_tool.is_record = False
    my_print_tool.init(secret)
    for i in tqdm(range(try_times)):
        test_ltz(secret)
        my_print_tool.new_record()
  
        


