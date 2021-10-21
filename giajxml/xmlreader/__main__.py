'''
Created on 2021/10/20

@author: Sin Shimozono
'''

#import json
import xmltodict
#from lxml.etree import parse
from collections import OrderedDict
from lxml import etree

with open('../GIAJ_DL/FG-GML-503032-ALL-20210701/test-0001.xml') as fp:
#with open('test.xml') as fp:
    xtree = etree.parse(fp)

#xml = bytes(bytearray(text, encoding='utf-8'))
#tree = etree.parse(xml)
root = xtree.getroot()

print( 'root tag = %s' % root.tag )
print( 'root nsmap = %s' % root.nsmap )
#print( etree.tostring(xtree, encoding='utf-8').decode())

for elem in xtree.iter():
    print('tag={}, attr={}, text={}'.format(elem.tag, elem.get('att'), elem.text))

print(xtree.find('gml:posList', namespaces={'gml': 'http://www.opengis.net/gml/3.2'}) )
exit()

def traverse(dic, search):
    #print(search[0:])
    if not len(search):
        yield dic
    elif isinstance(dic, (list, tuple)):
        for ea in dic:
            yield from traverse(ea, search)
    elif isinstance(dic, (dict, OrderedDict)):
        for k, v in dic.items():
            if len(search) and k == search[0]:
                yield from traverse(v, search[1:])
        # else:
        #     yield (k, v)

    
if __name__ == '__main__':
    with open('../GIAJ_DL/FG-GML-503032-ALL-20210701/FG-GML-503032-AdmArea-20210701-0001.xml', encoding='utf-8') as fp:
        oddata = xmltodict.parse(fp.read())
    
    #print(dict_data)
    #for a in traverse(oddata,['Dataset','AdmArea', 'area','gml:Surface','gml:patches','gml:PolygonPatch','gml:exterior','gml:Ring','gml:curveMember','gml:Curve','gml:segments','gml:LineStringSegment','gml:posList']):
    for a in traverse(oddata,['Dataset','AdmArea',]):
        print(str(a))
        print()