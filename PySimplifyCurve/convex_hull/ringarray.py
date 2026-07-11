'''
Created on 2026/03/17

@author: sin
'''

from math import log2, ceil

class ringarray:
    INITIAL_CAPACITY = 8
    
    def __init__(self, initcapacity = None):
        if initcapacity is not None :
            self.capacity = 1 << ceil(log2(int(initcapacity) + 1))
        else:
            self.capacity = ringarray.INITIAL_CAPACITY
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
    
    def add(self, elem):
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
        pos = self.head + index
        if index < 0 :
            pos += self.length
        pos &= (self.capacity - 1)
        
        if self.head < self.tail :
            if self.head <= pos < self.tail :
                return self.array[pos]
            else:
                raise ValueError(f'index {pos} out of bounds.')
        else:
            if self.head <= pos < self.capacity :
                return self.array[pos]
            elif pos < self.tail :
                return self.array[pos]
            else:
                raise ValueError(f'index {pos} out of bounds.')
            
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
    