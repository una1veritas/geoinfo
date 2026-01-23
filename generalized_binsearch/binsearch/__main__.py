'''
Created on 2026/01/20

@author: sin
'''
import random

def upper_bound(key, seq):
    lb, ub = 0, len(seq)
    while lb < ub :
        mix = (lb + ub) >> 1
        if seq[mix] <= key :
            lb = mix + 1
        else:
            ub = mix
    return ub

if __name__ == '__main__':
    seq = [random.randint(1,39) for _ in range(39)]
    key = random.randint(0, 40)
    seq = sorted(seq)
    print(f'search {key} in length {len(seq)} sequence {seq}.')
    hint = random.randint(0, len(seq)-1)
    lb = upper_bound(key, seq)
    print(f'lb = {lb}')
    print(f'key = {key}, \n {seq[0:lb]}, {seq[lb:]}')