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

    set<uint64_t> nodes;
    for(auto itr = ggraph.cbegin(); itr != ggraph.end(); ++itr) {
    	nodes.insert(itr->first);
    }

    cout << "nodes (swet of ids) size = " << dec << nodes.size() << endl;

    geopoint start_coord(33.651759, 130.672120);
    geopoint goal_coord(33.644224, 130.693827);
    // find the nearest end-point
    double dist_start = std::numeric_limits<double>::infinity();
    uint64_t id_start = 0;
    double dist_goal = std::numeric_limits<double>::infinity();
    uint64_t id_goal = 0;
    double d;
    for (auto & id : nodes) {
    	const geopoint & pt = ggraph.node(id).point();
    	d = pt.distance_to(start_coord);
    	if (d < dist_start) {
    		dist_start = d;
    		id_start = id;
    		cout << "id_start = " << id_start << " dist_start = " << dist_start << endl;
    	}
    	d = pt.distance_to(goal_coord);
    	if (d < dist_goal) {
    		dist_goal = d;
    		id_goal = id;
    		cout << "id_goal = " << id_goal << " dist_goal = " << dist_goal << endl;
    	}
    }
    cout << "start point = " << ggraph.node(id_start) << " index " << std::dec << id_start << endl;
    cout << "goal point = " << ggraph.node(id_goal) << " index " << std::dec << id_goal << endl;

    set<unsigned long> rem;
    for(unsigned long i = 0; i < nodes.size(); ++i)
    	rem.insert(i);
    double el[nodes.size()];
    for(unsigned long i = 0; i < nodes.size(); ++i) {
    	el[i] = std::numeric_limits<double>::infinity();
    }

    int c = 0;
    el[id_start] = 0;
    while ( rem.size() > 0 ) {
    	double elmin = std::numeric_limits<double>::infinity();
    	unsigned long u = 0;
    	for(const auto & ix : rem) {
    		if (el[ix] < elmin) {
    			u = ix;
    			elmin = el[ix];
    		}
    	}
    	cout << "u = " << u << endl;
    	rem.erase(u);
    	for( const auto & v : ggraph.adjacent_nodes(nodes[u].id()) ) {
    		if ( rem.contains(v) ) {
    			cout << "v = " << v << endl;
    			double dist_uv = nodes[u].point().distance_to(nodes[v].point());
    			if ( el[v] > el[u] + dist_uv ) {
    				el[v] = el[u] + dist_uv;
    			}
    		}
    	}
    	c++;
    	if (c > 100)
    		break;
    	cout << "rem size = " << rem.size() << endl;
    }

    /*
    uint64_t target_id = 772366981;
    cout << "from geopoint " << target_id << " at　coordinate " << ggraph.point(target_id) << endl;
    for(auto itr = ggraph.adjacent_nodes(target_id).cbegin();
    		itr != ggraph.adjacent_nodes(target_id).cend(); ++itr) {
    	cout << "distance to " << dec << *itr << ": " << ggraph.point(target_id).distance_to(ggraph.point(*itr)) << endl;
    }
    cout << endl;
*/
    return EXIT_SUCCESS;
}
