'''
Created on 2026/07/09

@author: sin
'''

from ringarray import ringarray
from point2d import vec, rhombus, distance, cross_product_norm, dot_product, \
distance_to_line, norm, unitvec

class ConvexHull(object):
    '''
    classdocs
    '''
    # def __init__(self, params):
    #     '''
    #     Constructor
    #     '''
    
    def __init__(self, xyseq):
        self.xy = list(xyseq)
        self.ptix = list() # index seq of Point2Ds considering
        self.polygon = ringarray(127)     # index seq in clockwise
    
    def clear(self):
        self.ptix.clear()
        self.polygon.clear()
        
    def __len__(self):
        return len(self.ptix)
    
    def __str__(self):
        return f'ConvexHull({self.ptix}, {[self.ptix[i] for i in self.polygon]})'
    
    def __getitem__(self, index):
        return self.xy[self.ptix[index]]
    
#    def point(self, index):
#        return self.xy[self.ptix[index]]
    
    def polypoint(self, index):
        return self.xy[self.ptix[self.polygon[index % len(self.polygon)]]]
    
    def polyptix(self, index):
        return self.ptix[self.polygon[index % len(self.polygon)]]
    
    def add(self, ptix):
        if len(self) <= 1 :
            self.ptix.append(ptix)
            self.polygon.append(len(self)-1)
            return
        
        # add ptix to ptix and polygon
        if rhombus(self.polypoint(1), self.polypoint(0), self.xy[ptix]) <= 0 :
            self.ptix.append(ptix)
            # right or front of the mouth
            self.polygon.append(self.polygon.popleft())
            self.polygon.appendleft(len(self)-1)
        elif rhombus(self.polypoint(-1), self.polypoint(0), self.xy[ptix]) >= 0 :
            self.ptix.append(ptix)
            # outside of the left line of the mouth
            self.polygon.appendleft(len(self)-1)
        # else:
        #     # error, not at growth position
        #     raise ValueError(f'point {pt} is inside the polygon.')
        #     return 
        
        self.remove_concave()
        return
           
    def remove_concave(self):
        # from tail
        mouthix = self.polygon.popleft()    # polygon is a ring sequence
        mouthpt = self[mouthix] #self.point(mouthix)
        # anti clockwise
        while len(self.polygon) > 2 :
            if rhombus(mouthpt, self.polypoint(-1), self.polypoint(-2)) < 0 : 
                self.polygon.pop() # pop-out polygon[-1]
            else:
                break
        # from mouth, clock wise
        while len(self.polygon) > 2 :
            if rhombus(mouthpt, self.polypoint(0), self.polypoint(1)) > 0 : 
                self.polygon.popleft() # pop-out polygon[0]
            else:
                break
        self.polygon.appendleft(mouthix)
    
    def peak_distances(self):
        fwix = 0    # forward peak index == mouth (polygon start)
        if len(self) <= 1 :
            return (0.0, 0.0, 0.0, 0.0)
        axis = unitvec(self[0], self[-1])
        # backward peak, - --> +
        lb, ub = 0, len(self.polygon) - 1
        mix = (lb + ub) >> 1
        while lb < ub :
            proj = dot_product(vec(self.polypoint(mix), self.polypoint(mix+1)), axis)
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
            proj = dot_product(vec(self.polypoint(mix), self.polypoint(mix+1)), perp9)
            if proj < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        rtix = ub
        # left peak
        perp3 = (-perp9[0], -perp9[1])
        lb, ub = bkix, len(self.polygon)
        mix = (lb + ub) >> 1
        while lb < ub :
            proj = dot_product(vec(self.polypoint(mix), self.polypoint(mix+1)), perp3)
            if proj < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        ltix = ub
        #print(f'peak indices = {self.polygon[0]}, {self.polygon[rtix]}, {self.polygon[bkix]}, {self.polygon[ltix % len(self.polygon)]}')
        return (0.0, dot_product(perp3, vec(self[0], self.polypoint(rtix))), \
                dot_product( (-axis[0], -axis[1]), vec(self[0], self.polypoint(bkix))), -dot_product(perp3, vec(self[0], self.polypoint(ltix))), )

        