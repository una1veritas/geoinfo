import gpxpy
import datetime
import sys

if len(sys.argv) < 2 :
    print('no supplied file name.')
    exit()
    
textstring = ''
with open(sys.argv[1], 'r') as gpxfile :
    gpx = gpxpy.parse(gpxfile)
    print(gpx)

if not gpx :
    print('Got an empty gpx data.')
    exit()
        
ptseq = list()
for track in gpx.tracks:
    for segment in track.segments:
        for pt in segment.points:
            # print(pt)
            tstr = pt.time.strftime('%Y%m%d.%H%M%S')
            ptseq.append([tstr, pt.latitude, pt.longitude])

print()
for pt in ptseq:
    print(pt)