'''
Created on 2026/03/10

@author: sin
'''
import random

if __name__ == '__main__':
    delta = 10  # deviation upper bound
    for i in range(100) :
        rf = random.random()
        rg = random.gauss()
        x = i + (rf - 0.5)*delta*0.1
        y = rg*delta*1.5
        x, y = round(x, 3), round(y, 3)
        print( (x,y) )