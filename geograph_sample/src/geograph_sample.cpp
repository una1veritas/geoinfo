//============================================================================
// Name        : geograph_sample.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <fstream>
#include <iomanip>
#include <map>
#include <set>

#include "geograph.h"
#include "bgeohash.h"

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

int main(int argc, char * argv[]) {
	ifstream csvf;

	if (argc < 2) {
		cerr << "usage: command map-file_name]" << endl;
		exit(EXIT_FAILURE);
	}

	cout << "reading geograph file " << argv[1] << ". " << endl;
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
        vector<uint64_t> adjacents;
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	adjacents.push_back(stoull(strvec[i]));
        ggraph.insert(id, lat, lon, adjacents);
        adjacents.clear();
    }
    csvf.close();

    cout << "goegraph node size = " << dec << ggraph.size() << endl;

	// show some entries.
    int count = 0;
    for(auto itr = ggraph.cbegin(); itr != ggraph.cend(); ++itr) {
    	uint64_t id = itr->first;
    	geograph::geonode node = itr->second;
    	cout << "id " << dec << id << " node " << node << endl;
    	count += 1;
    	if (count > 100) {
    		cout << "..." << endl;
    		break;
    	}
    }
    cout << endl;

    uint64_t target_id = 772366981;
    cout << "from geopoint " << target_id << " at　coordinate " << ggraph.point(target_id) << endl;
    for(auto itr = ggraph.adjacent_nodes(target_id).cbegin();
    		itr != ggraph.adjacent_nodes(target_id).cend(); ++itr) {
    	cout << "distance to " << dec << *itr << ": " << ggraph.point(target_id).distance_to(ggraph.point(*itr)) << endl;
    }
    cout << endl;

    return EXIT_SUCCESS;
}
