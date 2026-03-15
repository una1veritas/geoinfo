import numpy as np
import matplotlib.pyplot as plt
#from scipy.interpolate import make_interp_spline
import rdp
from collections import deque
import time

from point2d import vec, rhombus, distance, outer_prod_z, distance_to_line

class Timer:
    def __init__(self, mess = ''):
        self.message = str(mess)
        
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        self.end = time.time()
        print(self.message + f"Execution time: {self.end - self.start} seconds")

def simplify_RDP(xy : list, epsilon):
    nparray = np.array(xy)
    mask = rdp.rdp(nparray, epsilon=epsilon, return_mask=True)
    return [xy[i] for i in np.where(mask)[0]]

class ConvexHull:
    
    def __init__(self, points = None):
        self.xy = list() # of Point2D
        self.left_path = deque()     #clockwise path
        self.right_path = deque()    #anti/counter-clockwise path

        # the index of peak point on each convex path for the empty point set
        
        if isinstance(points, (list, tuple)) : 
            for p in points: 
                if isinstance(p, (list, tuple)) and len(p) >= 2 : 
                    p = tuple(p[:2])
                else :
                    raise ValueError(f"list/tuple needed, {p} ({type(p)}).")
                if not self.add(p) :
                    break
    
    def clear(self):
        self.xy.clear()
        self.left_path.clear()
        self.right_path.clear()
        # self.find_left_peak = None
        # self.find_right_peak = None
        
    def __len__(self):
        return len(self.xy)
    
    def __str__(self):
        return str(self.xy)+', '+str(self.left_path)+', '+str(self.right_path)
    
    def __getitem__(self, index):
        return self.xy[index]
    
    def leftpoint(self, ix):
        return self.xy[self.left_path[ix]]
    
    def rightpoint(self, ix):
        return self.xy[self.right_path[ix]]
    
    def growing_position(self, pt, Navel = False):
        if len(self) <= 2 :
            return True
        #if ( self.distance(self.xy[0], pt) < self.distance(self.xy[0], self.xy[-1]) ) or \
        # print('left:',self.leftpoint(-2), self.leftpoint(-1), pt, rhombus(self.leftpoint(-2), self.leftpoint(-1), pt))
        # print('right', self.rightpoint(-2), self.rightpoint(-1), pt, rhombus(self.rightpoint(-2), self.rightpoint(-1), pt))
        if rhombus(self.leftpoint(-2), self.leftpoint(-1), pt) <= 0 and rhombus(self.rightpoint(-2), self.rightpoint(-1), pt) >= 0 :
            # reject the point if it is inside the cone of the last segment of left path and that of the right path
            return False
        # print('left 1->0, pt:', rhombus(self.leftpoint(1), self.leftpoint(0), pt))
        # print('right 1->0, pt:', rhombus(self.rightpoint(1), self.rightpoint(0), pt))
        if Navel == True :
            return True
        elif rhombus(self.leftpoint(1), self.leftpoint(0), pt) < 0 :
            # reject the point if it is inside the cone of the last segment of left path and that of the right path
            return False
        return True
    
    def add(self, pt, Navel = False):
        if len(self) <= 1 :
            self.xy.append(pt)
            self.left_path.append(len(self)-1)
            self.right_path.append(len(self)-1)
            # self.find_left_peak = len(self)-1
            # self.find_right_peak = len(self)-1
            #print(f"len(self.xy) = {len(self.xy)}, self.find_left_peak = {self.find_left_peak}")
            return
        
        # add pt to xy and left path and right path
        self.xy.append(pt)
        self.left_path.append(len(self)-1)
        self.right_path.append(len(self)-1)
        self.make_leftpath_convex()
        self.make_rightpath_convex()
        if Navel == True :
            self.make_navel()
        return

    def make_navel(self):
        navelpt = self.leftpoint(0)  # == self.rightpoint(0)
        l2ndpt = self.leftpoint(1)
        r2ndpt = self.rightpoint(1)
        if rhombus(l2ndpt, navelpt, r2ndpt) < 0 :
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
           
    def make_leftpath_convex(self):
        #print(self.left_path)
        lastix = self.left_path.pop()
        lastpt = self.xy[lastix]
        while len(self.left_path) >= 2 :
            if rhombus(lastpt, self.leftpoint(-1), self.leftpoint(-2)) < 0 : 
                self.left_path.pop() # pop-out leftpoint(-1)
            else:
                break
        self.left_path.append(lastix)
        # self.find_left_peak = self.find_left_peak(self.find_left_peak) 
        
    def make_rightpath_convex(self):
        lastix = self.right_path.pop()
        last = self.xy[lastix]
        while len(self.right_path) >= 2 :
            if rhombus(last, self.rightpoint(-1), self.rightpoint(-2)) >= 0 :
                self.right_path.pop() # pop-out the prev point
            else:
                break
        self.right_path.append(lastix)
        # self.find_right_peak = self.find_right_peak(self.find_right_peak) 
    
    def find_left_peak(self):
        lb, ub = 0, len(self.left_path)
        mix = (lb + ub) >> 1
        # else:
        #     mix = max(min(1, peakhint), len(self.left_path) - 2)
        while lb < ub :
            if outer_prod_z(vec(self.leftpoint(mix-1), self.leftpoint(mix)), vec(self.xy[0], self.xy[-1])) < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        return max(0, ub - 1)
        
    def find_right_peak(self):
        lb, ub = 0, len(self.right_path)
        #if peakhint == None :
        mix = (lb + ub) >> 1
        # else:
        #     mix = max(min(1, peakhint), len(self.right_path) - 2)
        while lb < ub :
            if outer_prod_z(vec(self.rightpoint(0), self.rightpoint(-1)), vec(self.rightpoint(mix-1), self.rightpoint(mix)) ) < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        return max(0, ub - 1)        
    
    def leftpeak_distance(self):
        lpeak = self.find_left_peak()
        return distance_to_line(self.leftpoint(0), self.leftpoint(-1), self.leftpoint(lpeak))

    def rightpeak_distance(self):
        rpeak = self.find_right_peak()
        return distance_to_line(self.rightpoint(0), self.rightpoint(-1), self.rightpoint(rpeak))
    
def delta_decimation_alg(xy : list, delta) -> tuple:
    cvx = ConvexHull() # xy, SimplePolyline=False)
    dq = deque(xy)
    dpath = deque()
    lpath = deque()
    rpath = deque()
    dpath.append(dq[0])
    # cvx must have at least two points.
    while len(dq) :
        pt = dq.popleft()
        print(f'adding {pt}')
        if len(cvx) < 2 :
            cvx.add(pt)
            continue
        prelastpt = cvx[-1]
        preleft = deque(cvx.left_path)
        preright = deque(cvx.right_path)
        if cvx.growing_position(pt) : #, Navel = True) :
            cvx.add(pt) #, Navel = True)
            if cvx.leftpeak_distance() <= delta and cvx.rightpeak_distance() <= delta :
                print(cvx)
                if len(cvx) > 2 :
                    print(f'left peak {cvx[cvx.find_left_peak()]} dist = {cvx.leftpeak_distance()}, right peak {cvx[cvx.find_right_peak()]} dist = {cvx.rightpeak_distance()}')
                    print('cvx growing.\n')
            else:
                # added but stuck out
                print(f'left peak dist = {cvx.leftpeak_distance()}, right peak dist = {cvx.rightpeak_distance()}')
                # close the previous convex hull as a simplifi ed line segment
                lastpt = cvx[-1]
                dpath.append(prelastpt) # close the path
                lpath += [cvx[i] for i in preleft]
                rpath += [cvx[i] for i in preright]
                cvx.clear()
                dq.appendleft(lastpt)
                dq.appendleft(prelastpt)
                print(f'cvx has been reset: {cvx}\n')
        else:
            print(f'not growing position {pt}')
            print(f'terminate the hull')
            lastpt = cvx[-1]
            dpath.append(lastpt)
            print(f'new line {dpath[-2]}, {dpath[-1]}')
            lpath += [cvx[i] for i in preleft]
            rpath += [cvx[i] for i in preright]
            cvx.clear()
            dq.appendleft(pt)
            dq.appendleft(lastpt)
            print('cvx has been reset.\n')
    if len(cvx) > 0 :
        dpath.append(cvx[-1])
        lpath += [cvx[i] for i in cvx.left_path]
        rpath += [cvx[i] for i in cvx.right_path]
    return (dpath, lpath, rpath)
    
if __name__ == '__main__':
    # xy = [(-1, 0.5), (-0.5, -0.25), (0.0, 0.5), (-0.75, 1), (0.0, 1.5), (0, 2.4), (1, 2), (1, 3), \
    #       (1.5, 2.75), (2, 2.75),  (2.5, 3.2), (3, 3.5), (3.2, 2), (3, 0.5),  \
    #       (3.5, 1.0), (2.75, 1), (3.5, 0.5), (4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1) ]
    xy = [(0,0), (-0.2, -0.2), (-0.3, 0.0), (0,0.3), (0.3, 0.1), (0.3, -0.3), (-0.1, -0.4), ] #(-1.0, -1.0), (-1.5, 0.25), (-0.5, 1)]

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

    dpath, lpath, rpath = delta_decimation_alg(xy, 0.3)
    print(f'len(xy) = {len(xy)}, len(dpath) = {len(dpath)}')
    print(dpath)
    print(lpath)
    print(rpath)
    
    res = simplify_RDP(xy, 0.3)
    rdpx, rdpy = [x for x, y in res], [ y for x, y in res]
    
    x, y = [ x for x, y in xy], [ y for x, y in xy]
    leftx, lefty = [x for x,y in lpath], [y for x,y in lpath]
    rightx, righty = [x for x,y in rpath], [y for x,y in rpath]    
    #sx, sy = convex_xy[:,0], convex_xy[:,1]
    #ctrlparam = np.linspace(0,1,num=len(sx),endpoint=True)
    #spl = make_interp_spline(ctrlparam, np.c_[sx, sy])

    #drawparam = np.linspace(0, 1, len(sx)*8)
    #x_new, y_new = spl(drawparam).T
    
    # lxy = np.array([xy[i] for i in cvx.left_path])
    # rxy = np.array([xy[i] for i in cvx.right_path])
    # lx , ly = lxy[:,0], lxy[:,1]
    # rx, ry = rxy[:,0], rxy[:,1]
    # axisx = [lx[0], lx[-1]]
    # axisy = [ly[0], ly[-1]]
    dpathxy = np.array(dpath)
    axisx, axisy = dpathxy[:,0], dpathxy[:,1]
    fig, ax = plt.subplots()
    ax.plot(x, y, 'y.-', lw=4.0, alpha=0.5)
    ax.plot(rdpx, rdpy, 'r.-.', lw=2.0, alpha=0.75)
    ax.plot(leftx, lefty, 'b.--', lw=1) #, alpha=0.75)
    ax.plot(rightx, righty, 'r.-.', lw=1) #, alpha=0.75)
    ax.plot(axisx, axisy, 'k.-', lw=1.0, alpha=0.5)
    #ax.plot(rdpx, rdpy, 'g.-', lw=0.75) #, alpha=0.75)
    #plt.plot(x_new, y_new, 'y-')
    #plt.legend(['Input points', 'simplified line'],loc='best')
    plt.legend(['Input points', 'rdp', 'clockwise path', 'counter-clockwise path', 'simplified line'],loc='best')
    plt.title('Convex Hull function Test')
    ax.set_aspect('equal')
    plt.show()
