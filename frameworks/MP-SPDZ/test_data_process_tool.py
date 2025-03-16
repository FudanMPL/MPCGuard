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
            with open(filename, "w") as f:
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


    