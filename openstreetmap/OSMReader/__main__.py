'''
Created on 2021/12/16

@author: sin
'''

from lxml import etree
import sys

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
    print(nspaces)
    
    nodes = dict()
    ways = dict()
    for ch in xml:
        if ch.tag == 'node' :
            nodes[ch.attrib['id']] = (ch.attrib['lat'], ch.attrib['lon'])
            # print(ch.tag, ch.attrib)
            # for t in ch:
            #     if t.tag == 'tag' :
            #         print(t.attrib['k'], t.attrib['v'])
        elif ch.tag == 'way' :            
            poslist = list()
            tags = dict()
            for t in ch:
                if t.tag == 'nd':
                    poslist.append(nodes[t.attrib['ref']])
                elif t.tag == 'tag':
                    tags[t.attrib['k']] = t.attrib['v']
            ways[ch.attrib['id']] = (tags, poslist)

    print('nodes', len(nodes))
    print('ways', len(ways))
    for away in sorted(ways.items())[:10] :
        print(away[0], away[1][0])
        print(away[1][1])
        print()