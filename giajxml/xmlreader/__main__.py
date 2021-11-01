'''
Created on 2021/10/20

@author: Sin Shimozono
'''

#import json
#import xmltodict
#from collections import OrderedDict
from lxml import etree
import sys
import numpy as np
from simplification.cutil import (
    simplify_coords, # this is Douglas-Peucker 
    simplify_coords_vw,  # this is Visvalingam-Whyatt
)

if len(sys.argv) < 2 :
    print('xml file name is requested.',file=sys.stderr)
    exit(1)

separator = ','
for arg in sys.argv[2:]:
    if arg == '-tab' :
        separator = '\t'

try:
    with open(sys.argv[1], encoding='utf-8') as fp:
    #with open('test.xml') as fp:
        xmlbytes = bytes(bytearray(fp.read(), encoding='utf-8'))
except Exception as ex:
    print(ex, file=sys.stderr)
    exit(1)

xml = etree.fromstring(xmlbytes)
print("root info: ",xml.tag, xml.attrib,file=sys.stderr)
nspaces = xml.nsmap
if None in nspaces :
    nspaces['defns'] = nspaces.pop(None)
#print(nspaces)
#for ch in xroot:
#    print(ch.tag, ch.attrib)

extract_types = {u'真幅道路', u'索道', u'徒歩道', u'トンネル内の道路', u'索道', u'普通鉄道', u'トンネル内の鉄道', u'徒歩道'}
types = dict()

rdcount = 0
for ea in xml.xpath('./defns:RdEdg|./defns:RailCL|./defns:RdCompt', namespaces=nspaces):
    ##print(etree.tostring(ea, pretty_print=True).decode())
    eatype = ea.xpath('defns:type/text()', namespaces=nspaces)[0]
    if eatype in types:
        types[eatype] += 1
    else:
        types[eatype] = 1
    if eatype in extract_types:
        print(str(eatype)+separator+str(ea.attrib['{http://www.opengis.net/gml/3.2}id']))
        postext = ea.xpath('defns:loc/gml:Curve/gml:segments/gml:LineStringSegment/gml:posList/text()', namespaces=nspaces)[0]
        coords = list()
        for aline in postext.split('\n'):
            if not len(aline) : continue
            items = aline.split(' ')
            coords.append(tuple([float(anitem) for anitem in items]))
            print(('{:.9f}'+separator+'{:.9f}').format(coords[-1][0], coords[-1][1]))        
        simplified = simplify_coords(coords, 0.00001)
        print()
        for lat, lon in simplified:
            print(('{:.9f}'+separator+'{:.9f}').format(lat,lon))
        print()
    rdcount += 1
    #if rdcount > 12 : break
    #print(etree.tostring(ea, encoding='utf-8', pretty_print=True).decode())

print('rdcount=',rdcount,file=sys.stderr)
print('types=', types, file=sys.stderr)