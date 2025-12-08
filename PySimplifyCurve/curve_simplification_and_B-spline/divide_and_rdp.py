'''
Created on 2025/12/08

@author: sin
'''
import numpy as np
import rdp
import time

class Timer:
    def __init__(self, mess = ''):
        self.message = str(mess)
        
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        self.end = time.time()
        print(self.message + f"Execution time: {self.end - self.start} seconds")

    
def diff_vec(orig, dest : np.array): 
    return dest - orig

def norm(v : np.array):
    return np.linalg.norm(v)

def outer_prod_norm(v0, v1 : np.array):
    return v0[0]*v1[1] - v0[1]*v1[0]

def distance_to_line(p, a, b):
    ab = diff_vec(a, b)
    ap = diff_vec(a, p)
    if np.dot(ab, ap) < 0.0 :
        return norm(ap)
    ba = diff_vec(b,a)
    bp = diff_vec(b,p)
    if np.dot(ba, bp) < 0.0 :
        return norm(bp)
    return abs(outer_prod_norm(ab, ap)/norm(ab))
    
def simplify_RDP(xy : np.array, tolerance : float):
    mask = rdp.rdp(xy, epsilon=tolerance, return_mask=True)
    xy_rdp = xy[mask]
    return xy_rdp, [int(i) for i in np.where(mask)[0]]

def simplify_divide_and_RDP(xy : np.array, tolerance : float):
    pass

if __name__ == '__main__':
    '''read csv into numpy array.'''
    tbl = np.genfromtxt('2025-0726-151032-c.csv', delimiter=',', skip_header=0, missing_values='', dtype=float)
    print(f'raw data contains {len(tbl)} points.')
    #print(tbl)
    
    center_lonlat = (np.mean(tbl[:,1]), np.mean(tbl[:,0]))
    print(f'center = {center_lonlat}')
    
    
    tolerance = 8
    print(f'tolerance = {tolerance}')
    '''epsilon, the 1/2 width of simplified lines.'''
    exit(0)
    
    with Timer('divide and RDP '):
        drdp_xy, drdp_path = divide_and_RDP(xy, tolerance)
    #shortest_xy, shortest_path = simplify_shortest(xy, tolerance)
    with Timer('rdp '):
        rdp_xy, rdp_path = simplify_RDP(xy, tolerance)
    