#!/usr/bin/python3
#gpxreader version -1.0
#
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timedelta, timezone
import sys
import re

if len(sys.argv) < 2 :
    print('input (and optionally output) file names are needed.')
    print('usage: python3 gpxreader gpxfile cvsfile[return]')
    exit()
else :
    elevinfo = False
    mytracksgpx = False
    xmltext = ''
    outfilename = ''
    print('given args: ' + str(sys.argv[1:]))
    for arg in sys.argv[1:]:
        if arg[:1] == '-' :
            if arg == '-elev' :
                elevinfo = True
                print('will get elevation info.')
            elif arg == '-mytracks' :
                mytracksgpx = True
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
    ext = trk.find(gpxroot_namespace+'extensions')
#            print(elem.)
    if trkseg :
        if outfilename == '':
            if not trkname:
                trkname = 'no_track_name'
            outfilename = trkname + '.csv'
        print('writing '+trkname+' to '+outfilename+'...')
        with open(outfilename, mode='w') as outfile: 
            for trkpt in trkseg:
                t = trkpt.find(gpxroot_namespace+'time')
                if t.text.endswith('Z') :
                    # ISO UTC time
                    tstr = t.text[:-1] + '+00:00'
                else:
                    #JST?
                    tstr = t.text[:-1] + '+09:00'
                dt = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S%z')   
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
                print(dt, trkpt.attrib['lat'], trkpt.attrib['lon'], end='')
                if elevinfo :
                    print('\telev='+elev, end='')
                if mytracksgpx :
                    print('\tspeed='+gpxspeed, end='')
                print()
                
                outfile.write(str(dt))
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

