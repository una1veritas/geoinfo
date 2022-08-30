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
#include <set>
#include <map>
#include <iomanip>
#include <algorithm>

#include <stdexcept>
#include <cinttypes>

using std::pair;
using std::vector;
using std::cout;
using std::endl;

#include "bgeohash.h"
#include "geograph.h"
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



int main(const int argc, const char * argv[]) {
	ifstream csvf;

	if (argc != 3) {
		cerr << "usage: command [geograph csv file name] [GPS trajectory csv file name]" << endl;
		exit(EXIT_FAILURE);
	}

	cout << "reading geograph file." << endl;
	csvf.open(argv[1]);
	if (! csvf ) {
		cerr << "open a geograph file " << argv[1] << " failed." << endl;
		exit(EXIT_FAILURE);
	}
	geograph ggraph;
    string line;
    while (getline(csvf, line)) {
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 4) {
        	cerr << "insufficient parameters to define a node_edge." << endl;
        	continue;
        }
		uint64_t id = stoull(strvec[0]);
		double lat = stod(strvec[1]);
		double lon = stod(strvec[2]);
        std::vector<uint64_t> adjacents;
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	adjacents.push_back(stoull(strvec[i]));
        ggraph.insert(id, lat, lon, adjacents);
        adjacents.clear();
    }
    csvf.close();

    /*
    // construct the node table sorted by geohash
    vector<const geograph::geonode *> hash2id;
    for(auto & a_node : ggraph.nodes) {
    	hash2id.push_back(&a_node);
    }
	std::sort(hash2id.begin(), hash2id.end(), [ ](const geograph::geonode * a, const geograph::geonode * b) { return a->geohash < b->geohash; }
	);
	*/

	// show some entry
    int count = 0;
    for(const auto & a_pair : ggraph.nodes) {
    	cout << a_pair.first << endl;
    	count += 1;
    	if (count > 100) {
    		cout << "..." << endl;
    		break;
    	}
    }
    cout << endl;

    cout << "goegraph size = " << ggraph.size() << endl;

    cout << "reading GPS trajectory file." << endl;
	csvf.open(argv[2]);
	if (! csvf ) {
		cerr << "open a tracked-points file " << argv[2] << " failed." << endl;
		exit(EXIT_FAILURE);
	}
	vector<geopoint> mytrack;
    while (getline(csvf, line)) {
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 2) {
        	cerr << "insufficient parameters for a point." << endl;
        	continue;
        }
        mytrack.push_back(geopoint(stod(strvec[2]), stod(strvec[3])));
    }
    csvf.close();

    // collect points on the map along with the points in the GPS trajectory.
    for(unsigned int i = 0; i < mytrack.size(); ++i) {
    	binarygeohash gid = binarygeohash(mytrack[i].lat, mytrack[i].lon,37);
    	unsigned int countgp;
    	std::pair<uint64_t,uint64_t> range;
    	unsigned int z;
    	cout << mytrack[i] << " ";
    	for(z = 0; z < 2; ++z) {
			vector<binarygeohash> vec = gid.neighbors(z);
			cout << vec.size() << " ";
			countgp = 0;

			std::set<std::pair<uint64_t,uint64_t>> edges;
			for(const binarygeohash & ghash : vec) {
				// binary search algorithm std::range
				for(auto & a_node : ggraph.geohash_range(ghash)) {
					edges.merge(ggraph.adjacent_edges(a_node.id()));
				}
			}
			countgp = edges.size();
			edges.clear();
			/*
			if (countgp > 0)
				break;
			*/
    	}
    	cout << dec << countgp << endl;
    }
    cout << "finished." << endl;

    return EXIT_SUCCESS;
}