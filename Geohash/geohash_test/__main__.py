'''
Created on 2022/03/11

@author: sin
'''
import geohashlite as geohash

(lat, lon) = (33.65385, 130.67082)

hashcode = geohash.encode(lat, lon, 8)

print(hashcode)
print(geohash.decode(hashcode))
print(geohash.decode_exactly(hashcode))
print(geohash.bbox(hashcode))