#ifndef _GPSPOINT_H_
#define _GPSPOINT_H_

#define _USE_MATH_DEFINES
#include <iostream>
#include <iomanip>

#include <cmath>
#include <vector>
#include <algorithm>

/* Symbols for debug switches */
//#define SHOW_TABLE
/* light-weight functions by MACRO */

#define DEG2RAD(x)  ((M_PI / 180.0) * (x))
#define ABS(x)  ((x) >= 0 ? (x) : -(x))
#define MAX_AMONG3(x, y, z)  ((x) > (y) ? ((x) > (z) ? (x) : (z)): ((y) > (z) ? (y) : (z)))
#define MIN(x, y)  ((y) < (x) ? (y) : (x))

struct gpspoint {
	double time, lat, lon;

private:
	constexpr static double epsilon = 1.0e-8;

	struct metvector {
		double x, y;

		metvector(const gpspoint & a, const gpspoint & b) {
			x = a.distanceTo(gpspoint(0, a.lat, b.lon));
			if (a.lon > b.lon) x = -x;
			y = a.distanceTo(gpspoint(0, b.lat, a.lon));
			if (a.lat > b.lat) y = -y;
		}
	};

	/*
	friend bool operator ==(const gpspoint &p, const gpspoint &q) {
		// emulate by ``take maximum'' norm.
		if ( abs(p.lat - q.lat) < gpspoint::epsilon
				&& abs(p.lon - q.lon) < gpspoint::epsilon )
			return true;
		return false;
	}

	friend gpspoint operator -(const gpspoint &p, const gpspoint &q) {
		return gpspoint(p.time - q.time, p.lat - q.lat, p.lon - q.lon);
	}

	gpspoint operator-(void) {
		return gpspoint(-this->time, -this->lat, -this->lon);
	}
	*/

	static double inner_prod(const gpspoint & a, const gpspoint & b, const gpspoint & c) {
		metvector ab(a,b), ac(a,c);
		//std::cout << "(" << ab.x << ", " << ab.y << ") * (" << ac.x << ", " << ac.y << ") " << std::endl;
		return (ab.x * ac.x) + (ab.y * ac.y);
	}

	static double norm_outer_prod(const gpspoint & a, const gpspoint & b,
			const gpspoint & c) {
		metvector ab(a, b), ac(a, c);
		return (ab.x * ac.y) - (ab.y * ac.x);
	}

	struct dptable {
		struct triplet {
			uint16_t lp, ql, qp;

			triplet & clear(const uint16_t & val = 0) {
				lp = val; ql = val; qp = 0;
				return *this;
			}
		};

		std::vector<triplet *> rows;
		uint16_t column_size;

		dptable(uint16_t r, uint16_t c) {
			column_size = c;
			rows.resize(r);
			for(uint16_t i = 0; i < rows.size(); ++i)
				rows[i] = new triplet[column_size];
		}

		~dptable() {
			for(uint16_t i = 0; i < rows.size(); ++i)
				delete [] rows[i];
		}

		triplet & operator()(const uint16_t & row, const uint16_t col) {
			return rows[row][col];
		}
	};

public:
	gpspoint(const double &t, const double &la, const double &lo) :
			time(t), lat(la), lon(lo) {
	}

	double distanceTo(const gpspoint &q) const;
	double distanceTo(const gpspoint &q1, const gpspoint &q2) const;

//	typedef std::pair<unsigned int, unsigned int> uintpair;
	static std::vector<std::pair<float,float>> lcs(std::vector<gpspoint> &pseq, std::vector<gpspoint> &qseq,const double &bound = 50.0);
//	static std::pair<int, std::vector<uintpair>> lcs1(std::vector<gpspoint> &pseq, std::vector<gpspoint> &qseq,const double &bound = 50.0);

	friend std::ostream & operator<<(std::ostream & os, const gpspoint & p) {
		os << "[" << std::fixed << std::setprecision(6) << p.time << ", " << p.lat << ", " << p.lon << "] ";
		return os;
	}
};

#endif /* _GPSPOINT_H_ */
