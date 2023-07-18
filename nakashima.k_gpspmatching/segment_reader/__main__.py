# -*- coding: utf-8 -*-
import sys
from lxml import etree


class geograph:
    def __init__(self, xml):
        '''
        Get geoobjs from .osm file into a JSON-like python dict.
        '''
        # considers only the following three objects
        self.nodes = dict()
        self.ways = dict()
        self.relations = dict()
        self.labels = dict()
        ignore_way_attrib = set()
        ignore_node_attrib = set()
        for elem in xml:
            if elem.tag == 'node' :
                nodeid = int(elem.attrib['id'])
                (lat, lon) = (float(elem.attrib['lat']), float(elem.attrib['lon']))
#                if any([ a_tag in ('highway') for a_tag in tags]) :
                self.nodes[nodeid] = (lat, lon)
                for t in elem:
                    if t.tag != 'tag' : continue
                    print("node attrib ",t.attrib['k'])
                    if t.attrib['k'] in ('shop', 'leisure', 'amenity', 'highway', 'crossing', 'parking') :
                        #, 'name', 'name:en', 'name:ja'
                        if nodeid not in self.labels :
                            self.labels[nodeid] = list()
                        self.labels[nodeid].append(t.attrib['k'] + ":" + t.attrib['v'])
                    else:
                        if not t.attrib['k'] in ignore_node_attrib:
                            print('ignore node attrib[k]:', t.attrib['k'])
                            ignore_node_attrib.add(t.attrib['k'])
            elif elem.tag == 'way' :
                wayid = int(elem.attrib['id'])
                refs = list()
                tags = dict()
                for t in elem:
                    if t.tag == 'nd':
                        refs.append(int(t.attrib['ref']))
                    elif t.tag == 'tag':
                        tags[t.attrib['k']] = t.attrib['v']
                if any([ a_tag in ('highway') for a_tag in tags]) :
                    self.ways[wayid] = {'tag': tags, 'ref': refs}
                    for t in elem:
                        if t.tag != 'tag' : continue
                        if t.attrib['k'] in ('shop', 'leisure', 'amenity', 'highway', 'footway', 'oneway', 'tunnel', 'foot', 'sidewalk', 'parking') :
                            #, 'name', 'name:ja'
                            if id not in self.labels :
                                self.labels[wayid] = list()
                            self.labels[wayid].append(t.attrib['k'] + ":" + t.attrib['v'])
                        else:
                            if not t.attrib['k'] in ignore_way_attrib:
                                print('ignore label to way attrib:', t.attrib['k'])
                                ignore_way_attrib.add(t.attrib['k'])
    
            elif elem.tag == 'relation' :
                relid = int(elem.attrib['id'])
                members = [ t.attrib for t in elem if t.tag == 'member']
                #print('members = ', members)
                tags = dict()
                for t in elem:
                    if t.tag == 'tag' :
                        tags[t.attrib['k']] = t.attrib['v']
                self.relations[relid] = {'tag': tags, 'member': members}
            else:
                print('ignore:', elem.tag)
        return

    def __str__(self):
        return str(len(self.nodes)) + ' nodes ' + str(list(self.nodes)[:10]) + ", \n" \
            + str(len(self.ways)) + ' ways ' +str(list(self.ways.items())[:10]) + ", \n" \
            + str(len(self.relations)) + ' relations ' +str(list(self.relations.items())[:10])
    
trajectoryfile_name = '2019-10-05_114328.csv'
segmentsfile_name = 'segments_data/2023-05-06_221836_segment.csv'
edgefile_name = 'road_data/RoadNetwork_Fukuoka_Edge.csv'
nodefile_name = 'road_data/RoadNetwork_Node_Fukuoka.csv'
osmfile_name = 'fukuoka_momochi.osm'

try:
    print('osmfile name = ', osmfile_name)
    with open(osmfile_name, encoding='utf-8') as fp:
        #with open('test.xml') as fp:
        xmlbytes = bytes(bytearray(fp.read(), encoding='utf-8'))
        xml = etree.fromstring(xmlbytes)
        print("root info: ",xml.tag, xml.attrib)
except Exception as ex:
    print(ex, file=sys.stderr)
    exit(1)

nspaces = xml.nsmap
if None in nspaces :
    nspaces['defns'] = nspaces.pop(None)
print('nspaces = ', nspaces)
geog = geograph(xml)

# with open(trajectoryfile_name, 'r') as file:
#     for a_line in file:
#         items = a_line.strip().split(',')
#         print(items)

table = list()    
with open(segmentsfile_name, 'r') as file:
    isheadline = True
    for a_line in file:
        items = a_line.strip().split(',')
        if isheadline :
            table.append(items)
            isheadline = False
        else:
            for i in range(len(items)):
                try:
                    val = eval(items[i])
                    if isinstance(val,(int, float)):
                        items[i] = val 
                    elif isinstance(val, list):
                        items[i] = items[i].replace("' '", "','")
                        items[i] = ','.join(eval(items[i]))
                except:
                    # untouch a string.
                    pass
            table.append(items)


# graph = geograph()
# with open(nodefile_name, 'r', encoding='utf-8') as file:
#     isheadline = True
#     for a_line in file:
#         items = a_line.strip().split(',')
#         if isheadline :
#             #node_table.append(items)
#             # ['node_id', 'lat', 'lon']
#             isheadline = False
#         else:
#             #node_table.append([ eval(e) for e in items])
#             row = [ eval(e) for e in items]
#             graph.nodes[row[0]] = (row[1], row[2])
#
# with open(edgefile_name, mode='r', encoding='utf-8') as file:
#     isheadline = True
#     for a_line in file:
#         items = a_line.strip().split(',')
#         if isheadline :
#             #edge_table.append(items)
#             # ['edge_id', 'start', 'end', 'length', 'linestring', 'highway', 'oneway', 'reversed', 'lanes', 'name']
#             isheadline = False
#         else:
#             for i in range(len(items)):
#                 try:
#                     val = eval(items[i])
#                     if isinstance(val,(int, float)):
#                         items[i] = val 
#                 except:
#                     if items[i].strip() == "nan" :
#                         items[i] = float('nan')
#                     elif items[i].strip()[:10] == "LINESTRING" :
#                         t = items[i].strip()[11:].replace(' ', ',')
#                         items[i] = eval(t)
#             graph.edges[(items[1], items[2])] = items[3:]

print('---------segments-----------')
print(table[0])
print('--------------------')
for e in table[1:10]:
    print(e)

print('---------graph-----------')
print(geog)