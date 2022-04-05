'''
Created on 2022/03/11

@author: sin
'''
import binaryhash as geo
import bisect

if __name__ == '__main__' :
    hashcode = geo.binaryhash(33.5925135, 130.3560714, 37)
    # e6f5da1cc0000025
    print('hello.', hashcode)
    hashcode = geo.binaryhash(0xe6f5da1dc8000025)
    print(hashcode, hashcode.decode())
    print(hashcode.geohash())
    
    geograph = list()
    with open('../geograph/fukuoka.geo', mode = 'r', encoding='utf-8') as f:
        for a_line in f:
            items = a_line.strip().split(',')
            geopoint = (float(items[1]), float(items[2]))
            node_edge = (int(items[0]), geopoint, 
                         geo.binaryhash(geopoint[0], geopoint[1], 40), items[3:])
            geograph.append(node_edge)
    geograph.sort(key = lambda x: x[2])
    
    searchgp = geo.binaryhash(0xe6f5da1dc8000025, 38)
    left = bisect.bisect_left(geograph, searchgp, key = lambda x: x[2])
    right = bisect.bisect_right(geograph, searchgp, key = lambda x: x[2])

    for i in range(max(0, left - 3), right + 1) :
        print(geograph[i][2], i, geograph[i][0:2])
    print(searchgp, left, right)
