import numpy as np
import random
from tools_and_global_parameters import *

from load_data import adversary_views_in_ideal_world, input_shares_in_ideal_world, output_shares_in_ideal_world

def generate_element_in_ring():
    return np.random.randint(-2**63, 2**63, dtype=np.int64)


def generate_ass_shares(secret):
    secret = np.array(secret, dtype=np.int64)
    # Generate random shares of a secret
    shares = []
    for i in range(my_config['party_number'] - 1):
        random_share = generate_element_in_ring()
        shares.append(random_share)
    shares.append(secret - sum(shares))
    return shares



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


def F_ass_mul(secret):
    shares_x = generate_ass_shares(secret)
    # Reconstruct x and y using numpy arrays
    x = sum(np.array(shares_x, dtype=np.int64))
    
    shares_y = [1 for i in range(len(shares_x))]
    y = sum(np.array(shares_y, dtype=np.int64))
    
    # Compute z = x * y
    z = x * y
    
    shares_z = generate_ass_shares(z)
    ass_functionality_record(secret, shares_x, shares_z)


def F_ass_ltz(secret):
    shares_x = generate_ass_shares(secret)
    # Reconstruct x
    x = sum(np.array(shares_x, dtype=np.int64))
    
    # Compute z = x < 0
    z = int(x < 0)  # Convert boolean to int
    
    shares_z = generate_ass_shares(z)
    ass_functionality_record(secret, shares_x, shares_z)


def F_ass_eq(secret):
    shares_x = generate_ass_shares(secret)
    # Reconstruct x
    x = sum(np.array(shares_x, dtype=np.int64))
    
    # Compute z = x < 0
    z = int(x == 0)  # Convert boolean to int
    
    shares_z = generate_ass_shares(z)
    ass_functionality_record(secret, shares_x, shares_z)


def F_ass_truncpr(secret, f=10):
    shares_x = generate_ass_shares(secret)
    # Reconstruct x
    x = sum(np.array(shares_x, dtype=np.int64))
    
    # Compute x_f and x^f
    x_f = x & ((1 << f) - 1)
    x_to_f = x >> f
    
    rand_numb = np.abs(np.random.randint(0, 2**f, dtype=np.int64))
    
    # Randomly sample z based on x_f
    if rand_numb < abs(x_f):
        z = x_to_f + 1
    else:
        z = x_to_f
    
    shares_z = generate_ass_shares(z)
    ass_functionality_record(secret, shares_x, shares_z)



def F_ass_and(secret):
    shares_x = generate_ass_shares(secret)
    # Reconstruct x and y using numpy arrays
    x = sum(np.array(shares_x, dtype=np.int64))
    if shares_y is None:
        shares_y = [-1 for i in range(len(shares_x))]
    y = sum(np.array(shares_y, dtype=np.int64))
    z = x & y
    shares_z = generate_ass_shares(z)
    ass_functionality_record(secret, shares_x, shares_z)


def ass_functionality_record(secret, shares_x, shares_z):
    adversary_view = []
    for party in my_config['corrupted_party']:
        for j in range(4):
            adversary_view.append(generate_element_in_ring())
        adversary_view.append(shares_x[party])
        adversary_view.append(shares_z[party]) 
    adversary_views_in_ideal_world[secret].append(adversary_view)
    input_shares_in_ideal_world[secret].append(shares_x)
    output_shares_in_ideal_world[secret].append(shares_z)






def generate_rss_shares(secret):
    assert my_config['party_number'] == 3
    secret = np.array(secret, dtype=np.int64)
    # Generate random shares of a secret
    shares = []
    for i in range(my_config['party_number'] - 1):
        random_share = generate_element_in_ring()
        shares.append(random_share)
    shares.append(secret - sum(shares))
    return shares





def F_rss_linear(secret, a=1, b=2, c=3):
    shares_x = generate_rss_shares(secret)
    # Convert constants and reconstruct x and y from shares using numpy arrays
    a = np.array(a, dtype=np.int64)
    b = np.array(b, dtype=np.int64)
    c = np.array(c, dtype=np.int64)
    x = sum(np.array(shares_x, dtype=np.int64))
    
    shares_y = [1 for i in range(len(shares_x))]
    y = sum(np.array(shares_y, dtype=np.int64))
    
    # Compute z = a*x + b*y + c
    z = a * x + b * y + c
    
    shares_z = generate_rss_shares(z)
    rss_functionality_record(secret, shares_x, shares_z)


def F_rss_mul(secret):
    shares_x = generate_rss_shares(secret)
    # Reconstruct x and y using numpy arrays
    x = sum(np.array(shares_x, dtype=np.int64))
    
    shares_y = [1 for i in range(len(shares_x))]
    y = sum(np.array(shares_y, dtype=np.int64))
    
    # Compute z = x * y
    z = x * y
    
    shares_z = generate_rss_shares(z)
    rss_functionality_record(secret, shares_x, shares_z)


def F_rss_ltz(secret):
    shares_x = generate_rss_shares(secret)
    # Reconstruct x
    x = sum(np.array(shares_x, dtype=np.int64))
    
    # Compute z = x < 0
    z = int(x < 0)  # Convert boolean to int
    
    shares_z = generate_rss_shares(z)
    rss_functionality_record(secret, shares_x, shares_z)


def F_rss_eq(secret):
    shares_x = generate_rss_shares(secret)
    # Reconstruct x
    x = sum(np.array(shares_x, dtype=np.int64))
    
    # Compute z = x < 0
    z = int(x == 0)  # Convert boolean to int
    
    shares_z = generate_rss_shares(z)
    rss_functionality_record(secret, shares_x, shares_z)


def F_rss_truncpr(secret, f=10):
    shares_x = generate_rss_shares(secret)
    # Reconstruct x
    x = sum(np.array(shares_x, dtype=np.int64))
    
    # Compute x_f and x^f
    x_f = x & ((1 << f) - 1)
    x_to_f = x >> f
    
    rand_numb = np.abs(np.random.randint(0, 2**f, dtype=np.int64))
    
    # Randomly sample z based on x_f
    if rand_numb < abs(x_f):
        z = x_to_f + 1
    else:
        z = x_to_f
    
    shares_z = generate_rss_shares(z)
    rss_functionality_record(secret, shares_x, shares_z)





def F_rss_and(secret):
    shares_x = generate_rss_shares(secret)
    # Reconstruct x and y using numpy arrays
    x = sum(np.array(shares_x, dtype=np.int64))
    if shares_y is None:
        shares_y = [-1 for i in range(len(shares_x))]
    y = sum(np.array(shares_y, dtype=np.int64))
    z = x & y
    shares_z = generate_rss_shares(z)
    rss_functionality_record(secret, shares_x, shares_z)


def rss_functionality_record(secret, shares_x, shares_z):
    adversary_view = []
    for party in my_config['corrupted_party']:
        # for j in range(1):
        #     adversary_view.append(generate_element_in_ring())
        adversary_view.append(shares_x[(party-1) % 3])
        adversary_view.append(shares_x[party])
        adversary_view.append(shares_z[(party-1) % 3]) 
        adversary_view.append(shares_z[party])
    adversary_views_in_ideal_world[secret].append(adversary_view)
    input_shares_in_ideal_world[secret].append(shares_x)
    output_shares_in_ideal_world[secret].append(shares_z)




