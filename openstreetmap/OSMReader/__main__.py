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
            links[key] = ('highway', value['ref'])
            #print('highway',edges['highway'][key])
    
    geograph = dict()
    for key, val in links.items():
        plist = val[1]
        for ix in range(len(plist)-1):
            if plist[ix] not in geograph:
                geograph[plist[ix]] = list()
            if plist[ix+1] not in geograph:
                geograph[plist[ix+1]] = list()
            geograph[plist[ix]].append(plist[ix+1])
            geograph[plist[ix+1]].append(plist[ix])
    
    print(len(geograph.keys()))

    geohashgrid = dict()
    for pid in geograph.keys():
        gpoint = objects['node'][pid]
        hashcode = geohash.encode(gpoint[0], gpoint[1], 7)
        #print(k, hashcode, gpoint)
        if hashcode in geohashgrid:
            geohashgrid[hashcode].append(pid)
        else:
            geohashgrid[hashcode] = [ pid ]
    
    tally = 0
    for key, val in geohashgrid.items():
        tally += len(val)
    print(tally, ' points in highway/railway.')
    print(len(geohashgrid), ' areas.')
    
    (key, amax) = (0, 0)
    acnt = 0
    tally = 0
    for k in geohashgrid:
        #print(k, len(geohashgrid[k]), geohashgrid[k])
        if len(geohashgrid[k]) > amax :
            (key, amax) = (k, len(geohashgrid[k]) )
        tally += len(geohashgrid[k])
        acnt += 1
    print('max ', amax, ' point in area', key, float(tally)/acnt)
    areabbox = geohash.bbox('wvuzqh8')
    dlat, dlon = areabbox['n'] - areabbox['s'], areabbox['e'] - areabbox['w']
    topleft = (areabbox['n'],  areabbox['w'])
    
    from PIL import Image, ImageDraw
    (hight, width) = (int(dlat * 1e+6), int(dlon * 1e+6))
    print(hight, width)
    
    mapimg = Image.new("RGB", (width, hight), "White")
    draw = ImageDraw.Draw(mapimg)
    gpoints = set()
    for key in geohashgrid.keys():
        if key.startswith('wvuzqh'):
            for ea in geohashgrid[key]:
                gpoints.add(ea)
    for i in gpoints:
        coord = nodes[i]
        x, y = abs(int((topleft[1]-coord[1])*1e+6)), int((topleft[0]-coord[0])*1e+6)
        draw.ellipse([x-1,y-1,x+1,y+1], fill = "Black", outline = "Black")
        adjs = geograph[i]
        #print(x,y, adjs)
        for v in adjs:
            if v in gpoints :
                p2 = nodes[v]
                x2, y2 = abs(int((topleft[1]-p2[1])*1e+6)), int((topleft[0]-p2[0])*1e+6)
                draw.line([x,y,x2,y2], fill= "Black")
    mapimg.show()
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