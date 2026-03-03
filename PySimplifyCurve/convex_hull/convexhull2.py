'''
Created on 2026/03/01

@author: sin
'''
import numpy as np
import matplotlib.pyplot as plt
#from scipy.interpolate import make_interp_spline
import rdp
from collections import deque
import time

from point2d import vec, side_of_line, distance_between, outer_prod_z, inner_prod, \
distance_to_line, norm, perpvec, unitvec, negvec, perpvec

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
        self.polygon = deque()     #clockwise path
    
    def clear(self):
        self.xy.clear()
        self.polygon.clear()
        
    def __len__(self):
        return len(self.xy)
    
    def __str__(self):
        return str(self.xy)+', '+str(self.polygon)
    
    def __getitem__(self, index):
        return self.xy[index]
    
    def polypoint(self, ix):
        return self.xy[self.polygon[ix]]
    
    def growing_position(self, pt, Navel = False):
        if len(self) <= 2 :
            return True
        #if ( self.distance_between(self.xy[0], pt) < self.distance_between(self.xy[0], self.xy[-1]) ) or \
        # print('left:',self.leftpoint(-2), self.leftpoint(-1), pt, side_of_line(self.leftpoint(-2), self.leftpoint(-1), pt))
        # print('right', self.rightpoint(-2), self.rightpoint(-1), pt, side_of_line(self.rightpoint(-2), self.rightpoint(-1), pt))
        if side_of_line(self.leftpoint(-2), self.leftpoint(-1), pt) <= 0 and side_of_line(self.rightpoint(-2), self.rightpoint(-1), pt) >= 0 :
            # reject the point if it is inside the cone of the last segment of left path and that of the right path
            return False
        # print('left 1->0, pt:', side_of_line(self.leftpoint(1), self.leftpoint(0), pt))
        # print('right 1->0, pt:', side_of_line(self.rightpoint(1), self.rightpoint(0), pt))
        if Navel == True :
            return True
        elif side_of_line(self.leftpoint(1), self.leftpoint(0), pt) < 0 :
            # reject the point if it is inside the cone of the last segment of left path and that of the right path
            return False
        return True
    
    def add(self, pt):
        if len(self) == 0 :
            self.xy.append(pt)
            self.polygon.appendleft(len(self)-1)
            self.polygon.append(len(self)-1)
            return
        if len(self) == 1 :
            self.xy.append(pt)
            self.polygon.appendleft(len(self)-1)
            self.polygon.pop()
            self.polygon.append(len(self)-1)
            return
        
        # add pt to xy and polygon
        self.xy.append(pt)
        if side_of_line(self.polypoint(1), self.polypoint(0), pt) <= 0 or side_of_line(self.polypoint(-2), self.polypoint(-1), pt) >= 0 :
            #right or left of the beak
            self.polygon.appendleft(len(self)-1)
            self.polygon.append(len(self)-1)
            self.remove_concave()
        else:
            print(f'{self.polypoint(-2)}, {self.polypoint(0)}, {self.polypoint(1)}')
            self.xy.pop()
            raise ValueError(f'inside???')
        return
    
    def make_navel(self):
        navelpt = self.leftpoint(0)  # == self.rightpoint(0)
        l2ndpt = self.leftpoint(1)
        r2ndpt = self.rightpoint(1)
        if side_of_line(l2ndpt, navelpt, r2ndpt) < 0 :
            if len(self.left_path) > 2 :
                self.left_path.popleft()
                self.right_path.popleft()
                self.right_path.appendleft(self.left_path[0])
            elif len(self.right_path) > 2 :
                self.right_path.popleft()
                self.left_path.popleft()
                self.left_path.appendleft(self.right_path[0])
            else:
                raise ValueError(f'leftpath and rightpath becomes length 1!!')
           
    def remove_concave(self, reverse = False):
        #print(self.left_path)
        # from tail
        lastix = self.polygon.pop()
        lastpt = self.xy[lastix]
        while len(self.polygon) >= 2 :
            if side_of_line(lastpt, self.polypoint(-1), self.polypoint(-2)) < 0 : 
                self.polygon.pop() # pop-out polygon[-1]
            else:
                break
        self.polygon.append(lastix)
        # from head
        firstix = self.polygon.popleft()
        firstpt = self.xy[firstix]
        while len(self.polygon) >= 2 :
            if side_of_line(firstpt, self.polypoint(0), self.polypoint(1)) > 0 : 
                self.polygon.popleft() # pop-out polygon[0]
            else:
                break
        self.polygon.appendleft(firstix)
    
    def peak_distances(self):
        # along the clockwise polygon edges, 
        # outer_prod_z(axis vec, edge vec) changes
        # negative -> right peak -> positive -> left peak -> negative -> beak
        axis = unitvec(self.xy[0], self.xy[-1])
        negaxis = negvec(axis)
        threeoclock = perpvec(axis, clockwise = False)
        nineoclock = negvec(threeoclock)
        print('9 oclock = ', nineoclock)
        
        # firstly find the index in polygon-peaks of farthest point from the origin xy[0]
        # by nine-oclock direction
        lb, ub = 0, len(self.polygon)
        mix = (lb + ub) >> 1
        # else:
        #     mix = max(min(1, peakhint), len(self.left_path) - 2)
        while lb < ub :
            proj = inner_prod(vec(self.polypoint(mix), self.polypoint(mix+1)), axis)
            if proj >= 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        nopeak = max(0, ub - 1)
        return nopeak
    
    def right_peak_distance(self):
        lb, ub = 0, len(self.polygon) - 1
        mix = (lb + ub) >> 1
        axvec = vec(self.xy[0], self.xy[-1])
        while lb < ub :
            if outer_prod_z(axvec, vec(self.polypoint(mix-1), self.polypoint(mix)) ) < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        return max(0, ub - 1)        

        rpeak = self.find_right_peak()
        return distance_to_line(self.rightpoint(0), self.rightpoint(-1), self.rightpoint(rpeak))
    
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
    
if __name__ == '__main__':
    # xy = [(-1, 0.5), (-0.5, -0), (0.0, 0.5), (-1, 1.25), (0.0, 1.5), (0, 2.4), (1.25, 2), (1, 3), \
    #       (1.5, 2.75), (2, 2.75), (2.5, 3.2), (3, 3.5), (3.2, 2), (3, 0.5),  \
    #       (3.5, 1.0), (2.75, 1), (3.5, 0.5), (4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1), (1.5, -0.75) ]
    xy = [(0, 0), (1, 0.5), (0, 1), (0.5, 2.5), (1.5, 0.5), (1.6, 1.5), ] #(2.0, -1.0), (0.8, -0.15), \
    #(-0.25, -0.25), (1.0, -0.25), (1.5, 0.6), (1.25, 1.4), (0.5, 1.5), (-0.5, 0.9), ]#(2.0, -0.5), ]
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
    for pt in xy :
        try:
            cvx.add(pt)
            print(cvx)
        except:
            print('inside point error.')
            break
    
    print('-'*8)
    ax0, ax1 = cvx.xy[0], cvx.xy[-1]
    print(f'{ax0}, {ax1}, {ax1[0] - ax0[0]}, {ax1[1] - ax0[1]}, {norm(vec(ax0, ax1))}')
    axvec = unitvec(ax0, ax1)
    ax3oclock = perpvec(axvec, clockwise = True)
    print(f'axvec = {axvec}, ax3 = {ax3oclock}')
    for ix in range(len(cvx.polygon)) :
        pt0 = cvx.polypoint(ix)
        pt1ix = (ix + 1) % (len(cvx.polygon) - 1)
        pt1 = cvx.polypoint(pt1ix)
        ptvec = vec(pt0, pt1)
        print(f'{ix} ({cvx.polygon[ix]} - {cvx.polygon[pt1ix]}), {str(pt0):10}, \t{str(pt1):10}\t', end = ' ')
        print(f'{float(inner_prod(axvec, ptvec)):.5},\t{float(inner_prod(ax3oclock, ptvec)):.5}')
        print()
    #print(f'peak= {cvx.peak_distances()}')
    
    #dpath, lpath, rpath = delta_decimation_alg(xy, 6)
    

    #rdpx, rdpy = rdpxy[:,0], rdpxy[:,1]
    x, y = [ x for x, y in cvx.xy], [ y for x, y in cvx.xy]
    px, py = [xy[i][0] for i in cvx.polygon], [xy[i][1] for i in cvx.polygon]
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
