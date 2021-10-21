'''
Created on 2021/10/20

@author: Sin Shimozono
'''

import json
import xmltodict
#from lxml.etree import parse
from collections import OrderedDict

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
    # XMLÉtÉ@ÉCÉãÇÃèàóù
    with open('../GIAJ_DL/FG-GML-503032-ALL-20210701/FG-GML-503032-AdmArea-20210701-0001.xml', encoding='utf-8') as fp:
        # xmlì«Ç›çûÇ›
        # xml Å® dict
        oddata = xmltodict.parse(fp.read())
    
    #print(dict_data)
    #for a in traverse(oddata,['Dataset','AdmArea', 'area','gml:Surface','gml:patches','gml:PolygonPatch','gml:exterior','gml:Ring','gml:curveMember','gml:Curve','gml:segments','gml:LineStringSegment','gml:posList']):
    for a in traverse(oddata,['Dataset','AdmArea',]):
        print(str(a))
        print()