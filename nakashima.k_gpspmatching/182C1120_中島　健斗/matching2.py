import sys
import re
import csv
from geopy.distance import geodesic
from numpy.linalg import norm
import numpy as np
import math
import time
import geohash

POLE_RADIUS = 6356752  
EQUATOR_RADIUS = 6378137
E = 0.081819191042815790
E2= 0.006694380022900788

delta = int(input())

class Gpsposition:
    def __init__(self, latitude, longitude):
        self.latitude  = latitude
        self.longitude = longitude
        #self.altitude  = altitude

def distance(point_a, point_b):
    a_rad_lat = math.radians(point_a.latitude)
    a_rad_lon = math.radians(point_a.longitude)
    b_rad_lat = math.radians(point_b.latitude)
    b_rad_lon = math.radians(point_b.longitude)
    m_lat = (a_rad_lat + b_rad_lat) / 2
    d_lat = a_rad_lat - b_rad_lat
    d_lon = a_rad_lon - b_rad_lon
    W = math.sqrt(1-E2*math.pow(math.sin(m_lat),2))
    M = EQUATOR_RADIUS*(1-E2) / math.pow(W, 3)
    N = EQUATOR_RADIUS / W
    distance = math.sqrt(math.pow(M*d_lat,2) + math.pow(N*d_lon*math.cos(m_lat),2))
    return distance

def hash_function(lat,lon):
    return geohash.encode(lat,lon)


if len(sys.argv) < 2 :
    print('input (and optionally output) file names are needed.')
    print('usage: python3 gpxreader gpxfile cvsfile[return]')
    exit()


with open(sys.argv[1], mode='r') as f1:
        dataReader1 = csv.reader(f1) 
        h1=[]
        d1=[]
        for i, row in enumerate(dataReader1):
            h1.append(hash_function(float(row[0]),float(row[1])))
            d1.append(geohash.decode(h1[i]))


with open(sys.argv[2], mode='r') as f2:
        dataReader2 = csv.reader(f2)
        h2=[]
        d2=[]
        for i, row in enumerate(dataReader2):
            h2.append(hash_function(float(row[0]),float(row[1])))
            d2.append(geohash.decode(h2[i]))


with open( 'similer.csv', mode='w') as outfile:
    s_time = time.time()
    elist=[]
    dist=100
    matched=[]
    for i in range(len(h1)-1):
        for j  in range(len(h2)):
            if h1[i][:6] == h2[j][:6]:
                movepos = Gpsposition((d1[i][0]+d1[i+1][0])/2,(d1[i][1]+d1[i+1][1])/2)
                mappos = Gpsposition(d2[j][0],d2[j][1])
                dist = distance(movepos,mappos)
            if dist < delta:
                elist.append(j)
                matched.append(d2[j])
                dist=100

    for i in enumerate(elist):
        outfile.write(str(matched[i])+"\n")
    e_time = time.time() - s_time
    print(f'{e_time}s')
