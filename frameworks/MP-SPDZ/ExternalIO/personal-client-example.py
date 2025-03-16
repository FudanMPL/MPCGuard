#!/usr/bin/python3

import sys, random

sys.path.insert(0, 'ExternalIO')

from client import *

party = int(sys.argv[1])

client = Client(['localhost'], 15000 + party, 0)

n = 1000

if party < 2:
    client.send_public_inputs(random.gauss(0, 1) * 2 ** 16 for i in range(n))

x = [client.receive_plain_values() for i in range(2)]
client.send_public_inputs(a + b for a, b in zip(*x))
