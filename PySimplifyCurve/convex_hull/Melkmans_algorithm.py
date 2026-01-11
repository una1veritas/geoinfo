'''
Created on 2026/01/10

@author: sin
'''
import math
from collections import deque

class Point2D:
    def __init__(self, xy, yy = None):
        if yy != None :
            self.x = xy
            self.y = yy
        else:
            self.x, self.y = xy[:2]
            
    def __getitem__(self, key):
        if key == 0 or key == 'x' :
            return self.x
        elif key == 1 or key == 'y' :
            return self.y
        raise KeyError('has no such key {key}')

    def __setitem__(self, key, value):
        if key == 0 or key == 'x' :
            self.x = value
        elif key == 1 or key == 'y' :
            self.y = value
        raise KeyError('has no such key {key}')

    def __repr__(self):
        return f'({self.x}, {self.y})'
    
    def __str__(self):
        return f'({self.x}, {self.y})'
    
    def __tuple__(self):
        return (self.x, self.y)
    
    def __neg__(self):
        return Point2D(-self.x, -self.y)
        
    def __sub__(self, other):
        return Point2D( self.x - other.x, self.y - other.y)
        
    def norm(self):
        return math.sqrt(self.x*self.x + self.y*self.y)

    ''' distance between two Point2D points '''
    def distance_to(self, vdst):
        return (vdst - self).norm()

    def outer_prod_norm(self, other):
        return self.x * other.y - self.x * other.y

    ''' < 0 ... self is left , > 0 ... self is right''' 
    def side_from_vector(self, orgpt, dstpt):
        return (dstpt - orgpt).outer_prod_norm(self - orgpt)
    
    def left_of_line(self, a, b):
        return (b.x - a.x) * self.y - (b.y - a.y) * self.x >= 0

    def inner_prod(self, other):
        return self.x * other.x + self.x * other.y

    def distance_to_line(self, a, b):
        ab = b - a
        ap = self - a
        if ab.inner_prod(ap) < 0.0 :
            return ap.norm()
        ba = -ab
        bp = b - self
        if ba.inner_prod(bp) < 0.0 :
            return bp.norm()
        return abs(ab.outer_prod_norm(ap)/ab.norm())

class PathHull:
    '''
    struct PATH_HULL {
        int top, bot;
        int hp, op[TRICE_HULL_MAX];
        POINT * elt[TWICE_HULL_MAX];
        POINT *helt[TRICE_HULL_MAX];
    };
    '''

    def __init__(self):
        self.hist = deque()
        self.elt = deque()
        
    
    def __str__(self):
        return 'PathHull(' + str(self.hist) + ', ' + str(self.elt) + ') '
    
# pop from top
#define Hull_Pop_Top(h) \
#    (h)->helt[++(h)->hp] = (h)->elt[(h)->top--]; \
#    (h)->op[(h)->hp] = TOP_OP

    def pop_top(self):
        self.hist.appendleft( (self.elt.pop(), 'TOP_OP') )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           6`0 `````
    
# pop from bottom
#define Hull_Pop_Bot(h) \
#    (h)->helt[++(h)->hp] = (h)->elt[(h)->bot++]; \
#    (h)->op[(h)->hp] = BOT_OP

    def pop_bottom(self):
        self.hist.append( (self.elt.popleft(), 'BOT_TOP') )
    
# push element e onto path hull h
#define Hull_Push(h, e) \
#    (h)->elt[++(h)->top] = (h)->elt[--(h)->bot] = (h)->helt[++(h)->hp] = e; \
#    (h)->op[(h)->hp] = PUSH_OP

    def push(self, e):
        self.hist.append( (e, 'PUSH_OP') )
        self.elt.popleft()
        self.elt[0] = e
        self.elt.append(e)
'''
typedef double POINT[2];
typedef double HOMOG[3];

struct PATH_HULL {
    int top, bot;
    int hp, op[TRICE_HULL_MAX];
    POINT * elt[TWICE_HULL_MAX];
    POINT *helt[TRICE_HULL_MAX];
};

# inplements Melkman's Convex Hull 
void Hull_Add(PATH_HULL * h, POINT *p) {
    int topflag, botflag;
    topflag = LEFT_OF(h->elt[h->top], h->elt[h->top - 1], p);
    botflag = LEFT_OF(h->elt[h->bot + 1], h->elt[h->bot], p);

    if (topflag or botflag) {
        // if the new point is outside the hull
        while (topflag) {
            Hull_Pop_Top(h);
            topflag = LEFT_OF(h->elt[h->top], h->elt[h->top - 1], p);
        }
        while (botflag) {
            Hull_Pop_Bot(h);
            botflag = LEFT_OF(h->elt[h->bot + 1], h->elt[h->bot], p);
        }
        Hull_Push(h, p);
    }

}
'''

if __name__ == '__main__':
    a = Point2D(0,0)
    b = Point2D(1, 1)
    c = Point2D(0.5, 0.5)
    print(a, b, c, c.left_of_line(a, b))