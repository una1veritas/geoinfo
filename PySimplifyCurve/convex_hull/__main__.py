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
        self.cwpath = deque()
        self.acwpath = deque()
        
        if isinstance(points, (list, tuple)) :
            for p in points:
                if SimplePolyline == False :
                    if not self.add(p) :
                        break
                else:
                    if not self.add_simplepolyline(p):
                        break
    
    def __len__(self):
        return len(self.xy)
    
    def __str__(self):
        return str(self.xy)+', '+str(self.cwpath)+', '+str(self.acwpath)
    
    def cwise(self, ix):
        return self.xy[self.cwpath[ix]]
    
    def acwise(self, ix):
        return self.xy[self.acwpath[ix]]
    
    @staticmethod
    def left_side(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 0

    @staticmethod
    def right_side(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) < 0
    
    '''returns axis vector'''
    def axis(self):
        '''the first and the last points of the left and the right paths are identical.'''
        return self.xy[self.cwpath[-1]] - self.xy[0]
    
    def add(self, pt):
        if isinstance(pt, (list, tuple)) and len(pt) >= 2 :
            pt = tuple(pt[:2])
        elif isinstance(pt, (np.ndarray)) and len(pt) >= 2 :
            pt = (float(pt[0]), float(pt[1]))
        else :
            #isinstance(pt, Point2D) 
            raise ValueError(f"Point2D or list/tuple needed, {pt} ({type(pt)}).")
        
        self.xy.append(pt)
        if len(self) <= 2 :
            self.cwpath.append(len(self)-1)
            self.acwpath.append(len(self)-1)
            return True
        
        print(pt, self.cwise(-1), self.cwise(-2), self.right_side(self.cwise(-1), self.cwise(-2), pt))
        if self.right_side(self.cwise(-2), self.cwise(-1), pt) and self.left_side(self.acwise(-2), self.acwise(-1), pt) :
            # reject point if is is inside the last paths of clockwise path and anti-clockwise path
            #print(f'skip adding {pt} to left and right paths.\n')
            return False
        # axorg = self.xy[0]
        # axlast = self.xy[self.leftpath[-1]]
        # if axorg.distance_to(axlast) > axorg.distance_to(pt) :
        #     # print("a nearer point to axorg")
        #     # if pt.side_from_vector(self.xy[self.leftpath[-1]], self.xy[self.leftpath[-2]]) < 0 \
        #     # and pt.side_from_vector(self.xy[self.rightpath[-1]], self.xy[self.rightpath[-2]]) > 0 :
        #     #    return
        #     return False
        #print(f'adding {pt} to convex hull')
        self.cwpath.append(len(self)-1)
        self.cwpath_convexing()
        self.acwpath.append(len(self)-1)
        self.ccwpath_convexing()
        return True
    
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
            
    def cwpath_convexing(self):
        #print(self.cwpath)
        lastix = self.cwpath.pop() # from the lastpt to the first
        lastpt = self.xy[lastix]
        while len(self.cwpath) >= 2 :
            prev = self.xy[self.cwpath[-1]]
            befprev = self.xy[self.cwpath[-2]]
            if self.right_side(lastpt, self.cwise(-1), self.cwise(-2)) : # left inner side
                #print('pop!!!', lastpt, self.cwise(-1), self.cwise(-2), self.right_side(lastpt, self.cwise(-1), self.cwise(-2)))
                self.cwpath.pop() # pop-out the prev point
                #print(self.cwpath)
            else:
                break
        self.cwpath.append(lastix)
        
    def ccwpath_convexing(self):
        lastix = self.acwpath.pop()
        last = self.xy[lastix]
        while len(self.acwpath) >= 2 :
            prev = self.xy[self.acwpath[-1]]
            befprev = self.xy[self.acwpath[-2]]
            if self.left_side(last, self.acwise(-1), self.acwise(-2)) :
                self.acwpath.pop() # pop-out the prev point
            else:
                break
        self.acwpath.append(lastix)
    
    # def left_path_list(self):
    #     return list(self.leftpath)
    #
    # def right_path_list(self):
    #     return list(self.rightpath)

    def add_simplepolyline(self, ptlist):
        if ptlist == None or len(ptlist) < 3 :
            raise ValueError("Empty or too short point list")
        self.points = [Point2D(x, y) for x, y in ptlist]
        self.hull = deque()
        print(f"starts with self.points = {self.points}\n")
        
        ''' 1 '''
        v1 = self.points[0]
        v2 = self.points[1]
        v3 = self.points[2]
        if v3.side_of_line(v1, v2) > 0 :
            self.push(0)
            self.push(1)
        else:
            self.push(1)
            self.push(0)
        self.push(2)
        self.push(2)
        print(f"The first three points in hull: {self.hull}")
        
        pix = 3
        while pix < len(self.points) :
            ''' 2 '''
            v = self.points[pix]
            pix += 1
            print(f"v = {v}, points = {self.points[pix:]}")
            while pix < len(self.points) and \
            not ( self[1].side_of_line(v, self[0]) < 0 or v.side_of_line(self[-2], self[-1]) < 0 ) :
                v = self.points[pix]
                pix += 1
            print(f"v = {v}, points = {self.points[pix:]}")
            
            ''' 3 '''
            while not ( v.side_of_line(self[-2], self[-1]) > 0 ) :
                self.pop()
                print(f"d = {self.hull}\n")
            self.push(pix)
            print(f"self.hull = {self.hull}")
            print("Go Step 4\n")
            
            ''' 4 '''
            while not (self[1].side_of_line(v, self[0]) > 0) :
                self.remove()
            self.insert(pix)
        
if __name__ == '__main__':
    xy = [(0, 0), (-1, 1), (0.5, 1.5), (0, 2.5), (1, 2), (1, 3), (2, 1.5), (3, 1), (1.5, 4), (3, 4), (2.5, 3), (3.2, 2), (2, 0.5)]
    # if False:
    #     with open('xy.csv', 'w') as f :
    #         for x, y in xy:
    #             f.write(f'{x},{y}\n')
    print(xy, f'points in the input provided: {len(xy)}')
    print(f'{xy[2]} is right side of line {xy[0]} to {xy[1]}? {ConvexHull.left_side(xy[0], xy[1], xy[2]) }\n')
    
    ch = ConvexHull(xy)    
    print(ch)
    
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
    
    lxy = np.array([xy[i] for i in ch.cwpath])
    rxy = np.array([xy[i] for i in ch.acwpath])
    lx , ly = lxy[:,0], lxy[:,1]
    rx, ry = rxy[:,0], rxy[:,1]
    
    fig, ax = plt.subplots()
    ax.plot(x, y, 'y.-', lw=4.0)
    ax.plot(lx, ly, 'b.--', lw=1) #, alpha=0.75)
    ax.plot(rx, ry, 'r.--', lw=1) #, alpha=0.75)
    #ax.plot(rdpx, rdpy, 'g.-', lw=0.75) #, alpha=0.75)
    #plt.plot(x_new, y_new, 'y-')
    plt.legend(['Input points', 'clockwise path', 'counter-clockwise path', 'True'],loc='best')
    plt.title('Convex Hull function Test')
    ax.set_aspect('equal')
    plt.show()
