# MPCGuard: Detecting Data Leakage Vulnerabilities in MPC Implementations

## Overview

This repository contains the source code for the paper **"Is MPC Secure? Leveraging Neural Network Classifiers to Detect Data Leakage Vulnerabilities in MPC Implementations"**, which has been accepted for publication at **IEEE Symposium on Security and Privacy (S&P) 2025**.


MPCGuard is a practical framework designed to detect data leakage vulnerabilities in multi-party computation (MPC) implementations. With the increasing adoption of MPC for privacy-preserving computations, ensuring their security against data leakage vulnerabilities is critical. Unlike traditional security analysis methods that focus on theoretical proofs, MPCGuard employs neural network classifiers to analyze real-world MPC implementations and identify potential vulnerabilities.


## Features

- **Automated Data Leakage Detection**: Utilizes neural network classifiers designed according to MPC characteristics to identify potential data leakage vulnerabilities.
- **Delta-Based Vulnerability Localization**: Efficiently pinpoints the source of leakage within the code.

## Installation

### Requirements
- Python 3.10+
- PyTorch
- CUDA 12.4 (for GPU acceleration, optional)
- NVIDIA GeForce RTX 3080 (or any CUDA-compatible GPU, optional)


### Setup
```
coming soon...
```

## Usage

### Running MPCGuard

```sh
coming soon...
```

### Supported Frameworks
MPCGuard currently supports:
- **Crypten**
- **TF-Encrypted**
- **MP-SPDZ**

### Testing Specific MPC Implementations
You can test specific MPC protocols by specifying the protocol name. Supported protocols include:
- `mul` (Multiplication)
- `linear` (Linear Combination)
- `ltz` (Less Than Zero)
- `eqz` (Equal to Zero)
- `truncpr` (Probabilistic Truncation)



## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---
For any questions or contributions, please open an issue or submit a pull request!

