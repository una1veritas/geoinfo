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
            return
        if len(self) == 1 :
            self.xy.append(pt)
            self.polygon.append(len(self)-1)
            return
        
        # add pt to xy and polygon
        if side_of_line(self.polypoint(1), self.polypoint(0), pt) <= 0 :
            self.xy.append(pt)
            # right or front of the mouth
            self.polygon.append(self.polygon.popleft())
            self.polygon.appendleft(len(self)-1)
        elif side_of_line(self.polypoint(-1), self.polypoint(0), pt) >= 0 :
            self.xy.append(pt)
            # outside of the left line of the mouth
            self.polygon.appendleft(len(self)-1)
        # else:
        #     # error, not at growth position
        #     raise ValueError(f'point {pt} is inside the polygon.')
        #     return 
        
        self.remove_concave()
        return
           
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
        if len(self) <= 1 :
            return (0.0, 0.0, 0.0, 0.0)
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
        #print(f'peak indices = {self.polygon[0]}, {self.polygon[rtix]}, {self.polygon[bkix]}, {self.polygon[ltix % len(self.polygon)]}')
        distances = [0.0] * 4
        revvec = vec_neg(axis)
        distances[2] = dot_product(revvec, vec(self.first_point(), self.polypoint(bkix)))
        distances[1] = dot_product(perp3, vec(self.first_point(), self.polypoint(rtix)))        
        distances[3] = -dot_product(perp3, vec(self.first_point(), self.polypoint(ltix)))
        return tuple(distances)


def delta_decimation_alg(xy : list, delta, verbose = False) -> tuple:
    cvx = ConvexHull() 
    cvx_farthest_dist = 0.0
    dpath = deque()     # decimated path
    polygons = deque()   # considered polygons
    ix = 0
    dpath.append(xy[0])
    while ix < len(xy) :
        pt = xy[ix]
        verbose and print(ix, pt, cvx)
        
        if len(cvx) < 2 :
            cvx.add(pt)
            if len(cvx) == 2 :
                cvx_farthest_dist = distance_between(cvx.first_point(), cvx.last_point())
            ix += 1
            continue
        
        verbose and print(f'distance {cvx_farthest_dist} <= {delta} ?')
        verbose and print(f'side {cvx.polygon[-1]}-{cvx.polygon[0]}, {side_of_line(cvx.polypoint(-1), cvx.polypoint(0), pt)} >= 0 or {cvx.polygon[1]}-{cvx.polygon[0]}, {side_of_line(cvx.polypoint(1), cvx.polypoint(0), pt)} <= 0 ?' )
        
        if cvx_farthest_dist <= delta and \
        side_of_line(cvx.polypoint(-1), cvx.polypoint(0), pt) >= 0 or side_of_line(cvx.polypoint(1), cvx.polypoint(0), pt) <= 0 :
            verbose and print('within delta and in growth direction')
            cvx.add(pt)
            #update the furtherst dist
            cvx_farthest_dist = max(cvx_farthest_dist, distance_between(cvx.first_point(), cvx.last_point()))
            ix += 1
            continue
        
        if not cvx_farthest_dist < distance_between(cvx.first_point(), pt) :
            prevlastpt = cvx.last_point()
            dpath.append(prevlastpt)
            polygons.append([cvx.polypoint(ix) for ix in range(len(cvx.polygon) + 1)])
            cvx.clear()
            cvx.add(prevlastpt)
            cvx.add(pt)
            cvx_farthest_dist = distance_between(cvx.first_point(), cvx.last_point())
            ix += 1
            continue
                    
        # pt is in the growth position
        verbose and print('in growth distance')

        # preserve the outline of cvx before pt is added
        prev_polygon = [cvx.polypoint(ix) for ix in range(len(cvx.polygon) + 1)]
        
        # add pt to test width
        cvx.add(pt)
        cvx_farthest_dist = max(cvx_farthest_dist, distance_between(cvx.first_point(), cvx.last_point()))
        peakdists = cvx.peak_distances()
        verbose and print(peakdists, [e < delta for e in peakdists])
        
        if not all([e < delta for e in peakdists]) :
            prevlastpt = cvx.xy[-2]
            dpath.append(prevlastpt)
            polygons.append(prev_polygon)
            cvx.clear()
            cvx.add(prevlastpt)
            cvx.add(pt)
            cvx_farthest_dist = distance_between(cvx.first_point(), cvx.last_point())
        ix += 1
        verbose and print(cvx)
        verbose and print()
    
    if len(cvx) > 0 :
        #print('points exhausted,', cvx)
        dpath.append(cvx.last_point())
        polygons.append([cvx.polypoint(ix) for ix in range(len(cvx.polygon) + 1)])
    return (dpath, polygons)

if __name__ == '__main__':
    # xy = [(-1, 0.5), (-0.5, -0), (0.0, 0.5), (-1.3, 1.5), (0.0, 1.5), (0, 2.4), (1.0, 2), (1, 2.5), \
    #       (1.5, 2.75), (2, 2.75), (2.5, 3.2), \
    #       (3, 3.5), (3.2, 2), (3, 0.5),  \
    #       (3.25, 1.0), (3.25, -0.25), (3.5, 0.5), (4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1), (1.5, -0.0) ]
    
    xy = [ (0.0, 0.0), (0.3, 0.4), (0.5, -0.3), (-0.1, -0.4), (-0.3, -0.1), (-0.1, 0.2), (-0.5, 0.3), (-0.1, 0.4),  \
          (0.0, 0.8), (0.2, 0.6), (0.5, 1.1), (0.1, 1.3), (0.4, 1.5), (0.8, 1.3), (1.2, 0.9) ]
    
    # xy = [(0.0, 0.0), (-0.2, -0.3), (0.5, -0.3), (0.6, 0.2), (0.3, 0.8), (-0.1, 1.0), \
    #       (-0.2, 1.2), (0.3, 1.2), (0.5, 1.6), (0.8, 1.7), (0.9, 2.1), (1.3, 2.2), \
    #       (0.6, 1.8), (-0.1, 1.6), (-0.3, 2.1), \
    #       ]
    delta = 0.6
    # with open('xy.csv', 'w') as f :
    #     for x, y in xy:
    #         f.write(f'{x},{y}\n')
    #
    
    # xy = list()
    # with open('fukuoka_nishi_976_xy-metre.csv', 'r') as f :
    #     for l in f:
    #         lonlat = [float(e) for e in l.strip().split(',')]
    #         xy.append(tuple(lonlat))
    # # extract a part
    # xy = xy[9000:11000]
    # print(f'points in the input provided: {len(xy)}\n')
    # delta = 10

    print('-'*8)
    
    plt_annotate = False
    with Timer('delta_infinity: ') :
        dpath, polygons = delta_decimation_alg(xy, delta, verbose=True)
    print(f'len(xy) = {len(xy)}, len(dpath) = {len(dpath)}')
    
    npxy = np.array(xy)
    with Timer('rdp: ') :
        rdpxy, indices = simplify_RDP(npxy, delta)
    print(len(indices))
    
    rdpx, rdpy = rdpxy[:,0], rdpxy[:,1]
    x, y = [ x for x, y in xy], [ y for x, y in xy]
    drx, dry = [pt[0] for pt in dpath], [pt[1] for pt in dpath]
    fig, ax = plt.subplots()
    ax.plot(x, y, 'y.-', lw=4.0, alpha=0.5)
    ax.plot(drx, dry, 'k.-', lw=1) #, alpha=0.75)
    for polygon in polygons:
        px, py = [p[0] for p in polygon], [p[1] for p in polygon]
        ax.plot(px, py, 'b--', lw=1) #, alpha=0.75)

    labels = [f"{i}" for i in range(len(xy))]
    if plt_annotate :
        for x, y, label in zip(x, y, labels):
            plt.annotate(
                label,          # The text to display
                (x, y),         # The point to annotate (xy)
                textcoords="offset points", # How to position the text
                xytext=(5, 2), # Distance from the point to the text (offset)
                ha='center'     # Horizontal alignment of the text
            )
    plt.legend(['Input points', 'decimated path', 'polygon path'],loc='best')
    plt.title('delta-rect decimation Test')
    ax.set_aspect('equal')
    plt.show()
