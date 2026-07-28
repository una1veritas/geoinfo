'''
Created on 2026/03/14

@author: sin
'''
import time
from point2d import distance_to_line
import matplotlib.pyplot as plt
from collections import deque

class Timer:
    def __init__(self, mess = ''):
        self.message = str(mess)
        
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        self.end = time.time()
        print(self.message + f"Execution time: {self.end - self.start} seconds")


def rdp_simplification(xy : list, delta) -> tuple:
    ixseq = deque()
    ixseq.append(0)
    ixseq.append(len(xy)-1)
    declimatseq = deque()
    declimatseq.append(0)
    while len(ixseq) > 1 :
        #print(ixseq, declimatseq)
        ix_first = ixseq.popleft()
        ix_last = ixseq.popleft()
        d_max = 0
        ix_max = 0
        for ix in range(ix_first + 1, ix_last) :
            d = distance_to_line(xy[ix_first], xy[ix_last], xy[ix])
            if d > d_max :
                d_max = d
                ix_max = ix
        #print(ix_first, ix_last, d_max, ix_max, d_max <= delta)
        
        if d_max <= delta :
            declimatseq.popleft()
            declimatseq.appendleft(ix_first)
            declimatseq.appendleft(ix_last)
            ixseq.appendleft(ix_last)
        else:
            ixseq.appendleft(ix_last)
            ixseq.appendleft(ix_max)
            ixseq.appendleft(ix_first)
        #print(ixseq, declimatseq)
        #print()
    # in divide-and-conquer like manner
    return declimatseq

def rdp_simplification_recursive(xy : list, delta, first = None, last = None) -> tuple:
    #print('input: ', delta, first, last)
    if first == None or last == None :
        first = 0
        last = len(xy) - 1

    d_max = 0
    ix_max = 0
    for ix in range(first+1, last) :
        d = distance_to_line(xy[first], xy[last], xy[ix])
        #print(first, xy[first], last, xy[last], ix, xy[ix], d)
        if d > d_max :
            d_max = d
            ix_max = ix

    #print(first, last, d_max, ix_max, d_max <= delta)
    if d_max <= delta :
        return ([xy[first], xy[last]], [first, last])
    # in divide-and-conquer like manner
    pseq0, iseq0 = rdp_decimation_alg_recursive(xy, delta, first, ix_max)
    pseq1, iseq1 = rdp_decimation_alg_recursive(xy, delta, ix_max, last)
    return (pseq0+pseq1[1:], iseq0+iseq1[1:])
    
if __name__ == '__main__':
    xy = [(-1, 0.5), (-0.5, -0), (0.0, 0.5), (-1.3, 1.5), (0.0, 1.5), (0, 2.4), (1.0, 2), (1, 2.5), \
          (1.5, 2.75), (2, 2.75), (2.5, 3.2), \
          (3, 3.5), (3.2, 2), (3, 0.5),  \
          (3.25, 1.0), (3.25, -0.25), (3.5, 0.5), (4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1), (1.5, -0.0) ]
    
    # xy = [ (0.0, 0.0), (0.3, 0.4), (0.5, -0.3), (-0.1, -0.4), (-0.3, -0.1), (-0.1, 0.2), (-0.5, 0.3), (-0.1, 0.4),  \
    #       (0.0, 0.8), (0.2, 0.6), (0.5, 1.1), (0.1, 1.3), (0.4, 1.5), (0.8, 1.3), (1.0, 1.3), (1.2, 0.9) ]
    
    # xy = [(0.0, 0.0), (-0.2, -0.3), (0.5, -0.3), (0.6, 0.2), (0.3, 0.8), (-0.1, 1.0), \
    #       (-0.2, 1.2), (0.3, 1.2), (0.5, 1.6), (0.8, 1.7), (0.9, 2.1), (1.3, 2.2), \
    #       (0.6, 1.8), (-0.1, 1.6), (-0.3, 2.1), \
    #       ]
    delta = 0.6
    # with open('xy.csv', 'w') as f :
    #     for x, y in xy:
    #         f.write(f'{x},{y}\n')
    #

    print('-'*8)
    
    plt_annotate = True
    
    # with Timer('delta width: ') :
    #     dpath, polygons = delta_decimation_alg(xy, delta, verbose=False)
    # print(f'len(xy) = {len(xy)}, len(dpath) = {len(dpath)}')
    
    with Timer('rdp: ') :
        rdpxy, indices = rdp_decimation_alg(xy, delta)
    print(len(rdpxy))

    x, y = [ x for x, y in xy], [ y for x, y in xy]
    rdpx, rdpy = [pt[0] for pt in rdpxy], [pt[1] for pt in rdpxy]
    fig, ax = plt.subplots()
    ax.plot(x, y, 'y.-', lw=4.0, alpha=0.5)
    ax.plot(rdpx, rdpy, 'k.-', lw=1) #, alpha=0.75)
    # if len(polygons) > 0 :
    #     for polygon in polygons:
    #         px, py = [p[0] for p in polygon], [p[1] for p in polygon]
    #         ax.plot(px, py, 'b--', lw=1) #, alpha=0.75)
    
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