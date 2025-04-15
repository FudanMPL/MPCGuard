import os

# 协议列表按类型分类
ass_protocols = ["ass_mul", "ass_eq", "ass_linear", "ass_ltz", "ass_truncpr"]
rss_protocols = ["rss_mul", "rss_linear", "rss_ltz", "rss_eq", "rss_truncpr"]
all_protocols = ass_protocols + rss_protocols

thresholds = [0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3, 0.4, 0.5]

# YAML 模板
yaml_template = """
real_program: ["python", "./test_{proto}.py"]
ideal_program: F_{proto}
party_number: {party_num}
corrupted_party:
  - 0
victim_party: 1
protocol_execution_times: 2000
accuracy_verify_gap: {threshold}
use_model: MPCNN
run_mode: identify
bug_file: found_bugs_with_different_threshold/{threshold}/{proto}
real_view_data_dir: real_view_data/{proto}/
epochs: 200
"""

# 创建所有组合的 YAML 文件
for proto in all_protocols:
    party_num = 2 if proto in ass_protocols else 3
    for thr in thresholds:
        file_name = f"{proto}_with_{str(thr)}.yaml"
        content = yaml_template.strip().format(proto=proto, threshold=str(thr), party_num=party_num)
        with open(file_name, "w") as f:
            f.write(content)

print("✅ Generate all YAML files!")
