'''
Created on 2026/07/30

@author: sin
'''

from math import *
from ringarray import *
import random

def strictly_increasing_sequence(low, high, n):
    """
    指定された実数区間 [low, high] から、真に増加する n 個の実数列を確実に生成します。
    (整数サンプリング＆スケーリング方式)
    """
    if n <= 0:
        return []
    if n == 1:
        return [random.uniform(low, high)]
    if low >= high:
        raise ValueError("high は low より大きい値である必要があります。")
        
    # n が非常に大きい場合でもエラーにならないよう、解像度を動的に決定
    # 通常は 10^9（十分な精度）とし、n が大きい場合は n の 100 倍の精度を確保
    resolution = max(10**9, n * 100)
    
    # 0 から resolution までの範囲から重複なしで n 個を確実にサンプリング (O(n))
    sampled_ints = random.sample(range(resolution), n)
    
    # ソートして増加列にする (O(n log n))
    sampled_ints.sort()
    
    # [low, high] の実数区間にマッピング
    width = high - low
    return [low + (x / resolution) * width for x in sampled_ints]

if __name__ == '__main__':
    random.seed(1)
    ring = ringarray()
    for ringlen in range(1, 13):
        d = random.uniform(0, 2* pi)
        for e in strictly_increasing_sequence(0, 2 * pi, ringlen) :
            ring.append(round(10*sin(e), 1))
        print(ring)
        # --- Example Usage ---
        
        ix = ring.ternary_search_max(evfunc = lambda i: ring[i])
        print(f"The maximum element in the ring buffer is: ring[{ix}] = {ring[ix]}")
        # Output: The maximum element in the ring buffer is: 12
        
        ring.clear()
    print()
