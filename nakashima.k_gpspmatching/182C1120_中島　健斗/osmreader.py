'''
Created on 2021/12/16
@author: sin
'''
''' 
python3 OSMReader map.osm [return]
'''

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

    with open(str(sys.argv[1:])+ '.csv', mode='w') as outfile:

        nspaces = xml.nsmap
        if None in nspaces :
            nspaces['defns'] = nspaces.pop(None)
        print(nspaces)
        idl=[]
        nodes = dict()
        ways = dict()
        for ch in xml:
            if ch.tag == 'node' :
                nodes[ch.attrib['id']] = (ch.attrib['lat'], ch.attrib['lon'])
            elif ch.tag == 'way' :            
                poslist = list()
                tags = dict()
                for t in ch:
                    if t.tag == 'nd':
                        poslist.append(nodes[t.attrib['ref']])
                        idl.append(t.attrib['ref'])

                    elif t.tag == 'tag':
                        tags[t.attrib['k']] = t.attrib['v']

                        #if t.attrib['k'] == 'highway'and t.attrib['v']== 'unclassified':

                        if t.attrib['v']== 'secondary':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'unclassified':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'tertiary':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                print(1111)
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'primary':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'residential':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'motorway':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'trunk':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'path':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'track':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'steps':
                            for i in range(len(idl)):
                                #print(nodes[idl[i]])
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'tertiary_link':
                            for i in range(len(idl)):
                                print(3)
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'secondary_link':
                            for i in range(len(idl)):
                                print(2)
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        if t.attrib['v']== 'primary_link':
                            for i in range(len(idl)):
                                print(1)
                                #cnt+=1
                                outfile.write(str(nodes[idl[i]]))
                                outfile.write("\n")
                        
            
                        idl.clear()    
                        
                            
                ways[ch.attrib['id']] = (tags, poslist)

        print('nodes', len(nodes))
        print('ways', len(ways))
        """
        for away in sorted(ways.items())[:10] :
            #print(away[0], away[1][0])
            print(away[1][0])
        """
