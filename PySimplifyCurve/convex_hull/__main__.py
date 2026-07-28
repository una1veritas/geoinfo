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

from point2d import rhombus, distance
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



# def delta_rect_decimation_alg(xy : list, delta, verbose = False, polygons = False) -> tuple:
#     dixpath = list()        # decimated path, the seq. of indices to the reference point sequence xy
#     polygon_seq = list()    # considered & finished polygons
#     dixpath.add(0)       # the index of the the first point
#     cvx = ConvexHull() 
#     cvx_start_index = dixpath[-1];    # offset to index to xy
#     cvx.add(xy[0])
#     cvx.add(xy[1])
#     cvx_diameter = distance(cvx.first_point(), cvx.last_point())
#     ptix = 2
#     while ptix < len(xy) :
#         verbose and print(f'{ptix}, {xy[ptix]}, dia = {cvx_diameter}, delta = {delta}, {cvx}')
#         verbose and print(f'side {cvx.polygon_index[-1]}-{cvx.polygon_index[0]}, {rhombus(cvx.polygon_point(-1), cvx.polygon_point(0), xy[ptix])} >= 0 or {cvx.polygon_index[1]}-{cvx.polygon_index[0]}, {rhombus(cvx.polygon_point(1), cvx.polygon_point(0), xy[ptix])} <= 0 ?' )
#         if cvx_diameter <= delta and \
#         ( rhombus(cvx.polygon_point(-1), cvx.polygon_point(0), xy[ptix]) >= 0 or rhombus(cvx.polygon_point(1), cvx.polygon_point(0), xy[ptix]) <= 0 ):
#             verbose and print('within delta and in growth position')
#             cvx.add(xy[ptix]) # should be succeeded
#             cvx_diameter = max(cvx_diameter, distance(cvx[0], cvx[-1]) ) # = max(cvx_diameter, distance(cvx.first_point(), cvx.last_point()) )
#             ptix += 1
#             verbose and print(cvx)
#             verbose and print()
#             continue
#
#         verbose and print('check wether pt is furthest or not.')
#         if cvx_diameter > distance(cvx[0], xy[ptix]) : # distance(cvx.first_point(), xy[ptix]) :
#             verbose and print('getting nearer. stop extending cvx')
#             cvx_lastix = cvx_start_index + cvx.size()
#             dixpath.add(cvx_lastix)
#             if polygons : 
#                 polygon_seq.add([cvx_start_index + cvx.polygon_index[i] for i in range(len(cvx.polygon_index) + 1)])
#             cvx.clear()
#             # make new cvx for the 1st and 2nd points.
#             cvx_start_index = cvx_lastix
#             cvx.add(xy[cvx_lastix])
#             cvx.add(xy[ptix])
#             verbose and print(cvx)
#             verbose and print(cvx[0], cvx[-1]) #print(cvx.first_point(), cvx.last_point())
#             cvx_diameter = distance(cvx[0], cvx[-1])
#             ptix += 1
#             verbose and print(cvx)
#             verbose and print()
#             continue
#
#         # pt is in the growth position
#         verbose and print('pt is at growth distance')
#
#         # preserve the outline of cvx before pt is added
#         if polygons : 
#             prevcvx_polygon = [cvx.polygon_point(i) for i in range(len(cvx.polygon_index) + 1)]
#
#         # add pt to test width
#         cvx.add(xy[ptix])
#         peakdists = cvx.peak_distances()
#         verbose and print(peakdists, [e < delta for e in peakdists])
#
#         if all([e < delta for e in peakdists]) :
#             cvx_diameter = distance(cvx[0], cvx[-1])
#             ptix += 1
#             verbose and print(cvx)
#             verbose and print()
#             continue
#         else:
#             prevcvx_lastix = len(cvx) - 2
#             dixpath.add(cvx_start_index + prevcvx_lastix)
#             if polygons : 
#                 polygon_seq.add(prevcvx_polygon)
#             cvx.clear()
#             cvx_start_ix = prevcvx_lastix
#             cvx.add(xy[prevcvx_lastix])
#             cvx.add(xy[ptix])
#             cvx_diameter = distance(cvx[0], cvx[-1])
#             ptix += 1
#             verbose and print(cvx)
#             verbose and print()
#             continue
#         raise ValueError('???')
#
#     if len(cvx) > 0 :
#         #print('points exhausted,', cvx)
#         dixpath.add(cvx_start_index + len(cvx) - 1)
#         if polygons : 
#             polygon_seq.add([cvx.polygon_point(ix) for ix in range(len(cvx.polygon_index) + 1)])
#
#     if not polygons :
#         return dixpath
#     else:
#         return (dixpath, polygon_seq)


def delta_rect_decimation(xy : list, delta : float, record_polygons = False, verbose = False) -> tuple:
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
            fw, bk, rt, lt = cvx.peak_distances()
            if max(fw, bk, rt, lt ) > delta :
                if verbose : print(f'adding {xy[ix]} caused over size: ', fw, bk, rt, lt)
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
    
    delta = 0.5
    # with open('xy.csv', 'w') as f :
    #     for x, y in xy:
    #         f.write(f'{x},{y}\n')
    #
    
    xy = list()
    filename = '40-1836_itoshima_xy-metre.csv'
    with open(filename, 'r') as f :
        for l in f:
            lonlat = [float(e) for e in l.strip().split(',')]
            xy.append(tuple(lonlat))
    # extract a part
    print(f'points in the input {filename} provided: {len(xy)}\n')


    delta = 50.0

    # Set up the number of random points
    num_points = 50
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
    # print(xy)
    # cvx = ConvexHull(0.5)
    # for ix in range(len(xy)) :
    #     if cvx.add(xy[ix]) :
    #         print("after point added:", cvx)
    #     else:
    #         break
    #
    # #exit(0)
    # polygon = [cvx.polygon_point(i) for i in range(len(cvx.polygon_index))]
    # polygons = [polygon]
    # print(cvx.peak_distances())
    
    plt_annotate = False
    plot = True
    
    runs = 10
    
    print('delta-rect simplification:')
    exectimes = list()
    for _ in range(runs):
        swatch = time.perf_counter()
        
        drseq, polygons = delta_rect_decimation(xy, delta, verbose = False, record_polygons = False) 
        swatch = time.perf_counter() - swatch
        
        exectimes.append(swatch)
        
    print(f'length of simplified seq = {len(drseq)}, ' \
          f'avr. execution time = {statistics.mean(exectimes)} secs., dev = {statistics.pstdev(exectimes)}')
    if len(drseq) < 20 :
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
    exectimes.clear()
    for _ in range(runs):
        swatch = time.perf_counter()

        simplified = simplify_coords(xy, delta)
        swatch = time.perf_counter() - swatch
        
        exectimes.append(swatch)

    print(f'length of simplified seq = {len(simplified)}, ' \
          f'avr. execution time = {statistics.mean(exectimes)} secs., dev = {statistics.pstdev(exectimes)}')
    # print(simplified[:20])
    print()
    
    if not plot :
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
    ax.plot(drx, dry, 'b.-', lw=1) #, alpha=0.75)
    # ax.plot(rdpx, rdpy, 'b.-', lw=1) #, alpha=0.75)
    
    if len(polygons) > 0 :
        for polygon in polygons:
            px, py = [pt[0] for pt in polygon], [pt[1] for pt in polygon]
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
    plt.legend(['Input points', 'simplified path', 'polygon_index path'],loc='best')
    plt.title('Point-curve simplification Test')
    ax.set_aspect('equal')
    plt.show()
