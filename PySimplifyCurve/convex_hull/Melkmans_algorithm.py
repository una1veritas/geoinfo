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

class ConvexHull: 
    def __init__(self, ptlist = None):
        if ptlist == None or len(ptlist) < 3 :
            raise ValueError("Empty or too short point list")
        self.points = [Point2D(x, y) for x, y in ptlist]
        self.hull = deque()

        pts = deque(self.points)
        print(f"starts with pts = {pts}")
        ''' 1 '''
        v1 = pts.popleft()
        v2 = pts.popleft()
        v3 = pts.popleft()
        if v3.side_of_line(v1, v2) > 0 :
            self.hull.append(v1)
            self.hull.append(v2)
        else:
            self.hull.append(v2)
            self.hull.append(v1)
        self.hull.append(v3)
        self.hull.appendleft(v3)
        print(f"The first three points in hull: {self.hull}")
        
        while len(pts) > 0 :
            ''' 2 '''
            while True :
                v = pts.popleft()
                print(f"popped {v}, in pts remain {pts}.")
                if ( self.hull[1].side_of_line(v, self.hull[0]) < 0 or v.side_of_line(self.hull[-2], self.hull[-1]) < 0 ) :
                    break
                if len(pts) == 0 :
                    return
            print(f"Step 2 result: v = {v}\n")
            
            ''' 3 '''
            while True :
                print(f"{v} is side {v.side_of_line(self.hull[0], self.hull[1])} of line from {self.hull[0]} to {self.hull[1]}")
                if v.side_of_line(self.hull[0], self.hull[1]) > 0 :
                    break
                p = self.hull.pop()
                print(f"{p} has been popped from self.hull = {self.hull}")
            self.hull.append(v)
            print(f"self.hull = {self.hull}")
            
            
            ''' 4 '''
            while True :
                if self.hull[1].side_of_line(v, self.hull[0]) > 0 :
                    break
                self.hull.popleft()
            self.hull.appendleft(v)
            
            
        
    def __repr__(self):
        return f"ConvexHull({self.points}, {self.hull})"
        
    def __str__(self):
        return f"ConvexHull({self.points}, {list(self.hull)})"
        
    def __len__(self):
        return len(self.points)
    
    
if __name__ == '__main__':
    points = [(0, 0), (0, 1), (0.5, 0.5), (1, 0.2), ]
    a = Point2D(points[0])
    b = Point2D(points[1])
    c = Point2D(points[2])
    print(f"{c} is on side {c.side_of_line(a, b)} of the line from {a} to {b}.")
    
    cvh = ConvexHull(points)
    print("\rFinally got :")
    print(len(cvh))
    print(cvh)
    