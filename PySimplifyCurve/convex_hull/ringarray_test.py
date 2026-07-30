'''
Created on 2026/07/30

@author: sin
'''

from ringarray import *

if __name__ == '__main__':
    buffer = ringarray()
    for i in range(20):
        buffer.append(i)
    for i in range(-1, -20, -1):
        buffer.appendleft(i)
    print(buffer)
    for i in range(24):
        buffer.pop()
    for i in range(18):
        buffer.append(i)
    print(buffer)
    for i in range(100, 160):
        buffer.appendleft(i)
    print(buffer)