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

    
def diff_vec(orig, dest : np.array): 
    return dest - orig

def norm(v : np.array):
    return np.linalg.norm(v)

def outer_prod_norm(v0, v1 : np.array):
    return v0[0]*v1[1] - v0[1]*v1[0]

def distance_to_line(p, a, b):
    ab = diff_vec(a, b)
    ap = diff_vec(a, p)
    if np.dot(ab, ap) < 0.0 :
        return norm(ap)
    ba = diff_vec(b,a)
    bp = diff_vec(b,p)
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
        # print(f'from {path[-2]}: {xy[path[-2]]} to {path[-1]}: {xy[path[-1]]}')
        # for i in range(path[-1]+1, path[-1]):
        #     print(f'{i}:{distance_to_line(xy[i], xy[path[-2]], xy[path[-1]]):4}, ', end='')
        # print()
    return np.array([xy[i] for i in path]), path

def convex_hull(xy : np.array):
    l_path = [ 0 ]
    r_path = [ 0 ]
    current_ix = 0
    org_xy = xy[0]
    while True:
        next_ix = current_ix + 1
        if not (next_ix < len(xy)) : break
        if len(l_path) == 1 and len(r_path) == 1 :
            l_path.append(next_ix)
            r_path.append(next_ix)
        else:
            print(0, current_ix, next_ix)
            vec_oc = diff_vec(org_xy, xy[current_ix])
            vec_cx = diff_vec(xy[current_ix], xy[next_ix])
            if np.cross(vec_oc, vec_cx) >= 0 :
                print('left')
                l_path.append(next_ix)
                while len(l_path) > 2 :
                    vec_last = diff_vec(xy[l_path[-2]], xy[l_path[-1]])
                    vec_prev = diff_vec(xy[l_path[-3]], xy[l_path[-2]])
                    if np.cross(vec_prev,vec_last) >= 0 :
                        last_ix = l_path.pop()
                        l_path.pop()
                        l_path.append(last_ix)
                    else:
                        break
            else:
                print('right')
                r_path.append(next_ix)
                while len(r_path) > 2 :
                    vec_last = diff_vec(xy[r_path[-2]], xy[r_path[-1]])
                    vec_prev = diff_vec(xy[r_path[-3]], xy[r_path[-2]])
                    if np.cross(vec_prev,vec_last) <= 0 :
                        last_ix = r_path.pop()
                        r_path.pop()
                        r_path.append(last_ix)
                    else:
                        break
        current_ix = next_ix

    ''' close paths'''
    if l_path[-1] < r_path[-1] :
        l_path.append(r_path[-1])
    elif l_path[-1] > r_path[-1] :
        r_path.append(l_path[-1])
    print(l_path, r_path)
    return l_path, r_path

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
        if past.item().total_seconds() >= 30 :
            last_datetime = dt[i]
            x, y = proj(longi[i], lati[i])
            # if len(xy) > 0 and np.linalg.norm(np.array([x, y]) - xy[-1]) < 1/2*tolerance :
            #     continue
            xy.append((x, y))
    xy = xy[100:106]
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
