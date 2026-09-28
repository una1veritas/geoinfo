import os
from pyproj import Proj

dirname = '/Users/sin/Downloads/Geolife Trajectories 1.3/Data/{number}/Trajectory'
pltname = '20081103232153.plt'
path = os.path.join(dirname.format(number='000'), pltname)

if __name__ == '__main__':
    lats = []
    lons = []
    
    with open(path, 'r') as infile:
        for ln, l in enumerate(infile, start=1):
            if ln < 7:
                continue
            arr = l.strip().split(',')
            lat = float(arr[0])
            lon = float(arr[1])
            lats.append(lat)
            lons.append(lon)
            # print(f'{ln}: lat = {lat}, lon = {lon}') # 必要に応じて
            
    # 中心座標を計算
    center_lon = sum(lons) / len(lons)
    center_lat = sum(lats) / len(lats)
    print(f'center coordinate (longitude, latitude) = ({center_lon}, {center_lat})')
    
    # 正距方位図法で直交座標に投影
    proj = Proj(proj='aeqd', lon_0=center_lon, lat_0=center_lat, datum='WGS84')
    
    with open("test.csv", 'w') as outfile:
        for lat, lon in zip(lats, lons):
            x, y = proj(lon, lat)
            outfile.write(f'{x},{y}\n')
            
    print('finished.')
