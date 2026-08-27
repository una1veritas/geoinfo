import sys
from datetime import datetime, timezone
from pyproj import Proj
from statistics import mean

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
epoch_start = datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc)

if __name__ == '__main__':
    '''read csv into array.'''
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
    
    tbl = list()
    with open(filename, 'r') as file :
        for l in file:
            a = l.strip().split(',')
            tbl.add(a)
    
    for ln in range(len(tbl)):
        l = tbl[ln]
        if ln == 0 :
            tbl[ln] = tuple(l)
        else:
            lat = float(l[0])
            lon = float(l[1])
            if len(l) >= 3 : 
                alt = float(l[2])
            else:
                alt = 0.0
            if len(l) >= 4 :
                dt = datetime.fromisoformat(l[3])
            else:
                dt = epoch_start
            tbl[ln] = (lat, lon, alt, dt)

    centre = (mean([ea[1] for ea in tbl[1:]]), mean([ea[0] for ea in tbl[1:]]))
    
    print(f'center coordinate (longitude, latitude) = {centre}')
    
    '''convert (lon, lat) to points on the cartesian plane by azimuthal equidistance projection. '''
    proj = Proj(proj='aeqd', lon_0 = centre[0], lat_0 = centre[1], datum='WGS84')
    xy = list()
    last_datetime = epoch_start
    for t in tbl[1:] :
            x, y = proj(t[1], t[0])
            xy.add((x, y))
    
    '''返還後の出力'''
    #xy =xy[:10]
    if len(outfilename) :
        with open(outfilename, 'w') as f :
            for x, y in xy:
                f.write(f'{x},{y}\n')
    else:
        '''めんどくさいので numpy 配列にしてnumpy風表示'''
        print(f'points in the input provided: {len(xy)}')
        for ea in xy[:10] + xy[-10:] :
            print(ea)
    print('Done.')