import os

# 阈值列表
thresholds = [0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.4, 0.5]

# 框架路径
frameworks = [
    "frameworks/MP-SPDZ/found_bugs_with_different_threshold",
    "frameworks/CrypTen/found_bugs_with_different_threshold",
    "frameworks/tf-encrypted/found_bugs_with_different_threshold"
]

for threshold in thresholds:
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
    print(f"Threshold {threshold_str}: total {threshold_total} files")
