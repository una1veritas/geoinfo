import numpy as np
import matplotlib.pyplot as plt
#from scipy.interpolate import make_interp_spline
import rdp
import math
#from pyproj import Proj
from collections import deque
import time

from point2d import vec, side_of_line, distance_between, outer_prod_z, distance_to_line

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
    
    def __init__(self, points = None, SimplePolyline = False):
        self.xy = list() # of Point2D
        self.left_path = deque()     #clockwise path
        self.right_path = deque()    #anti/counter-clockwise path

        #the index of peak point on each convex path for 0 points
        self.left_peak = None
        self.right_peak = None
        
        if isinstance(points, (list, tuple)) :
            for p in points:
                if isinstance(p, (list, tuple)) and len(p) >= 2 :
                    p = tuple(p[:2])
                elif isinstance(p, (np.ndarray)) and len(p) >= 2 :
                    p = (float(p[0]), float(p[1]))
                else :
                    #isinstance(pt, Point2D) 
                    raise ValueError(f"list/tuple needed, {p} ({type(p)}).")
                if not self.add(p, SimplePolyline) :
                    break
    
    def __len__(self):
        return len(self.xy)
    
    def __str__(self):
        return str(self.xy)+', '+str(self.left_path)+', '+str(self.right_path)
    
    def leftpoint(self, ix):
        return self.xy[self.left_path[ix]]
    
    def rightpoint(self, ix):
        return self.xy[self.right_path[ix]]
    
    def add(self, pt, SimplePolyline=False):
        if len(self) < 2 :
            self.xy.append(pt)
            self.left_path.append(len(self)-1)
            self.right_path.append(len(self)-1)
            self.left_peak = len(self)-1
            self.right_peak = len(self)-1
            #print(f"len(self.xy) = {len(self.xy)}, self.left_peak = {self.left_peak}")
            return True
        
        #if ( self.distance_between(self.xy[0], pt) < self.distance_between(self.xy[0], self.xy[-1]) ) or \
        if side_of_line(self.leftpoint(-2), self.leftpoint(-1), pt) <= 0 and side_of_line(self.rightpoint(-2), self.rightpoint(-1), pt) >= 0 :
            # reject point if is is inside the cone formed from the last segment of the clockwise path and that of the anti-clockwise path
            if not SimplePolyline :
                return False
        
        self.xy.append(pt)
        self.left_path.append(len(self)-1)
        self.right_path.append(len(self)-1)
        self.make_leftpath_convex()
        self.make_rightpath_convex()
        return True
    
    def make_leftpath_convex(self):
        #print(self.left_path)
        lastix = self.left_path.pop()
        lastpt = self.xy[lastix]
        
        while len(self.left_path) >= 2 :
            if side_of_line(lastpt, self.leftpoint(-1), self.leftpoint(-2)) < 0 : 
                self.left_path.pop() # pop-out the prev point
            else:
                break
        self.left_path.append(lastix)
        self.left_peak = self.find_lpeak(self.left_peak) 
        
    def make_rightpath_convex(self):
        lastix = self.right_path.pop()
        last = self.xy[lastix]
        while len(self.right_path) >= 2 :
            if side_of_line(last, self.rightpoint(-1), self.rightpoint(-2)) >= 0 :
                self.right_path.pop() # pop-out the prev point
            else:
                break
        self.right_path.append(lastix)
        self.right_peak = self.find_rpeak(self.right_peak) 
    
    def find_lpeak(self, peakhint = None):
        lb, ub = 0, len(self.left_path)
        if peakhint == None :
            mix = (lb + ub) >> 1
        else:
            mix = max(min(1, peakhint), len(self.left_path) - 2)
        while lb < ub :
            if outer_prod_z(vec(self.leftpoint(mix-1), self.leftpoint(mix)), vec(self.leftpoint(0), self.leftpoint(-1))) <= 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        return max(0, ub - 1)
        
    def find_rpeak(self, peakhint = None):
        lb, ub = 0, len(self.right_path)
        if peakhint == None :
            mix = (lb + ub) >> 1
        else:
            mix = max(min(1, peakhint), len(self.right_path) - 2)
        while lb < ub :
            if outer_prod_z(vec(self.rightpoint(0), self.rightpoint(-1)), vec(self.rightpoint(mix-1), self.rightpoint(mix)) ) <= 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        return max(0, ub - 1)        
    
    def leftpeak_distance(self):
        return distance_to_line(self.leftpoint(0), self.leftpoint(-1), self.leftpoint(self.left_peak))

    def rightpeak_distance(self):
        return distance_to_line(self.rightpoint(0), self.rightpoint(-1), self.rightpoint(self.right_peak))
    
if __name__ == '__main__':
    xy = [(-1, 0.5), (0.5, -0.25), (-0.75, 1), (0.5, 1.5), (0, 2.4), (1, 2), (1, 3), (1.5, 1), \
          (2, 0), (1.5, 2.5), (2.5, 1), (1.5, 3.5), (2.5, 3.2), (3, 3.5), (3.2, 2), (3, 0.5),  \
          (3.5, 1.5), (3.5, 3), (2.25, 2.6), (2.5, 0) ]
    # if False:
    #     with open('xy.csv', 'w') as f :
    #         for x, y in xy:
    #             f.write(f'{x},{y}\n')
    print(xy, f'points in the input provided: {len(xy)}')
    
    cvx = ConvexHull(xy, SimplePolyline=False)
    print(cvx)
    print(f'left peak dist @ {cvx.left_peak} = {cvx.leftpeak_distance()}, right peak dist @ {cvx.right_peak} = {cvx.rightpeak_distance()}')
    
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
    
    lxy = np.array([xy[i] for i in cvx.left_path])
    rxy = np.array([xy[i] for i in cvx.right_path])
    lx , ly = lxy[:,0], lxy[:,1]
    rx, ry = rxy[:,0], rxy[:,1]
    axisx = [lx[0], lx[-1]]
    axisy = [ly[0], ly[-1]]
    fig, ax = plt.subplots()
    ax.plot(x, y, 'y.-', lw=4.0, alpha=0.5)
    ax.plot(lx, ly, 'b.--', lw=1) #, alpha=0.75)
    ax.plot(rx, ry, 'r.-.', lw=1) #, alpha=0.75)
    ax.plot(axisx, axisy, 'k.-', lw=1.0, alpha=0.5)
    #ax.plot(rdpx, rdpy, 'g.-', lw=0.75) #, alpha=0.75)
    #plt.plot(x_new, y_new, 'y-')
    plt.legend(['Input points', 'clockwise path', 'counter-clockwise path', 'simplified line'],loc='best')
    plt.title('Convex Hull function Test')
    ax.set_aspect('equal')
    plt.show()
