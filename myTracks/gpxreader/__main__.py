#!/usr/bin/python3
#gpxreader version -0.9
#
import xml.etree.ElementTree as ElementTree
from datetime import datetime
import sys
import re

def datetime2mjd(dt:datetime):
    y = dt.year
    m = dt.month
    if m <= 2 :
        y -= 1
        m = 12
    d = dt.day
    sec = 3600*dt.hour + 60*dt.minute + dt.second
    if sec >= 86400 :
        d += int(sec/86400)
        sec = sec % 86400
    mjd = int(365.25*y) + int(y/400) - int(y/100) + int(30.59*(m-2)) + d - 678912
    return (mjd, sec)

if len(sys.argv) < 2 :
    print('input (and optionally output) file names are needed.')
    print('usage: python3 gpxreader gpxfile cvsfile[return]')
    exit()
else :
    elevinfo = False
    mytracksgpx = False
    mjdtime = False
    xmltext = ''
    outfilename = ''
    print('command args: ' + str(sys.argv[1:]))
    for arg in sys.argv[1:]:
        if arg[:1] == '-' :
            if arg == '-elev' :
                elevinfo = True
                print('will add elevation info.')
            elif arg == '-mytracks' :
                mytracksgpx = True
                print('will add speed info.')
            elif arg == '-mjd' :
                mjdtime = True
                print('date time in modified julian day number.')                
        else:
            if not len(xmltext) :
                with open(arg, mode='r') as gpxfile :
                    xmltext = gpxfile.read()
            elif not len(outfilename) :            
                outfilename = arg
                if outfilename.split('.')[-1] != 'csv' :
                    outfilename += '.csv'
                with open(outfilename, 'w') as outfile:
                    pass
    if not len(xmltext) :
        print('opening file '+sys.argv[1]+' failed.')
        exit()

gpxroot = ElementTree.fromstring(xmltext)
gpxroot_namespace = ''
tmplist = (re.findall(r'\{[^\}]*\}', gpxroot.tag) )
if len(tmplist) :
    gpxroot_namespace = tmplist[0]
#print(gpxroot_namespace)

for trk in gpxroot.iter(gpxroot_namespace+'trk'):
    name = trk.find(gpxroot_namespace+'name') 
    trkname = name.text.replace(':', '').replace(' ', '_')
    trkseg = trk.find(gpxroot_namespace+'trkseg') 
    exts = trk.find(gpxroot_namespace+'extensions')
#            print(elem.)
    if trkseg :
        tzinfo = exts.find(gpxroot_namespace+'mytracks:timezone')
        print(tzinfo)
        if outfilename == '':
            if not trkname:
                trkname = 'no_track_name'
            outfilename = trkname + '.csv'
        print('writing '+trkname+' to '+outfilename+'...')
        with open(outfilename, mode='w') as outfile: 
            for trkpt in trkseg:
                t = trkpt.find(gpxroot_namespace+'time')
                tstr = t.text
                #print(tstr)
                if '.' in tstr and '+' in tstr:
                    dt = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S.%f%zZ')
                elif '+' in tstr:
                    dt = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S%zZ')
                else:
                    dt = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S.%fZ')
                dtstr = str(dt)
                if mjdtime :
                    mjd = datetime2mjd(dt)
                    dtstr = '{0},{1}'.format(mjd[0],mjd[1])
                if elevinfo :
                    elev = trkpt.find(gpxroot_namespace+'ele').text
                if mytracksgpx : #'{http://mytracks.stichling.info/myTracksGPX/1/0}
                    t = trkpt.find(gpxroot_namespace+'extensions')
                    gpxspeed = ''
                    for c in t.iter():
                        if c.tag.split('}')[-1] == 'speed':
                            gpxspeed = c.text
                            break
                    #print(trkpt.find(gpxroot_namespace+'extensions'))
                #print(dtstr, trkpt.attrib['lat'], trkpt.attrib['lon'], end='')
                #if elevinfo :
                #    print('\telev='+elev, end='')
                #if mytracksgpx :
                #    print('\tspeed='+gpxspeed, end='')
                #print()
                
                outfile.write(dtstr)
                outfile.write(',')
                outfile.write(trkpt.attrib['lat'])
                outfile.write(',')
                outfile.write(trkpt.attrib['lon'])
                if elevinfo :
                    outfile.write(',')
                    outfile.write(elev)
                if mytracksgpx :
                    outfile.write(',')
                    outfile.write(gpxspeed)
                outfile.write('\n')

