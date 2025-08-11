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

    
def vector(orig, dest : np.array): 
    return dest - orig

def norm(v : np.array):
    return np.linalg.norm(v)

def outer_prod_norm(v0, v1 : np.array):
    return v0[0]*v1[1] - v0[1]*v1[0]

def inner_prod(v0, v1 : np.array):
    return v0[0]*v1[0] + v0[1]*v1[1]

def distance_to_line(p, a, b):
    ab = vector(a, b)
    ap = vector(a, p)
    if np.dot(ab, ap) < 0.0 :
        return norm(ap)
    ba = vector(b,a)
    bp = vector(b,p)
    if np.dot(ba, bp) < 0.0 :
        return norm(bp)
    return abs(outer_prod_norm(ab, ap)/norm(ab))
    
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

def simplify_RDP(xy : np.array, epsilon):
    mask = rdp.rdp(xy, epsilon=epsilon, return_mask=True)
    xy_rdp = xy[mask]
    return xy_rdp, [int(i) for i in np.where(mask)[0]]

def simplify_greedy(xy : np.array, tolerance : float):
    path = list([0])
    while path[-1] < len(xy) - 1:
        #print(path)
        '''enhance the last line segment as far as possible.'''
        lastix = path[-1]
        path.append(lastix+1)
        for nextix in range(lastix+1, len(xy)):
            #print(f'trying {lastix}, {nextix}... ', end='')
            for chix in range(lastix + 1, nextix):
                if distance_to_line(xy[chix], xy[lastix], xy[nextix]) > tolerance :
                    #print(f'failed at chix={chix}, dist = {distance_to_line(xy[chix], xy[lastix], xy[nextix])} for tol = {tolerance}')
                    break
            else:
                path[-1] = nextix
                #print('updated',path)
            if path[-1] != nextix :
                break
    return np.array([xy[i] for i in path]), path

def convex_hull(xy : np.array):
    n = len(xy)
    lpath =deque([i for i in range(min(n, 2))])
    rpath = deque([i for i in range(min(n, 2))])
    lastix = lpath[-1]
    orgix = 0
    print(lastix, n)
    while lastix + 1 < n :
        nextix = lastix + 1
        vlast = vector(xy[orgix], xy[lastix])
        vnext = vector(xy[lastix], xy[nextix])
        if inner_prod(vlast, vnext) < 0 :
            break
        if np.cross(vlast, vnext) == 0 :
            print('streight')
        elif np.cross(vlast, vnext) > 0 :
            print('left')
        else:
            print('right')
        lpath.append(nextix)
        rpath.append(nextix)
        
        while len(lpath) > 2 :
            vlast = vector(xy[lpath[-2]], xy[lpath[-1]])
            vprev = vector(xy[lpath[-3]], xy[lpath[-2]])
            if np.cross(vprev,vlast) >= 0 :
                llast = lpath.pop()
                lpath.pop()
                lpath.append(llast)
            else:
                break
        while len(rpath) > 2 :
            vlast = vector(xy[rpath[-2]], xy[rpath[-1]])
            vprev = vector(xy[rpath[-3]], xy[rpath[-2]])
            if np.cross(vprev,vlast) <= 0 :
                rlast = rpath.pop()
                rpath.pop()
                rpath.append(rlast)
            else:
                break
        lastix = nextix
        print(lpath, rpath)
    a = xy[lpath[0]]
    b = xy[lpath[-1]]
    lmax = max([distance_to_line(xy[i], a, b) for i in lpath])
    rmax = max([distance_to_line(xy[i], a, b) for i in rpath])
    vab = vector(a,b)
    peakix = 0
    for i in range(1, len(lpath)):
        vlp = vector(xy[lpath[i-1]], xy[lpath[i]])
        if np.cross(vab, vlp) >= 0 :
            peakix = i
        else:
            break
    print(f'peak = {peakix}, distance = {distance_to_line(xy[lpath[peakix]], a, b)}')
    for i in range(1, len(rpath)):
        vlp = vector(xy[rpath[i-1]], xy[rpath[i]])
        if np.cross(vab, vlp) <= 0 :
            peakix = i
        else:
            break
    print(f'peak = {peakix}, distance = {distance_to_line(xy[rpath[peakix]], a, b)}')
    
    print(f'lmax = {lmax}, rmax = {rmax}')
    return (list(lpath), list(rpath))

'''constant'''
epoch_start = np.datetime64('1970-01-01T00:00:00Z')

if __name__ == '__main__':
    '''read csv into numpy array.'''
    tbl = np.genfromtxt('2025-0726-151032.csv', delimiter=',', skip_header=1, missing_values='', dtype=str)
    dt = np.datetime_as_string(tbl[:,3].astype(np.datetime64), timezone='UTC')
    dt = dt.astype(np.datetime64)
    print(f'raw data contains {len(dt)} points.')
    #print(dt)
    lati = tbl[:,0].astype(np.float64)
    longi = tbl[:,1].astype(np.float64)
    center_lonlat = (np.mean(longi), np.mean(lati))
    print(f'center = {center_lonlat}')
    
    tolerance = 8
    print(f'tolerance = {tolerance}')
    '''epsilon, the 1/2 width of simplified lines.'''
    
    '''convert (lon, lat) to points on the cartesian plane by azimuthal equidistance projection. '''
    proj = Proj(proj='aeqd', lon_0=center_lonlat[0], lat_0=center_lonlat[1], datum='WGS84')
    xy = list()
    last_datetime = epoch_start
    for i in range(len(tbl)):
        past = dt[i] - last_datetime
        if past.item().total_seconds() >= 15 :
            last_datetime = dt[i]
            x, y = proj(longi[i], lati[i])
            # if len(xy) > 0 and np.linalg.norm(np.array([x, y]) - xy[-1]) < 1/2*tolerance :
            #     continue
            xy.append((x, y))
    xy = xy[1:100]
    if False:
        with open('xy.csv', 'w') as f :
            for x, y in xy:
                f.write(f'{x},{y}\n')
    xy = np.array(xy)
    print(f'points in the input provided: {len(xy)}')
    
    lpath, rpath = convex_hull(xy)
    print(lpath, rpath)
        
    x, y = xy[:,0], xy[:,1]
    #sx, sy = convex_xy[:,0], convex_xy[:,1]
    #ctrlparam = np.linspace(0,1,num=len(sx),endpoint=True)
    #spl = make_interp_spline(ctrlparam, np.c_[sx, sy])

    #drawparam = np.linspace(0, 1, len(sx)*8)
    #x_new, y_new = spl(drawparam).T
    lxy = np.array([xy[i] for i in lpath])
    lx , ly = lxy[:,0], lxy[:,1]
    rxy = np.array([xy[i] for i in rpath])
    rx, ry = rxy[:,0], rxy[:,1]
    
    fig, ax = plt.subplots()
    ax.plot(x, y, 'yo')
    ax.plot(lx, ly, 'b.-', lw=0.75) #, alpha=0.75)
    ax.plot(rx, ry, 'r.-', lw=0.75) #, alpha=0.75)
    #plt.plot(x_new, y_new, 'y-')
    plt.legend(['Input points', 'Selected points', 'Interpolated B-spline', 'True'],loc='best')
    plt.title('B-Spline interpolation')
    ax.set_aspect('equal')
    plt.show()
