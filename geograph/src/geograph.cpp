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

#include "bgeohash.h"
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
	binarygeohash gbin;
	vector<uint64_t> adjacents;

	static constexpr int prec = 20;

	node_edge(void) : id(0), lat(0), lon(0), gbin(0), adjacents({}) { }
	node_edge(const binarygeohash & gid) : id(0), lat(0), lon(0), gbin(gid), adjacents({}) { }

	node_edge(const uint64_t & id, const double & latitude, const double & longitude)
	: id(id), lat(latitude), lon(longitude), adjacents({}) {
		gbin = binarygeohash(lat, lon, prec);
	}

	friend ostream & operator<<(ostream & out, const node_edge & ne) {
		out << dec << setw(10) << ne.id << " " << ne.gbin << " "
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

std::pair<int,int> geobinary_range(vector<node_edge> & gg, const binarygeohash & gbin) {
	node_edge key(gbin);
	vector<node_edge>::iterator lb = lower_bound(gg.begin(), gg.end(),
			key,
			[](const node_edge & a, const node_edge &b){ return a.gbin < b.gbin; } );
	vector<node_edge>::iterator ub = upper_bound(lb, gg.end(),
			key,
			[](const node_edge & a, const node_edge &b){ return a.gbin < b.gbin; } );
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
    		[](const node_edge & a, const node_edge & b) { return a.gbin < b.gbin; }
    		);


    int count = 0;
    for(auto i = ggraph.begin(); i != ggraph.end(); ++i) {
    	cout << *i << endl;
    	count += 1;
    	if (count > 100)
    		break;
    }
    cout << endl;
    cout << "goegraph size = " << ggraph.size() << endl;

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


    for(unsigned int i = 0; i < mytrack.size(); ++i) {
    	binarygeohash gid = binarygeohash(mytrack[i].lat, mytrack[i].lon,19);
    	unsigned int countgp;
    	pair<uint64_t,uint64_t> range;
    	unsigned int z;
    	cout << mytrack[i] << " ";
    	for(z = 0; z < 5; ++z) {
			vector<binarygeohash> vec = gid.neighbors(z);
			countgp = 0;
			for(auto i = vec.begin(); i != vec.end(); ++i) {
				node_edge key(*i);
				range = geobinary_range(ggraph, *i);
				countgp += range.second - range.first;
				cout << *i << " "; // << " [" << dec << range.first << ", " << range.second << ") ";
			}
			if (countgp > 0)
				break;
    	}
    	cout << dec << countgp << endl;
    }

    return EXIT_SUCCESS;
}
