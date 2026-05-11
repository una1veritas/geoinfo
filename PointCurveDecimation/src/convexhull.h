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

/*
    def remove_concave(self):
        # from tail
        mouthix = self.polygon.popleft()    # polygon is a ring sequence
        mouthpt = self.point(mouthix)
        # anti clockwise
        while len(self.polygon) > 2 :
            if rhombus(mouthpt, self.polypoint(-1), self.polypoint(-2)) < 0 :
                self.polygon.pop() # pop-out polygon[-1]
            else:
                break
        # from month, clock wise
        while len(self.polygon) > 2 :
            if rhombus(mouthpt, self.polypoint(0), self.polypoint(1)) > 0 :
                self.polygon.popleft() # pop-out polygon[0]
            else:
                break
        self.polygon.appendleft(mouthix)

    def peak_distances(self):
        fwix = 0    # forward peak index == mouth (polygon start)
        if len(self) <= 1 :
            return (0.0, 0.0, 0.0, 0.0)
        axis = unitvec(self.first_point(), self.last_point())
        # backward peak, - --> +
        lb, ub = 0, len(self.polygon) - 1
        mix = (lb + ub) >> 1
        while lb < ub :
            proj = dot_product(vec(self.polypoint(mix), self.polypoint(mix+1)), axis)
            if proj < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        bkix = ub
        # right peak
        perp9 = (-axis[1], axis[0])
        lb, ub = fwix, bkix
        mix = (lb + ub) >> 1
        while lb < ub :
            proj = dot_product(vec(self.polypoint(mix), self.polypoint(mix+1)), perp9)
            if proj < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        rtix = ub
        # left peak
        perp3 = (-perp9[0], -perp9[1])
        lb, ub = bkix, len(self.polygon)
        mix = (lb + ub) >> 1
        while lb < ub :
            proj = dot_product(vec(self.polypoint(mix), self.polypoint(mix+1)), perp3)
            if proj < 0 :
                lb = mix + 1
            else:
                ub = mix
            mix = (lb + ub) >> 1
        ltix = ub
        #print(f'peak indices = {self.polygon[0]}, {self.polygon[rtix]}, {self.polygon[bkix]}, {self.polygon[ltix % len(self.polygon)]}')
        return (0.0, dot_product(perp3, vec(self.first_point(), self.polypoint(rtix))), \
                dot_product( (-axis[0], -axis[1]), vec(self.first_point(), self.polypoint(bkix))), -dot_product(perp3, vec(self.first_point(), self.polypoint(ltix))), )
*/
};


#endif /* CONVEXHULL_H_ */
