'''
Created on 2021/10/20

@author: Sin Shimozono
'''


import io, xml.etree.ElementTree as ET

def traverse(dic, search):
    for k, v in dic.items():
        if isinstance(v, (dict, OrderedDict)):
            yield k
            yield from traverse(v, search)
        elif isinstance(v, list):
            yield k
            for ea in v:
                if isinstance(ea, (dict, OrderedDict)):
                    yield from traverse(ea, search)
                else:
                    yield v
        elif k == search:
            yield (k, v)

with open("streamlen.tsv") as f:
    target = f.readline().strip()
    slen = [int(line) for line in f.readlines()]

import bz2, io, xml.etree.ElementTree as ET

with open("streamlen.tsv") as f:
    target = f.readline().strip()
    slen = [int(line) for line in f.readlines()]

def getpages(bz2data):
    xml = bz2.decompress(bz2data).decode("utf-8")
    pages = ET.fromstring(f"<pages>{xml}</pages>")
    for page in pages:
        if int(page.find("ns").text) == 0:
            id = int(page.find("id").text)
            with io.StringIO(page.find("revision/text").text) as text:
                yield id, text

lines = 0
with open(target, "rb") as f:
    f.seek(slen[0])
    for length in slen[1:-1]:
        for id, text in getpages(f.read(length)):
            for line in text:
                lines += 1
print(f"lines: {lines:,}")

import json
import xmltodict
from _collections import OrderedDict
#from lxml.etree import parse

td = {'mon': 3, 'tue': {8: -1, 9: -5}}
    
if __name__ == '__main__':
    # XMLÉtÉ@ÉCÉãÇÃèàóù
    with open('../GIAJ_DL/FG-GML-503032-ALL-20210701/test-0001.xml', encoding='utf-8') as fp:
        # xmlì«Ç›çûÇ›
        xml_data = fp.read()
     
        # xml Å® dict
        dict_data = xmltodict.parse(xml_data)
    
    #print(dict_data)
    for a in traverse(dict_data,'gml:posList'):
        print(str(a))