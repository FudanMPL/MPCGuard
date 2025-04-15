import math
from scipy.stats import norm
import argparse

def compute_probability(n, thr):
    """
    caculate P(Z ≥ sqrt(2 * n) * thr)，with Z ~ N(0, 1)
    """
    threshold = math.sqrt(2 * n) * thr
    probability = norm.sf(threshold) 
    return probability


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="test a mpc protocol")
    parser.add_argument(
        "--n",
        metavar="FILE",
        type=int,
        default=1000,
        help="number of samples",
    )

    parser.add_argument(
        "--thr",
        metavar="FILE",
        type=float,
        default=0.01,
        help="threshold value",
    )

    args = parser.parse_args()
    n = args.n
    thr = args.thr
    # Calculate the probability
    probability = compute_probability(n, thr)
    print(f"P(Z ≥ sqrt(2 * {n})* {thr}) = {probability}")