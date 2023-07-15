# -*- coding: utf-8 -*-
import sys
import re
from _ast import If

class geograph:
    def __init__(self):
        self.nodes = dict()
        self.edges = dict()
        
    def __str__(self):
        return str(list(self.nodes)[:10]) + ", " + str(list(self.edges.items())[:10])
    
trajectoryfile_name = '2019-10-05_114328.csv'
segmentsfile_name = 'segments_data/2023-05-06_221836_segment.csv'
edgefile_name = 'road_data/RoadNetwork_Fukuoka_Edge.csv'
nodefile_name = 'road_data/RoadNetwork_Node_Fukuoka.csv'

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


graph = geograph()
with open(nodefile_name, 'r', encoding='utf-8') as file:
    isheadline = True
    for a_line in file:
        items = a_line.strip().split(',')
        if isheadline :
            #node_table.append(items)
            # ['node_id', 'lat', 'lon']
            isheadline = False
        else:
            #node_table.append([ eval(e) for e in items])
            row = [ eval(e) for e in items]
            graph.nodes[row[0]] = (row[1], row[2])

with open(edgefile_name, mode='r', encoding='utf-8') as file:
    isheadline = True
    for a_line in file:
        items = a_line.strip().split(',')
        if isheadline :
            #edge_table.append(items)
            # ['edge_id', 'start', 'end', 'length', 'linestring', 'highway', 'oneway', 'reversed', 'lanes', 'name']
            isheadline = False
        else:
            for i in range(len(items)):
                try:
                    val = eval(items[i])
                    if isinstance(val,(int, float)):
                        items[i] = val 
                except:
                    if items[i].strip() == "nan" :
                        items[i] = float('nan')
                    elif items[i].strip()[:10] == "LINESTRING" :
                        t = items[i].strip()[11:].replace(' ', ',')
                        items[i] = eval(t)
            graph.edges[(items[1], items[2])] = items[3:]

print('---------segments-----------')
print(table[0])
print('--------------------')
for e in table[1:10]:
    print(e)

print('---------graph-----------')
print(graph)