import numpy as np
import matplotlib.pyplot as plt
#from scipy.interpolate import make_interp_spline
import rdp
import math
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
        return f'({self.coord[0]}, {self.coord[1]})'
    
    def __str__(self):
        return f'({self.coord[0]}, {self.coord[1]})'
    
    def __tuple__(self):
        return self.coord
    
    def __neg__(self):
        return PointXY(-self.coord[0], -self.coord[1])
        
    def __sub__(self, other):
        return PointXY( self.coord[0] - other.coord[0], self.coord[1] - other.coord[1])
    
    ''' < 0 ... self is left , > 0 ... self is right''' 
    def side_from_vector(self, orgpt, dstpt):
        return (dstpt - orgpt).outer_prod_norm(self - orgpt)
    
    def norm(self):
        return math.sqrt(self.coord[0]*self.coord[0] + self.coord[1]*self.coord[1])

    ''' distance between two PointXY points '''
    def distance_to(self, vdst):
        return (vdst - self).norm()

    def outer_prod_norm(self, other):
        return self[0]*other[1] - self[1]*other[0]

    def inner_prod(self, other):
        return self[0]*other[0] + self[1]*other[1]

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
    def __init__(self):
        self.xy = list() # of PointXY
        self.leftpath = deque()
        self.rightpath = deque()
    
    def __len__(self):
        return len(self.xy)
    
    def __str__(self):
        return str(self.xy)+', '+str(self.leftpath)+', '+str(self.rightpath)
    
    '''returns axis vector'''
    def axis(self):
        '''the first and the last points of the left and the right paths are identical.'''
        return self.xy[self.leftpath[-1]] - self.xy[0]
    
    def add(self, pt):
        if isinstance(pt, (list, tuple)) and len(pt) >= 2 :
            pt = PointXY(pt[:2])
        if not isinstance(pt, PointXY) :
            raise ValueError(f"PointXY or list/tuple needed {pt}.")
        
        self.xy.append(pt)
        if len(self) <= 2 :
            self.leftpath.append(len(self)-1)
            self.rightpath.append(len(self)-1)
            return True
        else:
            print(pt, self.xy[self.leftpath[-1]], self.xy[self.leftpath[-2]], pt.side_from_vector(self.xy[self.leftpath[-1]], self.xy[self.leftpath[-2]]))
            if pt.side_from_vector(self.xy[self.leftpath[-1]], self.xy[self.leftpath[-2]]) < 0 \
            and pt.side_from_vector(self.xy[self.rightpath[-1]], self.xy[self.rightpath[-2]]) > 0 :
                # reject point if is is inside the last paths of leftpath and rightpath
                print(f'skip adding {pt} to left and right paths.')
                return False
            # axorg = self.xy[0]
            # axlast = self.xy[self.leftpath[-1]]
            # if axorg.distance_to(axlast) > axorg.distance_to(pt) :
            #     # print("a nearer point to axorg")
            #     # if pt.side_from_vector(self.xy[self.leftpath[-1]], self.xy[self.leftpath[-2]]) < 0 \
            #     # and pt.side_from_vector(self.xy[self.rightpath[-1]], self.xy[self.rightpath[-2]]) > 0 :
            #     #    return
            #     return False
            print(f'adding {pt} to convex hull')
            self.leftpath.append(len(self)-1)
            self.leftpath_convexing()
            self.rightpath.append(len(self)-1)
            self.rightpath_convexing()
    
    def isinside(self, pt):
        for ix in range(len(self.leftpath) - 1) : # from the first to the last
            orgpt = self.xy[self.leftpath[ix]]
            nxtpt = self.xy[self.leftpath[ix+1]]
            if pt.side_from_vector(orgpt, nxtpt) < 0 :
                # pt is left outer side of left path
                #print(f'{pt} is outside of left-path {orgpt}, {nxtpt}')
                return False
        print(f'{pt} is isinside of left path.')
        for ix in range(len(self.rightpath) - 1) : # from the first to the last
            orgpt = self.xy[self.rightpath[ix]]
            nxtpt = self.xy[self.rightpath[ix+1]]
            if pt.side_from_vector(orgpt, nxtpt) > 0 :
                # pt is right outer side of right path
                print(f'{pt} is outside of right-path {orgpt}, {nxtpt}')
                return False
        print(f'{pt} is isinside of right path.')
        return True
            
    def leftpath_convexing(self):
        lastix = self.leftpath.pop() # from the last to the first
        last = self.xy[lastix]
        while len(self.leftpath) >= 2 :
            prev = self.xy[self.leftpath[-1]]
            befprev = self.xy[self.leftpath[-2]]
            if prev.side_from_vector(befprev, last) > 0 : # left inner side
                self.leftpath.pop() # pop-out the prev point
            else:
                break
        self.leftpath.append(lastix)
        
    def rightpath_convexing(self):
        lastix = self.rightpath.pop()
        last = self.xy[lastix]
        while len(self.rightpath) >= 2 :
            prev = self.xy[self.rightpath[-1]]
            befprev = self.xy[self.rightpath[-2]]
            if prev.side_from_vector(befprev, last) < 0 :
                self.rightpath.pop() # pop-out the prev point
            else:
                break
        self.rightpath.append(lastix)
    
    def left_path_list(self):
        return list(self.leftpath)
    
    def right_path_list(self):
        return list(self.rightpath)

    def split(self):
        return
        
if __name__ == '__main__':
    xy = [(0, 0), (-1, 1), (0.5, 1.5), (0, 2.5), (1, 2), (1, 3), (2, 1.5), (3, 1), (1.5, 4), (3, 4), (2.5, 3), (3.2, 2), (2, 0.5)]
    # if False:
    #     with open('xy.csv', 'w') as f :
    #         for x, y in xy:
    #             f.write(f'{x},{y}\n')
    xy = np.array([[x, y] for (x,y) in xy])
    print(xy, f'points in the input provided: {len(xy)}')
    
    ch = ConvexHull()
    for pt in xy:
        ch.add(PointXY(pt))
    
    print(ch)
    
    rdpxy, indices = simplify_RDP(xy, 1.0)
    print(rdpxy, indices)
    # exit(0)
    rdpx, rdpy = rdpxy[:,0], rdpxy[:,1]
    x, y = xy[:,0], xy[:,1]
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
    ax.plot(x, y, 'y.-', lw=2.0)
    ax.plot(lx, ly, 'b.-', lw=0.75) #, alpha=0.75)
    ax.plot(rx, ry, 'r.-', lw=0.75) #, alpha=0.75)
    #ax.plot(rdpx, rdpy, 'g.-', lw=0.75) #, alpha=0.75)
    #plt.plot(x_new, y_new, 'y-')
    plt.legend(['Input points', 'Selected points', 'Interpolated B-spline', 'True'],loc='best')
    plt.title('Convex Hull function Test')
    ax.set_aspect('equal')
    plt.show()
