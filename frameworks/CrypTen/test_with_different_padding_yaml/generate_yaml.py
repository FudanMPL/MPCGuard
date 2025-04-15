import os

# 协议列表按类型分类
ass_protocols = ["ass_mul", "ass_eq", "ass_linear", "ass_ltz", "ass_truncpr"]
rss_protocols = ["rss_mul", "rss_linear", "rss_ltz", "rss_eq", "rss_truncpr"]
all_protocols = ass_protocols + rss_protocols

paddings = [1.0, 1.1, 1.3, 1.5, 1.7, 2, 3, 4, 5, 10]

# YAML 模板
yaml_template = """
real_program: ["python", "./test_{proto}.py"]
ideal_program: F_{proto}
party_number: {party_num}
corrupted_party:
  - 0
victim_party: 1
protocol_execution_times: 2000
accuracy_verify_gap: 0.1
use_model: MPCNN
run_mode: identify
bug_file: found_bugs_with_different_padding/{padding}/{proto}
real_view_data_dir: real_view_data/{proto}/
epochs: 200
padding: {padding}
"""

# 创建所有组合的 YAML 文件
for proto in all_protocols:
    party_num = 2 if proto in ass_protocols else 3
    for padding in paddings:
        file_name = f"{proto}_with_{str(padding)}.yaml"
        content = yaml_template.strip().format(proto=proto, padding=str(padding), party_num=party_num)
        with open(file_name, "w") as f:
            f.write(content)

print("✅ Generate all YAML files!")
