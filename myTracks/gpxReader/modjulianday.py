'''
Created on 2019/11/01

@author: sin
'''
from datetime import datetime
import math
import sys

def mjd(dt:datetime):
    y = dt.year
    m = dt.month
    if m <= 2 :
        y -= 1
        m = 12
    d = dt.day + (dt.hour + dt.minute/60 + dt.second/60/60)/24
    return math.floor(365.25*y) + math.floor(y/400) - math.floor(y/100) + math.floor(30.59*(m-2)) + d - 678912
    
if len(sys.argv) != 2:
    print('give 2019-10-27T07:26:47Z format date-time.')
    exit()

print(sys.argv[1])
dt = datetime.strptime(sys.argv[1], '%Y-%m-%dT%H:%M:%S%z')

print(mjd(dt))