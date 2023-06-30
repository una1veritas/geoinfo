/*
 * cartcoor.h
 *
 *  Created on: 2022/09/24
 *      Author: Sin Shimozono
 */

#ifndef CARTCOORD_H_
#define CARTCOORD_H_

#define sign(x) ((x) > 0 ? 1 : ((x) == 0 ? 0: -1))

struct CartCoord {
	double x, y;

	// origin
	CartCoord() : x(0), y(0) {}

	CartCoord(const double & xval, const double & yval) : x(xval), y(yval) {}

	CartCoord(const geopoint & org, const geopoint & dst) {
		x = org.distance_to(geopoint(org.lat, dst.lon));
		y = org.distance_to(geopoint(dst.lat, org.lon));
		if (dst.lon < org.lon)
			x = -x;
		if (dst.lat < org.lat)
			y = -y;
	}

	static bool crossing(const CartCoord & a, const CartCoord & b, const CartCoord & c, const CartCoord & d) {
		return (sign(a.outer_prod(b, c)) * sign(b.outer_prod(a,d)) > 0)
				and (sign(c.outer_prod(d, a)) * sign(d.outer_prod(c,b)) > 0);
	}

	static double distance_between(const CartCoord & a, const CartCoord & b, const CartCoord & c, const CartCoord & d) {
		if ( crossing(a,b,c,d) )
			return 0;
		return std::min(a.distance_to(c,d), b.distance_to(c,d));
	}

	static double length_along(CartCoord a, CartCoord b, CartCoord c, CartCoord d) {
		CartCoord ab = b - a;
		CartCoord cd = d - c;
		double inprod_ab_cd = ab.x * cd.x + ab.y * cd.y;
		if ( inprod_ab_cd < 0 ) { // swap c and d to make c -> d being same direction with a -> b
			std::swap(c, d);
			inprod_ab_cd = -inprod_ab_cd;
		}
		if (inprod_ab_cd == 0)
			return 0;
		if ( c.projection_on(a, b) < 0 and d.projection_on(a, b) < 0 ) {
			// c and d are outside of a-b
			return a.distance_to(b);
		} else if ( c.projection_on(a, b) < 0 ) {
			return std::min(inprod_ab_cd / a.distance_to(b) - c.projection_on(a, b), a.distance_to(b));
		} else if ( d.projection_on(b, a) < 0 ) {
			return std::min(inprod_ab_cd / a.distance_to(b) - d.projection_on(b, a), a.distance_to(b));
		} else {
			return inprod_ab_cd / a.distance_to(b);
		}
	}

	static double cosine(const CartCoord & a, const CartCoord & b, const CartCoord & c, const CartCoord & d) {
		return ((b.x - a.x) * (d.x - c.x) + (b.y - a.y) * (d.y - c.y)) / (a.distance_to(b) * c.distance_to(d));
	}

	CartCoord operator-(const CartCoord & b) const {
		return CartCoord(b.x - x, b.y - y);
	}

	double distance_to(const CartCoord & b) const {
		return sqrt((b.x - x)*(b.x - x) + (b.y - y)*(b.y - y));
	}

	double projection_on(const CartCoord & a, const CartCoord & b) const {
		return ((x - a.x) * (b.x - a.x) + (y - a.y) * (b.y - a.y)) / a.distance_to(b);
	}

	// the norm of outer product around *this
	double outer_prod(const CartCoord & a, const CartCoord & b) const {
		double ax = a.x - x, ay = a.y - y;
		double bx = b.x - x, by = b.y - y;
		return  (ax * by) - (ay * bx);
	}

	double distance_to(const CartCoord & p, const CartCoord & q) const {
		double dp = p.distance_to(*this);
		double dq = q.distance_to(*this);
		if ( this->projection_on(p, q) < 0 or this->projection_on(q, p) < 0 ) {
			// outer of both p and q
			return std::min(dp, dq);
		}
		return abs(p.outer_prod(q, *this))/p.distance_to(q);
	}

	friend std::ostream & operator<<(std::ostream & out, const CartCoord & v) {
		out << "(" << std::setw(3) << v.x << ", " << v.y << ") ";
		return out;
	}
};

#endif /* CARTCOORD_H_ */
