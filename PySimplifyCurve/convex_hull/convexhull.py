'''
Created on 2026/07/09

@author: sin
'''

from ringarray import ringarray
from point2d import vec, rhombus, distance, cross_product_norm, dot_product, \
distance_to_line, norm, unitvec, vec_neg

class ConvexHull(object):
    '''
    classdocs
    '''
    # def __init__(self, params):
    #     '''
    #     Constructor
    #     '''
    
    def __init__(self):
        # self.xy = list(xyseq)
        self.points = list() # index seq of Point2Ds considering
        self.polygon_index = ringarray(127)     # index seq in clockwise
    
    def clear(self):
        self.points.clear()
        self.polygon_index.clear()
        
    def __len__(self):
        return len(self.points)
    
    def __str__(self):
        return f'ConvexHull({[ str(i)+":"+str(self[i]) for i in range(len(self))]}, {[i for i in self.polygon_index]})'
    
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
    
    def add(self, pt):
        if len(self) <= 1 :
            self.points.append(pt)
            self.polygon_index.append(len(self)-1)
            return True
        
        # add ptix to ptix and polygon_index
        if rhombus(self.polygon_point(1), self.polygon_point(0), pt) <= 0 :
            self.points.append(pt)
            # right or front of the mouth
            self.polygon_index.append(self.polygon_index.popleft())
            self.polygon_index.appendleft(len(self) - 1)
        elif rhombus(self.polygon_point(-1), self.polygon_point(0), pt) >= 0 :
            self.points.append(pt)
            # outside of the left line of the mouth
            self.polygon_index.appendleft(len(self)-1)
        else:
            # reject point and close convex-hull
            return False
        
        self.remove_concave()
        return True
           
    def remove_concave(self):
        # from tail
        beak_ix = self.polygon_index.popleft()    # polygon_index is a ring sequence
        beak = self.point(beak_ix)
        
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
    
    def peak_distances(self):
        fwix = 0    # forward peak index == mouth (polygon_index start)
        if len(self) <= 1 :
            return (0.0, 0.0, 0.0, 0.0)
        axis = unitvec(self[0], self[-1])
        # backward peak, - --> +
        lb, ub = 0, len(self.polygon_index) - 1
        mix = (lb + ub) >> 1
        while lb < ub :
            proj = dot_product(vec(self.polygon_point(mix), self.polygon_point(mix+1)), axis)
            if proj < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        bkix = ub
        # right peak
        perp9 = (-axis[1], axis[0])
        lb, ub = fwix, bkix
        mix = (lb + ub) >> 1
        while lb < ub :
            proj = dot_product(vec(self.polygon_point(mix), self.polygon_point(mix+1)), perp9)
            if proj < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        rtix = ub
        # left peak
        perp3 = vec_neg(perp9)
        lb, ub = bkix, len(self.polygon_index)
        mix = (lb + ub) >> 1
        while lb < ub :
            proj = dot_product(vec(self.polygon_point(mix), self.polygon_point(mix+1)), perp3)
            if proj < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        ltix = ub
        #print(f'peak indices = {self.polygon_index[0]}, {self.polygon_index[rtix]}, {self.polygon_index[bkix]}, {self.polygon_index[ltix % len(self.polygon_index)]}')
        return (0.0, \
                dot_product(perp3, vec(self[0], self.polygon_point(rtix))), \
                dot_product( (-axis[0], -axis[1]), vec(self[0], self.polygon_point(bkix))), \
                -dot_product(perp3, vec(self[0], self.polygon_point(ltix))), )

        