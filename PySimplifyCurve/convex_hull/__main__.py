import numpy as np
import matplotlib.pyplot as plt
#from scipy.interpolate import make_interp_spline
import rdp
import math
from pyproj import Proj
from collections import deque

import time
from numpy import ix_

class Timer:
    def __init__(self, mess = ''):
        self.message = str(mess)
        
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        self.end = time.time()
        print(self.message + f"Execution time: {self.end - self.start} seconds")

class Point2D:
    def __init__(self, xy, yy = None):
        if yy != None :
            self.x = xy
            self.y = yy
        else:
            self.x, self.y = xy[:2]
            
    def __getitem__(self, key):
        if key == 0 or key == 'x' :
            return self.x
        elif key == 1 or key == 'y' :
            return self.y
        raise KeyError('has no such key {key}')

    def __setitem__(self, key, value):
        if key == 0 or key == 'x' :
            self.x = value
        elif key == 1 or key == 'y' :
            self.y = value
        raise KeyError('has no such key {key}')

    def __repr__(self):
        return f'({self.x}, {self.y})'
    
    def __str__(self):
        return f'({self.x}, {self.y})'
    
    def __tuple__(self):
        return (self.x, self.y)
    
    def __neg__(self):
        return Point2D(-self.x, -self.y)
        
    def __sub__(self, other):
        return Point2D( self.x - other.x, self.y - other.y)
        
    def norm(self):
        return math.sqrt(self.x*self.x + self.y*self.y)

    ''' distance between two Point2D points '''
    def distance_to(self, vdst):
        return (vdst - self).norm()

    def outer_prod_norm(self, other):
        return self.x * other.y - self.x * other.y

    # ''' < 0 ... self is left , > 0 ... self is right''' 
    # def side_from_vector(self, orgpt, dstpt):
    #     return (dstpt - orgpt).outer_prod_norm(self - orgpt)
    #
    # def left_of_line(self, a, b):
    #     return (b.x - a.x) * self.y - (b.y - a.y) * self.x >= 0
    ''' starboard, clock wise direction (right) is positive '''
    
    def side_of_line(self, a, b):
        return - (b.x - a.x) * self.y + (b.y - a.y) * self.x

    def inner_prod(self, other):
        return self.x * other.x + self.x * other.y

    def distance_to_line(self, a, b):
        ab = b - a
        ap = self - a
        if ab.inner_prod(ap) < 0.0 :
            return ap.norm()
        ba = -ab
        bp = b - self
        if ba.inner_prod(bp) < 0.0 :
            return bp.norm()
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

class ConvexHull:
    RIGHT_SIDE = -1
    LEFT_SIDE  = 1
    COLINEAR = 0
    
    def __init__(self, points = None, SimplePolyline = False):
        self.xy = list() # of Point2D
        self.leftpath = deque()     #clockwise path
        self.rightpath = deque()    #anti/counter-clockwise path

        #peak point on each convex path for 0 points
        self.leftpeak_ix = None
        self.rightpeak_ix = None
        
        if isinstance(points, (list, tuple)) :
            for p in points:
                if isinstance(p, (list, tuple)) and len(p) >= 2 :
                    p = tuple(p[:2])
                elif isinstance(p, (np.ndarray)) and len(p) >= 2 :
                    p = (float(p[0]), float(p[1]))
                else :
                    #isinstance(pt, Point2D) 
                    raise ValueError(f"list/tuple needed, {p} ({type(p)}).")
                if not self.add(p, SimplePolyline) :
                    break
    
    def __len__(self):
        return len(self.xy)
    
    def __str__(self):
        return str(self.xy)+', '+str(self.leftpath)+', '+str(self.rightpath)
    
    def leftq(self, ix):
        return self.xy[self.leftpath[ix]]
    
    def rightq(self, ix):
        return self.xy[self.rightpath[ix]]
    
    ''' 1, 0, -1 for left, co linear with, right, respectively.'''
    @staticmethod
    def side_of_line(a, b, c):
        val = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 1 if val > 0 else -1 if val < 0 else 0 

    @staticmethod
    def distance_between(a, b):
        return math.sqrt( (b[0] - a[0])** 2 + (b[1] - a[1])** 2 )
    
    '''returns axis vector'''
    def axis(self):
        '''the first and the last points of the left and the right paths are identical.'''
        return self.xy[self.leftpath[-1]] - self.xy[0]
    
    def add(self, pt, SimplePolyline=False):
        if len(self) < 2 :
            self.xy.append(pt)
            self.leftpath.append(len(self)-1)
            self.rightpath.append(len(self)-1)
            self.leftpeak_ix = len(self)-1
            self.rightpeak_ix = len(self)-1
            print(f"len(self.xy) = {len(self.xy)}, self.leftpeak_ix = {self.leftpeak_ix}")
            return True
        
        #if ( self.distance_between(self.xy[0], pt) < self.distance_between(self.xy[0], self.xy[-1]) ) or \
        if self.side_of_line(self.leftq(-2), self.leftq(-1), pt) < 0 and self.side_of_line(self.rightq(-2), self.rightq(-1), pt) > 0:
            # reject point if is is inside the last paths of clockwise path and anti-clockwise path
            #print(f'skip adding {pt} to left and right paths.\n')
            if not SimplePolyline :
                return False
        
        self.xy.append(pt)
        self.leftpath.append(len(self)-1)
        self.make_leftpath_convex()
        self.rightpath.append(len(self)-1)
        self.make_rightpath_convex()
        return True
    
    # def isinside(self, pt):
    #     for ix in range(len(self.leftpath) - 1) : # from the first to the last
    #         orgpt = self.xy[self.leftpath[ix]]
    #         nxtpt = self.xy[self.leftpath[ix+1]]
    #         if pt.side_from_vector(orgpt, nxtpt) < 0 :
    #             # pt is left outer side of left path
    #             #print(f'{pt} is outside of left-path {orgpt}, {nxtpt}')
    #             return False
    #     print(f'{pt} is isinside of left path.')
    #     for ix in range(len(self.rightpath) - 1) : # from the first to the last
    #         orgpt = self.xy[self.rightpath[ix]]
    #         nxtpt = self.xy[self.rightpath[ix+1]]
    #         if pt.side_from_vector(orgpt, nxtpt) > 0 :
    #             # pt is right outer side of right path
    #             print(f'{pt} is outside of right-path {orgpt}, {nxtpt}')
    #             return False
    #     print(f'{pt} is isinside of right path.')
    #     return True
            
    def make_leftpath_convex(self):
        #print(self.leftpath)
        lastix = self.leftpath.pop()
        lastpt = self.xy[lastix]
        
        while len(self.leftpath) >= 2 :
            if self.side_of_line(lastpt, self.leftq(-1), self.leftq(-2)) < 0 : # right side (out side)
                poppedix = self.leftpath.pop() # pop-out the prev point
                if poppedix <= self.leftpeak_ix :
                    print(f'poppedix = {poppedix}')
                    self.leftpeak_ix = self.leftpath[-1]
            else:
                break
        self.leftpath.append(lastix)
        self.leftpeak_ix = self.find_left_peak() 
        
    def make_rightpath_convex(self):
        lastix = self.rightpath.pop()
        last = self.xy[lastix]
        while len(self.rightpath) >= 2 :
            if self.side_of_line(last, self.rightq(-1), self.rightq(-2)) > 0 :
                self.rightpath.pop() # pop-out the prev point
            else:
                break
        self.rightpath.append(lastix)
    
    def find_left_peak(self):
        ix = self.leftpeak_ix
        lx = self.xy[-1][0] - self.xy[0][0]
        ly = self.xy[-1][1] - self.xy[0][1]
        a = self.leftq(ix-1)
        b = self.leftq(ix)
        ax = b[0] - a[0]
        ay = b[1] - a[1]
        width = 1
        outp = ax * lx - ay * ly 
        print(f"ix = {ix}, outp = {outp}") 
        return ix
        
        
if __name__ == '__main__':
    xy = [(-1, 1), (0, 0), (0.5, 1.5), (0, 2.5), (1, 2), (1, 3), (2, 1.5), (3, 1), (1.5, 4), (3, 4), (2.5, 3), (3.2, 2), (2, 0.5)]
    # if False:
    #     with open('xy.csv', 'w') as f :
    #         for x, y in xy:
    #             f.write(f'{x},{y}\n')
    print(xy, f'points in the input provided: {len(xy)}')
    print(f'{xy[2]} is right side of line {xy[0]} to {xy[1]}? {ConvexHull.side_of_line(xy[0], xy[1], xy[2]) }\n')
    
    ch = ConvexHull(xy, SimplePolyline=False)
    print(ch)
    print(ch.rightpeak_ix)
    
    #rdpxy, indices = simplify_RDP(xy, 1.0)
    #print(rdpxy, indices)
    # exit(0)
    #rdpx, rdpy = rdpxy[:,0], rdpxy[:,1]
    x, y = [ x for x, y in xy], [ y for x, y in xy]
    #sx, sy = convex_xy[:,0], convex_xy[:,1]
    #ctrlparam = np.linspace(0,1,num=len(sx),endpoint=True)
    #spl = make_interp_spline(ctrlparam, np.c_[sx, sy])

    #drawparam = np.linspace(0, 1, len(sx)*8)
    #x_new, y_new = spl(drawparam).T
    
    lxy = np.array([xy[i] for i in ch.leftpath])
    rxy = np.array([xy[i] for i in ch.rightpath])
    lx , ly = lxy[:,0], lxy[:,1]
    rx, ry = rxy[:,0], rxy[:,1]
    
    fig, ax = plt.subplots()
    ax.plot(x, y, 'y.-', lw=4.0, alpha=0.5)
    ax.plot(lx, ly, 'b.--', lw=1) #, alpha=0.75)
    ax.plot(rx, ry, 'r.-.', lw=1) #, alpha=0.75)
    #ax.plot(rdpx, rdpy, 'g.-', lw=0.75) #, alpha=0.75)
    #plt.plot(x_new, y_new, 'y-')
    plt.legend(['Input points', 'clockwise path', 'counter-clockwise path', 'True'],loc='best')
    plt.title('Convex Hull function Test')
    ax.set_aspect('equal')
    plt.show()
