'''
Created on 2022/03/31

@author: Sin Shimozono
'''

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
            prec = 41 if arg3 is None else int(arg3) if int(arg3) < 58 else 58 
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
        return self.code & 0x3f

    def binarycode(self):
        return self.code  & (0xffffffffffffffff ^ 0x3f)

    def set_precision(self, prec):
        self.code &= 0x3f
        self.code |= (prec & 0x3f)
        return self

    def set(self, value, prec = None):
        if prec is None :
            prec = value & 0x3f
        if prec > 58 :
            prec = 58
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
    
    def neighbor(self, d):
        bcode = self.binarycode()
        prec = self.precision()
        lsb = 1<<(64 - prec)
        lon = bcode & 0xaaaaaaaaaaaaaaaa
        lat = bcode & 0x5555555555555555
        if d == 'n' or d == 'ne' or d == 'nw' :
            lat = ((lat | 0xaaaaaaaaaaaaaaaa) + lsb) & 0x5555555555555555
        elif d == 's' or d == 'se' or d == 'sw' :
            lat = (lat - lsb) & 0x5555555555555555
        if d == 'e' or d == 'ne' or d == 'se' :
            lon = ((lon | 0x5555555555555555) + lsb) & 0xaaaaaaaaaaaaaaaa
        elif d == 'w' or d == 'sw' or d == 'ne':
            lon = (lon - lsb) & 0xaaaaaaaaaaaaaaaa

        return binaryhash( lon | lat | prec )
        

    def geohash(self, length=None):
        ghash = ''
        if length is None :
            length = int(self.precision() / 5)
        for pos in range(0, length) :
            ghash += binaryhash.GEOHASH_BASE32[self.code>>(59 - pos * 5) & 0x1f]
        return ghash

