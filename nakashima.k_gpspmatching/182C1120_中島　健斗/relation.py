"""
relation_output.py
"""
from lxml import etree
import sys
from geopy.distance import geodesic
import numpy as np

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

    with open( 'relation.csv', mode='w') as outfile:

        nspaces = xml.nsmap
        if None in nspaces :
            nspaces['defns'] = nspaces.pop(None)
        print(nspaces)
        way_ref=[]
        road_tipe=[]
        way=dict()
        nodes = dict()
        relation_of_road=[]
        for ch in xml:
            if ch.tag == 'node' :
                nodes[ch.attrib['id']] = (ch.attrib['lat'], ch.attrib['lon'])

            elif ch.tag == 'way' :            
                poslist = list()
                tags = dict()
                for t in ch:
                    if t.tag == 'nd':
                        poslist.append(nodes[t.attrib['ref']])
     
                    elif t.tag == 'tag':
                        tags[t.attrib['k']] = t.attrib['v']

                way[ch.attrib['id']]= poslist
                way_ref.append(ch.attrib['id'])

            elif ch.tag == 'relation' :
                for t in ch:
                    if t.tag=='member' and t.attrib['type']=='way':  
                        for i in range(len(way_ref)):
                            if way_ref[i] == t.attrib['ref']:
                                relation_of_road.append(way[t.attrib['ref']])
                                #road_tipe.append(t.attrib['v'])

                    if t.tag=='tag' and t.attrib['v'] == 'multipolygon':
                        relation_of_road.clear()
                        road_tipe.clear()

                    if t.tag=='tag' and t.attrib['v'] == 'train':
                        relation_of_road.clear()
                        road_tipe.clear()

                    if t.tag=='tag' and t.attrib['v'] == 'railway':
                        relation_of_road.clear()
                        road_tipe.clear()
                    
                    if t.tag=='tag' and t.attrib['k'] == 'building':
                        relation_of_road.clear()
                        road_tipe.clear()
                    
                    if t.tag=='tag' and t.attrib['v']=='road':

                        road_tipe.append(t.attrib['v'])
                        i = 0
                        for waynodes in relation_of_road:
                            for j in range(len(waynodes)):
                                print(relation_of_road[i][j])
                                outfile.write(str(relation_of_road[i][j]))
                                outfile.write('\n')
                            i+=1
                        relation_of_road.clear()
                        road_tipe.clear()
                    
                    
        print('nodes', len(nodes))

