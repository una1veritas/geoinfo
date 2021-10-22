'''
Created on 2021/10/20

@author: Sin Shimozono
'''

#import json
#import xmltodict
#from collections import OrderedDict
from lxml import etree
import sys

if len(sys.argv) < 2 :
    print('xml file name is requested.',file=sys.stderr)
    exit(1)

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

extract_types = {u'真幅道路', u'索道', u'普通鉄道'}

rdcount = 0
for ea in xml.xpath('./defns:RdEdg', namespaces=nspaces):
    ##print(etree.tostring(ea, pretty_print=True).decode())
    eatype = ea.xpath('defns:type/text()', namespaces=nspaces)[0]
    if eatype in extract_types:
        print('type:', eatype, 'id:',ea.attrib['{http://www.opengis.net/gml/3.2}id'],file=sys.stderr)
        postext = ea.xpath('defns:loc/gml:Curve/gml:segments/gml:LineStringSegment/gml:posList/text()', namespaces=nspaces)[0]
        for aline in postext.split('\n'):
            if not len(aline) : continue
            items = aline.split(' ')
            print('{},{}'.format(items[0], items[1]))        
        print()
    rdcount += 1
    #if rdcount > 12 : break
    #print(etree.tostring(ea, encoding='utf-8', pretty_print=True).decode())

print('rdcount=',rdcount,file=sys.stderr)