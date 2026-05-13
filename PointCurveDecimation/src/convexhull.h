/*
 * convexhull.h
 *
 *  Created on: 2026/04/02
 *      Author: sin
 */

#ifndef CONVEXHULL_H_
#define CONVEXHULL_H_

#include <cstddef>
#include <vector>
#include <deque>

#include "point2d.h"
#include "ringarray.h"

class ConvexHull {
private:
    const std::vector<Point2D> & xy; 	// reference to the original point sequence
    std::vector<long> ptix;				// index seq of points on xy in this convex hull
    ringarray<long> polygon = ringarray<long>(128);    	// subsequence of ptix forming the boundary polygon, in clockwise order

public:
    ConvexHull(const std::vector<Point2D> & xyseq) : xy(xyseq) {
         clear();
    }

    void clear() {
        ptix.clear();
        polygon.clear();
    }

    size_t size() const {
    	return ptix.size();
    }

    std::string to_string() const {
        return "ConvexHull( )" ;
    }

    const Point2D & operator[](const long & ix) const {
    	return xy[ptix[ix]];
    }

    const Point2D & polypt(const long & index) {
        return xy[ptix[polygon[index % polygon.size()]]];
    }

    const long & polyptix(const long & index) const {
		return ptix[polygon[index % polygon.size()]];
	}

    bool add(long ix);

    void remove_concave(void);

    std::ostream & printOn(std::ostream & out) const;

    friend std::ostream & operator<<(std::ostream & out, const ConvexHull & me) { return me.printOn(out); }
};


#endif /* CONVEXHULL_H_ */
