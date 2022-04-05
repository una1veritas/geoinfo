'''
Created on 2022/03/11

@author: sin
'''
import geohashlite as geohash

(lat, lon) = (33.58, 130.3)

hashcode = geohash.encode(lat, lon, 4)

print(hashcode)
print(geohash.decode(hashcode))
print(geohash.decode_exactly(hashcode))
print(geohash.bbox(hashcode))