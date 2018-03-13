# coding=utf-8

"""
Algorithms about probability
Author: 段凯强
"""

import math
import numpy as np


def entropy_of_list(ls):
    """
    Given a list of some items, compute entropy of the list
    The entropy is sum of -p[i]*log(p[i]) for every unique element i in the list, and p[i] is its frequency
    """
    elements = {}
    for e in ls:
        elements[e] = elements.get(e, 0) + 1
    length = float(len(ls))
    return sum(map(lambda v: -v / length * math.log(v / length), elements.values()))


def compute_pmi(total, word_count, left_part_count, right_part_count):
    # print(total, word_count, left_part_count, right_part_count)
    sub_product = left_part_count * right_part_count
    return np.min(np.log2(total * word_count / sub_product))


def entropy(counts):
    if len(counts) == 0:
        return 0
    freqs = counts / np.sum(counts)
    return -np.sum(freqs * np.log2(freqs))
