'''
Created on 2026/07/30

@author: sin
'''

from math import *
from ringarray import *

def cut_point(arr, evalfunc):
    n = len(arr)
    point0 = 0
    point1 = point0 + (n) // 3
    point2 = point1 + (n - point1) // 2
    print(f'length = {n}, points = {point0}, {point1}, {point2}')
    if arr[point0] <= arr[point1] and arr[point0] <= arr[point2] :
        point = point0
    elif arr[point1] <= arr[point0] and arr[point1] <= arr[point2] :
        point = point0
    elif arr[point2] <= arr[point0] and arr[point2] <= arr[point1] :
        point = point2
    return (point, n + point - 1)

if __name__ == '__main__':
    ring = ringarray()
    for ringlen in range(1, 10):
        for i in range(ringlen):
            theta = 2 * pi * (i + 0) / ringlen
            ring.append(int(10 * cos(theta)))
        print(ring)
        left, right = cut_point(ring, lambda x: x)
        print(f'cut_point = {(left, right)}, ring[left:right+1] = [', end='')
        for i in range(left, right + 1):
            print(f'{ring[i]}', end=", ")
        print(']')
        ring.clear()
