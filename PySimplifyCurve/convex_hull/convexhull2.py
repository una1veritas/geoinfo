'''
Created on 2026/03/01

@author: sin
'''
import numpy as np
import matplotlib.pyplot as plt
import math
import rdp
from collections import deque
import time

from point2d import vec, side_of_line, distance_between, cross_product_norm, dot_product, \
distance_to_line, norm, perpvec, unitvec, vec_neg

class Timer:
    def __init__(self, mess = ''):
        self.message = str(mess)
        
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        self.end = time.time()
        print(self.message + f"Execution time: {self.end - self.start} seconds")

def simplify_RDP(xy : np.array, epsilon):
    mask = rdp.rdp(xy, epsilon=epsilon, return_mask=True)
    xy_rdp = xy[mask]
    return xy_rdp, [int(i) for i in np.where(mask)[0]]

class ConvexHull:
    
    def __init__(self):
        self.xy = list() # of Point2D
        self.polygon = deque()     # in clockwise
    
    def clear(self):
        self.xy.clear()
        self.polygon.clear()
        
    def __len__(self):
        return len(self.xy)
    
    def __str__(self):
        return str(self.xy)+', '+str(self.polygon)
    
    def __getitem__(self, index):
        return self.xy[index]
    
    def polypoint(self, index):
        return self.xy[self.polygon[index % len(self.polygon)]]
    
    def first_point(self):
        return self.xy[0]
    
    def last_point(self):
        return self.xy[-1]
    
    def add(self, pt):
        if len(self) == 0 :
            self.xy.append(pt)
            self.polygon.append(len(self)-1)
            return True
        if len(self) == 1 :
            self.xy.append(pt)
            self.polygon.append(len(self)-1)
            return True
        
        # add pt to xy and polygon
        if distance_between(self.first_point(), self.last_point()) <= distance_between(self.first_point(), pt)  :
            self.xy.append(pt)
            if side_of_line(self.polypoint(1), self.polypoint(0), pt) <= 0 :
                # right or front of the mouth
                self.polygon.append(self.polygon.popleft())
                self.polygon.appendleft(len(self)-1)
            elif side_of_line(self.polypoint(-1), self.polypoint(0), pt) >= 0 :
                # outside of the left line of the mouth
                self.polygon.appendleft(len(self)-1)
            else:
                # error, not at growth position
                print(f'point gets inside.')
                self.xy.pop()
                return False
            
            self.remove_concave()
            return True
        else:
            print('point gets nearer.')
        return False
           
    def remove_concave(self, reverse = False):
        # from tail
        mouthix = self.polygon.popleft()    # polygon is a ring sequence
        mouthpt = self.xy[mouthix]
        # anti clockwise
        while len(self.polygon) > 2 :
            if side_of_line(mouthpt, self.polypoint(-1), self.polypoint(-2)) < 0 : 
                self.polygon.pop() # pop-out polygon[-1]
            else:
                break
        # from month, clock wise
        while len(self.polygon) > 2 :
            if side_of_line(mouthpt, self.polypoint(0), self.polypoint(1)) > 0 : 
                self.polygon.popleft() # pop-out polygon[0]
            else:
                break
        self.polygon.appendleft(mouthix)
    
    def peak_distances(self):
        fwix = 0    # forward peak index == mouth (polygon start)
        axis = unitvec(self.first_point(), self.last_point())
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
        perp3 = vec_neg(perp9)
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
        print(f'{self.polygon[0]}, {self.polygon[rtix]}, {self.polygon[bkix]}, {self.polygon[ltix]}')
        distances = [0.0] * 4
        revvec = vec_neg(axis)
        distances[2] = dot_product(revvec, vec(cvx.first_point(), cvx.polypoint(bkix)))
        distances[1] = dot_product(perp3, vec(cvx.first_point(), cvx.polypoint(rtix)))        
        distances[3] = -dot_product(perp3, vec(cvx.first_point(), cvx.polypoint(ltix)))
        return tuple(distances)
    
# def delta_decimation_alg(xy : list, delta) -> tuple:
#     cvx = ConvexHull() # xy, SimplePolyline=False)
#     dq = deque(xy)
#     dpath = deque()
#     lpath = deque()
#     rpath = deque()
#     dpath.append(dq[0])
#     # cvx must have at least two points.
#     while len(dq) :
#         pt = dq.popleft()
#         print(f'adding {pt}')
#         if len(cvx) < 2 :
#             cvx.add(pt)
#             continue
#         prelastpt = cvx[-1]
#         preleft = deque(cvx.left_path)
#         preright = deque(cvx.right_path)
#         if cvx.growing_position(pt) : #, Navel = True) :
#             cvx.add(pt) #, Navel = True)
#             if cvx.leftpeak_distance() <= delta and cvx.rightpeak_distance() <= delta :
#                 print(cvx)
#                 if len(cvx) > 2 :
#                     print(f'left peak {cvx[cvx.find_left_peak()]} dist = {cvx.leftpeak_distance()}, right peak {cvx[cvx.find_right_peak()]} dist = {cvx.rightpeak_distance()}')
#                     print('cvx growing.\n')
#             else:
#                 # added but stuck out
#                 print(f'left peak dist = {cvx.leftpeak_distance()}, right peak dist = {cvx.rightpeak_distance()}')
#                 # close the previous convex hull as a simplifi ed line segment
#                 lastpt = cvx[-1]
#                 dpath.append(prelastpt) # close the path
#                 lpath += [cvx[i] for i in preleft]
#                 rpath += [cvx[i] for i in preright]
#                 cvx.clear()
#                 dq.appendleft(lastpt)
#                 dq.appendleft(prelastpt)
#                 print(f'cvx has been reset: {cvx}\n')
#         else:
#             print(f'not growing position {pt}')
#             print(f'terminate the hull')
#             lastpt = cvx[-1]
#             dpath.append(lastpt)
#             print(f'new line {dpath[-2]}, {dpath[-1]}')
#             lpath += [cvx[i] for i in preleft]
#             rpath += [cvx[i] for i in preright]
#             cvx.clear()
#             dq.appendleft(pt)
#             dq.appendleft(lastpt)
#             print('cvx has been reset.\n')
#     if len(cvx) > 0 :
#         dpath.append(cvx[-1])
#         lpath += [cvx[i] for i in cvx.left_path]
#         rpath += [cvx[i] for i in cvx.right_path]
#     return (dpath, lpath, rpath)

def sgn(val):
    if isinstance(val, int) :
        return -1 if val < 0 else 0 if val == 0 else 1
    if isinstance(val, float) :
        return -1.0 if val < 0.0 else 0.0 if val == 0.0 else 1.0
     
if __name__ == '__main__':
    # xy = [(-1, 0.5), (-0.5, -0), (0.0, 0.5), (-1, 1.25), (0.0, 1.5), (0, 2.4), (1.25, 2), (1, 3), \
    #     (1.5, 2.75), (2, 2.75), (2.5, 3.2), (3, 3.5), (3.2, 2), (3, 0.5),  \
    #     (3.5, 1.0), (2.5, -0.25), (3.5, 0.5), ] #(4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1), (1.5, -0.75) ]
    xy = [(0.0, 0.0), (-0.15, -0.1), (0.25, -0.35), (0.5, 0.25), (0.35, 0.65), (-0.25, 0.85), (0.25, 1.0), (0.45, 1.2)]
    # with open('xy.csv', 'w') as f :
    #     for x, y in xy:
    #         f.write(f'{x},{y}\n')
    #
    # xy = list()
    # with open('2026-02-28-225436-metre.csv', 'r') as f :
    #     for l in f:
    #
    #         lonlat = [float(e) for e in l.strip().split(',')]
    #         xy.append(tuple(lonlat))
    # print(xy[:10])
    # print(f'points in the input provided: {len(xy)}\n')
    # xy = xy[500:]
    
    cvx = ConvexHull()
    distmax = 0.0
    for pt in xy :
        if len(cvx) == 0 :
            cvx.add(pt)
        else:
            if not cvx.add(pt) :
                print(f'failed to add {pt}')
                break
        print(cvx)
        
    peakdists = [f'{d:.3}' for d in cvx.peak_distances()]
    print(peakdists)
    # axvec = vec(cvx.first_point(), cvx.last_point())
    # revvec = vec_neg(axvec)
    # bkpeak = cvx.polypoint(peaks[2])
    # bkvec = vec(cvx.first_point(), cvx.polypoint(peaks[2]))
    # print(revvec, bkpeak, bkvec, dot_product(revvec, bkvec))
    #
    # perp3vec = perpvec(axvec)
    # rtpeak = cvx.polypoint(peaks[1])
    # rtvec = vec(cvx.first_point(), rtpeak)
    # print(perp3vec, rtpeak, rtvec, dot_product(perp3vec, rtvec))
    #
    # ltpeak = cvx.polypoint(peaks[3])
    # ltvec = vec(cvx.first_point(), ltpeak)
    # print(perp3vec, ltpeak, ltvec, -dot_product(perp3vec, ltvec))
    print('-'*8)
    
    p0, pn = cvx.first_point(), cvx.last_point()
    axis = vec(p0, pn)
    print(f'{p0}, {pn}, {axis}')
    uaxis = unitvec(axis)
    u3oclock = perpvec(uaxis, clockwise = True)
    print(f'uaxis = {uaxis}, u3oclock = {u3oclock}')
    for ix in range(len(cvx.polygon)) :
        pt0 = cvx.polypoint(ix - 1)
        pt1 = cvx.polypoint(ix)
        pt2 = cvx.polypoint(ix + 1)
        ptvec0 = unitvec(pt0, pt1)
        ptvec1 = unitvec(pt1, pt2)
        print(f'{cvx.polygon[ix-1]} - {cvx.polygon[ix]}, \t', end = ' ')
        print(f'{dot_product(uaxis, ptvec0):.3}, {dot_product(u3oclock, ptvec0):.3}, ')
        #print()
        
    #dpath, lpath, rpath = delta_decimation_alg(xy, 6)
    

    #rdpx, rdpy = rdpxy[:,0], rdpxy[:,1]
    x, y = [ x for x, y in cvx.xy], [ y for x, y in cvx.xy]
    polygon = list(cvx.polygon) + [cvx.polygon[0]]
    px, py = [xy[i][0] for i in polygon], [xy[i][1] for i in polygon]
    axisx, axisy = [pt[0] for pt in cvx.xy[:1]+cvx.xy[-1:]], [pt[1] for pt in cvx.xy[:1]+cvx.xy[-1:]]
    fig, ax = plt.subplots()
    ax.plot(x, y, 'y.-', lw=4.0, alpha=0.5)
    ax.plot(px, py, 'b.--', lw=1) #, alpha=0.75)
    ax.plot(axisx, axisy, 'k.-', lw=1) #, alpha=0.75)
    labels = [f"{i}" for i in range(len(cvx.xy))]
    for x, y, label in zip(x, y, labels):
        plt.annotate(
            label,          # The text to display
            (x, y),         # The point to annotate (xy)
            textcoords="offset points", # How to position the text
            xytext=(5, 2), # Distance from the point to the text (offset)
            ha='center'     # Horizontal alignment of the text
        )
    plt.legend(['Input points', 'clockwise polygon path'],loc='best')
    plt.title('Convex Hull function Test')
    ax.set_aspect('equal')
    plt.show()
