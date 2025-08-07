'''
Created on 2025/07/25

@author: sin
'''

import numpy as np
import shapefile
from scipy import interpolate
import matplotlib.pyplot as plt

def read_csv(file_name, columns=[0,1]):
    table = list()
    maxindex = max(columns)
    with open(file_name, 'r') as fp:
        for a_line in fp:
            items = a_line.strip().split(',')
            if maxindex > len(items):
                continue
            table.append([items[i] for i in columns])
    return table
        
if __name__ == '__main__':
    
    tbl = np.loadtxt('2023-06-22_164837.csv', delimiter=',')
    print('tbl=', tbl[:,[1,2]])
    ctr = tbl[:,[2,1]]
    for i in range(len(ctr)):
        ctr[i,1] = -ctr[i,1]
    #x = np.arange(0, 2*np.pi+np.pi/4, 2*np.pi/8)
    #y = np.sin(x)
        
    #ctr =np.array( [(3 , 1), (2.5, 4), (0, 1), (-2.5, 4),
    #                (-3, 0), (-2.5, -4), (0, -1), (2.5, -4), (3, -1)])
    ctr = ctr[8:256]
    x=ctr[:,0]
    y=ctr[:,1]
    
    #x=np.append(x,x[0])
    #y=np.append(y,y[0])
    
    tck,u = interpolate.splprep([x,y],k=3,s=0)
    u=np.linspace(0,1,num=50,endpoint=True)
    print(list(u))
    out = interpolate.splev(u,tck)
    print(list(out))
    plt.figure()
    plt.plot(x, y, 'ro', out[0], out[1], 'b')
    plt.legend(['Points', 'Interpolated B-spline', 'True'],loc='best')
    w_m = abs(min(x) - max(x)) * 0.05
    h_m = abs(min(y) - max(y)) * 0.05
    plt.axis([min(x) - w_m, max(x) + w_m, min(y) - h_m, max(y)+h_m])
    plt.title('B-Spline interpolation')
    plt.show()