import os
import shutil
import tensorflow as tf




is_record = True
view_files = {}
output_files = {}
input_files = {}
vulnerability_message_idx = None
pid = None
try_time = 0
count = 0
bug_file = None

folder_path = None
secret = None

idx = 0

def init(s):
    if not is_record:
        return
    global folder_path
    global try_time 
    global secret
    try_time = 0
    secret = s
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)

def new_record():
    if not is_record:
        return
    global try_time
    global input_files
    global output_files
    global view_files
    global count 
    try_time += 1
    if len(view_files) != 0 is not None:
        view_files = {}
        input_files = {}
        output_files = {}
    count = 0


def get_my_pid():
    tmp = tf.constant([1])
    device_name = tmp.device
    if device_name:
        components = device_name.split('/')
        for comp in components:
            if 'task:' in comp:
                # 提取 'task:' 后的序号
                task_number = comp.split('task:')[1]
                return int(task_number)
    raise RuntimeError("no pid detected")



def my_print_or_match(data, name=None):
    global view_files
    global try_time
    global input_files
    global output_files
    global view_files
    global count

    pid = get_my_pid()
    print_datas = []
    # if data is tf.tensor, convert it to list
    if isinstance(data, tf.Tensor):
        print_datas = data.numpy().tolist()
    
    global is_record
    if is_record:
        if pid not in view_files:
            view_files[pid] = open(f"{folder_path}/P-{pid}-view-{try_time}", "w")
            input_files[pid] = open(f"{folder_path}/P-{pid}-input-{try_time}", "w")
            output_files[pid] = open(f"{folder_path}/P-{pid}-output-{try_time}", "w")
    elif pid == 0:
        add_length = count_len(print_datas)
        if count < vulnerability_message_idx and  count + add_length >= vulnerability_message_idx:
            # print stack trace
            import traceback
            traceback.print_stack()
            # print stack trace to bug file
            with open(bug_file, "a") as f:
                traceback.print_stack(file=f)
        count = count + add_length
    recursive_print_list(print_datas, pid, name)

def count_len(l):
    if isinstance(l, list):
        count = 0
        for i in l:
            count += count_len(i)
        return count
    else:
        return 1


def recursive_print_list(l, pid, name=None):
    global idx
    global is_record
    if isinstance(l, list):
        for i in l:
            recursive_print_list(i, pid, name)
    else:
        l = int(l)
        if is_record:
            view_files[pid].write(str(l) + "\n")
            view_files[pid].flush()
            if name == "output":
                output_files[pid].write(str(l) + "\n")
                output_files[pid].flush()
            if name == "input":
                input_files[pid].write(str(l) + "\n")
                input_files[pid].flush()
        # if pid == 0:
        #     idx = idx + 1
        #     print("idx ", idx, "name: ", name, "data: ", l, flush=True)
     
