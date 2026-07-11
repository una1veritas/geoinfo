'''
Created on 2026/07/09

@author: sin
'''

from ringarray import ringarray
from point2d import *　

class ConvexHull(object):
    '''
    Convex Hull for simple polygon points by double ended queue
    '''
    def __init__(self, delta = 0.0):
        self.points = list() # index seq of Point2Ds considering
        self.polygon_index = ringarray(127)     # index seq in clockwise
        self.tolerance = delta
    
    def clear(self):
        self.points.clear()
        self.polygon_index.clear()　　
        
    def __len__(self):
        return len(self.points)
    
    def __str__(self):
        return f'ConvexHull({", ".join([ str(i)+":"+str(self[i]) for i in range(len(self))])} {[i for i in self.polygon_index]}'
    
    def __getitem__(self, index):
        return self.points[index]
    
    def point(self, index):
        return self.points[index]
    
    def first_point(self):
        return self.points[0]
    
    def last_point(self):
        return self.points[-1]
    
    def polygon_point(self, index):
        return self.points[self.polygon_index[index % len(self.polygon_index)]]
    
    def polygon_points(self):
        if len(self.polygon_index) == 0 :
            return []
        return [self.polygon_point(i) for i in range(len(self.polygon_index) + 1)]
    
    # test and add pt to points
    def add(self, pt):
        #print(pt)
        if len(self) == 0 :
            self.points.append(pt)
            return True
        if self.tolerance > 0.0 and distance(self.first_point(), pt) <= self.tolerance :
            self.points.append(pt)
            return True
        if len(self.polygon_index) == 0 :
            self.points.append(pt)
            self.polygon_index.add(0)
            self.polygon_index.add(len(self) - 1)
            return True
        if len(self.polygon_index) == 1 :
            self.points.add(pt)
            self.polygon_index.add(len(self) - 1)
            return True

        axvec = vec(self.points[0], self.points[-1])
        newvec = vec(self.points[0], pt)
        if norm(axvec) > norm(newvec) :
            # pt getting nearer.
            return False
        
        # point[0]-point[1]-pt
        if rhombus(self.polygon_point(1), self.polygon_point(0), pt) <= 0 :
            self.points.append(pt)
            # right or front of the mouth
            self.polygon_index.add(self.polygon_index.popleft())
            self.polygon_index.appendleft(len(self) - 1)
        elif rhombus(self.polygon_point(-1), self.polygon_point(0), pt) >= 0 :
            self.points.append(pt)
            # outside of the left line of the mouth
            self.polygon_index.appendleft(len(self)-1)
        else:
            # reject point and close convex-hull
            print(f"failed on point {pt}")
            print(self.polygon_point(1), self.polygon_point(0), pt, rhombus(self.polygon_point(1), self.polygon_point(0), pt))
            print(self.polygon_point(-1), self.polygon_point(0), pt, rhombus(self.polygon_point(-1), self.polygon_point(0), pt))
            return False
        
        self.remove_concave()
        return True
           
    def remove_concave(self):
        # from tail
        #print(self.polygon_index)
        beak_ix = self.polygon_index.popleft()    # polygon_index is a ring sequence
        beak = self.point(beak_ix)
        
        #print(f'beak = {beak} ({beak_ix})')
        # anti-clockwise check and pop
        while len(self.polygon_index) > 2 :
            if rhombus(beak, self.polygon_point(-1), self.polygon_point(-2)) < 0 : 
                self.polygon_index.pop() # pop-out polygon_index[-1]
            else:
                break
        # from mouth, clock wise check and pop
        while len(self.polygon_index) > 2 :
            if rhombus(beak, self.polygon_point(0), self.polygon_point(1)) > 0 : 
                self.polygon_index.popleft() # pop-out polygon_index[0]
            else:
                break
        self.polygon_index.appendleft(beak_ix)
        #print(self.polygon_index)
        
    def peak_distances(self):
        if len(self) <= 2 or len(self.polygon_index) <= 2 :
            return (0.0, 0.0, 0.0, 0.0)
        
        axis = unitvec(self[0], self[-1])   #代表線ベクトル
        # print(f'axis = {axis}')

        # forward peak -- the beak of the polygon
        fwix = 0
        #print(self)
        #print(f'fwix = {fwix}, point ix = {self.polygon_index[fwix]}, {self.polygon_point(fwix)}')
        
        # print('polygon index array head = ',self.polygon_index.array_head())
        # backward peak -- 
        # backard peak exists between the first point and the last point (beak), 
        # because the beak cannot be the backward peak
        # determine which side, clockwise or counter-clock wise, of the polygon has backward peak 
        # by taking dot product with the lines to or from the first point

        # backward peak
        # the starting point == self.points[0] is possibly not on self.polygon
        # so we search it as the point where dot product with axis switches to negative to positive
        # by binary search on polygon cycle in clockwise direction
        
        lb, ub = fwix, len(self.polygon_index) - 1
        while lb < ub :
            mix = (lb + ub) >> 1
            # print(f'lb = {lb}, ub = {ub}, mix = {mix}')
            proj = dot_product(vec(self.polygon_point(mix), self.polygon_point(mix+1)), axis)
            if proj < 0 :
                lb = mix + 1
            else:
                ub = mix
            #mix = (lb + ub) >> 1
        bkix = ub   # (bkix)-th of polygon_index
        #print(f'bkix = {bkix},  point ix = {self.polygon_index[bkix]}, {self.polygon_point(bkix)}')
        
        # clockwise
        perp3 = perpvec(axis)
        # anti-clockwise
        perp9 = perpvec(axis, clockwise=False)
        # print(f'perp3 = {perp3}, perp9 = {perp9}')
        
        # right peak
        lb, ub = fwix, bkix
        # print(f'rtix lb = {lb}, ub = {ub}')
        while lb < ub :
            mix = (lb + ub) >> 1
            proj = dot_product(vec(self.polygon_point(mix), self.polygon_point(mix+1)), perp3)
            # mvec = vec(self.polygon_point(mix), self.polygon_point(mix+1))
            # print(f'lb = {lb}, ub = {ub}, mix = {mix}, mvec = {mvec}, proj = {proj}')
            if proj > 0 :
                lb = mix + 1
            else:
                ub = mix
            #mix = (lb + ub) >> 1
        rtix = ub
        #print(f'rtix = {rtix},  point ix = {self.polygon_index[rtix]}, {self.polygon_point(rtix)}')
        
        # left peak
        lb, ub = bkix, len(self.polygon_index) # last index + 1 -> 0
        mix = (lb + ub) >> 1
        while lb < ub :
            proj = dot_product(vec(self.polygon_point(mix), self.polygon_point(mix+1)), perp9)
            if proj > 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        ltix = ub
        #print(f'ltix = {ltix}, point ix = {self.polygon_index[ltix % len(self.polygon_index)]}, {self.polygon_point(ltix)}')

        #print(f'peak indices = {self.polygon_index[0]}, {self.polygon_index[rtix]}, {self.polygon_index[bkix]}, {self.polygon_index[ltix % len(self.polygon_index)]}')
        return (0.0, \
                dot_product(perp3, vec(self[0], self.polygon_point(rtix))), \
                dot_product( vec_neg(axis), vec(self[0], self.polygon_point(bkix))), \
                -dot_product(perp9, vec(self[0], self.polygon_point(ltix))), )

        