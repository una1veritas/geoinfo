'''
Created on 2026/03/09

@author: sin
'''
import geopandas as gpd
import json
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
                    elif ext == 'geojson' :
                        opts['type'] = 'json'
        else:
            if sys.argv[argix][1:] == 'out' :
                argix += 1
                opts['out'] = sys.argv[argix]
            elif sys.argv[argix][1:] == 'list' :
                opts['list'] = True
            elif sys.argv[argix][1:] == 'load' :
                argix += 1
                opts['load'] = sys.argv[argix]
            else:
                print(f'option? {sys.argv[argix]}')
        argix += 1
            
    if 'filepath' in opts and opts['type'] == 'shp' :
        # shp を読み込み
        filepath = opts['filepath']
        gdf = gpd.read_file(filepath)
        print(f'gp loaded {filepath} into df.')
    elif 'filepath' in opts and opts['type'] == 'json' :
        # json を読み込み
        filepath = opts['filepath']
        with open(filepath, 'r') as f:
            gjdic = json.load(f)
        for entry in gjdic['features']:
            if len(entry['geometry']['coordinates'][0]) > 10000 :
                print(entry['properties'])
                print(len(entry['geometry']['coordinates'][0]))
        
    if 'list' in opts :
        print(gdf.head())
        for ix in range(gdf.shape[0]) :
            parray = gdf.iloc[ix].geometry.exterior.xy
            l = list(zip(parray[0], parray[1]))
            if len(l) > 500 :
                print(ix, len(l))

    mxl = None
    if 'load' in opts :
        ix = int(opts['load'])
        parray = gdf.iloc[ix].geometry.exterior.xy
        mxl = list(zip(parray[0], parray[1]))
        print(f'read {ix} in list of the length = {len(mxl)}')
    
    if 'out' in opts:
        if mxl == None :
            raise ValueError('empty list')
        
        outfile = opts['out']
        if outfile.split('.')[-1] != 'csv' :
            outfile += '.csv'
        with open(outfile, 'w') as f:
            for e in mxl:
                f.write(f'{e[1]},{e[0]}\n')
        
    # f = plt.figure(figsize=(6, 6))
    # a = f.gca()
    # a.plot(*gdf.iloc[0].geometry.exterior.xy)
