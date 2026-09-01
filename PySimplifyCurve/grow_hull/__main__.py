'''
Created on 2026/03/01

@author: sin
'''
import numpy as np
import matplotlib.pyplot as plt
import math, random, time
import rdp
import fastrdp
from collections import deque
from convexhull import ConvexHull

from point2d import distance
from myrdp import rdp_simplification, rdp_simplification_recursive
from simplification.cutil import simplify_coords
import statistics

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



def Grow_Hull(xy : list, delta : float, record_polygons = False, verbose = False) -> tuple:
    decpath = list()        # index seq. of decimated point seq.
    polygons = list()    # considered & finished polygons
    decpath.append(0)   # add the first point
    cvx = ConvexHull(delta)     # reusable convex hull
    
    ix = 0
    while ix < len(xy) :
        if verbose : print(ix, xy[ix])
        if len(cvx) == 0 :
            cvx.add(xy[decpath[-1]])
            start_ix = decpath[-1]
            if verbose : print(f'X: start_ix = {start_ix}')
            if record_polygons : polygons.append(cvx.polygon_points())
            ix += 1
            continue
        
        if cvx.add(xy[ix]) :
            peak_dists = cvx.peak_distances()
            if verbose : print(f'adding {xy[ix]} to cvx, peak distances = {peak_dists}')
            if max(peak_dists) > delta :
                if verbose : print(f'adding {xy[ix]} caused over size: \n')
                # cancel the last addition
                if verbose : print(len(cvx), f'start ix = {start_ix}', cvx)
                last_ix = ix - 1
                decpath.append(last_ix)
                cvx.clear()
                start_ix = last_ix
                if verbose : print(f'A: start_ix = {start_ix}')
                cvx.add(xy[start_ix])
                cvx.add(xy[start_ix + 1])
                if record_polygons : polygons.append(cvx.polygon_points())
                ix += 1     # advances to the next
                continue
            if polygons : polygons[-1] = cvx.polygon_points()     # update
            ix += 1
        else:
            # rejected xy[ix], so close cvx and restart
            last_ix = ix - 1
            decpath.append(last_ix)
            cvx.clear()
            start_ix = decpath[-1]
            if verbose : print(f'B: start_ix = {start_ix}')
            cvx.add(xy[start_ix])
            cvx.add(xy[ix])
            if record_polygons : polygons.append(cvx.polygon_points())
            ix += 1     # advances to the next
            continue
    if len(cvx) > 0 :
        # add the last line segment
        if verbose : print(len(cvx), cvx)
        last_ix = start_ix + len(cvx) - 1
        if verbose : print(start_ix, last_ix, xy[start_ix:last_ix])
        decpath.append(last_ix)
        if record_polygons : polygons.append(cvx.polygon_points())
        if verbose : print(f'remained cvx = {cvx}, {start_ix}, {len(cvx)}')
        #cvx.clear()
    
    return (decpath, polygons)

if __name__ == '__main__':
    
    run_info = { 'input': 'file', 'plot': True, 'annotate': False, 'runs': 10 }
    
    if run_info['input'] == 'specified' :
        delta = 0.5
        xy = [ (0,0), (0.1, -0.1), (-0.2, 0.1), (-0.1, -0.1), (-0.1, -0.2), (0.25, 0.5), \
              (0.8, 0.25), (1.0, 0.75), (1.4, 0.7), (1.5, 1.0), \
              (1.5, 2.75), (2, 2.75), (2.5, 3.2), \
              (3, 3.5), (3.2, 2), (3, 0.5),  \
              (3.25, 1.0), (3.25, -0.25), (3.5, 0.5), (4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1), (1.5, -0.0) \
        ]
        # xy = [ (0.0, 0.0), (0.3, 0.4), (0.5, -0.3), (-0.1, -0.4), (-0.3, -0.1), (-0.1, 0.2), \
        #       (-0.5, 0.3), (-0.1, 0.4), (0.0, 0.8), (0.2, 0.6), (0.5, 1.1), \
        #       (0.1, 1.3), (0.4, 1.5), (0.8, 1.3), (1.0, 1.3), (1.2, 0.9) 
        #       ]
        # xy = [(0.0, 0.0), (-0.2, -0.3), (0.5, -0.3), (0.6, 0.2), (0.3, 0.8), (-0.1, 1.0), \
        #       (-0.2, 1.2), (0.3, 1.2), (0.5, 1.6), (0.8, 1.7), (0.9, 2.1), (1.3, 2.2), \
        #       (0.6, 1.8), (-0.1, 1.6), (-0.3, 2.1), \
        #       ]
    
        delta = 50.0
        xy = [(-2252.08, -9008.75), (-2274.34, -9033.79), (-2293.84, -9076.09), (-2325.88, -9150.36), (-2337.55, -9172.08), (-2357.59, -9189.33), (-2386.54, -9201.0), (-2409.93, -9206.57), (-2436.08, -9195.96), (-2471.71, -9187.05), (-2500.66, -9192.62), (-2531.44, -9198.07), (-2544.63, -9200.4), (-2570.22, -9207.08), (-2579.7, -9222.64), (-2583.03, -9236.56), (-2578.86, -9264.66), (-2585.0, -9280.8), (-2598.36, -9300.82), (-2599.78, -9305.41), (-2605.59, -9324.21), (-2605.06, -9353.69), (-2611.47, -9389.58), (-2615.37, -9463.0), (-2630.7, -9547.87), (-2658.27, -9633.27), (-2668.4, -9657.94), (-2672.2, -9667.22), (-2728.45, -9727.87), (-2775.48, -9763.74), (-2856.78, -9811.01), (-2861.35, -9813.71), (-2915.22, -9845.5), (-2957.55, -9866.1), (-2969.04, -9868.65), (-3008.47, -9877.48), (-3020.05, -9877.1), (-3076.95, -9875.24), (-3162.08, -9885.78), (-3232.47, -9906.06), (-3340.44, -9939.42), (-3390.0, -9945.54), (-3450.92, -9976.91), (-3479.32, -9978.56), (-3517.15, -9975.78), (-3580.59, -9965.22), (-3603.03, -9963.42), (-3608.42, -9962.99), (-3636.03, -9978.51), (-3651.84, -9987.4), (-3706.66, -10011.04), (-3738.81, -10019.24), (-3761.52, -10021.93), (-3773.34, -10022.84), (-3802.43, -10026.17), (-3830.3, -10025.86), (-3845.45, -10023.11), (-3868.78, -10016.41), (-3891.28, -10006.6), (-3924.4, -9978.49), (-3956.77, -9960.59), (-3979.67, -9947.65), (-4003.16, -9933.84), (-4030.62, -9922.69), (-4062.04, -9920.03), (-4084.75, -9924.79), (-4113.8, -9929.03), (-4139.85, -9923.8), (-4169.33, -9894.86), (-4180.74, -9891.8), (-4221.39, -9906.24), (-4265.91, -9930.71), (-4287.61, -9941.82), (-4340.47, -9948.48), (-4366.62, -9947.36), (-4383.32, -9932.32), (-4403.35, -9914.5), (-4410.63, -9913.55), (-4416.16, -9912.83), (-4430.34, -9922.01), (-4448.17, -9948.16), (-4457.57, -9957.55), (-4458.73, -9958.72), (-4469.86, -9960.93), (-4488.25, -9960.37), (-4491.6, -9959.2), (-4510.5, -9952.56), (-4519.1, -9950.07), (-4523.85, -9948.68), (-4550.55, -9948.66), (-4575.6, -9966.46), (-4588.26, -9979.49), (-4594.54, -9985.92), (-4601.23, -9988.14), (-4635.72, -9988.12), (-4662.71, -10005.64), (-4687.76, -10013.98), (-4729.52, -10028.99), (-4769.58, -10033.44), (-4797.98, -10026.18), (-4819.12, -10012.25)]

        # with open('xy.csv', 'w') as f :
        #     for x, y in xy:
        #         f.write(f'{x},{y}\n')
        #
    
    elif run_info['input'] == 'file' :
        delta = 50.0
        xy = list()
        filename = '47-936_ishigakishi_xy-metre.csv' #'40-1836_itoshima_xy-metre.csv'
        with open(filename, 'r') as f :
            for l in f:
                lonlat = [float(e) for e in l.strip().split(',')]
                xy.append(tuple(lonlat))
        # extract a part
        print(f'points in the input {filename} provided: {len(xy)}\n')
        
        #xy = xy[1727:1828]
        #xy = [(round(e[0],2), round(e[1],2)) for e in xy]
        #print(xy)
    
    elif run_info['input'] == 'random' :
        # Set up the number of random points
        delta = 50
        num_points = 100000
        random.seed(20260726)
        xy = list()
        for i in range(0, num_points):
            param = i/num_points
            x = param * 10000 + random.uniform(-50, 50)
            y = (0.25 + (param - 0.5)**2) * 10000 * (random.choice( (-1.0, -0.5, 0.5, 1.0) ))
            xy.append( [x,y] )
        print(xy[:10])
        print(f'length of xy = {len(xy)}')
    
    print('-'*8)
    
    
    exec_times = dict()
        
    print('Grow_Hull:')
    exec_times['Grow_Hull'] = list()
    for _ in range(run_info['runs']):
        swatch = time.perf_counter()
        
        drseq, polygons = Grow_Hull(xy, delta, verbose = False, record_polygons = False) 
        swatch = time.perf_counter() - swatch
        
        exec_times['Grow_Hull'].append(swatch)
    
    print(f'length of simplified seq = {len(drseq)}, ' \
          f'avr. execution time = {statistics.mean(exec_times['Grow_Hull'])} secs., dev = {statistics.pstdev(exec_times['Grow_Hull'])}')
    if len(drseq) < 200 :
        print(f'{drseq}, {polygons}')
    else:
        polygons.clear()
    print()
    
    # print('my non-recursive RDP:')
    # exectimes.clear()
    # for _ in range(runs):
    #     swatch = time.perf_counter()
    #
    #     rdpseq = rdp_simplification(xy, delta)
    #     swatch = time.perf_counter() - swatch
    #
    #     exectimes.append(swatch)
    #
    # print(f'length of simplified seq = {len(rdpseq)}, ' \
    #       f'avr. execution time = {statistics.mean(exectimes)} secs., dev = {statistics.pstdev(exectimes)}')
    # mrdpx, mrdpy = [xy[i][0] for i in rdpseq], [xy[i][1] for i in rdpseq]
    # print()
    
    # npxy = np.array(xy)
    # print('rdp module:')
    # exectimes.clear()
    # for _ in range(runs):
    #     swatch = time.perf_counter()
    #
    #     mask = rdp.rdp(npxy, epsilon=delta, return_mask=True)
    #     swatch = time.perf_counter() - swatch
    #
    #     exectimes.append(swatch)
    #
    # rdpseq = [i for i in range(len(mask)) if mask[i]]
    # print(f'length of simplified seq = {len(rdpseq)}, ' \
    #       f'avr. execution time = {statistics.mean(exectimes)} secs., dev = {statistics.pstdev(exectimes)}')
    # print()
    
    print('simplification.cutil:')
    exec_times['simplification.cutil'] = list()
    for _ in range(run_info['runs']):
        swatch = time.perf_counter()

        simplified = simplify_coords(xy, delta)
        swatch = time.perf_counter() - swatch
        
        exec_times['simplification.cutil'].append(swatch)

    print(f'length of simplified seq = {len(simplified)}, ' \
          f'avr. execution time = {statistics.mean(exec_times['simplification.cutil'])} secs., dev = {statistics.pstdev(exec_times['simplification.cutil'])}')
    # print(simplified[:20])
    print()
    
    if not run_info['plot'] :
        exit(0)
    
    # npx , npy = npxy[:,0], npxy[:,1]
    # with Timer('module fastrdp: ') :
    #     frdpx, frdpy = fastrdp.rdp(npx, npy, epsilon=delta)
    # print(f'length of decimated seq = {len(frdpx), len(frdpy)}')
    # print()
    
    x, y = [ x for x, y in xy], [ y for x, y in xy]
    drx, dry = [xy[ix][0] for ix in drseq], [xy[ix][1] for ix in drseq]
    rdpx, rdpy = [ x for x, y in simplified], [ y for x, y in simplified]

    fig, ax = plt.subplots()
    ax.plot(x, y, 'y.-', lw=2.0, alpha=0.35)
    # ax.plot(drx, dry, 'b.-', lw=1) #, alpha=0.75)
    # plt_title = f'Greedy+CH, delta = {delta}, points = {len(xy)}, simplified = {len(drseq)}'
    ax.plot(rdpx, rdpy, 'b.-', lw=1) #, alpha=0.75)
    plt_title = f'simplify_coords, delta = {delta}, points = {len(xy)}, simplified = {len(simplified)}'
    
    if len(polygons) > 0 :
        for polygon in polygons:
            px, py = [pt[0] for pt in polygon], [pt[1] for pt in polygon]
            ax.plot(px, py, 'g--', lw=1) #, alpha=0.75)
    
    labels = [f"{i}" for i in range(len(xy))]
    if run_info['annotate'] :
        for x, y, label in zip(x, y, labels):
            plt.annotate(
                label,          # The text to display
                (x, y),         # The point to annotate (xy)
                textcoords="offset points", # How to position the text
                xytext=(5, 2), # Distance from the point to the text (offset)
                ha='center'     # Horizontal alignment of the text
            )
    plt.legend(['Input points', 'simplified path', 'polygon_index path'],loc='best')
    plt.title(plt_title)
    ax.set_aspect('equal')
    plt.show()
