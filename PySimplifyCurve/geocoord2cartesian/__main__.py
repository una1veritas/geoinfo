import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import rdp
#import math
from pyproj import Proj
from collections import deque

import time

class Timer:
    def __init__(self, mess = ''):
        self.message = str(mess)
        
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        self.end = time.time()
        print(self.message + f"Execution time: {self.end - self.start} seconds")

# def copilot_distance(a, b, p):
#     ab = b - a
#     ap = p - a
#     distance = np.abs(np.cross(ab, ap)) / np.linalg.norm(ab)
#     return distance
'''
double gpspoint::distanceTo(const gpspoint &q1, const gpspoint &q2) const {
    if ( inner_prod(q1, q2, *this) < epsilon ) { // < 0.0
        return q1.distanceTo(*this);
    }
    if ( inner_prod(q2, q1, *this) < epsilon ) { // < 0.0
        return q2.distanceTo(*this);
    }
    return ABS(norm_outer_prod(q1, q2, *this)) / q1.distanceTo(q2);
}
'''


'''constant'''
epoch_start = np.datetime64('1970-01-01T00:00:00Z')

if __name__ == '__main__':
    '''read csv into numpy array.'''
    filename = '2025-0726-151032.csv'
    tbl = np.genfromtxt(filename, delimiter=',', skip_header=1, missing_values='', dtype=str)
    dt = np.datetime_as_string(tbl[:,3].astype(np.datetime64), timezone='UTC')
    dt = dt.astype(np.datetime64)
    print(f'raw data contains {len(dt)} points.')
    #print(dt)
    lati = tbl[:,0].astype(np.float64)
    longi = tbl[:,1].astype(np.float64)
    center_lonlat = (np.mean(longi), np.mean(lati))
    print(f'center(longitude, latitude) = {center_lonlat}')
    
    '''convert (lon, lat) to points on the cartesian plane by azimuthal equidistance projection. '''
    proj = Proj(proj='aeqd', lon_0=center_lonlat[0], lat_0=center_lonlat[1], datum='WGS84')
    xy = list()
    last_datetime = epoch_start
    for i in range(len(tbl)):
        past = dt[i] - last_datetime
        if past.item().total_seconds() >= 5 :
            last_datetime = dt[i]
            x, y = proj(longi[i], lati[i])
            xy.append((x, y))

    #xy =xy[:10]
    writeout_csv = False
    if writeout_csv:
        with open('xy.csv', 'w') as f :
            for x, y in xy:
                f.write(f'{x},{y}\n')
    
    xy = np.array(xy)
    print(f'points in the input provided: {len(xy)}')
    print(xy)
    