/*
 * convexhull.cpp
 *
 *  Created on: 2026/04/02
 *      Author: sin
 */

#include "convexhull.h"

std::ostream & ConvexHull::printOn(std::ostream & out) const {
	out << "ConvexHull(";

	out << " points = [";
	for(int i = 0; i < points.size(); ++i) {
		if (i > 0)
			out << ", ";
		out << points[i];
	}
	out << "], ";
	out << endl << "polygon = [";
	for(int ix = 0; ix < polygon.size(); ++ix) {
		if (ix > 0)
			out << ", ";
		out << polygon[ix] << " " << points[polygon[ix]];
	}
	out << "] ";
	out << ") ";
	return out;
}


bool ConvexHull::add(const Point2D & pt) {
	// the first and the seconds
	if ( size() <= 1 ) {
		points.push_back(pt);
		polygon.push_back(points.size() - 1);
		return true;
	}

	// add pt to points and polygon
	if ( polygon_point(1).rhombus(polygon_point(0), pt) <= 0 ) {
		// right or front of the beak (polygon_point(0))
		points.push_back(pt);
		polygon.push_back(polygon.pop_front());
		polygon.push_front(points.size() - 1);
	} else if ( polygon_point(-1).rhombus(polygon_point(0), pt) >= 0 ) {
		// left or front of the beak
		points.push_back(pt);
		polygon.push_front(points.size() - 1);
	}
	//     # error, not at growth position
	//raise ValueError(f'point {pt} is inside the polygon.')
	//return

	remove_concave();
	return true;
}

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

void ConvexHull::remove_concave(void) {
	long mouthix = polygon.pop_back(); 	// the last index in polygon is the index of the polygon mouth
	Point2D mouthpt = point(mouthix);	// the point of the polygon mouth
//	std::cout << "remove_concave mouthix = " << mouthix << ", mouthpt = " << mouthpt << std::endl;
//	std::cout << "anti-clockwise check" << std::endl;
	while ( polygon.size() > 2 ) {
//		std::cout << "polygon = ";
//		for(int i = 0; i < polygon.size(); ++i) {
//			std::cout << polygon[i] << " = " << polygon_point(i) << ", ";
//		}
//		std::cout << std::endl;
//		std::cout << "rhombus mouth, -1, -2 = " << mouthpt.rhombus(polygon_point(-1), polygon_point(-2)) << std::endl;
		if (mouthpt.rhombus(polygon_point(-1), polygon_point(-2)) < 0 ) {
			//std::cout << "remove concave peak " << polygon_point(-2) << ", " << polygon_point(-1) << std::endl;
			polygon.pop_back();
		} else
			break;
	}
//	// clockwise check
//	std::cout << "clockwise check" << std::endl;
	while ( polygon.size() > 2 ) {
		if ( mouthpt.rhombus(polygon_point(0), polygon_point(1)) > 0 ) {
//			std::cout << "remove concave peak " << polygon_point(1) << ", " << polygon_point(0) << std::endl;
			polygon.pop_front();
		} else
			break;
	}
	polygon.push_back(mouthix);	// add the mouth index back to polygon
}

ConvexHull::quad_double ConvexHull::peak_distances(void) const {
	quad_double result = {0.0, 0.0, 0.0, 0.0};
	long lb, ub, mix;

	if ( size() <= 1 )
    	return result;

    //Point2D axis = Point2D::vector( first_point(), last_point(), true);
    const Point2D axis = Point2D::vector( point(0), point(-1), true);
    cout << "axis = " << axis << std::endl << std::endl;

    long fwix = 0;    // mouth (polygon start)
	// find forward peak index (fwix) by binary search on cross product sign
	lb = 0; // mouth (polygon start index) as start index
	ub = polygon.size() - 1; // polygon end index

	mix = (lb + ub) >> 1;  // center index
	while (lb < ub) {
    	const Point2D perptoedge = Point2D::vector(polygon_point(mix), polygon_point(mix+1));
    	double crossprod = perptoedge.cross_norm(axis);
    	if (crossprod > 0)
    		lb = mix + 1;
    	else
    		ub = mix;
    	mix = (lb + ub) >> 1;
	}
	fwix = ub;
	cout << "forward peak index = " << fwix << ", point = " << polygon_point(fwix) << std::endl;
	result.fw = axis.dot(Point2D::vector(point(0), polygon_point(fwix)));

    //# backward peak, - --> +
    lb = 0;
    ub = polygon.size() - 1;
    mix = (lb + ub) >> 1;  // center index
    while (lb < ub) {
    	double proj = Point2D::vector(polygon_point(mix), polygon_point(mix+1)).dot(axis);
		if (proj < 0)
			lb = mix + 1;
		else
			ub = mix;
		mix = (lb + ub) >> 1;
    }
    long bkix = ub;

    //# right peak
    Point2D perp9(-axis.y, axis.x);
    lb = fwix, ub = bkix;
    mix = (lb + ub) >> 1;

	while (lb < ub) {
		double proj = Point2D::vector(polygon_point(mix), polygon_point(mix+1)).dot(perp9);
		if (proj < 0)
			lb = mix + 1;
		else
			ub = mix;
		mix = (lb + ub) >> 1;
	}
	long rtix = ub;

	//# left peak
	Point2D perp3 = -perp9;
	lb = bkix, ub = polygon.size();
	mix = (lb + ub) >> 1;
	while (lb < ub) {
		double proj = Point2D::vector(polygon_point(mix), polygon_point(mix+1)).dot(perp3);
		if ( proj < 0 )
			lb = mix + 1;
		else
			ub = mix;
		mix = (lb + ub) >> 1;
	}
	long ltix = ub;

    //#print(f'peak indices = {self.polygon[0]}, {self.polygon[rtix]}, {self.polygon[bkix]}, {self.polygon[ltix % len(self.polygon)]}')
	result.rt = perp3.dot( Point2D::vector(point(0), polygon_point(rtix)));
	result.bk = -axis.dot(Point2D::vector(point(0), polygon_point(bkix)));
	result.lt = perp9.dot(Point2D::vector(point(0), polygon_point(ltix)));
	return result;
}

/*
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
