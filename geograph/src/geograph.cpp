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

#include "geohash.h"

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
	unsigned long id;
	double lat, lon;
	string hash;
	vector<unsigned long> adjacents;

	static constexpr int prec = 8;

	node_edge(void) : id(0), lat(0), lon(0), hash(""), adjacents({0}) { }
	node_edge(const string key) : id(0), lat(0), lon(0), hash(key), adjacents({0}) { }

	node_edge(const vector<string> & strvec) {
		id = strtol(strvec[0].c_str(), NULL, 10);
		lat = strtod(strvec[1].c_str(), NULL);
		lon = strtod(strvec[2].c_str(), NULL);
		hash = geohash::encode(lat, lon, prec);
		for(unsigned i = 3; i < strvec.size(); ++i) {
			adjacents.push_back(strtol(strvec[i].c_str(), NULL, 10));
		}
	}

	friend ostream & operator<<(ostream & out, const node_edge & ne) {
		out << setw(10) << ne.id << " " << ne.hash << " "
				<< " (" << fixed << setprecision(7) << ne.lat << ","
				<< setprecision(7) << ne.lon << "), ";
		out << "{";
		for(unsigned int i = 0; i+1 < ne.adjacents.size(); ++i) {
			out << ne.adjacents[i] << ", ";
		}
		out << ne.adjacents[ne.adjacents.size() -1] << "} ";
		return out;
	}
};

int stringcomp(const string & a, const string & b) {
	int l = min(a.length(),b.length());
	return a.substr(0,l) < b.substr(0,l);
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
        node_edge a_node(strvec);
        ggraph.push_back(a_node);
    }
    csvf.close();
    sort(ggraph.begin(), ggraph.end(),
    		[](const node_edge & a, const node_edge & b) { return a.hash < b.hash; }
    		);

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
    	string hash = geohash::encode(mytrack[i].lat, mytrack[i].lon,8);
    	cout << mytrack[i] << ", " << hash << endl;

		node_edge key(hash);
		vector<node_edge>::iterator lb = lower_bound(ggraph.begin(), ggraph.end(),
				key,
				[](const node_edge & a, const node_edge &b){ return stringcomp(a.hash,b.hash); } );
		vector<node_edge>::iterator ub = upper_bound(ggraph.begin(), ggraph.end(),
				key,
				[](const node_edge & a, const node_edge &b){ return stringcomp(a.hash,b.hash); } );
		unsigned int countp = ub - lb;
		cout << countp << " points." << endl;
		if (countp == 0) {
			//key.hash = hash.substr(0,hash.length() - 1);
			for(int i = geohash::NORTH; i <= geohash::NORTHWEST; ++i) {
				key.hash = geohash::neighbor(hash, i);
				lb = lower_bound(ggraph.begin(), ggraph.end(), key,
						[](const node_edge & a, const node_edge &b){ return stringcomp(a.hash,b.hash); } );
				ub = upper_bound(ggraph.begin(), ggraph.end(), key,
						[](const node_edge & a, const node_edge &b){ return stringcomp(a.hash,b.hash); } );
				cout << key.hash << " " << (ub - lb) << ", ";
			}
			cout << endl;
		}
    }

    return EXIT_SUCCESS;
}
