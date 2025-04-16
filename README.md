# MPCGuard: Detecting Data Leakage Vulnerabilities in MPC Implementations


This repository contains the source code for the paper **"Is MPC Secure? Leveraging Neural Network Classifiers to Detect Data Leakage Vulnerabilities in MPC Implementations"**, which has been accepted for publication at **IEEE Symposium on Security and Privacy (S&P) 2025**.


MPCGuard is a practical framework designed to detect data leakage vulnerabilities in multi-party computation (MPC) implementations. With the increasing adoption of MPC for privacy-preserving computations, ensuring their security against data leakage vulnerabilities is critical. Unlike traditional security analysis methods that focus on theoretical proofs, MPCGuard employs neural network classifiers to analyze real-world MPC implementations and identify potential vulnerabilities.


## Features

- **Automated Data Leakage Detection**: Utilizes neural network classifiers designed according to MPC characteristics to identify potential data leakage vulnerabilities.
- **Delta-Based Vulnerability Localization**: Efficiently pinpoints the source of leakage within the code.

## Installation

### Requirements
- Docker
- CUDA 12.4 (for GPU acceleration, optional)
- NVIDIA GeForce RTX 3080 (or any CUDA-compatible GPU, optional)


### Setup

Using GPU

```
sudo apt-get install nvidia-container-toolkit
sudo systemctl restart docker
git clone https://github.com/FudanMPL/MPCGuard.git
docker build -t mpcguard .
docker run --gpus all -it mpcguard bash
```

Without using GPU

```
git clone https://github.com/FudanMPL/MPCGuard.git
docker build -t mpcguard .
docker run -it mpcguard bash
```

## Usage

### Supported Frameworks
MPCGuard currently supports:

- **Crypten**
- **TF-Encrypted**
- **MP-SPDZ**

### Testing Specific MPC Implementations

You can test the following protocol without modifying any code:

- `mul` (Multiplication)
- `linear` (Linear Combination)
- `ltz` (Less Than Zero)
- `eqz` (Equal to Zero)
- `truncpr` (Probabilistic Truncation)


#### 1. Test a single implementation (e.g. ass_eq in Crypten)

Step 1. 

```
cd /MPCGuard/frameworks/CrypTen
```

Step 2. Create a yaml file (e.g. test.yaml) with the following content

```
real_program: ["python", "./test_ass_eq.py"]
ideal_program: F_ass_eq # Choice: "F_ass_mul", "F_ass_eq", "F_ass_linear", "F_ass_ltz", "F_ass_truncpr", "F_rss_mul", "F_rss_linear", "F_rss_ltz", "F_rss_eq", "F_rss_truncpr"
party_number: 2
corrupted_party:
  - 0
victim_party: 1
protocol_execution_times: 2000
accuracy_verify_gap: 0.1
use_model: MPCNN # Choice: MPCNN, BasicDNN, BasicCNN, BasicLSTM, xgboost
run_mode: Detect # Choice: Detect (if view exist, do not collect again), All (always re-collect the view)
bug_file: found_bugs_with_different_model/MPCNN/ass_eq
real_view_data_dir: real_view_data/ass_eq/
epochs: 200
```

Step 3. 

```
python ../../main.py --config=./test.yaml
```


#### 2. Test with different models 


```sh
cd /MPCGuard
./test_with_different_models.sh
```

The found bugs will be stored in /MPCGuard/frameworks/Crypten/found_bugs_with_different_model/, /MPCGuard/frameworks/TF-Encrypted/found_bugs_with_different_model/, and /MPCGuard/frameworks/MP-SPDZ/found_bugs_with_different_model/


#### 3. Test with different thresholds 


```sh
cd /MPCGuard
./test_with_different_thresholds.sh
```

The found bugs will be stored in /MPCGuard/frameworks/Crypten/found_bugs_with_different_threshold/, /MPCGuard/frameworks/TF-Encrypted/found_bugs_with_different_threshold/, and /MPCGuard/frameworks/MP-SPDZ/found_bugs_with_different_threshold/

#### 4. Test with different paddings 


```
cd /MPCGuard
./test_with_different_paddings.sh
```

The found bugs will be stored in /MPCGuard/frameworks/Crypten/found_bugs_with_different_padding/, /MPCGuard/frameworks/TF-Encrypted/found_bugs_with_different_padding/, and /MPCGuard/frameworks/MP-SPDZ/found_bugs_with_different_padding/


#### 5. Test a new implementation 

Step 1. Place your implementation in /MPCGuard/frameworks/[framework_name]/, and 

```
cd /MPCGuard/frameworks/[framework_name]/
```


Step 2. Write a python program (e.g. test_new_protocol.py) that accepts the following arguments:

```
--try_times           # Number of executions to collect views
--secret              # Input secret value
--no-record           # Skip recording views/inputs/outputs
--vul_index           # Minimum adversary view length for leakage detection
--bug_file            # Path to save bug info
--real_view_data_dir  # Path to save collected views
```

After executing test_new_protocol.py with the above parameters, it should be able to collect the the parties' view, input and output. See ```MPCGuard/frameworks/MP-SPDZ/test_with_different_model_yaml/ass_eq_with_MPCNN.yaml``` for reference.

Step 3. Create the corresponding functionality in ```/MPCGuard/functionality.py```

For example, 

```
def F_ass_linear(secret, a=1, b=2, c=3):
    shares_x = generate_ass_shares(secret)

    # Convert constants and reconstruct x and y from shares using numpy arrays
    a = np.array(a, dtype=np.int64)
    b = np.array(b, dtype=np.int64)
    c = np.array(c, dtype=np.int64)
    x = sum(np.array(shares_x, dtype=np.int64))
    
    shares_y = [1 for i in range(len(shares_x))]
    y = sum(np.array(shares_y, dtype=np.int64))
    
    # Compute z = a*x + b*y + c
    z = a * x + b * y + c
    shares_z = generate_ass_shares(z)
    ass_functionality_record(secret, shares_x, shares_z)
```


Step 4. Create a yaml file (e.g. test.yaml) with the following content

```
real_program: ["python", "./test_new_protocol.py"]
ideal_program: F_ass_linear
party_number: 2
corrupted_party:
  - 0
victim_party: 1
protocol_execution_times: 2000
accuracy_verify_gap: 0.1
use_model: MPCNN # Choice: MPCNN, BasicDNN, BasicCNN, BasicLSTM, xgboost
run_mode: Detect # Choice: Detect (if view exist, do not collect again), All (always re-collect the view)
bug_file: found_bugs_with_different_model/MPCNN/ass_eq
real_view_data_dir: real_view_data/ass_eq/
epochs: 200
```

Step 4. Run


```
python ../../main.py --config=./test.yaml
```


## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---
For any questions or contributions, please open an issue or submit a pull request!

