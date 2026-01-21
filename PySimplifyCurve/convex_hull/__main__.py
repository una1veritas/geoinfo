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
    
    def __init__(self, points = None, SimplePolyline = False):
        self.xy = list() # of Point2D
        self.left_path = deque()     #clockwise path
        self.right_path = deque()    #anti/counter-clockwise path

        #peak point on each convex path for 0 points
        self.lpeak_ix = None
        self.rpeak_ix = None
        
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
        return str(self.xy)+', '+str(self.left_path)+', '+str(self.right_path)
    
    def lpath(self, ix):
        return self.xy[self.left_path[ix]]
    
    def rpath(self, ix):
        return self.xy[self.right_path[ix]]

    ''' (b-a) X (d-c)'''
    @staticmethod
    def outer_prod_z(a, b, c, d):
        return (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
    
    @staticmethod
    def right_side_of_line(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) < 0

    @staticmethod
    def left_side_of_line(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 0

    @staticmethod
    def distance_between(a, b):
        return math.sqrt( (b[0] - a[0])** 2 + (b[1] - a[1])** 2 )
    
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

    '''returns axis vector'''
    def axis(self):
        '''the first and the last points of the left and the right paths are identical.'''
        return self.xy[self.left_path[-1]] - self.xy[0]
    
    def add(self, pt, SimplePolyline=False):
        if len(self) < 2 :
            self.xy.append(pt)
            self.left_path.append(len(self)-1)
            self.right_path.append(len(self)-1)
            self.lpeak_ix = len(self)-1
            self.rpeak_ix = len(self)-1
            #print(f"len(self.xy) = {len(self.xy)}, self.lpeak_ix = {self.lpeak_ix}")
            return True
        
        #if ( self.distance_between(self.xy[0], pt) < self.distance_between(self.xy[0], self.xy[-1]) ) or \
        if self.right_side_of_line(self.lpath(-2), self.lpath(-1), pt) and self.left_side_of_line(self.rpath(-2), self.rpath(-1), pt) :
            # reject point if is is inside the last paths of clockwise path and anti-clockwise path
            #print(f'skip adding {pt} to left and right paths.\n')
            if not SimplePolyline :
                return False
        
        self.xy.append(pt)
        self.left_path.append(len(self)-1)
        self.right_path.append(len(self)-1)
        self.make_leftpath_convex()
        self.make_rightpath_convex()
        return True
    
    def make_leftpath_convex(self):
        #print(self.left_path)
        lastix = self.left_path.pop()
        lastpt = self.xy[lastix]
        
        while len(self.left_path) >= 2 :
            if self.right_side_of_line(lastpt, self.lpath(-1), self.lpath(-2)) : 
                self.left_path.pop() # pop-out the prev point
            else:
                break
        self.left_path.append(lastix)
        self.lpeak_ix = self.find_lpeak() 
        
    def make_rightpath_convex(self):
        lastix = self.right_path.pop()
        last = self.xy[lastix]
        while len(self.right_path) >= 2 :
            if self.left_side_of_line(last, self.rpath(-1), self.rpath(-2)) :
                self.right_path.pop() # pop-out the prev point
            else:
                break
        self.right_path.append(lastix)
        self.rpeak_ix = self.find_rpeak() 
    
    def find_lpeak(self):
        lb, ub = 0, len(self.left_path)
        while lb < ub :
            mix = (lb + ub) >> 1
            if self.outer_prod_z(self.lpath(mix-1), self.lpath(mix), self.lpath(0), self.lpath(-1)) <= 0 :
                lb = mix + 1
            else:
                ub = mix
        return max(0, ub - 1)
        
    def find_rpeak(self):
        lb, ub = 0, len(self.right_path)
        while lb < ub :
            mix = (lb + ub) >> 1
            if self.outer_prod_z(self.rpath(0), self.rpath(-1), self.rpath(mix-1), self.rpath(mix), ) <= 0 :
                lb = mix + 1
            else:
                ub = mix
        return max(0, ub - 1)        
        
if __name__ == '__main__':
    xy = [(-1, 1), (0, 0), (0.5, 1.5), (0, 2.5), (1, 2), (1, 3), (2, 1.5), (3, 1), (1.5, 4), (3, 4), (2.5, 3), (3.2, 2), (2, 0.5)]
    # if False:
    #     with open('xy.csv', 'w') as f :
    #         for x, y in xy:
    #             f.write(f'{x},{y}\n')
    print(xy, f'points in the input provided: {len(xy)}')
    
    ch = ConvexHull(xy, SimplePolyline=False)
    print(ch)
    print(f'left peak = {ch.lpeak_ix}, right peak = {ch.rpeak_ix}')
    
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
    
    lxy = np.array([xy[i] for i in ch.left_path])
    rxy = np.array([xy[i] for i in ch.right_path])
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
