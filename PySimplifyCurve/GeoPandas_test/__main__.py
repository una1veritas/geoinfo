'''
Created on 2026/03/09

@author: sin
'''
import geopandas as gpd
#import matplotlib.pyplot as plt
import sys

if __name__ == '__main__':
    if len(sys.argv) == 0 :
        print('[options] input file name ')
    opts = dict()
    argix = 1
    while argix < len(sys.argv) :
        if not sys.argv[argix].startswith('-') :
            if 'filepath' not in opts and len(sys.argv[argix].strip()) > 0 :
                opts['filepath'] = sys.argv[argix].strip()
                dsv = opts['filepath'].split('/')
                if len(dsv) > 0 :
                    ext = dsv[-1].split('.')[-1]
                    if ext == 'shp' :
                        opts['type'] = 'shp'
                    elif ext == 'gpx' :
                        opts['type'] = 'gpx'
                    elif ext == 'csv' :
                        opts['type'] = 'csv'
        else:
            print(f'option? {sys.argv[argix]}')
        argix += 1
            
    
    # GeoJSON を読み込み
    gdf = gpd.read_file(opts['filepath'])
    
    mxid = -1
    mxl = []
    print(gdf.head())
    for id in range(gdf.shape[0]) :
        parray = gdf.iloc[id].geometry.exterior.xy
        l = list(zip(parray[0], parray[1]))
        if len(l) > 10000 :
            print(id, len(l))
            if len(l) > len(mxl) :
                mxid = id
                mxl = l
    
    with open(f'{mxid}_xy.csv', 'w') as f:
        for e in mxl:
            f.write(f'{e[1]},{e[0]}\n')
    
    # f = plt.figure(figsize=(6, 6))
    # a = f.gca()
    # a.plot(*gdf.iloc[0].geometry.exterior.xy)
