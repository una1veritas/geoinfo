import sys
import re
import csv
from geopy.distance import geodesic

import numpy as np
import math
'''
POLE_RADIUS = 6356752  
EQUATOR_RADIUS = 6378137
E = 0.081819191042815790
E2= 0.006694380022900788

class Gpsposition:
    def __init__(self, latitude, longitude, altitude):
        self.latitude  = latitude
        self.longitude = longitude
        self.altitude  = altitude

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
'''
if len(sys.argv) < 2 :
    print('input (and optionally output) file names are needed.')
    print('usage: python3 gpxreader gpxfile cvsfile[return]')
    exit()


with open(str(sys.argv[1:])+ '.csv', mode='w') as outfile:
    with open(sys.argv[1], mode='r') as f:
        dataReader = csv.reader(f)
        id = 0
        lat=[]
        lon=[]

        for row in dataReader:
            lat.append(float(row[0]))
            lon.append(float(row[1]))
           
        for i in range(len(lat)):
            flag = False
            for j in range(len(lat)):
                if lat[i] == lat[j] and i != j:
                    flag = True

            if flag:
                outfile.write(str(lat[i]))
                outfile.write(",")
                outfile.write(str(lon[i]))
                outfile.write("\n")