#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import crypten
import torch
from crypten.cuda import CUDALongTensor
import my_print_tool

def generate_random_ring_element(size, ring_size=(2**64), generator=None, **kwargs):
    """Helper function to generate a random number from a signed ring"""
    if generator is None:
        device = kwargs.get("device", torch.device("cpu"))
        device = torch.device("cpu") if device is None else device
        device = torch.device(device) if isinstance(device, str) else device
        generator = crypten.generators["local"][device]
    # TODO (brianknott): Check whether this RNG contains the full range we want.
    rand_element = torch.randint(
        -(ring_size // 2),
        (ring_size - 1) // 2,
        size,
        generator=generator,
        dtype=torch.long,
        **kwargs,
    )
    if rand_element.is_cuda:
        return CUDALongTensor(rand_element)
    my_print_tool.my_print_or_match(rand_element, "generate_random_ring_element")
    return rand_element


def generate_kbit_random_tensor(size, bitlength=None, generator=None, **kwargs):
    """Helper function to generate a random k-bit number"""
    if bitlength is None:
        bitlength = torch.iinfo(torch.long).bits
    if bitlength == 64:
        return generate_random_ring_element(size, generator=generator, **kwargs)
    if generator is None:
        device = kwargs.get("device", torch.device("cpu"))
        device = torch.device("cpu") if device is None else device
        device = torch.device(device) if isinstance(device, str) else device
        generator = crypten.generators["local"][device]
    rand_tensor = torch.randint(
        0, 2**bitlength, size, generator=generator, dtype=torch.long, **kwargs
    )
    if rand_tensor.is_cuda:
        return CUDALongTensor(rand_tensor)
    my_print_tool.my_print_or_match(rand_tensor, "generate_kbit_random_tensor")
    return rand_tensor
