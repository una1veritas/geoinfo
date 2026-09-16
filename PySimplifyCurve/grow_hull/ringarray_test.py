'''
Created on 2026/07/30

@author: sin
'''

from math import *
from ringarray import *


def ternary_search_ring(arr):
    if not arr:
        return None
        
    n = len(arr)
    if n == 1:
        return 0

    low = 0
    high = n - 1

    while low <= high:
        # Small interval fallback: safe linear scan over the active window
        if high - low < 3:
            maxix = low
            for i in range(low, high + 1):
                if arr[i] > arr[maxix]:
                    maxix = i
            return maxix  # Returns the raw index (handled by your container)

        # Calculate the two standard internal midpoints
        m1 = low + (high - low) // 3
        m2 = high - (high - low) // 3

        # Read the 4 tracking points directly via your container object
        v_low = arr[low]
        v_m1 = arr[m1]
        v_m2 = arr[m2]
        v_high = arr[high]

        # DETECT VALLEY: If both middle values are lower than the outer edges,
        # the peak is wrapping around the outside of the current window.
        if v_m1 < v_low and v_m2 < v_high:
            if v_low > v_high:
                high = m2 - 1  # Peak is closer to 'low', discard the right side
            else:
                low = m1 + 1   # Peak is closer to 'high', discard the left side
                
        # Standard Ternary Search for Maxima
        elif v_m1 < v_m2:
            low = m1 + 1       # Right side is higher; discard left
        elif v_m1 > v_m2:
            high = m2 - 1      # Left side is higher; discard right
        else:
            # Handles plateau or flat valley floors where v_m1 == v_m2
            if v_low > v_m1:   
                # It's a valley floor, meaning the peak is outside
                if v_low > v_high:
                    high = m2 - 1
                else:
                    low = m1 + 1
            else:
                # Normal flat peak, narrow down both sides
                low = m1 + 1
                high = m2 - 1

    return low


if __name__ == '__main__':
    ring = ringarray()
    for ringlen in range(1, 16):
        for i in range(ringlen):
            theta = 2 * pi / ringlen * (i + 4)
            ring.append(int(10 * sin(theta)))
        print(ring)
        # --- Example Usage ---
        
        ix = ternary_search_ring(ring)
        print(f"The maximum element in the ring buffer is: ring[{ix}] = {ring[ix]}")
        # Output: The maximum element in the ring buffer is: 12
        
        ring.clear()
        print()
