import argparse
import os
from tqdm import tqdm
import subprocess
import shutil


from test_data_process_tool import *



    


# if main 
if __name__ == '__main__':
    command = ['python', './compile.py', '-R', '64', 'linear']  
    result = subprocess.run(command, capture_output=True, text=True)

    parser = argparse.ArgumentParser(description="Train a TF Encrypted model")
    parser.add_argument(
        "--dir",
        metavar="FILE",
        type=str,
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
    args = parser.parse_args()
    bug_file = args.bug_file
    # set envirnment variables SECRET, NO_RECORD, VUL_INDEX
    os.environ["SECRET"] = str(args.secret)
    folder_path = "./real-data/ass_linear/s-"+str(args.secret)+"/"
    if args.no_record:
        os.environ["NO_RECORD"] = str(args.no_record)
    else:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

    os.environ["VUL_INDEX"] = str(args.vul_index)

    os.environ["FOLDER_PATH"] = folder_path
    os.makedirs(folder_path, exist_ok=True)
    # write secret to Player-Data/Input-P1-0
    with open("Player-Data/Input-P1-0", "w") as f:
        f.write(str(args.secret)+"\n")
    for i in tqdm(range(args.try_times)):
        # set envirnment variables FILE_ID
        os.environ["FILE_ID"] = str(i)
        command0 = ["./semi2k-party.x", "0", "linear", "-OF", ".", "-pn", "14752", "-h", "localhost",  "-b", "1", "-B", "3"]
        command1 = ["./semi2k-party.x", "1", "linear", "-OF", ".", "-pn", "14752", "-h", "localhost",  "-b", "1", "-B", "3"]
        command2 = ["./semi2k-party.x", "2", "linear", "-OF", ".", "-pn", "14752", "-h", "localhost",  "-b", "1", "-B", "3"]
        process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        output0, _ = process0.communicate()
        output1, _ = process1.communicate()
        output2, _ = process2.communicate()


        get_data_from_output_str(output0, folder_path+"P-0-{}-"+str(i))
        get_data_from_output_str(output1, folder_path+"P-1-{}-"+str(i))
        get_data_from_output_str(output2, folder_path+"P-2-{}-"+str(i))


        if output0.find("==============") != -1:
            tmp = output0.split("==============")

            with open(bug_file, "a") as f:
                f.write("\n")
                f.write(tmp[1])