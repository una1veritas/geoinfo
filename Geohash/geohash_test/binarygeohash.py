'''
Created on 2022/03/31

@author: Sin Shimozono
'''
import bisect

class binarygeohash:
    MAX_LAT = 90.0
    MIN_LAT = -90.0
    MAX_LONG = 180.0
    MIN_LONG = -180.0
    
    def __init__(self, value = None, precision = None, latitude = None, longitude = None) :    
        self.code = 0
        if value != None and precision == None:
            self.code = value
            return
        if value != None and precision != None:
            prec = min(int(precision), 56)
            self.code = int(value) & (0xffffffffffffffff << (64 - prec))
            self.code |= prec
            return
        elif latitude != None and longitude != None:
            prec = 41 if precision == None else precision if precision < 56 else 56 
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
                    if not i < precision :
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

    def set(self, value):
        self.code = value
    
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

if __name__ == '__main__' :
    bingh = binarygeohash(latitude = 33.5925135, longitude = 130.3560714, precision = 37)
    # e6f5da1cc0000025
    print('hello.', bingh)
    bingh2 = binarygeohash(0xe6f5da1dc8000025)
    # (33.5950178,130.3563308)
    print(bingh2.decode())
    
    geograph = list()
    with open('../geograph/fukuoka.geo', mode = 'r', encoding='utf-8') as f:
        for a_line in f:
            items = a_line.strip().split(',')
            geopoint = (float(items[1]), float(items[2]))
            node_edge = (int(items[0]), geopoint, 
                         binarygeohash(precision=40, latitude = geopoint[0], longitude = geopoint[1]), 
                         items[3:])
            geograph.append(node_edge)
    geograph.sort(key = lambda x: x[2])
    
    searchgp = binarygeohash(0xe6f5da1dc8000025, precision = 37)
    left = bisect.bisect_left(geograph, searchgp, key = lambda x: x[2])
    right = bisect.bisect_right(geograph, searchgp, key = lambda x: x[2])

    for i in range(max(0, left - 3), right + 1) :
        print(geograph[i][2], i, geograph[i][0:2])
    print(searchgp, left, right)
