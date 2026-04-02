/*
 * rdp.h
 *
 *  Created on: 2026/04/02
 *      Author: sin
 */

#ifndef RDP_H_
#define RDP_H_

#include <deque>
#include "point2d.h"

/*
 * algorithm class RDP (Ramer-Douglas-Peucker) decimation algorithm
 */

class RDP {
public:
	static std::deque<long> decimation(const std::vector<Point2D> & xy, double delta);

};


#endif /* RDP_H_ */
