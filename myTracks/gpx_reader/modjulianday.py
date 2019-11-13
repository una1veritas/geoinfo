'''
Created on 2019/11/01

@author: sin
'''
from datetime import datetime
import sys

def datetime2mjd(dt:datetime):
    y = dt.year
    m = dt.month
    if m <= 2 :
        y -= 1
        m = 12
    d = dt.day + (3600*dt.hour + 60*dt.minute/60 + dt.second)/86400
    return int(365.25*y) + int(y/400) - int(y/100) + int(30.59*(m-2)) + d - 678912
    
if len(sys.argv) != 2:
    print('give 2019-10-27T07:26:47Z format date-time.')
    exit()

print(sys.argv[1])
dt = datetime.strptime(sys.argv[1], '%Y-%m-%dT%H:%M:%S%z')

print(datetime2mjd(dt))