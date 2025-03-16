import crypten
import torch
import os
import shutil

is_record = True
view_file = None
output_file = None
input_file = None
vulnerability_message_idx = None
bug_file = None

count = 0

folder_path = "./real-data"
secret = None


def init(s):
    if not is_record:
        return
    global folder_path
    global try_time 
    global secret
    try_time = 0
    secret = s
    os.makedirs(folder_path, exist_ok=True)

def new_record():
    if not is_record:
        return
    global try_time
    global input_file
    global output_file
    global view_file
    global count 
    try_time += 1
    if view_file is not None:
        view_file.close()
        input_file.close()
        output_file.close()
    view_file = None
    input_file = None
    output_file = None
    count = 0


def my_print_or_match(data, name=None):
    global view_file
    global try_time
    global input_file
    global output_file
    global view_file
    global count
    global is_record
    import crypten.communicator as comm 
    rank = crypten.communicator.get().get_rank()
    if is_record and view_file is None:
        view_file = open(f"{folder_path}/P-{rank}-view-{try_time}", "w")
        input_file = open(f"{folder_path}/P-{rank}-input-{try_time}", "w")
        output_file = open(f"{folder_path}/P-{rank}-output-{try_time}", "w")
    print_datas = []
    if isinstance(data, torch.Tensor):
        if data.numel() == 0:
            return
        if data.numel() == 1:
            print_datas.append(data.item())
        else:
            print_datas = data.tolist()

    if is_record:
        recursive_print_list(print_datas, name)
    elif rank == 0:
        if count < vulnerability_message_idx and  count + count_len(print_datas) >= vulnerability_message_idx:
            # print stack trace
            import traceback
            traceback.print_stack()
            with open(bug_file, "a") as f:
                traceback.print_stack(file=f)
        count = count + count_len(print_datas)

def count_len(l):
    if isinstance(l, list):
        count = 0
        for i in l:
            count += count_len(i)
        return count
    else:
        return 1


def recursive_print_list(l, name=None):
    if isinstance(l, list):
        for i in l:
            recursive_print_list(i, name)
    else:
        # rank = crypten.communicator.get().get_rank()
        # crypten.print(f"\nRank {rank}: {l} from {name}\n", in_order=True)
        view_file.write(str(l) + "\n")
        view_file.flush()
        if name == "output":
            output_file.write(str(l) + "\n")
            output_file.flush()
        if name == "input":
            input_file.write(str(l) + "\n")
            input_file.flush()