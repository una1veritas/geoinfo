#gpxreader version -2.0
#
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timedelta, timezone
import sys
import re

if len(sys.argv) < 2 :
    print('input (and optionally output) file names are needed.')
    print('usage: python3 gpxreader gpxfile cvsfile[return]')
    exit()
    
xmltext = ''
with open(sys.argv[1], 'r') as gpxfile :
    xmltext = gpxfile.read()

if len(sys.argv) < 3 :
    outfilename = ''
else:
    outfilename = sys.argv[2]
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
    print(name)
    print(trkname)
    print(trkseg)
    print(ext)

    if trkseg :
        if outfilename == '':
            if not trkname:
                trkname = 'no_track_name'
            outfilename = trkname + '.csv'
        print('writing '+trkname+' to '+outfilename+'...')
        with open(outfilename, mode='w') as outfile: 
            for trkpt in trkseg:
                print(trkpt)
                if trkpt[1].text.endswith('Z') :
                    # ISO UTC time
                    tstr = trkpt[1].text[:-1] + '+00:00'
                else:
                    #JST?
                    tstr = trkpt[1].text[:-1] + '+09:00'
                dt = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S%z')
                print(dt, trkpt.attrib['lat'], trkpt.attrib['lon'])
                outfile.write(str(dt))
                outfile.write(',')
                outfile.write(trkpt.attrib['lat'])
                outfile.write(',')
                outfile.write(trkpt.attrib['lon'])
                outfile.write('\n')

