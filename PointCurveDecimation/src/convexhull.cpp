/*
 * convexhull.cpp
 *
 *  Created on: 2026/04/02
 *      Author: sin
 */

#include "convexhull.h"

std::ostream & ConvexHull::printOn(std::ostream & out) const {
	out << "ConvexHull(";
	/*
	for(const auto & elem : xy) {
		out << elem << ", ";
	}
	out << std::endl;
	*/
	out << " [";
	for(const auto & elem : ptix) {
		out << elem << ": " << xy[elem] << ", ";
	}
	out << "], " << std::endl;
	out << "[";
	for(long ix = 0; ix < polygon.size(); ++ix) {
		out << polygon[ix] << ", ";
	}
	out << "] ";
	out << ") ";
	return out;
}


bool ConvexHull::add(long ix) {
	// the first and the seconds
	if ( size() <= 1 ) {
		ptix.push_back(ix);
		polygon.push_back(size() - 1);
		return true;
	}

	// add ptix to ptix and polygon
	if ( polypt(1).rhombus(polypt(0), xy[ix]) <= 0 ) {
		ptix.push_back(ix);
		// right or front of the mouth
		polygon.push_back(polygon.pop_front());
		polygon.push_front(size() - 1);
	} else if ( polypt(-1).rhombus(polypt(0), xy[ix]) >= 0 ) {
		ptix.push_back(ix);
		// outside of the left line of the mouth
		polygon.push_front(size() - 1);
	}
	//     # error, not at growth position
	//raise ValueError(f'point {pt} is inside the polygon.')
	//return

	//remove_concave();
	return true;
}

void remove_concave(void) {}
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
*/
/*
void ConvexHull::remove_concave(void) {
	long mouthix = polygon.pop_back();
	Point2D mouthpt = point(mouthix);

}
*/
/*


    def add(self, ptix):
        if len(self) <= 1 :
            self.ptix.append(ptix)
            self.polygon.append(len(self)-1)
            return

        # add ptix to ptix and polygon
        if rhombus(self.polypoint(1), self.polypoint(0), self.xy[ptix]) <= 0 :
            self.ptix.append(ptix)
            # right or front of the mouth
            self.polygon.append(self.polygon.popleft())
            self.polygon.appendleft(len(self)-1)
        elif rhombus(self.polypoint(-1), self.polypoint(0), self.xy[ptix]) >= 0 :
            self.ptix.append(ptix)
            # outside of the left line of the mouth
            self.polygon.appendleft(len(self)-1)
        # else:
        #     # error, not at growth position
        #     raise ValueError(f'point {pt} is inside the polygon.')
        #     return

        self.remove_concave()
        return

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


def delta_rect_decimation_alg(xy : list, delta, verbose = False, polygons = False) -> tuple:
    dixpath = list()     # index sequence of decimated path
    polygon_seq = list()   # considered polygons
    dixpath.append(0)
    cvx = ConvexHull(xy)
    cvx.add(0)
    cvx.add(1)
    cvx_diameter = distance(cvx.first_point(), cvx.last_point())
    ptix = 2
    while ptix < len(xy) :

        verbose and print(f'{ptix}, {xy[ptix]}, dia = {cvx_diameter}, delta = {delta}, {cvx}')
        verbose and print(f'side {cvx.polygon[-1]}-{cvx.polygon[0]}, {rhombus(cvx.polypoint(-1), cvx.polypoint(0), xy[ptix])} >= 0 or {cvx.polygon[1]}-{cvx.polygon[0]}, {rhombus(cvx.polypoint(1), cvx.polypoint(0), xy[ptix])} <= 0 ?' )
        if cvx_diameter <= delta and \
        ( rhombus(cvx.polypoint(-1), cvx.polypoint(0), xy[ptix]) >= 0 or rhombus(cvx.polypoint(1), cvx.polypoint(0), xy[ptix]) <= 0 ):
            verbose and print('within delta and in growth position')
            cvx.add(ptix)
            cvx_diameter = max(cvx_diameter, distance(cvx.first_point(), cvx.last_point()) )
            ptix += 1
            verbose and print(cvx)
            verbose and print()
            continue

        verbose and print('check wether pt is furthest or not.')
        if cvx_diameter > distance(cvx.first_point(), xy[ptix]) :
            verbose and print('getting nearer. stop extending cvx')
            cvx_lastix = cvx.ptix[-1]
            dixpath.append(cvx_lastix)
            if polygons :
                polygon_seq.append([cvx.polyptix(i) for i in range(len(cvx.polygon) + 1)])
            cvx.clear()
            # make new cvx for the 1st and 2nd points.
            cvx.add(cvx_lastix)
            cvx.add(ptix)
            verbose and print(cvx)
            verbose and print(cvx.first_point(), cvx.last_point())
            cvx_diameter = distance(cvx.first_point(), cvx.last_point())
            ptix += 1
            verbose and print(cvx)
            verbose and print()
            continue

        # pt is in the growth position
        verbose and print('pt is at growth distance')

        # preserve the outline of cvx before pt is added
        if polygons :
            prevcvx_polygon = [cvx.polyptix(i) for i in range(len(cvx.polygon) + 1)]

        # add pt to test width
        cvx.add(ptix)
        peakdists = cvx.peak_distances()
        verbose and print(peakdists, [e < delta for e in peakdists])

        if all([e < delta for e in peakdists]) :
            cvx_diameter = distance(cvx.first_point(), cvx.last_point())
            ptix += 1
            verbose and print(cvx)
            verbose and print()
            continue
        else:
            prevcvx_lastix = cvx.ptix[-2]
            dixpath.append(prevcvx_lastix)
            if polygons :
                polygon_seq.append(prevcvx_polygon)
            cvx.clear()
            cvx.add(prevcvx_lastix)
            cvx.add(ptix)
            cvx_diameter = distance(cvx.first_point(), cvx.last_point())
            ptix += 1
            verbose and print(cvx)
            verbose and print()
            continue
        raise ValueError('???')

    if len(cvx) > 0 :
        #print('points exhausted,', cvx)
        dixpath.append(cvx.ptix[-1])
        if polygons :
            polygon_seq.append([cvx.polyptix(ix) for ix in range(len(cvx.polygon) + 1)])

    if not polygons :
        return dixpath
    else:
        return (dixpath, polygon_seq)

*/
