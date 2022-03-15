'''
Created on 2021/12/16

@author: sin
'''
''' 
python3 OSMReader map.osm [return]
'''

from lxml import etree
import sys
import geohashlite as geohash
from PIL import Image, ImageDraw
import math

def getobject(xml):
    '''
    Get objects from .osm file into a JSON-like python dict.
    '''
    objects = dict()
    # considers only the following three objects
    objects['node'] = dict()
    objects['way'] = dict()
    objects['relation'] = dict()
    for ch in xml:
        if ch.tag == 'node' :
            objects[ch.tag][int(ch.attrib['id'])] = (float(ch.attrib['lat']), float(ch.attrib['lon']))
            # print(ch.tag, ch.attrib)
            # for t in ch:
            #     if t.tag == 'tag' :
            #         print(t.attrib['k'], t.attrib['v'])
        elif ch.tag == 'way' :
            refs = list()
            tags = dict()
            for t in ch:
                if t.tag == 'nd':
                    refs.append(int(t.attrib['ref']))
                elif t.tag == 'tag':
                    tags[t.attrib['k']] = t.attrib['v']
            objects[ch.tag][int(ch.attrib['id'])] = {'tag': tags, 'ref': refs}
        elif ch.tag == 'relation' :
            members = [ t.attrib for t in ch if t.tag == 'member']
            #print('members = ', members)
            tags = dict()
            for t in ch:
                if t.tag == 'tag' :
                    tags[t.attrib['k']] = t.attrib['v']
            objects[ch.tag][int(ch.attrib['id'])] = {'tag': tags, 'member': members}
    return objects

def showgeograph(gg, bbox=None):
    if bbox == None:
        bbox = [0, 180, 90, 0]
        for key, val in gg.items():
            lat, lon = val[0]
            bbox[0] = max(bbox[0], lat)
            bbox[1] = min(bbox[1], lon)
            bbox[2] = min(bbox[2], lat)
            bbox[3] = max(bbox[3], lon)
    dlat = bbox[0] - bbox[2]
    dlon = bbox[3] - bbox[1]
    dangle = min(dlat/2, dlon/2)
    h = geodist((bbox[0], bbox[1]), (bbox[0], bbox[1]+dangle) )
    v = geodist((bbox[0], bbox[1]), (bbox[0]+dangle, bbox[1]))
    print(dangle, h,v,h/v)
    r = h/v
    scale = 1024
    while int(dlon*scale) < 4096 :
        scale *= 2
    print(dlat, dlon, scale)
    width = int(dlon*scale)
    hight = int(dlat*scale)

    mapimg = Image.new("RGB", (width, hight), "White")
    draw = ImageDraw.Draw(mapimg)

    for i in gg.keys():
        coord = gg[i][0]
        if coord[0] < bbox[2] or coord[0] > bbox[0] or coord[1] < bbox[1] or coord[0] > bbox[3] :
            continue
        x, y = abs(int((bbox[1]-coord[1])*scale)), int((bbox[0]-coord[0])*scale*r)
        draw.ellipse([x-1,y-1,x+1,y+1], fill = "Black", outline = "Black")
        adjs = gg[i][1]
        #print(x,y, adjs)
        for v in adjs:
            if v in gg :
                p2 = gg[v][0]
                x2, y2 = abs(int((bbox[1]-p2[1])*scale)), int((bbox[0]-p2[0])*scale*r)
                draw.line([x,y,x2,y2], fill= "Black")
    mapimg.show()

def deg2rad(x):
    return math.pi * x / 180.0

def geodist(gp1, gp2):
    #const int mode = 1;
    gp1rad = (deg2rad(gp1[0]), deg2rad(gp1[1]));
    gp2rad = (deg2rad(gp2[0]), deg2rad(gp2[1]));
    #double latdiff = plat - qlat, londiff = plon - qlon;
    latavr = (gp2rad[0] + gp2rad[0]) / 2.0;

    a = 6378137.0           #mode ? 6378137.0 : 6377397.155; // 襍､驕灘濠蠕�
    #b = 6356752.314140356   #mode ? 6356752.314140356 : 6356078.963; // 讌ｵ蜊雁ｾ�
    e2 = 0.00669438002301188    #mode ? 0.00669438002301188 : 0.00667436061028297; // 隨ｬ荳�髮｢蠢�邇�^2
    a1e2 = 6335439.32708317     #mode ? 6335439.32708317 : 6334832.10663254; // 襍､驕謎ｸ翫�ｮ蟄仙壕邱壽峇邇�蜊雁ｾ�

    sin_latavr = math.sin(latavr)
    W2 = 1.0 - e2 * (sin_latavr*sin_latavr)
    M = a1e2 / (math.sqrt(W2)*W2)
    N = a / math.sqrt(W2)

    t1 = M * (gp1rad[0] - gp2rad[1])        #latdiff;
    t2 = N * math.cos(latavr) * (gp1rad[1] - gp2rad[1])    #londiff;
    return math.sqrt((t1*t1) + (t2*t2))

if __name__ == '__main__':
    if len(sys.argv) < 2 :
        print('osm file is requested.',file=sys.stderr)
        exit(1)
    
    try:
        with open(sys.argv[1], encoding='utf-8') as fp:
            #with open('test.xml') as fp:
            xmlbytes = bytes(bytearray(fp.read(), encoding='utf-8'))
    except Exception as ex:
        print(ex, file=sys.stderr)
        exit(1)
    
    xml = etree.fromstring(xmlbytes)
    print("root info: ",xml.tag, xml.attrib)

    nspaces = xml.nsmap
    if None in nspaces :
        nspaces['defns'] = nspaces.pop(None)
    print('nspaces = ', nspaces)
    
    objects = getobject(xml)
    nodes = objects['node']
    links = dict()
    for key, value in sorted(objects['way'].items()):
        if 'railway' in value['tag']:
            links[key] = ('railway', value['ref'])
            #print('railway',edges['railway'][key])
        elif 'highway' in value['tag']:
            # if value['tag']['highway'] == 'residential':
            #     pass
            # else:
            links[key] = ('highway', value['ref'])
            #print('highway', value)
    
    geograph = dict()
    for key, val in links.items():
        plist = val[1]
        for ix in range(len(plist)-1):
            if plist[ix] not in geograph:
                geograph[plist[ix]] = (nodes[plist[ix]],list())
            if plist[ix+1] not in geograph:
                geograph[plist[ix+1]] = (nodes[plist[ix+1]],list())
            geograph[plist[ix]][-1].append(plist[ix+1])
            geograph[plist[ix+1]][-1].append(plist[ix])
    
    print(len(geograph))

    geohashlist = list()
    for pid in geograph.keys():
        gpoint = geograph[pid][0]
        hashcode = geohash.encode(gpoint[0], gpoint[1], 8)
        geohashlist.append((hashcode, pid))
    
    geohashlist.sort(key=lambda entry: entry[0])
    
    showgeograph(geograph) #, [bbox['n'],bbox['w'],bbox['s'],bbox['e']])
    exit()
    '''
    Show example data. 
    '''
    for i in sorted(objects['node'].keys()):
        print('node', i, ':', objects['node'][i])
    else:
        print(len(objects['node']))
    for i in sorted(objects['way'].keys()):
        print('way', i, ':', objects['way'][i])
    else:
        print(len(objects['way']))
    for i in objects['relation']:
        tags = objects['relation'][i]['tag']
        if tags['type'] == 'route' or tags['type'] == 'route_master' : 
            print('relation', i, ':', objects['relation'][i])
            members = objects['relation'][i]['member']
            for m in members:
                ref = m['ref']
                if ref in objects['way'] :
                    for r in objects['way'][ref]['ref']:
                        print(' '+str(r), end=',')
                else:
                    print('-',end='')
            print()
        
'''
  <tag k="route" v="road"/>
  <tag k="type" v="route"/>

  <tag k="route_master" v="road"/>
  <tag k="type" v="route_master"/>
'''