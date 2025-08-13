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

class PointXY:
    def __init__(self, xy, yy = None):
        if yy != None :
            self.coord = (xy, yy)
        else:
            self.coord = (xy[0], xy[1])
            
    def __getitem__(self, key):
        if key == 0 or key == 'x' :
            return self.coord[0]
        elif key == 1 or key == 'y' :
            return self.coord[1]
        raise KeyError('has no such key {key}')

    def __setitem__(self, key, value):
        if key == 0 or key == 'x' :
            self.coord[0] = value
        elif key == 1 or key == 'y' :
            self.coord[1] = value
        raise KeyError('has no such key {key}')

    def __repr__(self):
        return f'PointXY({self.coord[0]}, {self.coord[1]})'
    
    def __str__(self):
        return f'({self.coord[0]}, {self.coord[1]})'
    
    def __tuple__(self):
        return self.coord
    
    def __neg__(self):
        return PointXY(-self.coord[0], -self.coord[1])
        
    def __sub__(self, other):
        return PointXY( self.coord[0] - other.coord[0], self.coord[1] - other.coord[1])

    def norm(self):
        return sqrt(self.coord[0]*self.coord[0] + self.coord[1]*self.coord[1])

    def distance(self, vdst):
        return norm(vdst - self)

    def outer_prod_norm(self, other):
        return self[0]*other[1] - self[1]*other[0]

    def inner_prod(self, other):
        return self[0]*other[0] + self[1]*other[1]

    def distance_to_line(self, a, b):
        ab = b - a
        ap = self - a
        if ab.inner_prod(ap) < 0.0 :
            return norm(ap)
        ba = -ab
        bp = b - self
        if ba.inner_prod(bp) < 0.0 :
            return norm(bp)
        return abs(ab.outer_prod_norm(ap)/ab.norm())
    
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

class ConvexHull:
    def __init__(self):
        self.xy = list()
        self.leftpath = deque()
        self.rightpath = deque()
    
    def __len__(self):
        return self.size()
    
    def size(self):
        return len(self.xy)
    
    '''returns axis vector'''
    def axis(self):
        '''the first and the last points of both paths are identical.'''
        return self.xy[self.leftpath[-1]] - self.xy[0]
    
    def add_point(self, pt):
        n = len(self.xy)
        if n == 0 :
            self.leftpath.append(n)
            self.rightpath.append(n)
            self.xy.append( PointXY(pt) )
            return True
        elif n == 1 :
            self.leftpath.append(n)
            self.rightpath.append(n)
            self.xy.append( PointXY(pt) )
            return True
        #
        lastix = self.leftpath[-1]
        vlast = self.xy[lastix] - self.xy[0]
        vnext = pt - self.xy[-1]            
        if vlast.inner_prod(vnext) < 0 :
            print('point gets near.')
            return False
        
        if vlast.outer_prod_norm(vnext) == 0 :
            print('streight')
        elif vlast.outer_prod_norm(vnext) > 0 :
            print('left')
        else:
            print('right')
        
        self.xy.append(pt)
        self.leftpath.append(n)
        self.rightpath.append(n)
        
        return True
    
        while len(self.leftpath) > 2 :
            vlast = vector(xy[self.leftpath[-2]], xy[self.leftpath[-1]])
            vprev = vector(xy[self.leftpath[-3]], xy[self.leftpath[-2]])
            if np.cross(vprev,vlast) >= 0 :
                llast = self.leftpath.pop()
                self.leftpath.pop()
                self.leftpath.append(llast)
            else:
                break
        while len(self.rightpath) > 2 :
            vlast = vector(xy[self.rightpath[-2]], xy[self.rightpath[-1]])
            vprev = vector(xy[self.rightpath[-3]], xy[self.rightpath[-2]])
            if np.cross(vprev,vlast) <= 0 :
                rlast = self.rightpath.pop()
                self.rightpath.pop()
                self.rightpath.append(rlast)
            else:
                break
        lastix = nextix

    
    def convex_hull(self, xy : np.array):
        n = len(xy)
        self.leftpath = deque([i for i in range(min(n, 2))])
        self.rightpath = deque([i for i in range(min(n, 2))])
        lastix = self.leftpath[-1]
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
            self.leftpath.append(nextix)
            self.rightpath.append(nextix)
            
            while len(self.leftpath) > 2 :
                vlast = vector(xy[self.leftpath[-2]], xy[self.leftpath[-1]])
                vprev = vector(xy[self.leftpath[-3]], xy[self.leftpath[-2]])
                if np.cross(vprev,vlast) >= 0 :
                    llast = self.leftpath.pop()
                    self.leftpath.pop()
                    self.leftpath.append(llast)
                else:
                    break
            while len(self.rightpath) > 2 :
                vlast = vector(xy[self.rightpath[-2]], xy[self.rightpath[-1]])
                vprev = vector(xy[self.rightpath[-3]], xy[self.rightpath[-2]])
                if np.cross(vprev,vlast) <= 0 :
                    rlast = self.rightpath.pop()
                    self.rightpath.pop()
                    self.rightpath.append(rlast)
                else:
                    break
            lastix = nextix
            print(self.left_path_list(), self.right_path_list())
        a = xy[self.leftpath[0]]
        b = xy[self.leftpath[-1]]
        vab = vector(a,b)
        peakix = 0
        for i in range(1, len(self.leftpath)):
            vlp = vector(xy[self.leftpath[i-1]], xy[self.leftpath[i]])
            if np.cross(vab, vlp) >= 0 :
                peakix = i
            else:
                break
        self.leftpeak = peakix
        print(f'left peak = {peakix}, distance = {distance_to_line(xy[self.leftpath[peakix]], a, b)}')
        for i in range(1, len(self.rightpath)):
            vlp = vector(xy[self.rightpath[i-1]], xy[self.rightpath[i]])
            if np.cross(vab, vlp) <= 0 :
                peakix = i
            else:
                break
        self.rightpeak = peakix
        print(f'right peak = {peakix}, distance = {distance_to_line(xy[self.rightpath[peakix]], a, b)}')
        
        #print(f'lmax = {lmax}, rmax = {rmax}')
        return
    
    def left_path_list(self):
        return list(self.leftpath)
    
    def right_path_list(self):
        return list(self.rightpath)

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
    
    tolerance = 16
    print(f'tolerance = {tolerance}')
    '''epsilon, the 1/2 width of simplified lines.'''
    
    '''convert (lon, lat) to points on the cartesian plane by azimuthal equidistance projection. '''
    proj = Proj(proj='aeqd', lon_0=center_lonlat[0], lat_0=center_lonlat[1], datum='WGS84')
    xy = list()
    last_datetime = epoch_start
    for i in range(len(tbl)):
        past = dt[i] - last_datetime
        if past.item().total_seconds() >= 60 :
            last_datetime = dt[i]
            x, y = proj(longi[i], lati[i])
            if len(xy) > 0 and np.linalg.norm(np.array([x, y]) - xy[-1]) < tolerance :
                 continue
            xy.append((x, y))
    xy = xy[1:100]
    if False:
        with open('xy.csv', 'w') as f :
            for x, y in xy:
                f.write(f'{x},{y}\n')
    xy = np.array(xy)
    print(f'points in the input provided: {len(xy)}')
    
    cvxhull = ConvexHull()
    for pt in xy:
        if not cvxhull.add_point(PointXY(pt)) :
            break
    lpath, rpath = cvxhull.left_path_list(), cvxhull.right_path_list()
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
