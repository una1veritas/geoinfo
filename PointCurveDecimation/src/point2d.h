//============================================================================
// Name        : PointCurveDecimation.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#ifndef _POINT2D_H_
#define _POINT2D_H_

#include <iostream>
#include <vector>
#include <cmath>


struct Point2D {
	// instance members
	double x;
	double y;

	// static methods

	static Point2D vector(const Point2D & startpt, const Point2D & endpt, const bool unit = false) {
		Point2D vec(endpt.x - startpt.x, endpt.y - startpt.y);
		if (unit) {
			double norm = vec.norm();
			if (norm > 0) {
				vec.x /= norm;
				vec.y /= norm;
			}
		}
		return vec;
	}

	static Point2D perpvector(const Point2D & a, const Point2D & b, bool clockwise = true) {
		if (clockwise) {
			return Point2D(b.y - a.y, a.x - b.x);
		} else {
			return Point2D(a.y - b.y, b.x - a.x);
		}
	}

	// constructors

	Point2D() : x(0), y(0) {}

	Point2D(double x_val, double y_val) : x(x_val), y(y_val) {}

	Point2D(const double vals[]) : x(vals[0]), y(vals[1]) {}

	Point2D(const Point2D& other) : x(other.x), y(other.y) {}


	// instance methods

	Point2D & operator=(const Point2D& other) {
		if (this != &other) {
			x = other.x;
			y = other.y;
		}
		return *this;
	}

	Point2D operator-(const Point2D& other) const {
		return Point2D(x - other.x, y - other.y);
	}

	Point2D operator+(const Point2D& other) const {
		return Point2D(x + other.x, y + other.y);
	}

	// vector operations for points representing vectors

	Point2D & scale(double factor) {
		x *= factor;
		y *= factor;
		return *this;
	}

	double dot(const Point2D& other) const {
		return x * other.x + y * other.y;
	}

	double cross_norm(const Point2D& other) const {
		return x * other.y - y * other.x;
	}

	double rhombus(const Point2D& a, const Point2D& b) const {
		return (a - *this).cross_norm(b - *this);
	}

	bool operator==(const Point2D& other) const {
		return (x == other.x) and (y == other.y);
	}

	bool operator!=(const Point2D& other) const {
		return (x != other.x) or (y != other.y);
	}

	double norm() const {
		return std::sqrt(x * x + y * y);
	}

	double distance_to(const Point2D& other) const {
		return std::sqrt((other.x - x) * (other.x - x) + (other.y - y) * (other.y - y));
	}

	double distance_to(const Point2D & a, const Point2D & b, bool infinite = false) const {
		double d_a_p = this->distance_to(a);
		double d_b_p = this->distance_to(b);
		double d_a_b = a.distance_to(b);
		if (d_a_p == 0 || d_b_p == 0) {
			return 0;
		}
		if (!infinite) {
			if (this->dot(vector(a, b)) <= 0.0 || a == b) {
				return d_a_p;
			}
			if (this->dot(vector(b, a)) <= 0.0) {
				return d_b_p;
			}
		}
		return std::fabs(this->rhombus(a, b)) / d_a_b;
	}

	// conversion operators

	friend std::ostream& operator<<(std::ostream& os, const Point2D& pt) {
		os << "(" << pt.x << ", " << pt.y << ")";
		return os;
	}
};

#endif /* _POINT2D_H_ */
