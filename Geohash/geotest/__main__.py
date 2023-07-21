'''
Created on 2022/03/11

@author: sin
'''

import bisect
from geohash import bghash

if __name__ == '__main__' :
    hashcode = bghash(33.5925135, 130.3560714, 37)
    # e6f5da1cc0000025
    print('hello.', (33.5925135, 130.3560714, 37), hashcode, hashcode.precision())
    hashcode = bghash(0xe6f5da1dc8000025)
    print('from 0xe6f5da1dc8000025', hashcode)
    print()
    
    hashcode = 'wvuxn7f'
    hashcode = bghash(hashcode)
    print('wvuxn7f', hashcode, hashcode.decode())
    
    print(hashcode.decode())
    print(hashcode.geohash())
    
    print(hashcode.neighbor('w'))
    print(hashcode.neighbor('n').decode())
    print(hashcode.neighbor('e').decode())
    print(hashcode.neighbor('s').decode())
    print(hashcode.neighbor('w').decode())
    print(hashcode.neighbor('ne').decode())
    print(hashcode.neighbor('se').decode())
    print(hashcode.neighbor('sw').decode())
    print(hashcode.neighbor('nw').decode())
    
    geograph = list()
    with open('../geograph/fukuoka.geo', mode = 'r', encoding='utf-8') as f:
        for a_line in f:
            items = a_line.strip().split(',')
            geopoint = (float(items[1]), float(items[2]))
            node_edge = (int(items[0]), geopoint, 
                        bghash(geopoint[0], geopoint[1], 40), items[3:])
            geograph.append(node_edge)
    geograph.sort(key = lambda x: x[2])
    
    searchgp = bghash(0xe6f5da1dc8000025, 38)
    left = bisect.bisect_left(geograph, searchgp, key = lambda x: x[2])
    right = bisect.bisect_right(geograph, searchgp, key = lambda x: x[2])

    for i in range(max(0, left - 3), right + 1) :
        print(geograph[i][2], i, geograph[i][0:2])
    print(searchgp, left, right)
