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
#include <vector>
#include <iomanip>
#include <algorithm>

#include <stdexcept>
#include <cinttypes>

using namespace std;

#include "geoid.h"
//#include <cmath>
//#include "geodistance.h"

vector<string> split(string& input, char delimiter) {
    istringstream stream(input);
    string field;
    vector<string> result;
    while (getline(stream, field, delimiter)) {
        result.push_back(field);
    }
    return result;
}

struct geopoint {
	double lat, lon;

	geopoint(const double & lattitude, const double & longitude) :lat(lattitude), lon(longitude) { }
	geopoint(const string & latstr, const string & lonstr) {
		lat = strtod(latstr.c_str(), NULL);
		lon = strtod(lonstr.c_str(), NULL);
	}

	friend ostream & operator<<(ostream & out, const geopoint & p) {
		out << " (" << fixed << setprecision(7) << p.lat << ","
				<< setprecision(7) << p.lon << ") ";
		return out;
	}
};

struct node_edge {
	uint64_t id;
	double lat, lon;
	geoid gid;
	vector<uint64_t> adjacents;

	static constexpr int prec = 20;

	node_edge(void) : id(0), lat(0), lon(0), gid(0), adjacents({}) { }
	node_edge(const geoid & gid) : id(0), lat(0), lon(0), gid(gid), adjacents({}) { }

	node_edge(const uint64_t & id, const double & latitude, const double & longitude)
	: id(id), lat(latitude), lon(longitude), adjacents({}) {
		gid = geoid(lat, lon, prec);
	}

	friend ostream & operator<<(ostream & out, const node_edge & ne) {
		out << dec << setw(10) << ne.id << " " << ne.gid << " "
				<< " (" << fixed << setprecision(7) << ne.lat << ","
				<< setprecision(7) << ne.lon << "), ";
		out << "{" << dec;
		for(unsigned int i = 0; i+1 < ne.adjacents.size(); ++i) {
			out << ne.adjacents[i] << ", ";
		}
		out << ne.adjacents[ne.adjacents.size() -1] << "} ";
		return out;
	}
};

/*
int stringcomp(const string & a, const string & b) {
	int l = min(a.length(),b.length());
	return a.substr(0,l) < b.substr(0,l);
}
*/

std::pair<int,int> geoid_index(vector<node_edge> & gg, const geoid & id) {
	node_edge key(id);
	vector<node_edge>::iterator lb = lower_bound(gg.begin(), gg.end(),
			key,
			[](const node_edge & a, const node_edge &b){ return a.gid < b.gid; } );
	vector<node_edge>::iterator ub = upper_bound(lb, gg.end(),
			key,
			[](const node_edge & a, const node_edge &b){ return a.gid < b.gid; } );
	return std::pair<int,int>(lb - gg.begin(),ub - gg.begin());
}


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
		uint64_t id = stoull(strvec[0]);
		double lat = stod(strvec[1]);
		double lon = stod(strvec[2]);
        node_edge a_node(id,lat,lon);
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	a_node.adjacents.push_back(stoull(strvec[i]));
        ggraph.push_back(a_node);
    }
    csvf.close();

    sort(ggraph.begin(), ggraph.end(),
    		[](const node_edge & a, const node_edge & b) { return a.gid < b.gid; }
    		);


    int count = 0;
    for(auto i = ggraph.begin(); i != ggraph.end(); ++i) {
    	cout << *i << endl;
    	count += 1;
    	if (count > 100)
    		break;
    }
    cout << endl;


	csvf.open(argv[2]);
	if (! csvf ) {
		cerr << "open " << argv[2] << " failed." << endl;
		exit(EXIT_FAILURE);
	}
	vector<geopoint> mytrack;
    while (getline(csvf, line)) {
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 2) {
        	cerr << "insufficient parameters for a point in my tracking." << endl;
        	continue;
        }
        mytrack.push_back(geopoint(strvec[2], strvec[3]));
    }
    csvf.close();

    /*
    for(unsigned int i = 0; i < mytrack.size(); ++i) {
    	geoid gid = geoid(mytrack[i].lat, mytrack[i].lon,20);
    	unsigned int countgp;
    	pair<int,int> range;
    	unsigned int z;
    	cout << mytrack[i] << " " << gid << " ";
    	for(z = 0; z < 5; ++z) {
			vector<geoid> vec = gid.neighbors(z);
			countgp = 0;
			for(auto i = vec.begin(); i != vec.end(); ++i) {
				node_edge key(*i);
				range = geoid_index(ggraph, *i);
				countgp += range.second - range.first;
				cout << "[" << range.first << ", " << range.second << "], ";
			}
			//cout << endl;
			//geoid::coordbox box = hash.decode();
			//cout << box << " " << box.covers(mytrack[i].lat, mytrack[i].lon) << endl;
			if (countgp > 0)
				break;
    	}
    	//if (countgp < 1 or z > 2 or countgp > 99) {
    	//	cout << mytrack[i] << ", " << hash << ": " << countgp << " points within " << z << endl;
    	//}
    	cout << countgp << endl;
    }
    */

    /*
    int oddbits[] = { 0x0, 0x2, 0x8, 0xa, };
    int evenbits[] = { 0x0, 0x1, 0x4, 0x5, 0x10, 0x11, 0x14, 0x15, };
    int revbits[] = {};

    int oddbit_mask = 0xaa;
    int evenbit_mask = 0x55;
    int evenbit[] = { 0, 1, 4, 5, 0x10, 0x11, 0x14, 0x15, };
    int evenbit_length = 8;
    int oddbit[] = { 0, 2, 8, 0xa, };
    int oddbit_length = 4;
    int revbit[] = {
    		0, 1, 1, -1, 2, 3, -1, -1, 2, -1, 3, -1, -1, -1, -1, -1,
    		4, 5, -1, -1, 6, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1};
    string sample = "wvuxn7df";
    cout << geohash::bincode(sample) << endl;
    int odd = 0, even = 0;
    for(int i = 0; i < sample.length(); ++i) {
    	int c = geohash::char_revmap(sample[i]);
    	if ((i & 1) == 0) {
			even<<= 3;
			even|= revbit[evenbit_mask & c];
			odd <<= 2;
			odd |= revbit[oddbit_mask & c];
    	} else {
			odd <<= 3;
			odd|= revbit[evenbit_mask & c];
			even <<= 2;
			even |= revbit[oddbit_mask & c];
    	}
    }
    cout << "e: " << bitset<32>{even} << " o: " << bitset<32>{odd} << endl;
    */
    cout << sizeof(unsigned long) << ", " << sizeof(unsigned long long) << endl;
    return EXIT_SUCCESS;
}
