# !/usr/bin/env python
# coding: utf-8
import random
import hashlib

__author__ = 'zhouhenglc'


def random_assign(total, range_list, span=None):
    """
    :param total:  60
    :param range_list: [
        [10, 100],
        [10, 100],
        [10, 100],
        [10, 13],
    ]
    :param span: 5
    :return:
    """
    final_list = []
    for r in range_list:
        final_list.append(r[0])
        total -= r[0]
        r[1] -= r[0]
        r[0] = 0
    indexs = [i for i in range(len(range_list))]
    if span is None:
        span = total
    while total > 0:
        random.shuffle(indexs)
        no_v = True
        for i in indexs:
            item = range_list[i]
            if item[1] <= 0:
                continue
            if total <= 0:
                break
            no_v = False
            v = random.randint(0, min(item[1], total, span))
            total -= v
            item[1] -= v
            final_list[i] += v
        if no_v:
            break
    return final_list, total


def hashlib_sha1():
    pass


if __name__ == '__main__':
    fl = random_assign(55, [
        [10, 100],
        [10, 100],
        [10, 100],
        [10, 13],
    ], 15)
    print(fl)

