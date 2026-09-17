'''
Created on 2026/07/30

@author: sin
'''

from math import *
from ringarray import *

if __name__ == '__main__':
    ring = ringarray()
    for ringlen in range(1, 16):
        for i in range(ringlen):
            theta = 2 * pi / ringlen * (i + 4)
            ring.append(int(5 * (sin(theta) + 2)))
        print(ring)
        # --- Example Usage ---
        
        ix = ring.ternary_search(evfunc = lambda i: ring[i])
        print(f"The maximum element in the ring buffer is: ring[{ix}] = {ring[ix]}")
        # Output: The maximum element in the ring buffer is: 12
        
        ring.clear()
        print()
