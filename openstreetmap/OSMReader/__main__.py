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
                    refs.append(t.attrib['ref'])
                elif t.tag == 'tag':
                    tags[t.attrib['k']] = t.attrib['v']
            objects[ch.tag][ch.attrib['id']] = {'tag': tags, 'ref': refs}
        elif ch.tag == 'relation' :
            members = [ t.attrib for t in ch if t.tag == 'member']
            #print('members = ', members)
            tags = dict()
            for t in ch:
                if t.tag == 'tag' :
                    tags[t.attrib['k']] = t.attrib['v']
            objects[ch.tag][ch.attrib['id']] = {'tag': tags, 'member': members}

    cnt = 0
    geohashgrid7 = dict()
    for k in objects['node'].keys():
        gpoint = objects['node'][k]
        hashcode = geohash.encode(gpoint[0], gpoint[1], 7)
        #print(k, hashcode, gpoint)
        if hashcode in geohashgrid7:
            geohashgrid7[hashcode].append(k)
        else:
            geohashgrid7[hashcode] = [ k ]  
        cnt += 1
        # if cnt > 100 :
        #     break
    print(cnt, ' nodes.')
    print(len(geohashgrid7), ' areas.')
    cnt = 0
    for k in geohashgrid7:
        print(k, len(geohashgrid7[k]), geohashgrid7[k])
        cnt += 1
        if cnt > 200:
            break
    
    for i in sorted(objects['way'].keys()):
        print('way', i, ':', objects['way'][i])
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