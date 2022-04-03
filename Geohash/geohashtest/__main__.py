'''
Created on 2022/03/11

@author: sin
'''

import sys, os

print(sys.path)

import geohash as bg

(lat, lon) = (33.58, 130.3)

hashcode = bg.binary(latitude=lat, longitude=lon, precision=41)

print(hashcode)
print(binary.precision(hashcode))
print(hex(binary.significantbits(hashcode, 37)), hex(hashcode))