'''
Created on 2026/03/09

@author: sin
'''
import geopandas as gpd
import matplotlib.pyplot as plt

if __name__ == '__main__':    
    shape_file = "/Users/sin/Downloads/N03-190101_40_GML/N03-19_40_190101.shp"
    
    # GeoJSON を読み込み
    gdf = gpd.read_file(shape_file)
    
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
