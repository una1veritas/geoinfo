'''
Created on 2026/03/10

@author: sin
'''
import random, math, sys

if __name__ == '__main__':
    args = dict()
    argc = len(sys.argv)
    ix = 1
    while ix < argc :
        if sys.argv[ix] == '-d' :
            args['dev'] = float(sys.argv[ix+1])
            ix += 2
        elif sys.argv[ix] == '-n' :
            args['num'] = int(sys.argv[ix+1])
            ix += 2
        elif sys.argv[ix] == '-w' :
            args['width'] = int(sys.argv[ix+1])
            ix += 2
        else:
            ix += 1
    
    seq = list()
    x, y = 0.0, 0.0
    dev = args['dev']  # deviation upper bound
    num = args['num']
    width = args['width']
    step = float(width/(num+1))
    print(num, dev, width)
    for i in range(num) :
        rf = random.random()
        rg = random.gauss(0.0, 1.0)/4.0
        x += step + rf*int(width/num)
        y = rg*dev*2.5*(1+math.fabs(width/2.0 - i*step)/(width/4))
        x, y = round(x, 3), round(y, 3)
        seq.append( (x,y) )
        print(x,y)
    
    with open('gen.csv', 'w') as f :
        for pt in seq :
            f.write(f'{pt[0]},{pt[1]}\n')
    