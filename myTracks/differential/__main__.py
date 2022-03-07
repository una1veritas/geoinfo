'''
Created on 2022/01/19

@author: sin
'''
import gpxpy
import datetime
import sys

def datetime2mjd(dt:datetime):
    y = dt.year
    m = dt.month
    if m <= 2 :
        y -= 1
        m = 12
    d = dt.day + (3600*dt.hour + 60*dt.minute + dt.second)/86400
    return int(365.25*y) + int(y/400) - int(y/100) + int(30.59*(m-2)) + d - 678912

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
            ptseq.append([(datetime2mjd(pt.time), pt.latitude, pt.longitude)])

for i in range(len(ptseq)):
    if i > 0 :
        ptseq[i].append(tuple([ptseq[i][0][j] - ptseq[i-1][0][j] for j in range(len(ptseq[i][0]))]))

for i in range(len(ptseq)):
    if i > 1 :
        ptseq[i].append(tuple([ptseq[i][1][j] - ptseq[i-1][1][j] for j in range(len(ptseq[i][1]))]))

for e in ptseq:
    print(e)
