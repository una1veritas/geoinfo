/*
 * geobinary.h
 *
 *  Created on: 2022/03/21
 *      Author: Sin Shimozono
 *
 *   c++14 or later
 */

#ifndef GEOBINARY_H_
#define GEOBINARY_H_

#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <cinttypes>

using namespace std;

struct geobinary {
private:
	uint64_t id;

	static constexpr double MAX_LAT = 90.0;
	static constexpr double MIN_LAT = -90.0;
	static constexpr double MAX_LONG = 180.0;
	static constexpr double MIN_LONG = -180.0;

public:
	geobinary(void) : id(0) {}

	geobinary(const uint64_t & num) {
		unsigned int prec = num & 0xff;
		prec = (prec < 28 ? prec : 28);
		id = (num & (0xffffffffffffffff << (64 - prec*2))) | prec;
	}

	geobinary(const uint64_t & num, unsigned int prec) {
		prec = (prec < 28 ? prec : 28);
		id = (num & (0xffffffffffffffff << (64 - prec*2))) | (prec & 0xff);
	}

	geobinary(const geobinary & gb) : id(gb.id) {}

	// encode
	geobinary(const double &lat, const double &lon,	const unsigned int & precision = 20) {
		id = 0;
		unsigned int prec = (precision < 28 ? precision : 28);
		if (lat <= 90.0 && lat >= -90.0 && lon <= 180.0 && lon >= -180.0) {
			coordbox interval(MAX_LAT, MIN_LAT, MAX_LONG, MIN_LONG);

			double latmid, lonmid;
			uint64_t bit = uint64_t(1)<<63;
			for (unsigned int i = 0; i < precision; i++) {
				latmid = (interval.s + interval.n) / 2.0;
				lonmid = (interval.w + interval.e) / 2.0;
				if (lat > latmid) {
					interval.s = latmid;
					id |= bit;
				} else {
					interval.n = latmid;
				}
				bit >>= 1;
				if (lon > lonmid) {
					interval.w = lonmid;
					id |= bit;
				} else {
					interval.e = lonmid;
				}
				bit >>= 1;
			}
		}
		id |= uint64_t(prec);
	}

	inline unsigned int precision(void) const {
		return id & 0xff;
	}

	inline uint64_t location(void) const {
		return id & 0xffffffffffffff00;
	}

	unsigned int set_precision(unsigned int prec) {
		prec = (prec < 28 ? prec : 28);
		id &= 0xffffffffffffffff << (64 - prec*2);
		id |= prec;
		return prec;
	}

	operator uint64_t() const {
		return id;
	}

	friend ostream & operator<<(ostream & out, const geobinary & num) {
		out << hex << setw(16) << setfill('0') << num.id;
		return out;
	}

	friend bool operator<(const geobinary & a, const geobinary & b) {
		unsigned int prec = min(a.precision(), b.precision());
		uint64_t mask = 0xffffffffffffffff << (64 - 2*prec);
		if ( (a.id & mask) == (b.id & mask) ) {
			return a.precision() < b.precision();
		}
		return (a.id & mask) < (b.id & mask);
	}


	struct coordbox {
		double n;
		double s;
		double e;
		double w;

		coordbox(void) : n(0), s(0), e(0), w(0) {}
		coordbox(const double & lathigh, const double & latlow, const double & lonhigh, const double & lonlow) {
			n = lathigh;
			s = latlow;
			e = lonhigh;
			w = lonlow;
		}

		double lat_center() const {
			return n - (n - s) / 2.0;
		}

		double lon_center() const {
			return e - (e - w) / 2.0;
		}

		bool covers(const double & lat, const double & lon) const {
			return (lat < n && lat >= s) && (lon < e && lon >= w);
		}

		friend ostream& operator<<(ostream &out, const coordbox &box) {
			out << "(s: " << box.s << ", n: " << box.n << ", w: " << box.w
					<< ", e: " << box.e << ") ";
			return out;
		}
	};

	coordbox decode(void) const {
		coordbox interval(MAX_LAT, MIN_LAT, MAX_LONG, MIN_LONG);

		if (id > 0) {
			double delta;
			uint64_t checkbit = uint64_t(1)<<63;
			for (unsigned int i = 0; i < precision(); i++) {
				delta = (interval.n - interval.s) / 2.0;
				if ((id & checkbit) != 0)
					interval.s += delta;
				else
					interval.n -= delta;
				checkbit >>= 1;
				delta = (interval.e - interval.w) / 2.0;
				if ((id & checkbit) != 0)
					interval.w += delta;
				else
					interval.e -= delta;
				checkbit >>= 1;
			}
		}
		return interval;
	}

	geobinary north_side() const {
		geobinary g(*this);
		uint64_t uintval = 2<<(64 - 2 * precision());
		uint64_t latbits = g.id & 0xaaaaaaaaaaaaaa00;
		uint64_t lonbits = g.id & 0x5555555555555500;
		g.id = (latbits | 0x5555555555555500) + uintval;
		g.id &= 0xaaaaaaaaaaaaaa00;
		g.id |= lonbits;
		g.id |= precision();
		return g;
	}

	geobinary south_side() const {
		geobinary g(*this);
		uint64_t uintval = 2<<(64 - 2 * precision());
		uint64_t latbits = g.id & 0xaaaaaaaaaaaaaa00;
		uint64_t lonbits = g.id & 0x5555555555555500;
		g.id = latbits - uintval;
		g.id &= 0xaaaaaaaaaaaaaa00;
		g.id |= lonbits;
		g.id |= precision();
		return g;
	}

	geobinary east_side() const {
		geobinary g(*this);
		uint64_t uintval = 1<<(64 - 2 * precision());
		uint64_t latbits = g.id & 0xaaaaaaaaaaaaaa00;
		uint64_t lonbits = g.id & 0x5555555555555500;
		g.id = (lonbits | 0xaaaaaaaaaaaaaa00) + uintval;
		g.id &= 0x5555555555555500;
		g.id |= latbits;
		g.id |= precision();
		return g;
	}

	geobinary west_side() const {
		geobinary g(*this);
		uint64_t uintval = 1<<(64 - 2 * precision());
		uint64_t latbits = g.id & 0xaaaaaaaaaaaaaa00;
		uint64_t lonbits = g.id & 0x5555555555555500;
		g.id = lonbits - uintval;
		g.id &= 0x5555555555555500;
		g.id |= latbits;
		g.id |= precision();
		return g;
	}
	vector<geobinary> neighbors(const int zone) const {
		vector<geobinary> neighbors;
		if (zone == 0) {
			neighbors.push_back(*this);
			return neighbors;
		}
		geobinary current(*this);
		//cout << "center: " << lat << ", " << lon << "; ";
		int side = 2*zone + 1;
		int inner = 2*(zone - 1) + 1;
		// starts from upper left
		int mvdir;
		for(int i = 0; i < zone; ++i) {
			current = current.north_side();
			current = current.west_side();
		}
		for(int i = inner*inner; i < side*side; ++i) {
			neighbors.push_back(current);
			mvdir = ((i-inner*inner)/(side-1)) % 4 ;
			//cout << i << " " << mvdir << ": " << gplat << ", " << gplon << "; ";
			switch(mvdir) {
			case 0: // r
				current = current.east_side();
				break;
			case 1: // d
				current = current.south_side();
				break;
			case 2: // l
				current = current.west_side();
				break;
			case 3: // u
				current = current.north_side();
			}
		}
		//cout << endl;
		return neighbors;
	}

//	static string get_neighbor(const string & hash, int direction) {
//		char last_char = hash[hash.length() - 1];
//
//	    int is_odd = hash.length() % 2;
//	    char * const *border = is_odd ? odd_borders : even_borders;
//	    char * const *neighbor = is_odd ? odd_neighbors : even_neighbors;
//
//	    string base(hash, hash.length() - 1);
//
//		if(index(last_char, border[direction]) != -1)
//			base = get_neighbor(base, direction);
//
//	    int neighbor_index = index(last_char, neighbor[direction]);
//	    last_char = char_map[neighbor_index];
//		return base + last_char;
//	}
};

#endif /* GEOBINARY_H_ */
