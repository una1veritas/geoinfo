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

using std::vector;
using std::cout;
using std::endl;

class ConvexHull {
private:
    vector<Point2D> points; 	// the original input point sequence
    ringarray<int> polygon = ringarray<int>(128);
    // sequence of indices of points forming the convex hull polygon,
    // in clock-wise order, starting from the mouth point (the first point of the polygon)

public:
    ConvexHull(void) {
         clear();
    }

    void clear() {
    	points.clear();
        polygon.clear();
    }

    size_t size() const {
    	return points.size();
    }

    // get the i-th point in this convex hull
    const Point2D & point(int ix) const {
       	if ( ix >= 0 ) {
       		return points[ix];
       	} else {
       		return points[points.size() + ix];
       	}
    }

    inline const Point2D & operator[](int ix) const {
    	return point(ix);
    }

//    const Point2D & first_point(void) const {
//        return points[0];
//    }
//
//    const Point2D & last_point(void) const {
//        return points[points.size() - 1];
//    }

    // get the i-th point in polygon
    const Point2D & polygon_point(int ix) const {
    	if ( ix < 0 ) {
    		return points[polygon[polygon.size() + ix]];
    	} else {
    		return points[polygon[ix]];
    	}
    }

	bool add(const Point2D & pt);

    void remove_concave(void);

    struct quad_double {
    	double fw, rt, bk, lt;
    };

    quad_double peak_distances() const;

    std::ostream & printOn(std::ostream & out) const;

    friend std::ostream & operator<<(std::ostream & out, const ConvexHull & me) { return me.printOn(out); }
};

#endif /* CONVEXHULL_H_ */
