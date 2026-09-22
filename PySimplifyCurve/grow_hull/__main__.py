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
        if verbose : print(f"\nconvex-hull growing: {ix}, {xy[ix]}")
        if len(cvx) == 0 :
            cvx.add(xy[decpath[-1]])
            start_ix = decpath[-1]
            if verbose : print(f'X: cvx start_ix = {start_ix}')
            if record_polygons : 
                polygons.append(cvx.polygon_points())
            ix += 1
            continue
        
        if cvx.add(xy[ix]) :
            peak_dists = cvx.peak_distances()
            if verbose : print(f'adding {xy[ix]} to vcx {len(cvx)}, peak distances = {peak_dists}')
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
    
    run_info = { 'input': 'random', 'plot': False, 'annotate': False, 'runs': 1}
    
    if run_info['input'] == 'specified' :
        delta = 1.0
        # xy = [(0.0, 0.0), (0.5, 0.0), (0.4, 1.2), (0.6, 1.0), (0.7, 0.5), (0.65, 1.1) \
        # ]
        # xy = [ (0,0), (0.1, -0.1), (-0.2, 0.1), (-0.1, -0.1), (-0.1, -0.2), (0.25, 0.5), \
        #       (0.8, 0.25), (1.0, 0.75), (1.4, 0.7), (1.5, 1.0), \
        #       (1.5, 2.75), (2, 2.75), (2.5, 3.2), \
        #       (3, 3.5), (3.2, 2), (3, 0.5),  \
        #       (3.25, 1.0), (3.25, -0.25), (3.5, 0.5), \
        #       (4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1), (1.5, -0.0) \
        # ]
        xy = [ (0.0, 0.0), (0.25, 0.75), (0.25, -0.5), (0, -1.0), (-0.25, -0.5)]

        # xy = [
        #     (1.0, 5.0),   # [P0] START ANCHOR (Center of epsilon circle)
        #     (1.3, 5.4),   # Dist = 0.50 < 1.0 (Inside circle: direction should be IGNORED)
        #     (0.8, 4.6),   # Dist = 0.45 < 1.0 (Inside circle: direction flips back, IGNORED)
        #     (1.4, 4.7),   # Dist = 0.50 < 1.0 (Inside circle: IGNORED)
        #     (2.5, 5.2),   # [P4] Dist = 1.51 > 1.0 (EXITS CIRCLE: Hull/Axis initializes here!)
        #     (4.5, 5.5),   # Dev < 1.0 from baseline
        #     (6.5, 5.8),   # Dev < 1.0 from baseline
        #     (8.5, 6.0),   # Dev < 1.0 from baseline
        #     (10.5, 6.2),  # Dev < 1.0 from baseline
        #     (13.0, 6.5)   # [P9] END
        # ]

        delta = 50.0
        xy = [(2350.2985962134862, 7339.665950622174), (2354.9986330515962, 7332.633508395293), (2364.4513634485625, 7306.101929872164), (2373.268798564042, 7279.145573831715), (2373.75303331286, 7277.501034047238), (2374.127624418002, 7275.831430235097), (2374.4555097926927, 7273.724116865384), (2374.713653217295, 7271.535790202184), (2376.0221407820545, 7212.0333223956195), (2375.9556324546015, 7207.985497224532), (2375.800208614555, 7204.11241009253), (2372.7144108407115, 7174.934807976959), (2372.5258201152947, 7173.572790564528), (2369.7644555743796, 7155.877560548451), (2369.270337966272, 7153.923857479379), (2368.7376742699144, 7151.940320028185), (2366.511931495072, 7144.159660671146), (2361.9269319783098, 7132.9500539654055), (2359.3226035456223, 7127.4197372222425), (2349.5250689850245, 7106.866880579354), (2341.1534409476512, 7318.938495575385), (2341.1423940083814, 7320.096677078148), (2341.3226429128595, 7321.110867802426), ]
        
        # with open('xy.csv', 'w') as f :
        #     for x, y in xy:
        #         f.write(f'{x},{y}\n')
        #
    
    elif run_info['input'] == 'file' :
        delta = 50.0
        xy = list()
        filename = '40-1836_itoshima_xy-metre.csv' #'47-936_ishigakishi_xy-metre.csv'
        with open(filename, 'r') as f :
            for l in f:
                lonlat = [float(e) for e in l.strip().split(',')]
                xy.append(tuple(lonlat))
        # extract a part
        print(f'points in the input {filename} provided: {len(xy)}\n')
        
        # xy = xy[20300:20319+24]
        #xy = [(round(e[0],2), round(e[1],2)) for e in xy]
        #print(xy)
    
    elif run_info['input'] == 'random' :
        # Set up the number of random points
        delta = 50
        num_points = 50000
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
    
    print(f'length of simplified seq = {len(drseq)}, ', end='')
    print(f'avr. execution time = {statistics.mean(exec_times["Grow_Hull"])} secs., dev = {statistics.pstdev(exec_times["Grow_Hull"])}')
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
    
    # print('simplification.cutil:')
    # exec_times['simplification.cutil'] = list()
    # for _ in range(run_info['runs']):
    #     swatch = time.perf_counter()
    #
    #     simplified = simplify_coords(xy, delta)
    #     swatch = time.perf_counter() - swatch
    #
    #     exec_times['simplification.cutil'].append(swatch)
    #
    # print(f'length of simplified seq = {len(simplified)}, ' \
    #       f'avr. execution time = {statistics.mean(exec_times["simplification.cutil"])} secs., dev = {statistics.pstdev(exec_times["simplification.cutil"])}')
    # # print(simplified[:20])
    # print()
    
    if not run_info['plot'] :
        exit(0)
    
    # npx , npy = npxy[:,0], npxy[:,1]
    # with Timer('module fastrdp: ') :
    #     frdpx, frdpy = fastrdp.rdp(npx, npy, epsilon=delta)
    # print(f'length of decimated seq = {len(frdpx), len(frdpy)}')
    # print()
    
    x, y = [ x for x, y in xy], [ y for x, y in xy]
    drx, dry = [xy[ix][0] for ix in drseq], [xy[ix][1] for ix in drseq]
    # rdpx, rdpy = [ x for x, y in simplified], [ y for x, y in simplified]

    fig, ax = plt.subplots()
    ax.plot(x, y, 'r.-', lw=2.0, alpha=0.35)
    ax.plot(drx, dry, 'b.-', lw=1) #, alpha=0.75)
    plt_title = f'Greedy+CH, delta = {delta}, points = {len(xy)}, simplified = {len(drseq)}'
    # ax.plot(rdpx, rdpy, 'b.-', lw=1) #, alpha=0.75)
    # plt_title = f'simplify_coords, delta = {delta}, points = {len(xy)}, simplified = {len(simplified)}'
    
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
