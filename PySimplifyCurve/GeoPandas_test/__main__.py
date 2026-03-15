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
    params = dict()
    argix = 1
    while argix < len(sys.argv) :
        if not sys.argv[argix].startswith('-') :
            if 'in_filepath' not in params and len(sys.argv[argix].strip()) > 0 :
                params['in_filepath'] = sys.argv[argix].strip()
                dsv = params['in_filepath'].split('/')
                if len(dsv) > 0 :
                    ext = dsv[-1].split('.')[-1]
                    if ext == 'shp' :
                        params['type'] = 'shp'
                    elif ext == 'gpx' :
                        params['type'] = 'gpx'
                    elif ext == 'csv' :
                        params['type'] = 'csv'
                    elif ext == 'geojson' :
                        params['type'] = 'json'
        else:
            if sys.argv[argix][1:] == 'out' :
                argix += 1
                params['out_filepath'] = sys.argv[argix]
            elif sys.argv[argix][1:] == 'list' :
                params['list'] = True
            elif sys.argv[argix][1:] == 'load' :
                argix += 1
                params['load'] = sys.argv[argix]
            else:
                print(f'option? {sys.argv[argix]}')
        argix += 1
    print(params)
    
    if 'in_filepath' in params:
        filepath = params['in_filepath']
        if params['type'] == 'shp' :
            # shp を読み込み
            params['df'] = gpd.read_file(filepath)
            print(f'gp loaded {filepath} into df.')
            print(params['df'].head())
        elif params['type'] == 'json' :
            # json を読み込み
            filepath = params['in_filepath']
            with open(filepath, 'r') as f:
                params['geojson'] = json.load(f)
            for entry in params['geojson']['features']:
                if len(entry['geometry']['coordinates'][0]) > 1000 :
                    print(entry['properties'])
                    print(len(entry['geometry']['coordinates'][0]))
        
    if 'list' in params :
        if 'df' in params :
            print(params['df'].head())
            for ix in range(params['df'].shape[0]) :
                parray = params['df'].iloc[ix].geometry.exterior.xy
                l = list(zip(parray[0], parray[1]))
                if len(l) > 500 :
                    print(ix, len(l))

    mxl = None
    if 'load' in params :
        ix = int(params['load'])
        if 'df' in params :
            parray = params['df'].iloc[ix].geometry.exterior.xy
            mxl = list(zip(parray[0], parray[1]))
            print(f'read {ix} in list of the length = {len(mxl)}')
        elif 'geojson' in params :
            count = 0
            for entry in params['geojson']['features']:
                if 'N03_007' in entry['properties'] and entry['properties']['N03_007'] == params['load'] :
                    coordinates = entry['geometry']['coordinates']
                    if len(coordinates[0]) > 1000 :
                        print(count)
                        count += 1
                        print(len(coordinates[0]), coordinates[0])
                        mxl = coordinates[0]
                # if entry['geometry']['N03_007'] == params['load'] :
                #     print(entry['properties'])
                #     print(entry['geometry']['coordinates'])
                # if len(entry['geometry']['coordinates'][0]) > 10000 :
                #     print(entry['properties'])
                #     print(len(entry['geometry']['coordinates'][0]))    
    
    if 'out_filepath' in params:
        if mxl == None :
            raise ValueError('empty list')
        
        outfile = params['out_filepath']
        if outfile.split('.')[-1] != 'csv' :
            outfile += '.csv'
        print(f'write to {outfile}...')
        with open(outfile, 'w') as f:
            for e in mxl:
                f.write(f'{e[1]},{e[0]}\n')
        
    # f = plt.figure(figsize=(6, 6))
    # a = f.gca()
    # a.plot(*gdf.iloc[0].geometry.exterior.xy)
