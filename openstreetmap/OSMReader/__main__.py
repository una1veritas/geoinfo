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
    Get geoobjs from .osm file into a JSON-like python dict.
    '''
    # considers only the following three objects
    #geoobjs = { 'node':{}, 'way': {}, 'relation': {}}
    nodes = dict()
    ways = dict()
    relations = dict()
    labels = dict()
    for ch in xml:
        if ch.tag == 'node' :
            nodeid = int(ch.attrib['id'])
            (lat, lon) = (float(ch.attrib['lat']), float(ch.attrib['lon']))
            nodes[nodeid] = (lat, lon)
            for t in ch:
                if t.tag != 'tag' : continue
                if t.attrib['k'] in ('shop', 'leisure', 'amenity', 'name') :
                    if nodeid not in labels :
                        labels[nodeid] = list()
                    labels[nodeid].append(t.attrib['k'] + ":" + t.attrib['v'])
                
        elif ch.tag == 'way' :
            wayid = int(ch.attrib['id'])
            refs = list()
            tags = dict()
            for t in ch:
                if t.tag == 'nd':
                    refs.append(int(t.attrib['ref']))
                elif t.tag == 'tag':
                    tags[t.attrib['k']] = t.attrib['v']
            ways[wayid] = {'tag': tags, 'ref': refs}
            for t in ch:
                if t.tag != 'tag' : continue
                if t.attrib['k'] in ('shop', 'leisure', 'amenity', 'name') :
                    if id not in labels :
                        labels[wayid] = list()
                    labels[wayid].append(t.attrib['k'] + ":" + t.attrib['v'])

        elif ch.tag == 'relation' :
            relid = int(ch.attrib['id'])
            members = [ t.attrib for t in ch if t.tag == 'member']
            #print('members = ', members)
            tags = dict()
            for t in ch:
                if t.tag == 'tag' :
                    tags[t.attrib['k']] = t.attrib['v']
            relations[relid] = {'tag': tags, 'member': members}
    return (nodes, ways, relations, labels)

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
    dangle = max(dlat, dlon)
    h = geodist((bbox[0], bbox[1]), (bbox[0], bbox[1]+dangle) )
    v = geodist((bbox[0], bbox[1]), (bbox[0]+dangle, bbox[1]))
    print(bbox, dangle, h,v,h/v)
    r = 1.15 #h/v
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
    
    a = 6378137.0           #mode ? 6378137.0 : 6377397.155;
    #b = 6356752.314140356   #mode ? 6356752.314140356 : 6356078.963; 
    e2 = 0.00669438002301188    #mode ? 0.00669438002301188 : 0.00667436061028297; 
    a1e2 = 6335439.32708317     #mode ? 6335439.32708317 : 6334832.10663254; 
    
    sin_latavr = math.sin(latavr)
    W2 = 1.0 - e2 * (sin_latavr*sin_latavr)
    M = a1e2 / (math.sqrt(W2)*W2)
    N = a / math.sqrt(W2)
    
    t1 = M * (gp1rad[0] - gp2rad[1])        #latdiff;
    t2 = N * math.cos(latavr) * (gp1rad[1] - gp2rad[1])    #londiff;
    return math.sqrt((t1*t1) + (t2*t2))

#
#
# main program
if __name__ == '__main__':
    if len(sys.argv) < 2 :
        print('osm file is requested.',file=sys.stderr)
        exit(1)
    
    paths = []
    mapbbox = None
    ix = 1
    while ix < len(sys.argv) :
        if sys.argv[ix].startswith('-g'):
            ix += 1
            if ix >= len(sys.argv):
                print("error: supply GeoHash code after -g.")
                exit()
            ghcode = sys.argv[ix]
            mapbbox = geohash.decode(ghcode)
            print(mapbbox)
            ix += 1
        else:
            paths.append(sys.argv[ix])
            ix += 1
    
    geograph = dict()
    for filename in paths :
        try:
            print(filename)
            with open(filename, encoding='utf-8') as fp:
                #with open('test.xml') as fp:
                xmlbytes = bytes(bytearray(fp.read(), encoding='utf-8'))
        except Exception as ex:
            print(ex, file=sys.stderr)
            continue
        
        xml = etree.fromstring(xmlbytes)
        print("root info: ",xml.tag, xml.attrib)
        
        nspaces = xml.nsmap
        if None in nspaces :
            nspaces['defns'] = nspaces.pop(None)
        print('nspaces = ', nspaces)
        
        (nodes, ways, relations, labels) = getobject(xml)
        links = dict()
        # extract the points only referred in way-links. 
        for wayid, value in sorted(ways.items()):
            #print(id, value)
            if 'railway' in value['tag']:
                links[wayid] = ('railway:'+value['tag']['railway'], value['ref'])
                #print('railway',edges['railway'][key])
            elif 'highway' in value['tag']:
                # if value['tag']['highway'] == 'residential':
                #     pass
                # else:
                links[wayid] = ('highway:' + value['tag']['highway'], value['ref'])
                #print('highway', value)
            elif 'natural' in value['tag']:
                links[wayid] = ('natural:'+ value['tag']['natural'], value['ref'])
            elif 'leisure' in value['tag']:
                links[wayid] = ('leisure:'+ value['tag']['leisure'], value['ref'])
        
        for nodeid, coordval in nodes.items() :
            if nodeid in labels: 
                label = '"' + ' '.join([s for s in labels[nodeid]])+'"'
            else:
                label = ''
            geograph[nodeid] = [coordval, label]
            #print(nodeid, geograph[nodeid])
    
        for wayid, val in links.items():
            (wayclass, pointids) = val
            #print(wayid, wayclass, pointids)
            # add edges along with link
            if wayid in labels :
                label = '"' + ' '.join([s for s in labels[wayid]])+'"'
            else:
                label = ''
            for ix in range(len(pointids) - 1):
                if len(label) :
                    geograph[pointids[ix]][1] += label
                if pointids[ix] < pointids[ix+1] :
                    geograph[pointids[ix]].append(pointids[ix+1])
                else:
                    geograph[pointids[ix+1]].append(pointids[ix])
                
            '''
                if gplist[ix] not in geograph:
                    geograph[gplist[ix]] = (nodes[gplist[ix]],list())
                if gplist[ix+1] not in geograph:
                    geograph[gplist[ix+1]] = (nodes[gplist[ix+1]],list())
                if gplist[ix+1] not in geograph[gplist[ix]][-1] :
                    geograph[gplist[ix]][-1].append(gplist[ix+1])
                if gplist[ix] not in geograph[gplist[ix+1]][-1] :
                    geograph[gplist[ix+1]][-1].append(gplist[ix])
            '''
    
    with open('output.csv', mode='w', encoding='utf-8') as fp:
        #fp.write(#node id,latitude,longitude,adjacent node id 1, node id 2,...)
        for nodeid, values in sorted(geograph.items()) :
            #print(values)
            fp.write(str(nodeid))
            fp.write(',')
            fp.write(str(values[0])) # coordinates
            fp.write(',')
            fp.write(str(values[1])) # labels
            fp.write(',')
            fp.write(', '.join([str(eachid) for eachid in values[2:]])) # adjacent node ids
            fp.write('\n')
    
    with open('facility.csv', mode='w', encoding='utf-8') as fp:
        #fp.write(#node id,latitude,longitude,adjacent node id 1, node id 2,...)
        for t in sorted(labels.items()) :
            if 'shop:convenience' in t[1] or 'shop:supermarket' in t[1] \
                or 'leisure:park' in t[1] or 'amenity:atm' in t[1] :
                fp.write(str(t[0]))
                fp.write(',')
                for ea in t[1]:
                    fp.write(ea)
                    fp.write(',')
                fp.write('\n')
    
    # for some tests
    geohashlist = list()
    for pid in geograph.keys():
        gpoint = geograph[pid][0]
        hashcode = geohash.encode(gpoint[0], gpoint[1], 8)
        geohashlist.append((hashcode, pid))
    
    geohashlist.sort(key=lambda entry: entry[0])
    
    #showgeograph(geograph) #, [bbox['n'],bbox['w'],bbox['s'],bbox['e']])
    exit()
    '''
    Show example data. 
    '''
    for i in sorted(geoobjs['node'].keys()):
        print('node', i, ':', geoobjs['node'][i])
    else:
        print(len(geoobjs['node']))
    for i in sorted(geoobjs['way'].keys()):
        print('way', i, ':', geoobjs['way'][i])
    else:
        print(len(geoobjs['way']))
    for i in geoobjs['relation']:
        tags = geoobjs['relation'][i]['tag']
        if tags['type'] == 'route' or tags['type'] == 'route_master' : 
            print('relation', i, ':', geoobjs['relation'][i])
            members = geoobjs['relation'][i]['member']
            for m in members:
                ref = m['ref']
                if ref in geoobjs['way'] :
                    for r in geoobjs['way'][ref]['ref']:
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