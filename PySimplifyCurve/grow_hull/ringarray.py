'''
Created on 2026/03/17

@author: sin
'''

from math import log2, ceil

class ringarray:
    INITIAL_CAPACITY = 16
    
    def __init__(self, initcapacity = None):
        try:
            initcapacity = int(initcapacity)
        except (ValueError, TypeError):
            initcapacity = ringarray.INITIAL_CAPACITY
        self.capacity = 1 << (max(initcapacity, ringarray.INITIAL_CAPACITY) - 1).bit_length()
        self.array = [None] * self.capacity
        self.tail = 0
        self.head = 0
        self.length = 0
    
    def __len__(self):
        return self.length
    
    def array_head(self):
        return self.array[0]
    
    def double_capacity(self):
        self.array += ([None] * self.capacity)
        #print('before move', self)
        if self.tail <= self.head :
            #print('copying!')
            for ix in range(self.tail):
                #print(f'moving from {ix} to {self.capacity + ix}')
                self.array[self.capacity + ix] = self.array[ix]
            self.tail += self.capacity
        self.capacity <<= 1
        return 
    
    def append(self, elem):
        if not (self.length < self.capacity) :
            self.double_capacity()
        
        self.array[self.tail] = elem
        self.tail += 1
        self.tail &= (self.capacity - 1)
        self.length += 1
    
    def appendleft(self, elem):
        if not (self.length < self.capacity) :
            self.double_capacity()

        self.head += self.capacity - 1
        self.head &= (self.capacity - 1)
        self.array[self.head] = elem
        self.length += 1
    
    def pop(self):
        if self.length > 0 :
            self.tail += self.capacity - 1
            self.tail &= self.capacity - 1
            self.length -= 1
            return self.array[self.tail]
        else:
            raise ValueError(f'tried pop to empty queue')
        
    def popleft(self):
        if self.length > 0 :
            val = self.array[self.head]
            self.head += 1
            self.head &= self.capacity - 1
            self.length -= 1
            return val
        else:
            raise ValueError(f'tried pop to empty queue')

    def __getitem__(self, index):
        index %= self.length
        pos = self.head + index
        pos &= (self.capacity - 1)
        return self.array[pos]
    
    def __iter__(self):
        index = self.head
        for _ in range(self.length):
            yield self.array[index]
            index += 1
            index &= (self.capacity - 1)
            
    
    def __next__(self):
        pass
            
    def __str__(self):
        return f'{[e for e in self]}' #, array = {self.array}, head, tail = {(self.head, self.tail)}, capacity = {self.capacity}, length = {self.length}'
    
    def clear(self):
        self.head = 0
        self.tail = 0
        self.length = 0

    # perform binary search to find the least index ix satisfying value <= evfunc(ix)
    # among the clock-wise range [lb, ub]. 
    def binary_search_upper_bound(self, lb, ub, value = 0, evfunc = None):
        if self.length == 0 :
            return None
        if lb >= self.length or ub < lb :
            lb %= self.length
            ub %= self.length
            if ub < lb :
                ub += self.length
        #print(f'binary_search_upper_bound: lb = {lb}, ub = {ub}')
        
        if evfunc == None :
            evfunc = lambda ix: self[ix]
        
        while lb < ub :
            mix = lb + ((ub - lb) >> 1)
            #print(f'lb = {lb}, ub = {ub}, mix = {mix}, evfunc = {evfunc(mix)}')
            if evfunc(mix) < value :
                lb = mix + 1
            else:
                # evfunc(mix) >= value
                ub = mix
        
        #print(f'ub = {ub % self.length}')
        return ub % self.length


    def ternary_search_max(self, evfunc = None):
        
        if self.length == 0 :
            return None
        
        n = self.length
        if n == 1:
            return 0
        
        if evfunc == None :
            evfunc = lambda i: self[i]
        
        low = 0
        high = n - 1
        # --- 最初に1回だけ：山がリングの裏側（中央が谷）にあるかチェックして正常化 ---
        # 3個以下のときは以下の処理をスキップ
        if high - low > 2:
            m1 = low + (high - low) // 3
            m2 = low + ((high - low) << 1) // 3
            if evfunc(low) >= evfunc(m1) and evfunc(m2) <= evfunc(high):
                # 山をおもて側に引きずり出す（最初の一発だけ有効）
                low = m2 + 1
                high = m1 + n - 1

        while high - low > 2:
            m1 = low + (high - low) // 3
            m2 = low + ((high - low)<<1) // 3
    
            v_low = evfunc(low) # arr[low]
            v_m1 = evfunc(m1) # arr[m1]
            v_m2 = evfunc(m2) # arr[m2]
            v_high = evfunc(high) # arr[high]

            # print(f'ternary search: {high-low}, low={low}, m1={m1}, m2={m2}, high={high}, v_low={v_low}, {v_m1}, {v_m2}, v_high={v_high}')
            
            # 2. 通常の三分探索（標準ロジック）
            if v_m1 < v_m2:
                low = m1 + 1
                # print('case 3')
            elif v_m1 > v_m2:
                high = m2 - 1
                # print('case 4')      

            # 3. 平坦な山頂（プラトー）
            else:
                # 通常の平坦な山頂：両側を狭める
                low = m1 + 1
                high = m2 - 1
                # print('case 7')
    
            # 探索範囲は絞られる一方なので low, high は最大 2n 程度、
            # したがってわざわざ % を取って小さく維持する必要はない
        # print(f'low = {low}, low % n = {low % n}')
        # print(f'high - low = {high - low}')
        # low <= high が完全に維持されているため、引き算も range も100%安全！
        if high > low :
            # print(f'ternary search: brute force search between: low={low}, high={high}')
            maxix = low
            for i in range(low + 1, high + 1):
                # print(f'ternary search: {self[i]}:{evfunc(i)} > {self[maxix]}:{evfunc(maxix)}')
                if evfunc(i) > evfunc(maxix):
                    maxix = i
            return maxix % n

        return low % n

if __name__ == '__main__':
    ring = ringarray()
    data = [9, 1, 3, -1, -5, 7, 7, 0, 11, -12, 99]
    for ea in data:
        if ea >= 0 :
            ring.add(ea)
        else:
            ring.appendleft(ea)
        print('ring = ', ring)
        print()
    
    print(ring.popleft())
    print(ring.popleft())
    print(ring.popleft())
    print(ring.popleft())
    print(ring.popleft())
    print(ring)
    print('heads and tails ', ring[0], ring[1], ring[-1], ring[-2])
    while len(ring) > 0 :
        print(ring.pop())
        print(ring)
    