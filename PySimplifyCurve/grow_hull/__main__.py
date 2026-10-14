'''
Created on 2026/03/01

@author: sin
'''
import matplotlib.pyplot as plt
import math, sys, random, time
from convexhull import ConvexHull

from point2d import distance
from myrdp import rdp_simplification, rdp_simplification_recursive
from myvw import vw_simplification
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

# def simplify_RDP(xy : np.array, epsilon):
#     mask = rdp.rdp(xy, epsilon=epsilon, return_mask=True)
#     xy_rdp = xy[mask]
#     return xy_rdp, [int(i) for i in np.where(mask)[0]]

def Grow_Hull(xy : list, epsilon : float, record_polygons = False, verbose = False) -> tuple:
    decpath = list()        # index seq. of decimated point seq.
    if record_polygons :
        polygons = list()    # considered & finished polygons
    else:
        polygons = None
    
    # add the first point
    decpath.append(0)   
    cvx = ConvexHull() #delta)     # reusable convex hull
    cvx.add(xy[0])
    start_ix = decpath[-1]
    cvx.add(xy[1])
    if verbose : print(f'X: cvx start_ix = {start_ix}')
    if record_polygons : polygons.append(cvx.polygon_points())
    
    for ix in range(2, len(xy)) :
        if verbose : print(f"\nconvex-hull growing: {ix}, {xy[ix]}")
        
        if cvx.add(xy[ix]) :    # add or reject if crossing
            peak_dists = cvx.peak_distances()
            if verbose : print(f'adding {xy[ix]} to vcx len(vcx) = {len(cvx)}, peak distances = {peak_dists}')
            if max(peak_dists) > epsilon :
                if verbose : print(f'adding {xy[ix]} caused over size: \n')
                # cancel the last addition
                if verbose : print(len(cvx), f'start ix = {start_ix}', cvx)
                last_ix = ix - 1
                decpath.append(last_ix)
                cvx.clear()
                start_ix = last_ix
                cvx.add(xy[start_ix])
                if verbose : print(f'A: start_ix = {start_ix}')
                cvx.add(xy[start_ix + 1])
                if record_polygons : polygons.append(cvx.polygon_points())
                #ix += 1     # advances to the next
            elif record_polygons : 
                polygons[-1] = cvx.polygon_points()     # update
            # ix += 1
            # continue
        else:
            # rejected xy[ix], so close cvx and restart
            if verbose : print(f'xy[{ix}] = {xy[ix]} is rejected.')
            last_ix = ix - 1
            decpath.append(last_ix)
            cvx.clear()
            start_ix = decpath[-1]
            if verbose : print(f'B: start_ix = {start_ix}')
            cvx.add(xy[start_ix])
            cvx.add(xy[ix])
            if record_polygons : polygons.append(cvx.polygon_points())
            # ix += 1     # advances to the next
            # continue
    #
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

def plot_algorithm_comparison(xy, results):
    """
    3つのアルゴリズム（Grow-Hull, RDP, V-W）の簡略化結果（座標列）を並列表示して比較する関数
    
    :param xy: 元の座標リスト [(x0, y0), (x1, y1), ...]
    :param results: 各アルゴリズムの実行結果情報のリスト
                    [
                        {'name': 'Grow-Hull', 'coords': gh_coords, 'param': f'eps={eps}'},
                        {'name': 'RDP',       'coords': rdp_coords, 'param': f'eps={eps}'},
                        {'name': 'Visvalingam-Whyatt', 'coords': vw_coords, 'param': f'area={area}'},
                    ]
    """
    x_orig = [pt[0] for pt in xy]
    y_orig = [pt[1] for pt in xy]
    
    # 3つのグラフを1行3列で作成 (拡大・パン操作が全画面で連動するよう sharex/sharey を設定)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True)
    
    for i, res in enumerate(results):
        ax = axes[i]
        coords = res['coords']
        print(i, res['name'], coords[:10])
        
        # 1. 元の軌跡（薄い赤色・下地）
        ax.plot(x_orig, y_orig, 'r.-', lw=1.5, alpha=0.35, label='Input points')
        
        # 2. 簡略化された軌跡（青色）
        sx = [pt[0] for pt in coords]
        sy = [pt[1] for pt in coords]
        ax.plot(sx, sy, 'b.-', lw=1.2, alpha=0.85, label='Simplified path')
        
        # タイトルと削減率の表示
        reduction_rate = (1 - len(coords) / len(xy)) * 100
        title_str = (f"{res['name']} ({res.get('param', '')})\n"
                     f"{len(xy)} -> {len(coords)} pts ({reduction_rate:.1f}% reduced)")
        
        ax.set_title(title_str, fontsize=11)
        ax.set_aspect('equal')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, linestyle=':', alpha=0.5)

    plt.suptitle("Simplification Algorithm Comparison", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
if __name__ == '__main__':
    
    run_info = { 'input': 'file', 'epsilon' : 5.0, 'plot': True, 'annotate': False, 'runs': 1, 
                'gh': True, 'rdp': True, 'vw': True, 'file': None }
    if len(sys.argv) > 1 :
        for kv in sys.argv[1:] :
            k, sep, v = kv.partition('=')
            if k in ('file', 'random', 'specified') :
                run_info['input'] = k
                if k == 'file' and len(v) > 0:
                    run_info['file'] = v
            if k.startswith('--') :
                k = k[2:]
                if k in run_info :
                    if k in ['epsilon'] :
                        run_info[k] = float(v)
                    elif k in ['plot', 'annotate', 'gh', 'rdp', 'vw'] :
                        if len(v) > 0 and v.lowewr() in ('0', 'false', 'no') :
                            run_info[k] = False
                        else:
                            run_info[k] = True
                    elif k in ['runs'] :
                        run_info[k] = int(v)
                else:
                    print(f'Unknown option: {k}')
        
    if run_info['input'] == 'specified' :
        run_info['epsilon'] = 1.0
        # xy = [(0.0, 0.0), (0.5, 0.0), (0.4, 1.2), (0.6, 1.0), (0.7, 0.5), (0.65, 1.1) \
        # ]
        xy = [ (0,0), (0.1, -0.1), (-0.2, 0.1), (-0.1, -0.1), (-0.1, -0.2), (0.25, 0.5), \
              (0.8, 0.25), (1.0, 0.75), (1.4, 0.7), (1.5, 1.0), \
            (1.5, 2.75), (2, 2.75), (2.5, 3.2), \
            (3, 3.5), (3.2, 2), (3, 0.5),  \
            (3.25, 1.0), (3.25, -0.25), (3.5, 0.5), \
            (4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1), (1.5, -0.0) \
        ]
        # xy = [ (0.0, 0.0), (0.25, 0.75), (0.25, -0.5), (0, -1.0), (-0.25, -0.5)]

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

        # with open('xy.csv', 'w') as f :
        #     for x, y in xy:
        #         f.write(f'{x},{y}\n')
        #
    
    elif run_info['input'] == 'file' :
        if 'file' not in run_info or run_info['file'] is None :
            run_info['file'] = '40-1836_itoshima_xy-metre.csv'
        if 'epsilon' not in run_info or run_info['epsilon'] is None :
            run_info['epsilon'] = 50.0
        xy = list()
        filename = run_info['file']
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
        run_info['epsilon'] = 50
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
    results = list()
    
    if not (run_info['gh'] or run_info['rdp'] or run_info['vw']) or run_info['gh'] :
        print('Grow_Hull:')
        exec_times['Grow_Hull'] = list()
        for _ in range(run_info['runs']):
            swatch = time.perf_counter()
            
            ghindices, polygons = Grow_Hull(xy, run_info['epsilon'], verbose = False, record_polygons = False) 
            swatch = time.perf_counter() - swatch
            exec_times['Grow_Hull'].append(swatch)
        
        ghseq = [xy[ix] for ix in ghindices]
        print(f'length of output seq = {len(ghseq)}, ', end='')
        print(f'avr. execution time = {statistics.mean(exec_times["Grow_Hull"])} secs., dev = {statistics.pstdev(exec_times["Grow_Hull"])}')
        if len(ghseq) < 200 :
            print(f'{ghseq}, {polygons}')
        print()
        results.append(
            { 'name': 'Grow-Hull', 'coords': ghseq, 'param': f"ε={run_info['epsilon']}" }
            )
        
    if run_info['vw'] :
        print('VW:')
        exec_times['VW'] = list()
        run_info['threshold_area'] = 1.5 * run_info['epsilon']**2 
        for _ in range(run_info['runs']):
            swatch = time.perf_counter()
            
            vwindices = vw_simplification(xy, run_info['threshold_area'])   # area threshold = (epsilon^2)/2
            swatch = time.perf_counter() - swatch
            exec_times['VW'].append(swatch)
        
        vwseq = [xy[ix] for ix in vwindices]
        print(f'length of output seq = {len(vwseq)}, ', end='')
        print(f'avr. execution time = {statistics.mean(exec_times["VW"])} secs., dev = {statistics.pstdev(exec_times["VW"])}')
        print()
        results.append( 
            { 'name': 'Visvalingam-Whyatt', 'coords': vwseq, 'param': f"Δ={run_info['threshold_area']}" } 
            )
    
    if run_info['rdp'] :
        print('simplification.cutil:')
        exec_times['simplification.cutil'] = list()
        for _ in range(run_info['runs']):
            swatch = time.perf_counter()
        
            rdpseq = simplify_coords(xy, run_info['epsilon'])
            swatch = time.perf_counter() - swatch
        
            exec_times['simplification.cutil'].append(swatch)
        
        print(f'length of output seq = {len(rdpseq)}, ' \
              f'avr. execution time = {statistics.mean(exec_times["simplification.cutil"])} secs., dev = {statistics.pstdev(exec_times["simplification.cutil"])}')
        # print(rdpseq[:20])
        print()
        results.append( 
            { 'name': 'RDP', 'coords': rdpseq, 'param': f"ε={run_info['epsilon']}" }
            )
    
    if not run_info['plot'] :
        exit(0)
    
    # プロットの実行
    plot_algorithm_comparison(
        xy=xy,
        results=results
    )
    
    exit(0)

    # npx , npy = npxy[:,0], npxy[:,1]
    # with Timer('module fastrdp: ') :
    #     frdpx, frdpy = fastrdp.rdp(npx, npy, epsilon=epsilon)
    # print(f'length of decimated seq = {len(frdpx), len(frdpy)}')
    # print()
    
    x, y = [ x for x, y in xy], [ y for x, y in xy]
    drx, dry = [xy[ix][0] for ix in ghseq], [xy[ix][1] for ix in ghseq]
    vx, vy = [ x for x, y in xy], [ y for x, y in xy]
    rdpx, rdpy = [ x for x, y in rdpseq], [ y for x, y in rdpseq]

    fig, ax = plt.subplots()
    ax.plot(x, y, 'r.-', lw=2.0, alpha=0.35)
    ax.plot(drx, dry, 'b.-', lw=1) #, alpha=0.75)
    plt_title = f'Grow Hull, epsilon = {run_info["epsilon"]}, {len(xy)} points rdpseq to {len(ghseq)} points'
    #ax.plot(rdpx, rdpy, 'b.-', lw=1) #, alpha=0.75)
    #plt_title = f'RDP (simplify_coords), epsilon = {epsilon}, {len(xy)} points rdpseq to {len(rdpseq)} points'
    
    if polygons and len(polygons) > 0 :
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
    fig = plt.gcf()
    fig.set_size_inches(8, 8, forward=True) 
    plt.legend(['Input points', 'rdpseq path', 'polygon_index path'],loc='best')
    plt.title(plt_title)
    ax.set_aspect('equal')
    plt.show()
