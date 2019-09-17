'''
Created on 2019/09/16

@author: sin
'''
# -*- coding: utf-8 -*-
import requests
import json
import sys

if ( len(sys.argv) < 3 ) :
    print('command coord/addr values')
    exit()

param = {}
if (sys.argv[1] == 'coord') :
    param['MODE'] = 'coord'
else:
    param['MODE'] = 'addr'
print('MODE = ', param['MODE'])

param['VALUES'] = sys.argv[2:]
print('VALUES = ', param['VALUES'])
    
key = "AIzaSyAdIk5KmgwvvT4batQGfB-JPN0H1q0-O0c"
if param['MODE'] == 'coord' :
    query_coord = "https://maps.googleapis.com/maps/api/geocode/json?latlng={q_lat},{q_long}&key={api_key}&language=ja"
    url = query_coord.format(q_lat = param['VALUES'][0],q_long = param['VALUES'][1], api_key = key)
elif param['MODE'] == 'addr' :
    query_addr = "https://maps.googleapis.com/maps/api/geocode/json?address={q_addr}&key={api_key}&language=ja"
    url = query_addr.format(q_addr = param['VALUES'][0], api_key = key)

resp = requests.get(url)
data_dict = json.loads(resp.text)
print(data_dict)
