import sys
import numpy as np
from pyproj import Proj

# def copilot_distance(a, b, p):
#     ab = b - a
#     ap = p - a
#     distance = np.abs(np.cross(ab, ap)) / np.linalg.norm(ab)
#     return distance
'''
double gpspoint::distanceTo(const gpspoint &q1, const gpspoint &q2) const {
    if ( inner_prod(q1, q2, *this) < epsilon ) { // < 0.0
        return q1.distanceTo(*this);
    }
    if ( inner_prod(q2, q1, *this) < epsilon ) { // < 0.0
        return q2.distanceTo(*this);
    }
    return ABS(norm_outer_prod(q1, q2, *this)) / q1.distanceTo(q2);
}
'''


'''constant'''
epoch_start = np.datetime64('1970-01-01T00:00:00Z')

if __name__ == '__main__':
    '''read csv into numpy array.'''
    filename = ''
    outfilename = ''
    '''引数処理'''
    if len(sys.argv) == 1 :
        print('A CSV file name as an input is requested.')
        print('options: -o output_CSV_filename ')
        exit(1)
    else:
        argi = 1
        while argi < len(sys.argv) :
            argstr = sys.argv[argi]
            if argstr.startswith('-') :
                if argstr == '-o' :
                    argi += 1
                    outfilename = sys.argv[argi]
                    argi += 1
            else:
                filename = argstr
                argi += 1
                    
    '''表形式に変換'''
    tbl = np.genfromtxt(filename, delimiter=',', skip_header=1, missing_values='', dtype=str)
    dt = np.datetime_as_string(tbl[:,3].astype(np.datetime64), timezone='UTC')
    dt = dt.astype(np.datetime64)
    print(f'raw data contains {len(dt)} points.')
    
    lati = tbl[:,0].astype(np.float64)
    longi = tbl[:,1].astype(np.float64)
    center_lonlat = (np.mean(longi), np.mean(lati))
    
    print(f'center coordinate (longitude, latitude) = {center_lonlat}')
    
    '''convert (lon, lat) to points on the cartesian plane by azimuthal equidistance projection. '''
    proj = Proj(proj='aeqd', lon_0=center_lonlat[0], lat_0=center_lonlat[1], datum='WGS84')
    xy = list()
    last_datetime = epoch_start
    for i in range(len(tbl)):
        past = dt[i] - last_datetime
        if past.item().total_seconds() >= 5 :
            last_datetime = dt[i]
            x, y = proj(longi[i], lati[i])
            xy.add((x, y))
    
    '''返還後の出力'''
    #xy =xy[:10]
    if len(outfilename) :
        with open(outfilename, 'w') as f :
            for x, y in xy:
                f.write(f'{x},{y}\n')
    else:
        '''めんどくさいので numpy 配列にしてnumpy風表示'''
        xy = np.array(xy)
        print(f'points in the input provided: {len(xy)}')
        print(xy)
    
    print('Done.')