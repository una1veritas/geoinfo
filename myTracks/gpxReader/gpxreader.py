import xml.etree.ElementTree as ElementTree
from datetime import datetime, timedelta, timezone
import sys

if len(sys.argv) < 3 :
    print('input and output file names are needed.')
    print('usage: python3 gpxreader gpxfile cvsfile[return]')
    exit()
    
xmltext = ''
with open(sys.argv[1], 'r') as gpxfile :
    xmltext = gpxfile.read()

outfilename = sys.argv[2]
if outfilename.split('.')[-1] != 'csv' :
    outfilename += '.csv'
with open(sys.argv[2], 'w') as outfile:
    pass

if not len(xmltext) :
    print('opening file '+sys.argv[1]+' failed.')
    exit()

gpxroot = ElementTree.fromstring(xmltext)

for trk in gpxroot:
    trkname = trk[0]
    trkseq = trk[2]
    print('writing '+trkname.text+' to '+outfilename+'...')
    with open(outfilename, mode='w') as outfile: 
        for trkpt in trkseq:
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

