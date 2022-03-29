/*
 * geobinary.h
 *
 *  Created on: 2022/03/21
 *      Author: Sin Shimozono
 *
 *   c++14 or later
 */

#ifndef BGEOHASH_H_
#define BGEOHASH_H_

#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <cinttypes>

using namespace std;

struct binarygeohash {
private:
	uint64_t hash;

	static constexpr double MAX_LAT = 90.0;
	static constexpr double MIN_LAT = -90.0;
	static constexpr double MAX_LONG = 180.0;
	static constexpr double MIN_LONG = -180.0;

	static constexpr char * char_map = (char *) "0123456789bcdefghjkmnpqrstuvwxyz";

public:
	binarygeohash(void) : hash(0) {}

	binarygeohash(const uint64_t & num) {
		unsigned int prec = num & 0xff;
		prec = (prec < 28 ? prec : 28);
		hash = (num & (0xffffffffffffffff << (64 - (prec<<1)))) | prec;
	}

	binarygeohash(const uint64_t & num, unsigned int prec) {
		prec = (prec < 28 ? prec : 28);
		hash = (num & (0xffffffffffffffff << (64 - (prec<<1)))) | (prec & 0xff);
	}

	binarygeohash(const binarygeohash & bghash) : hash(bghash.hash) {}

	// encode
	binarygeohash(const double &lat, const double &lon,	const unsigned int & precision = 20) {
		hash = 0;
		unsigned int prec = (precision < 28 ? precision : 28);
		if (lat <= 90.0 && lat >= -90.0 && lon <= 180.0 && lon >= -180.0) {
			coordbox interval(MAX_LAT, MIN_LAT, MAX_LONG, MIN_LONG);

			double latmid, lonmid;
			uint64_t bit = uint64_t(1)<<63;
			for (unsigned int i = 0; i < precision; i++) {
				latmid = (interval.s + interval.n) / 2.0;
				lonmid = (interval.w + interval.e) / 2.0;
				if (lon > lonmid) {
					interval.w = lonmid;
					hash |= bit;
				} else {
					interval.e = lonmid;
				}
				bit >>= 1;
				if (lat > latmid) {
					interval.s = latmid;
					hash |= bit;
				} else {
					interval.n = latmid;
				}
				bit >>= 1;
			}
		}
		hash |= uint64_t(prec);
	}

	inline unsigned int precision(void) const {
		return hash & 0xff;
	}

	inline uint64_t location(void) const {
		return hash & 0xffffffffffffff00;
	}

	unsigned int set_precision(unsigned int prec) {
		prec = (prec < 28 ? prec : 28);
		hash &= 0xffffffffffffffff << (64 - (prec<<1));
		hash |= prec;
		return prec;
	}

	operator uint64_t() const {
		return hash;
	}

	string geohash(void) const {
		string str("");
		uint64_t bit63 = uint64_t(1)<<63;
		uint64_t val = hash & 0xffffffffffffff00;
		unsigned int length = (precision()<<1)/5 + ((precision()<<1) % 5 > 0 ? 1 : 0);
		unsigned int charindex;
		for(unsigned int i = 0; i < length; ++i) {
			charindex = 0;
			for(unsigned int bpos = 0; bpos < 5; ++bpos) {
				charindex <<= 1;
				if ( (bit63 & val) != 0 ) {
					charindex |= 1;
				}
				val <<= 1;
			}
			str += char_map[charindex];

		}
		return str;
	}

	friend ostream & operator<<(ostream & out, const binarygeohash & num) {
		out << hex << setw(16) << setfill('0') << num.hash;
		return out;
	}

	friend bool operator<(const binarygeohash & a, const binarygeohash & b) {
		unsigned int prec = min(a.precision(), b.precision());
		uint64_t mask = 0xffffffffffffffff << (64 - (prec<<1));
		return (a.hash & mask) < (b.hash & mask);
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

		if (hash > 0) {
			double delta;
			uint64_t checkbit = uint64_t(1)<<63;
			for (unsigned int i = 0; i < precision(); i++) {
				delta = (interval.e - interval.w) / 2.0;
				if ((hash & checkbit) != 0)
					interval.w += delta;
				else
					interval.e -= delta;
				checkbit >>= 1;
				delta = (interval.n - interval.s) / 2.0;
				if ((hash & checkbit) != 0)
					interval.s += delta;
				else
					interval.n -= delta;
				checkbit >>= 1;

			}
		}
		return interval;
	}

	binarygeohash north_side() const {
		binarygeohash g(*this);
		uint64_t uintval = 1<<(64 - (precision()<<1));
		uint64_t latbits = g.hash & 0x5555555555555500;
		uint64_t lonbits = g.hash & 0xaaaaaaaaaaaaaa00;
		g.hash = (latbits | 0xaaaaaaaaaaaaaa00) + uintval;
		g.hash &= 0x5555555555555500;
		g.hash |= lonbits;
		g.hash |= precision();
		return g;
	}

	binarygeohash south_side() const {
		binarygeohash g(*this);
		uint64_t uintval = 1<<(64 - (precision()<<1));
		uint64_t latbits = g.hash & 0x5555555555555500;
		uint64_t lonbits = g.hash & 0xaaaaaaaaaaaaaa00;
		g.hash = latbits - uintval;
		g.hash &= 0x5555555555555500;
		g.hash |= lonbits;
		g.hash |= precision();
		return g;
	}

	binarygeohash east_side() const {
		binarygeohash g(*this);
		uint64_t uintval = 2<<(64 - (precision()<<1));
		uint64_t latbits = g.hash & 0x5555555555555500;
		uint64_t lonbits = g.hash & 0xaaaaaaaaaaaaaa00;
		g.hash = (lonbits | 0x5555555555555500) + uintval;
		g.hash &= 0xaaaaaaaaaaaaaa00;
		g.hash |= latbits;
		g.hash |= precision();
		return g;
	}

	binarygeohash west_side() const {
		binarygeohash g(*this);
		uint64_t uintval = 2<<(64 - 2 * precision());
		uint64_t latbits = g.hash & 0x5555555555555500;
		uint64_t lonbits = g.hash & 0xaaaaaaaaaaaaaa00;
		g.hash = lonbits - uintval;
		g.hash &= 0xaaaaaaaaaaaaaa00;
		g.hash |= latbits;
		g.hash |= precision();
		return g;
	}
	vector<binarygeohash> neighbors(const int zone) const {
		vector<binarygeohash> neighbors;
		if (zone == 0) {
			neighbors.push_back(*this);
			return neighbors;
		}
		binarygeohash current(*this);
		//cout << "center: " << lat << ", " << lon << "; ";
		int side = (zone<<1) + 1;
		int inner = ((zone - 1)<<1) + 1;
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

};

#endif /* BGEOHASH_H_ */
