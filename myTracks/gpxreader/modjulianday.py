'''
Created on 2019/11/01

@author: sin
'''
from datetime import datetime
import sys
import math

def datetime2mjd(dt:datetime):
    y = dt.year
    m = dt.month
    if m <= 2 :
        y -= 1
        m = 12
    d = dt.day + (3600*dt.hour + 60*dt.minute/60 + dt.second)/86400
    return int(365.25*y) + int(y/400) - int(y/100) + int(30.59*(m-2)) + d - 678912
    
def mjd2datetime(mjd:float):
    n = math.floor(mjd + 678881)
    a = 4*n + 3 + 4 * math.floor(3/4 * math.floor(4*(n+1)/146097 + 1))
    b = 5 * math.floor((a % 1461)/4) + 2
    y = math.floor(a/1461)
    m = math.floor(b/153) + 3
    d = math.floor((b % 153)/5) + 1
    
    r = mjd - math.floor(mjd)
    r, hour = math.modf(r * 24)
    hour = int(hour)
    r, minu = math.modf(r * 60)
    minu = int(minu)
    secs = int(math.floor(r * 60))
    return datetime(y, m, d, hour, minu, secs)
        
if len(sys.argv) < 2:
    print(sys.argv)
    print('give 2019-10-27T07:26:47Z format date-time.')
    exit()

dtstr = ''
caltomjd = True
if sys.argv[1].startswith('-') :
    if sys.argv[1] == '-cal' :
        caltomjd = False
    dtstr = sys.argv[2]
else:
    dtstr = sys.argv[1]

if caltomjd :
    dt = datetime.strptime(dtstr, '%Y-%m-%dT%H:%M:%S%z')
    print(datetime2mjd(dt))
else:
    mjd = float(dtstr)
    print(mjd2datetime(mjd))
