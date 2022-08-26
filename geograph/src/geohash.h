/*
 * geohash.h
 *
 *  Created on: 2022/03/21
 *      Author: Sin Shimozono
 *
 *   c++14 or later
 */

#ifndef GEOHASH_H_
#define GEOHASH_H_

#include <iostream>
#include <string>
#include <vector>

using namespace std;

namespace geohash {
	static constexpr double MAX_LAT = 90.0;
	static constexpr double MIN_LAT = -90.0;
	static constexpr double MAX_LONG = 180.0;
	static constexpr double MIN_LONG = -180.0;
	static constexpr char * char_map = (char *) "0123456789bcdefghjkmnpqrstuvwxyz";
	static constexpr int bz_map[] = {
			10, 11, 12, 13, 14, 15, 16, -1,
			17, 18, -1,
			19, 20, -1,
			21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
	};

	/*
	 *  The follow character maps were created by Dave Troy and used in his Javascript Geohashing
	 *  library. http://github.com/davetroy/geohash-js
	 */
	static constexpr char *even_neighbors[] = {
			(char *) "p0r21436x8zb9dcf5h7kjnmqesgutwvy",
			(char *) "bc01fg45238967deuvhjyznpkmstqrwx",
			(char *) "14365h7k9dcfesgujnmqp0r2twvyx8zb",
			(char *) "238967debc01fg45kmstqrwxuvhjyznp"
	};

	static constexpr char *odd_neighbors[] = {
			(char *) "bc01fg45238967deuvhjyznpkmstqrwx",
			(char *) "p0r21436x8zb9dcf5h7kjnmqesgutwvy",
			(char *) "238967debc01fg45kmstqrwxuvhjyznp",
			(char *) "14365h7k9dcfesgujnmqp0r2twvyx8zb"
	};

	static constexpr char *even_borders[] = {(char *) "prxz", (char *) "bcfguvyz", (char *) "028b", (char *) "0145hjnp"};
	static constexpr char *odd_borders[] = {(char *) "bcfguvyz", (char *) "prxz", (char *) "0145hjnp", (char *) "028b"};

	static int char_revmap(const char c) {
		int result = -1;
		if (c < '9' + 1) {
			//"0123456789"
			result = c - '0';
		} else if (c < 'z' + 1) {
			result = bz_map[c - 'b'];
		}
		if (result < 0)
			return -1;
		return result;
	}

	static int index(const char c, const string & str) {
	    for(unsigned int i = 0; i < str.length(); i++) {
	        if (c == str[i])
	        	return i;
	    }
	    return -1;
	}

	struct interval {
		double high, low;

		interval(const double &hi, const double &lo) :
				high(hi), low(lo) {
		}
	};


	struct coordbox {
	    double n;
	    double e;
	    double s;
	    double w;

	    double center_lat() const {
	    	return n - (n-s)/2.0;
	    }

	    double center_lon() const {
	    	return e - (e-w)/2.0;
	    }

	    friend ostream & operator<<(ostream & out, const coordbox & box) {
	    	out << "(s: " << box.s << ", n: " << box.n
	    			<< ", w: " << box.w << ", e: " << box.e << ") ";
	    	return out;
	    }
	};

	static string bincode(const string & hash) {
		string binary;
		for(unsigned int pos = 0; pos < hash.length(); ++pos) {
			int val = char_revmap(hash[pos]);
			if (val < 0) break;
			for(unsigned int i = 0; i < 5; ++i) {
				binary += (val & 0x10) ? "1" : "0";
				val <<= 1;
			}
		}
		return binary;
	}

	static string encode(const double & lat, const double & lng, int precision = 8) {
		static char hash[12];
		if (precision < 1 || precision > 12)
			precision = 6;
		if (lat <= 90.0 && lat >= -90.0 && lng <= 180.0 && lng >= -180.0) {
			hash[precision] = '\0';

			precision *= 5.0;

			interval lat_interval(MAX_LAT, MIN_LAT);
			interval lng_interval(MAX_LONG, MIN_LONG);

			interval *intv;
			double coord, mid;
			int is_even = 1;
			unsigned int hashChar = 0;
			int i;
			for (i = 1; i <= precision; i++) {
				if (is_even) {
					intv = &lng_interval;
					coord = lng;
				} else {
					intv = &lat_interval;
					coord = lat;
				}
				mid = (intv->low + intv->high) / 2.0;
				hashChar = hashChar << 1;
				if (coord > mid) {
					intv->low = mid;
					hashChar |= 0x01;
				} else
					intv->high = mid;

				if (!(i % 5)) {
					hash[(i - 1) / 5] = char_map[hashChar];
					hashChar = 0;
				}
				is_even = !is_even;
			}
		} else {
			hash[0] = '\0';
		}
		return string(hash);
	}

	static coordbox decode(const string & hash) {
		coordbox box = { 0.0, 0.0, 0.0, 0.0 };

		if (hash.length() > 0) {
			unsigned int char_mapIndex;
			interval lat_interval = { MAX_LAT, MIN_LAT };
			interval lng_interval = { MAX_LONG, MIN_LONG };
			interval *intv;

			int is_even = 1;
			double delta;
			unsigned int i, j;
			for (i = 0; i < hash.length(); i++) {
				char_mapIndex = geohash::char_revmap(hash[i]);
				if (char_mapIndex < 0)
					break;
				// Interpret the last 5 bits of the integer
				for (j = 0; j < 5; j++) {
					intv = is_even ? &lng_interval : &lat_interval;
					delta = (intv->high - intv->low) / 2.0;
					if ((char_mapIndex << j) & 0x0010)
						intv->low += delta;
					else
						intv->high -= delta;

					is_even = !is_even;
				}
			}
			box.n = lat_interval.high;
			box.e = lng_interval.high;
			box.s = lat_interval.low;
			box.w = lng_interval.low;
		}
		return box;
	}

	enum {
		NORTH 		= 0,
		NORTHEAST 	= 1,
		EAST  		= 2,
		SOUTHEAST 	= 3,
		SOUTH 		= 4,
		SOUTHWEST 	= 5,
		WEST  		= 6,
		NORTHWEST 	= 7,
		DIRECTION_END = 8,
	};

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

};

#endif /* GEOHASH_H_ */
