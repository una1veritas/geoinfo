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

#include <limits>

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

    set<uint64_t> vertices;  // the set of OSM IDs.
    for(auto itr = ggraph.cbegin(); itr != ggraph.end(); ++itr) {
    	vertices.insert(itr->first);
    }

    cout << "vertices size = " << dec << vertices.size() << endl;

    geopoint start_coord(33.651759, 130.672120);
    geopoint goal_coord(33.644224, 130.693827);

    // find the nearest points corresponds to the start and the goal.
    uint64_t osmid_start = ggraph.node_nearest_to(start_coord).id();
	uint64_t osmid_goal = ggraph.node_nearest_to(goal_coord).id();
    cout << "start point = " << ggraph.node(osmid_start) << " id " << std::dec << osmid_start << endl;
    cout << "goal point = " << ggraph.node(osmid_goal) << " id " << std::dec << osmid_goal << endl;

    // Dijkstra's algorithm to compute the length of shortest path to the nodes
    //
    // use vertices as the set (V - P) of remained (still not visited) vertices.
    // label (mapping) from vertices to the distance of the shortest path.
    map<uint64_t, double> el;
    for(const auto & osmid : vertices) {
    	el[osmid] = std::numeric_limits<double>::infinity();  // initialize as +infinity
    }

    //int c = 0;
    el[osmid_start] = 0;
    while ( vertices.size() > 0 ) {
    	// find the point u to which the path is shortest
    	double elmin = std::numeric_limits<double>::infinity();
    	unsigned long u = 0;
    	for(const auto & osmid : vertices) {
    		if (el[osmid] < elmin) {
    			u = osmid;
    			elmin = el[osmid];
    		}
    	}
    	//cout << "u = " << u << endl;
    	vertices.erase(u);  // the dist. of the shortest path to u is determined.
    	if (u == 0)
    		break; // unreachable points?
    	if (u == osmid_goal)
    		break;
    	// for each point adjacent to u and in vertices
    	for(const auto & v : ggraph.adjacent_nodes(u) ) {
    		if ( vertices.contains(v) ) {  // C++20
    			//cout << "v = " << v << endl;
    			double dist_uv = ggraph.node(u).point().distance_to(ggraph.node(v).point());
    			if ( el[v] > el[u] + dist_uv ) {
    				el[v] = el[u] + dist_uv;
    			}
    		}
    	}
    	//c++;
    	//if (c > 100)
    	//	break;
    	//cout << "vertices size = " << vertices.size() << " determined distance = " << el[u] << endl;
    }

    // find the shortest path from the start to the goal by back-tracking

    vector<uint64_t> path;
    path.push_back(osmid_goal);

    cout << "distance from the start to the goal is " << el[osmid_goal] << endl;
    return EXIT_SUCCESS;
}
