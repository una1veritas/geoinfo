//============================================================================
// Name        : geograph.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <iomanip>
#include <algorithm>


using namespace std;

vector<string> split(string& input, char delimiter) {
    istringstream stream(input);
    string field;
    vector<string> result;
    while (getline(stream, field, delimiter)) {
        result.push_back(field);
    }
    return result;
}

struct node_edge {
	unsigned long id;
	double lat, lon;
	vector<unsigned long> adjacents;

	node_edge(const vector<string> & strvec) {
		id = strtol(strvec[0].c_str(), NULL, 10);
		lat = strtod(strvec[1].c_str(), NULL);
		lon = strtod(strvec[2].c_str(), NULL);
		for(unsigned i = 3; i < strvec.size(); ++i) {
			adjacents.push_back(strtol(strvec[i].c_str(), NULL, 10));
		}
	}

	friend ostream & operator<<(ostream & out, const node_edge & ne) {
		out << ne.id << " (" << setprecision(10) << ne.lat << ","
				<< setprecision(10) << ne.lon << "), ";
		out << "{";
		for(unsigned int i = 0; i+1 < ne.adjacents.size(); ++i) {
			out << ne.adjacents[i] << ", ";
		}
		out << ne.adjacents[ne.adjacents.size() -1] << "} ";
		return out;
	}
};

struct geohash {
	static constexpr double MAX_LAT = 90.0;
	static constexpr double MIN_LAT = -90.0;
	static constexpr double MAX_LONG = 180.0;
	static constexpr double MIN_LONG = -180.0;
	static constexpr char char_map[] = "0123456789bcdefghjkmnpqrstuvwxyz";
	static constexpr int bz_map[] = {
			10, 11, 12, 13, 14, 15, 16, -1,
			17, 18, -1,
			19, 20, -1,
			21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
	};

	struct interval {
		double high, low;

		interval(const double &hi, const double &lo) :
				high(hi), low(lo) {
		}
	};

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

	static string encode(double lat, double lng, int precision = 8) {
		static char hash[12];
		if (precision < 1 || precision > 12)
			precision = 6;
		if (lat <= 90.0 && lat >= -90.0 && lng <= 180.0 && lng >= -180.0) {
			hash[precision] = '\0';

			precision *= 5.0;

			interval lat_interval(MAX_LAT, MIN_LAT);
			interval lng_interval(geohash::MAX_LONG, MIN_LONG);

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

	struct coordbox {
	    double n;
	    double e;
	    double s;
	    double w;
	};

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
};


int main(const int argc, const char * argv[]) {
	ifstream csvf;

	if (argc <= 1) {
		cerr << "arg as a file name needed." << endl;
		exit(EXIT_FAILURE);
	}
	csvf.open(argv[1]);
	if (! csvf ) {
		cerr << "open " << argv[1] << " failed." << endl;
		exit(EXIT_FAILURE);
	}

	vector<node_edge> ggraph;
    string line;
    while (getline(csvf, line)) {
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 4) {
        	cerr << "insufficient parameters for a node_edge." << endl;
        	continue;
        }
        ggraph.push_back(node_edge(strvec));
    }

    unsigned degree = 0;
    cout << ggraph.size() << " nodes." << endl;
    for(unsigned int i = 0; i < ggraph.size(); ++i) {
    	if (i < min((unsigned) 12, (const unsigned) ggraph.size()) ) {
    		cout << geohash::encode(ggraph[i].lat, ggraph[i].lon, 9) << " ";
    		cout << ggraph[i] << endl;
    	}
    	if (degree < ggraph[i].adjacents.size()) {
    		degree = ggraph[i].adjacents.size();
    	}
    }
    cout << "max. degree is " << degree << "." << endl;
    geohash::coordbox coord = geohash::decode("wvuxn178z");
    cout << coord.s << ", " << coord.n << ", " << coord.w << ", " << coord.e << endl;
    cout << coord.n - (coord.n - coord.s)/2 << ", " << coord.e - (coord.e - coord.w)/2 << endl;
    return EXIT_SUCCESS;
}
