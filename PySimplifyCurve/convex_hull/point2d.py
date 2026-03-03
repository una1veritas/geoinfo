'''
Created on 2026/01/23

@author: sin
'''
import math

def negvec(v):
    return (-v[0], -v[1])
    
def vec(a, b):
    if isinstance(a, (tuple, list)) and isinstance(a, (tuple, list)) :
        return (b[0] - a[0], b[1] - a[1])
    elif isinstance(a, (int, float)) and isinstance(a, (int, float)) :
        return (a, b)
    
def unitvec(a, b = None):
    if b == None and isinstance(a, (tuple, list)) :
        norm_a = norm(a)
        return (a[0]/norm_a, a[1]/norm_a)
    elif isinstance(a, (tuple, list)) and isinstance(a, (tuple, list)) :
        v = (b[0] - a[0], b[1] - a[1])
        norm_v = norm(v)
        #print(f'v={v}, norm = {norm_v}')
        return (v[0]/norm_v, v[1]/norm_v)
    elif isinstance(a, (int, float)) and isinstance(a, (int, float)) :
        v = (a, b)
        norm_v = norm(v)
        #print(f'v={v}', norm = {norm_v})
        return (v[0]/norm_v, v[1]/norm_v)
    else:
        raise ValueError(*f'uintvec: illegal parameters {a}, {b}')

def perpvec(a, b = None, clockwise = True):
    if isinstance(b, (tuple, list)) :
        if clockwise :
            return (b[1] - a[1], a[0] - b[0])
        else:
            return (a[1] - b[1], b[0] - a[0])
    elif b is None :
        if clockwise :
            return (a[1], -a[0])
        else:
            return (-a[1], a[0])
    
def norm(va):
    return math.sqrt(va[0]*va[0] + va[1]*va[1])

''' distance between two Point2D points '''
def distance_between(a, b):
    return math.sqrt( (b[0] - a[0])**2 + (b[1] - a[1])**2 )

def inner_prod(va, vb):
    return va[0] * vb[0] + va[1] * vb[1]

def outer_prod_z(va, vb):
    return va[0] * vb[1] - va[1] * vb[0]

def side_of_line(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])

def distance_to_line(a, b, p):
    d_a_p = distance_between(a,p)
    d_b_p = distance_between(b,p)
    if d_a_p == 0 or d_b_p == 0 :
        return 0
    if inner_prod(vec(a, b), vec(a, p)) <= 0.0 :
        return d_a_p #norm(vec(a, p))
    if inner_prod(vec(b,a), vec(b, p)) <= 0.0 :
        return d_b_p #norm(vec(b, p))
    return math.fabs(outer_prod_z(vec(a,b),vec(a,p))/d_a_p)


'''
double gpspoint::distanceTo(const gpspoint &q1, const gpspoint &q2) const {
    if ( inner_prod(q1, q2, *this) < epsilon ) { // < 0.0
        return q1.distanceTo(*this);
    }
    if ( inner_prod(q2, q1, *this) < epsilon ) { // < 0.0
        return q2.distanceTo(*this);
    }
    return ABS(norm_outer_prod(q1, q2, *this)) / q1.distanceTo(q2);
}
'''
