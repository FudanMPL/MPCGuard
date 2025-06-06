import os
import subprocess

def execute_protocol(commands):
    outputs = []
    for p, command in enumerate(commands):
        result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        outputs.append(result)
        if not get_data_from_output_str(result, folder_path+"P-{}-{}-"+str(i)):
            return None
    return outputs

def get_data_from_output_str(output, path_format):
    lines = output.split("\n")
    for line in lines:
        tmp = line.split(" ")
        if tmp[0] != "from" or len(tmp) != 3:
            continue

        if tmp[1] == "input" or tmp[1] == "output":
            if tmp[2].find(",") != -1:
                data = tmp[2].split(",")[0]
            else:
                data = tmp[2]
            try:
                data = int(data)
            except Exception as e:
                print(e)
                print(line)
                continue
            filename = path_format.format(tmp[1])
            with open(filename, "a") as f:
                f.write(str(data)+"\n")
        else:
            filename = path_format.format("view")
            data = tmp[2]
            try:
                data = int(data)
            except Exception as e:
                print(e)
                print(line)
                continue
            with open(filename, "a") as f:
                f.write(str(data)+"\n")
    # if file do not exist, return False
    if not os.path.exists(path_format.format("input")) or not os.path.exists(path_format.format("output")) or not os.path.exists(path_format.format("view")):
        return False
    return True

    