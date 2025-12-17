'''
Created on 2025/12/08

@author: sin
'''
import math
import numpy as np
import rdp
import time
from collections import deque
from numpy import ix_

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

def distance_to_line_min_max_ix(xypoints, startix, stopix, a, b):
    min_dist = float('inf')
    max_dist = 0
    min_dist_ix = startix
    max_dist_ix = startix
    for ix in range(startix, stopix + 1):
        pt = xypoints[ix]
        dist = distance_to_line(pt, a, b)
        if dist < min_dist :
            min_dist = dist
            mindist_ix = ix
        if dist > max_dist :
            max_dist = dist
            max_dist_ix = ix
    return (min_dist_ix, min_dist, max_dist_ix, max_dist)
    
def simplify_RDP(xy : np.array, tolerance : float):
    mask = rdp.rdp(xy, epsilon=tolerance, return_mask=True)
    xy_rdp = xy[mask]  #''' extracting elements and make a sub-sequence by boolean indexing'''
    return xy_rdp, [int(i) for i in np.where(mask)[0]]

def simplify_divide_and_RDP(xy : np.array, tolerance : float):
    if len(xy) < 2 :
        raise ValueError('xy array must have two or more points.')
        exit(1)
    '''準備'''
    curve_ix_q = deque() # stack/queue of ix
    curve_ix_q.append(0) # the first point
    curve_ix_q.append(len(xy) - 1) # the last queue 
    
    if curve_ix_q[-1] - curve_ix_q[0] < 1 :
        '''no points between the indices start and stop.'''
        return xy[[True, True]], [int(i) for i in np.where(mask)[0]]
    
    simplified_ix_q = deque()
    simplified_ix_q.append(curve_ix_q[0]) 
    '''単純化した区間の最初の点の添え字は、直前の区間の最後の点として追加済みとみなすため。'''
    
    '''decimates the indices of the points in xy 
    by moving chosen indices of points from curve_ix_q to simplified_ix_q. '''
    while len(curve_ix_q) > 0 :
        '''base line (xy[start_ix], xy[stop_ix])'''
        '''curve_ix_q は分割されうる区間の点の最初と最後のものの添え字を持つ．'''
        start_ix = curve_ix_q.popleft() # get the first index and remove from queue
        stop_ix= curve_ix_q[0] # the second index since the first one has been renoved

        if stop_ix - start_ix == 1 :
            '''間に点がないので無条件に追加｡'''
            simplified.append(stop_ix)
            continue
        
        '''三つの区間にわける．[start_ix, midletf_ix, midright_ix, stop_ix]'''
        '''中央の区間は、開始と終了が同じ点でもかまわない。'''
        mid_start = math.ceil((final_ix - start_ix)/3)
        mid_final = math.floor((final_ix - start_ix)*2/3)
        (min_dist_ix, min_dist, max_dist_ix, max_dist) = min_max_distance_to_line(xy, start_ix, mid_start, xy[start_ix], xy[final_ix])
        print(start_ix, final_ix)
        print(min_dist_ix, min_dist, max_dist_ix, max_dist)
        break
        
if __name__ == '__main__':
    '''read csv into numpy array.'''
    xy = np.genfromtxt('2025-0726-151032-c.csv', delimiter=',', skip_header=0, missing_values='', dtype=float)
    print(f'raw data contains {len(xy)} points.')
    #print(tbl)
    
    center_lonlat = (np.mean(xy[:,1]), np.mean(xy[:,0]))
    print(f'center = {center_lonlat}')
    
    tolerance = 8
    print(f'tolerance = {tolerance}')
    '''epsilon, the 1/2 width of simplified lines.'''
    
    #shortest_xy, shortest_path = simplify_shortest(xy, tolerance)
    with Timer('rdp '):
        rdp_xy, rdp_ixpath = simplify_RDP(xy, tolerance)
    print(xy[:20])
    print(rdp_xy[:10])
    print(rdp_ixpath[:10])
    print()
    
    with Timer('divide and RDP '):
        drdp_xy, drdp_ixpath = simplify_divide_and_RDP(xy, tolerance)
