import os


paddings = [1.0, 1.1, 1.3, 1.5, 1.7, 2, 3, 4, 5, 10]

# 框架路径
frameworks = [
    "frameworks/MP-SPDZ/found_bugs_with_different_padding",
    "frameworks/CrypTen/found_bugs_with_different_padding",
    "frameworks/tf-encrypted/found_bugs_with_different_padding"
]

for threshold in paddings:
    threshold_str = str(threshold)
    threshold_total = 0
    for framework_path in frameworks:
        full_path = os.path.join(framework_path, threshold_str)
        if os.path.exists(full_path):
            num_files = len([
                f for f in os.listdir(full_path)
                if os.path.isfile(os.path.join(full_path, f))
            ])
        else:
            num_files = 0
        threshold_total += num_files
    print(f"Padding {threshold_str}: total {threshold_total} files")
