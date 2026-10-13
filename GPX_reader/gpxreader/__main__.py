#!/usr/bin/python3
# gpxreader version -0.9.1
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timezone, timedelta
import sys
import re

def datetime2mjd(dt: datetime):
    y = dt.year
    m = dt.month
    if m <= 2:
        y -= 1
        m += 12
    d = dt.day
    sec = 3600 * dt.hour + 60 * dt.minute + dt.second
    if sec >= 86400:
        d += int(sec / 86400)
        sec = sec % 86400
    mjd = int(365.25 * y) + int(y / 400) - int(y / 100) + int(30.59 * (m - 2)) + d - 678912
    return (mjd, sec)

# main
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('input (and optionally output) file names are needed.')
        print('usage: python3 gpxreader [-elev] [-mytracks] [-mjd] [-elapsed] gpxfile [csvfile]')
        sys.exit()
    
    elevinfo = False
    mytracksgpx = False
    mjdtime = False
    jsttime = False
    elapsedtime = False
    xmltext = ''
    outfilename = ''
    
    print('command args: ' + str(sys.argv[1:]))
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            if arg == '-elev':
                elevinfo = True
                print('will add elevation info.')
            elif arg == '-mytracks':
                mytracksgpx = True
                print('will add speed info.')
            elif arg == '-mjd':
                mjdtime = True
                print('date time in modified julian day number.')
            elif arg == '-jst':
                mjdtime = False
                jsttime = True
                print('date time in JST.')
            elif arg == '-elapsed':
                elapsedtime = True
                print('time in elapsed seconds since the previous.')
        else:
            if not xmltext:
                try:
                    with open(arg, mode='r', encoding='utf-8') as gpxfile:
                        xmltext = gpxfile.read()
                except Exception as e:
                    print(f'opening file {arg} failed: {e}')
                    sys.exit()
            elif not outfilename:
                outfilename = arg
                if not outfilename.endswith('.csv'):
                    outfilename += '.csv'
    
    if not xmltext:
        print('no GPX content loaded.')
        sys.exit()
    
    gpxroot = ElementTree.fromstring(xmltext)
    gpxroot_namespace = ''
    tmplist = re.findall(r'\{[^\}]*\}', gpxroot.tag)
    if tmplist:
        gpxroot_namespace = tmplist[0]
    
    start_dt = None
    for trk in gpxroot.iter(gpxroot_namespace + 'trk'):
        name = trk.find(gpxroot_namespace + 'name')
        trkname = name.text.replace(':', '').replace(' ', '_') if (name is not None and name.text) else 'no_track_name'
        trkseg = trk.find(gpxroot_namespace + 'trkseg')
        exts = trk.find(gpxroot_namespace + 'extensions')
        
        if trkseg is not None:
            tzinfo = None
            if exts is not None:
                tzinfo = exts.find(gpxroot_namespace + 'mytracks:timezone')
            print('tzinfo = ' + str(tzinfo))
            
            if not outfilename:
                outfilename = trkname + '.csv'
                
            print(f'writing {trkname} to {outfilename}...')

            # JST (UTC+9) の定義
            JST = timezone(timedelta(hours=9))
            with open(outfilename, mode='w', encoding='utf-8') as outfile:
                for trkpt in trkseg:
                    t = trkpt.find(gpxroot_namespace + 'time')
                    if t is None or not t.text:
                        continue
                    
                    tstr = t.text.strip()
                    # ISO 8601 / RFC 3339 形式の汎用パース
                    try:
                        iso_str = tstr.replace('Z', '+00:00')
                        if jsttime:
                            # パース後に JST へ変換する場合の例
                            current_dt = datetime.fromisoformat(iso_str).astimezone(JST)
                        else:
                            current_dt = datetime.fromisoformat(iso_str)
                            
                    except ValueError:
                        # サポート外形式へのフォールバック（ミリ秒有無等）
                        current_dt = datetime.strptime(tstr.split('.')[0], '%Y-%m-%dT%H:%M:%S')
    
                    if start_dt is None:
                        start_dt = current_dt
                        
                    if mjdtime:
                        mjd = datetime2mjd(current_dt)
                        dtstr = f'{mjd[0]},{mjd[1]}'
                    elif elapsedtime:
                        dtstr = f'{(current_dt - start_dt).total_seconds():.03f}'
                        start_dt = current_dt
                    else:
                        dtstr = str(current_dt)
                    
                    elev = ''
                    if elevinfo:
                        ele_node = trkpt.find(gpxroot_namespace + 'ele')
                        elev = ele_node.text if ele_node is not None else ''
    
                    gpxspeed = ''
                    if mytracksgpx:
                        pt_exts = trkpt.find(gpxroot_namespace + 'extensions')
                        if pt_exts is not None:
                            for c in pt_exts.iter():
                                if c.tag.endswith('speed'):
                                    gpxspeed = c.text if c.text else ''
                                    break
    
                    line = [dtstr, trkpt.attrib.get('lat', ''), trkpt.attrib.get('lon', '')]
                    if elevinfo:
                        line.append(elev)
                    if mytracksgpx:
                        line.append(gpxspeed)
                    
                    outfile.write(','.join(line) + '\n')
