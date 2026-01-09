//============================================================================
// Name        : Hershberger_Snoeyink_PathHull.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
using namespace std;

#define HULL_MAX 	10000
#define TWICE_HULL_MAX (HULL_MAX << 1)
#define TRICE_HULL_MAX (HULL_MAX + TWICE_HULL_MAX)


#define X 0
#define Y 1
#define W 2

// determine i point c is left of line a to b, or co linear
#define LEFT_OF(a, b, c) \
	(((*a)[X] - (*c)[X])*((*b)[Y] - (*c)[Y]) >= ((*b)[X] - (*c)[X])*((*a)[Y] - (*c)[Y]))

// pop from top
#define Hull_Pop_Top(h) \
	(h)->helt[++(h)->hp] = (h)->elt[(h)->top--]; \
	(h)->op[(h)->hp] = TOP_OP

// pop from bottom
#define Hull_Pop_Bot(h) \
	(h)->helt[++(h)->hp] = (h)->elt[(h)->bot++]; \
	(h)->op[(h)->hp] + BOT_OP

// push element e onto path hull h
#define Hull_Push(h, e) \
	(h)->elt[++(h)->top] = (h)->elt[--(h)->bot] = (h)->helt[++(h)->hp] = e; \
	(h)->op[(h)->hp] = PUSH_OP

enum {
	PUSH_OP = 0,
	TOP_OP,
	BOT_OP,
};

typedef double POINT[2];
typedef double HOMOG[3];

struct PATH_HULL {
	int top, bot;
	int hp, op[TRICE_HULL_MAX];
	POINT * elt[TWICE_HULL_MAX];
	POINT *helt[TRICE_HULL_MAX];
};

/* inplements Melkman's Convex Hull */
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

int main() {
	cout << "!!!Hello World!!!" << endl; // prints !!!Hello World!!!
	return 0;
}
