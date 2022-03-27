/*
 * geonumber.h
 *
 *  Created on: 2022/03/21
 *      Author: Sin Shimozono
 *
 *   c++14 or later
 */

#ifndef GEONUMBER_H_
#define GEONUMBER_H_

#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <cinttypes>

using namespace std;

struct geonumber {
	uint64_t number;

	geonumber(void) : number(0) {}
	geonumber(uint64_t num) : number(num) {}
	geonumber(const geonumber & num) : number(num.number) {}

	// encode
	geonumber(const double &lat, const double &lon,	const unsigned int &precision = 20) {
		number = 0;
		if (lat <= 90.0 && lat >= -90.0 && lon <= 180.0 && lon >= -180.0) {
			coordbox interval(MAX_LAT, MIN_LAT, MAX_LONG, MIN_LONG);

			double latmid, lonmid;
			uint64_t bit = uint64_t(1)<<63;
			for (unsigned int i = 0; i < precision; i++) {
				latmid = (interval.s + interval.n) / 2.0;
				lonmid = (interval.w + interval.e) / 2.0;
				if (lat > latmid) {
					interval.s = latmid;
					number |= bit;
				} else {
					interval.n = latmid;
				}
				bit >>= 1; //number <<= 1;
				if (lon > lonmid) {
					interval.w = lonmid;
					number |= bit;
				} else {
					interval.e = lonmid;
				}
				bit >>= 1; //number <<= 1;
			}
		}
		number |= uint64_t(precision & 0xff);
	}

	inline unsigned int precision(void) const {
		return number & 0xff;
	}

	operator uint64_t() const {
		return number;
	}

	friend ostream & operator<<(ostream & out, const geonumber & num) {
		int d = (num.precision()) / 8 + (num.precision() % 8 ? 1 : 0);
		out << hex << setw(d*2) << setfill('0') << (num.number>>(64 - 2*num.precision()));
		return out;
	}

	friend bool operator<(const geonumber & a, const geonumber & b) {
		unsigned int prec = min(a.precision(), b.precision());
		uint64_t mask = 0xffffffffffffffff << (64 - 2*prec);
		return (a.number & mask) < (b.number & mask);
	}

	static constexpr double MAX_LAT = 90.0;
	static constexpr double MIN_LAT = -90.0;
	static constexpr double MAX_LONG = 180.0;
	static constexpr double MIN_LONG = -180.0;

	/*
	struct interval {
		double high, low;

		interval(const double &hi, const double &lo) :
				high(hi), low(lo) {
		}
	};
	*/

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

		double center_lat() const {
			return n - (n - s) / 2.0;
		}

		double center_lon() const {
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

	/*
	static string bincode(const string &hash) {
		string binary;
		for (unsigned int pos = 0; pos < hash.length(); ++pos) {
			int val = char_revmap(hash[pos]);
			if (val < 0)
				break;
			for (unsigned int i = 0; i < 5; ++i) {
				binary += (val & 0x10) ? "1" : "0";
				val <<= 1;
			}
		}
		return binary;
	}
	*/

	coordbox decode(void) const {
		coordbox interval(MAX_LAT, MIN_LAT, MAX_LONG, MIN_LONG);
		unsigned int precision = number & 0xff;
		uint64_t location = number & 0xffffffffffffff00;

		if (number > 0) {
			double delta;
			uint64_t checkbit = uint64_t(1)<<63;
			for (unsigned int i = 0; i < precision; i++) {
				delta = (interval.n - interval.s) / 2.0;
				if ((location & checkbit) != 0)
					interval.s += delta;
				else
					interval.n -= delta;
				checkbit >>= 1;
				delta = (interval.e - interval.w) / 2.0;
				if ((location & checkbit) != 0)
					interval.w += delta;
				else
					interval.e -= delta;
				checkbit >>= 1;
			}
		}
		return interval;
	}

	enum {
		NORTH = 0,
		NORTHEAST = 1,
		EAST = 2,
		SOUTHEAST = 3,
		SOUTH = 4,
		SOUTHWEST = 5,
		WEST = 6,
		NORTHWEST = 7,
		DIRECTION_END = 8,
	};

	/*
	static vector<string> neighbors(const string & hash, const int zone) {
		vector<string> codes;
		if (zone < 1) {
			codes.push_back(hash);
			return codes;
		}
		coordbox box = decode(hash);
		int prec = hash.length();
		double width = box.e - box.w;
		double height = box.n - box.s;
		double lat = box.n - height/2.0;
		double lon = box.e - width/2.0;
		//cout << "center: " << lat << ", " << lon << "; ";
		int side = 2*zone + 1;
		int inner = 2*(zone - 1) + 1;
		// starts from upper left
		double gplat = lat + zone*height, gplon = lon - zone*width;
		int mvdir;
		for(int i = inner*inner; i < side*side; ++i) {
			codes.push_back(encode(gplat, gplon, prec));
			mvdir = ((i-inner*inner)/(side-1)) % 4 ;
			//cout << i << " " << mvdir << ": " << gplat << ", " << gplon << "; ";
			switch(mvdir) {
			case 0: // r
				gplon += width;
				break;
			case 1: // d
				gplat -= height;
				break;
			case 2: // l
				gplon -= width;
				break;
			case 3: // u
				gplat += height;
			}
			if (gplon >= 180.0) {
				gplon = -(gplon -360.0);
			}
			if ( gplon < -180.0) {
				gplon += 360.0;
			}
		}
		//cout << endl;
		return codes;
	}
	*/

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

#endif /* GEONUMBER_H_ */
