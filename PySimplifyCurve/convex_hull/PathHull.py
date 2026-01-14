'''
Created on 2026/01/14

@author: sin
'''
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
        self.hist.appendleft( [self.elt.pop(), 'TOP_OP'] )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           6`0 `````
    
# pop from bottom
#define Hull_Pop_Bot(h) \
#    (h)->helt[++(h)->hp] = (h)->elt[(h)->bot++]; \
#    (h)->op[(h)->hp] =  BOT_OP

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
