'''
Created on 2026/03/01

@author: sin
'''
import numpy as np
import matplotlib.pyplot as plt
import math
import rdp
import fastrdp
from collections import deque
from ringarray import ringarray
import time

from point2d import vec, rhombus, distance, cross_product_norm, dot_product, \
distance_to_line, norm, unitvec
from myrdp import rdp_decimation_alg, rdp_decimation_alg_recursive

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
        while len(self.polygon) > 3 :
            if rhombus(mouthpt, self.polypoint(-1), self.polypoint(-2)) < 0 : 
                self.polygon.pop() # pop-out polygon[-1]
            else:
                break
        # from mouth, clock wise
        while len(self.polygon) > 3 :
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


def delta_rect_decimation_alg(xy : list, delta, verbose = False, polygons = False) -> tuple:
    dixpath = list()     # index sequence of decimated path
    polygon_seq = list()   # considered polygons
    dixpath.append(0)
    cvx = ConvexHull(xy) 
    cvx.add(0)
    cvx.add(1)
    cvx_diameter  = distance(cvx[0], cvx[-1]) #= distance(cvx.first_point(), cvx.last_point())
    ptix = 2
    while ptix < len(xy) :

        verbose and print(f'{ptix}, {xy[ptix]}, dia = {cvx_diameter}, delta = {delta}, {cvx}')
        verbose and print(f'side {cvx.polygon[-1]}-{cvx.polygon[0]}, {rhombus(cvx.polypoint(-1), cvx.polypoint(0), xy[ptix])} >= 0 or {cvx.polygon[1]}-{cvx.polygon[0]}, {rhombus(cvx.polypoint(1), cvx.polypoint(0), xy[ptix])} <= 0 ?' )
        if cvx_diameter <= delta and \
        ( rhombus(cvx.polypoint(-1), cvx.polypoint(0), xy[ptix]) >= 0 or rhombus(cvx.polypoint(1), cvx.polypoint(0), xy[ptix]) <= 0 ):
            verbose and print('within delta and in growth position')
            cvx.add(ptix)
            cvx_diameter = max(cvx_diameter, distance(cvx[0], cvx[-1]) ) # = max(cvx_diameter, distance(cvx.first_point(), cvx.last_point()) )
            ptix += 1
            verbose and print(cvx)
            verbose and print()
            continue
        
        verbose and print('check wether pt is furthest or not.')
        if cvx_diameter > distance(cvx[0], xy[ptix]) : # distance(cvx.first_point(), xy[ptix]) :
            verbose and print('getting nearer. stop extending cvx')
            cvx_lastix = cvx.ptix[-1]
            dixpath.append(cvx_lastix)
            if polygons : 
                polygon_seq.append([cvx.polyptix(i) for i in range(len(cvx.polygon) + 1)])
            cvx.clear()
            # make new cvx for the 1st and 2nd points.
            cvx.add(cvx_lastix)
            cvx.add(ptix)
            verbose and print(cvx)
            verbose and print(cvx[0], cvx[-1]) #print(cvx.first_point(), cvx.last_point())
            cvx_diameter = distance(cvx[0], cvx[-1])
            ptix += 1
            verbose and print(cvx)
            verbose and print()
            continue
        
        # pt is in the growth position
        verbose and print('pt is at growth distance')
        
        # preserve the outline of cvx before pt is added
        if polygons : 
            prevcvx_polygon = [cvx.polyptix(i) for i in range(len(cvx.polygon) + 1)]
        
        # add pt to test width
        cvx.add(ptix)
        peakdists = cvx.peak_distances()
        verbose and print(peakdists, [e < delta for e in peakdists])
        
        if all([e < delta for e in peakdists]) :
            cvx_diameter = distance(cvx[0], cvx[-1])
            ptix += 1
            verbose and print(cvx)
            verbose and print()
            continue
        else:
            prevcvx_lastix = cvx.ptix[-2]
            dixpath.append(prevcvx_lastix)
            if polygons : 
                polygon_seq.append(prevcvx_polygon)
            cvx.clear()
            cvx.add(prevcvx_lastix)
            cvx.add(ptix)
            cvx_diameter = distance(cvx[0], cvx[-1])
            ptix += 1
            verbose and print(cvx)
            verbose and print()
            continue
        raise ValueError('???')
    
    if len(cvx) > 0 :
        #print('points exhausted,', cvx)
        dixpath.append(cvx.ptix[-1])
        if polygons : 
            polygon_seq.append([cvx.polyptix(ix) for ix in range(len(cvx.polygon) + 1)])
    
    if not polygons :
        return dixpath
    else:
        return (dixpath, polygon_seq)

if __name__ == '__main__':
    xy = [ (0,0), (0.25, 0.6), (0.8, 0.25), (1.0, 0.75), (1.4, 0.7), (1.5, 1.0), \
          (1.5, 2.75), (2, 2.75), (2.5, 3.2), \
    #      (3, 3.5), (3.2, 2), (3, 0.5),  \
    #      (3.25, 1.0), (3.25, -0.25), (3.5, 0.5), (4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1), (1.5, -0.0) ]
    ]
    # xy = [ (0.0, 0.0), (0.3, 0.4), (0.5, -0.3), (-0.1, -0.4), (-0.3, -0.1), (-0.1, 0.2), (-0.5, 0.3), (-0.1, 0.4), \
    #       (0.0, 0.8), (0.2, 0.6), (0.5, 1.1), (0.1, 1.3), (0.4, 1.5), (0.8, 1.3), (1.0, 1.3), (1.2, 0.9) ]
    #
    # xy = [(0.0, 0.0), (-0.2, -0.3), (0.5, -0.3), (0.6, 0.2), (0.3, 0.8), (-0.1, 1.0), \
    #       (-0.2, 1.2), (0.3, 1.2), (0.5, 1.6), (0.8, 1.7), (0.9, 2.1), (1.3, 2.2), \
    #       (0.6, 1.8), (-0.1, 1.6), (-0.3, 2.1), \
    #       ]
    delta = 0.95
    # with open('xy.csv', 'w') as f :
    #     for x, y in xy:
    #         f.write(f'{x},{y}\n')
    #
    
    # xy = list()
    # with open('47-936_ishigakishi_xy-metre.csv', 'r') as f :
    #     for l in f:
    #         lonlat = [float(e) for e in l.strip().split(',')]
    #         xy.append(tuple(lonlat))
    # # extract a part
    # print(f'points in the input provided: {len(xy)}\n')
    # delta = 25.0

    print('-'*8)
    
    plt_annotate = False
    with Timer('delta rect: ') :
        drseq, polygons = delta_rect_decimation_alg(xy, delta, verbose = False, polygons = True)
    print(f'length of decimated seq = {len(drseq)}')
    
    # with Timer('my rdp: ') :
    #     rdpseq = rdp_decimation_alg(xy, delta)
    # print(f'length of decimated seq = {len(rdpseq)}')
    # mrdpx, mrdpy = [xy[i][0] for i in rdpseq], [xy[i][1] for i in rdpseq]
    #
    # npxy = np.array(xy)
    # with Timer('module rdp: ') :
    #     mask = rdp.rdp(npxy, epsilon=delta, return_mask=True)
    # rdpseq = [i for i in range(len(mask)) if mask[i]]
    # print(f'length of decimated seq = {len(rdpseq)}')
    #
    # npx , npy = npxy[:,0], npxy[:,1]
    # with Timer('module fastrdp: ') :
    #     frdpx, frdpy = fastrdp.rdp(npx, npy, delta)
    # print(f'length of decimated seq = {len(frdpx), len(frdpy)}')
    
    # rdpx, rdpy = [ xy[i][0] for i in rdpseq], [ xy[i][1] for i in rdpseq]
    x, y = [ x for x, y in xy], [ y for x, y in xy]
    drx, dry = [xy[ix][0] for ix in drseq], [xy[ix][1] for ix in drseq]
    fig, ax = plt.subplots()
    ax.plot(x, y, 'y.-', lw=2.0, alpha=0.35)
    ax.plot(drx, dry, 'b.-', lw=1) #, alpha=0.75)
    #ax.plot(frdpx, frdpy, 'b.-', lw=1) #, alpha=0.75)
    #ax.plot(mrdpx, mrdpy, 'b.-', lw=1) #, alpha=0.75)
    if len(polygons) > 0 :
        for polygon in polygons:
            px, py = [xy[i][0] for i in polygon], [xy[i][1] for i in polygon]
            ax.plot(px, py, 'g--', lw=1) #, alpha=0.75)
    
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
