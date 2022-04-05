'''
Created on 2022/03/31

@author: Sin Shimozono
'''
import bisect
from pip._internal.utils.hashes import MissingHashes

# def encode(latitude, longitude, precision = 41) :    
#     hashcode = 0
#     if precision > 56 :
#         precision = 56
#     if -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0 :
#         northsouth = [90.0, -90.0]
#         eastwest   = [180.0, -180.0]
#         bit = 1 <<63;
#         i = 0
#         while i < precision:
#             latmid = (northsouth[0] + northsouth[1]) / 2.0
#             lonmid = (eastwest[0] + eastwest[1]) / 2.0
#             if longitude > lonmid :
#                 eastwest[1] = lonmid
#                 hashcode |= bit
#             else:
#                 eastwest[0] = lonmid                
#             bit >>= 1
#             i += 1
#             if not i < precision :
#                 break
#             if latitude > latmid :
#                 northsouth[1] = latmid
#                 hashcode |= bit
#             else: 
#                 northsouth[0] = latmid
#             bit >>= 1
#             i += 1
#     hashcode |= precision
#     return hashcode
#
# def precision(binary):
#     return binary & 0xff
#
# def significantbits(binary, prec):
#     binary &= 0xffffffffffffffff << (64 - prec)
#     binary |= prec
#     return binary
    
class binaryhash:
    MAX_LAT = 90.0
    MIN_LAT = -90.0
    MAX_LONG = 180.0
    MIN_LONG = -180.0
    GEOHASH_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    
    def __init__(self, arg1 = None, arg2 = None, arg3 = None) :
        self.code = 0
        defaultprec = 41
        if isinstance(arg1, (int, str)) and arg3 is None :
            if arg2 is None :
                prec = defaultprec
            else:
                prec = int(arg2)
            self.set(int(arg1), prec)
            return
        if isinstance(arg1, float) and isinstance(arg2, float) :
            latitude = arg1
            longitude = arg2
            prec = 41 if arg3 is None else int(arg3) if int(arg3) < 56 else 56 
            if -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0 :
                northsouth = [self.MAX_LAT, self.MIN_LAT]
                eastwest   = [self.MAX_LONG, self.MIN_LONG]
                bit = 1 <<63;
                i = 0
                while i < prec:
                    latmid = (northsouth[0] + northsouth[1]) / 2.0
                    lonmid = (eastwest[0] + eastwest[1]) / 2.0
                    if longitude > lonmid :
                        eastwest[1] = lonmid
                        self.code |= bit
                    else:
                        eastwest[0] = lonmid                
                    bit >>= 1
                    i += 1
                    if not i < prec :
                        break
                    if latitude > latmid :
                        northsouth[1] = latmid
                        self.code |= bit
                    else: 
                        northsouth[0] = latmid
                    bit >>= 1
                    i += 1
            self.code |= prec
            return

    def precision(self):
        return self.code & 0xff

    def set_precision(self, prec):
        self.code &= 0xff
        self.code |= (prec & 0xff)
        return self

    def set(self, value, prec = None):
        if prec is None :
            prec = value & 0xff
        if prec > 56 :
            prec = 56
        self.code = value & (0xffffffffffffffff << (64 - prec))
        self.code |= prec
        return self
      
    def __str__(self):
        return hex(self.code)
    
    def __lt__(self, another):
        if self.precision() == another.precision() :
            return self.code < another.code
        minprec = min(self.precision(), another.precision())
        mask = 0xffffffffffffffff << (64 - minprec)
        return (self.code & mask) < (another.code & mask)

    def decode(self):
        northsouth = [self.MAX_LAT, self.MIN_LAT]
        eastwest   = [self.MAX_LONG, self.MIN_LONG]

        if self.code > 0 :
            checkbit = 1 <<63
            i = 0
            while i < self.precision() :
                delta = (eastwest[0] - eastwest[1]) / 2.0;
                if (self.code & checkbit) != 0 :
                    eastwest[1] += delta
                else:
                    eastwest[0] -= delta
                checkbit >>= 1
                i += 1
                if not i < self.precision():
                    break
                delta = (northsouth[0] - northsouth[1]) / 2.0
                if (self.code & checkbit) != 0 :
                    northsouth[1] += delta
                else:
                    northsouth[0] -= delta
                checkbit >>= 1
                i += 1
        return {'n': northsouth[0], 's': northsouth[1], 'e': eastwest[0], 'w': eastwest[1]}

    def geohash(self, length=None):
        ghash = ''
        if length is None :
            length = int(self.precision() / 5)
        for pos in range(0, length) :
            ghash += binaryhash.GEOHASH_BASE32[self.code>>(59 - pos * 5) & 0x1f]
        return ghash
    
if __name__ == '__main__' :
    ghash = binaryhash(33.5925135, 130.3560714, 37)
    # e6f5da1cc0000025
    print('hello.', ghash)
    bingh2 = binaryhash(0xe6f5da1dc8000025)
    print(bingh2, bingh2.decode())
    
    geograph = list()
    with open('../geograph/fukuoka.geo', mode = 'r', encoding='utf-8') as f:
        for a_line in f:
            items = a_line.strip().split(',')
            geopoint = (float(items[1]), float(items[2]))
            node_edge = (int(items[0]), geopoint, 
                         binaryhash(geopoint[0], geopoint[1], 40), items[3:])
            geograph.append(node_edge)
    geograph.sort(key = lambda x: x[2])
    
    searchgp = binaryhash(0xe6f5da1dc8000025, 38)
    left = bisect.bisect_left(geograph, searchgp, key = lambda x: x[2])
    right = bisect.bisect_right(geograph, searchgp, key = lambda x: x[2])

    for i in range(max(0, left - 3), right + 1) :
        print(geograph[i][2], i, geograph[i][0:2])
    print(searchgp, left, right)
