'''
Created on 2026/01/10

@author: sin
'''
import math
from collections import deque

class Point2D:
    def __init__(self, xy, yy = None):
        if yy != None :
            self.x = xy
            self.y = yy
        elif isinstance(xy, Point2D) :
            self.x = xy.x
            self.y = xy.y
        elif isinstance(xy, (list, tuple)) :
            self.x = xy[0]
            self.y = xy[1]
        else:
            raise ValueError(f"undefined conversion to Point2D from {xy} ({type(xy)})")
            
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

    ''' < 0 ... self is left , > 0 ... self is right''' 
    def side_from_vector(self, orgpt, dstpt):
        return (dstpt - orgpt).outer_prod_norm(self - orgpt)
    
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

class ConvexHullOfSimplePolyline: 
    def __init__(self, ptlist = None):
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
            
    def __getitem__(self, key):
        if isinstance(key, int) :
            return self.points[self.hull[key]]
        raise KeyError('has no such key {key}')
        
    def __repr__(self):
        return f"ConvexHull({self.points}, {self.hull})"
        
    def __str__(self):
        return f"ConvexHull({self.points}, {list(self.hull)})"
        
    def __len__(self):
        return len(self.points)
    
    def hullpoint(self, ix):
        return self.points[self.hull[ix]]
    
    def push(self, ix):
        self.hull.append(ix)
        
    def pop(self):
        return self.points[self.hull.pop()]
    
    def insert(self, ix):
        self.hull.appendleft(ix)
        
    def remove(self):
        return self.points[self.hull.popleft()]
    
if __name__ == '__main__':
    points = [(0, 0), (0, 1), (0.5, 0.5), (1, 0.2), ]
    a = Point2D(points[0])
    b = Point2D(points[1])
    c = Point2D(points[2])
    print(f"{c} is on side {c.side_of_line(a, b)} of the line from {a} to {b}.\n")
    
    cvh = ConvexHullOfSimplePolyline(points)
    print("\rFinally got :")
    print(len(cvh))
    print(cvh)
    