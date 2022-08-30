//============================================================================
// Name        : geograph.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
//#include <fstream>
//#include <string>
#include <vector>
#include <set>
#include <map>
#include <iomanip>
#include <algorithm>

//#include <stdexcept>
//#include <cinttypes>

using std::pair;
using std::vector;
using std::cout;
using std::endl;

#include "bgeohash.h"
#include "geograph.h"


void geograph::insert(const uint64_t & id, const double & lat, const double & lon, const vector<uint64_t> & alist) {
	nodes[id] = geonode(id,lat,lon);
	if (adjacents.find(id) == adjacents.end()) {
		adjacents[id] = std::set<uint64_t>(alist.begin(),alist.end());
	} else {
		for(const uint64_t & adj_id : alist) {
			adjacents[id].insert(adj_id) ;
		}
	}
	hashes.insert(nodes[id]);

	for(const uint64_t & xid : alist) {
		if (adjacents.find(xid) == adjacents.end()) {
			adjacents[xid] = std::set<uint64_t>();
		}
		adjacents[id].insert(id);
	}
}

std::set<uint64_t> geograph::adjacent_nodes(const uint64_t & id) {
	return nodes[geonode(id)];
}


// all the edges having id as an end point.
std::set<pair<uint64_t,uint64_t>> geograph::adjacent_edges(const uint64_t & id) {
	std::set<pair<uint64_t, uint64_t>> edgeset;
	for(auto & adjid : nodes[geonode(id)]) {
		if (id < adjid) {
			edgeset.insert(pair<uint64_t,uint64_t>(id, adjid));
		} else {
			edgeset.insert(pair<uint64_t,uint64_t>(adjid, id));
		}
	}
	return edgeset;
}


vector<const geograph::geonode> geograph::geohash_range(const binarygeohash & ghash) {
	vector<const geograph::geonode> tmp;
	geonode key(ghash);
	set<geonode>::const_iterator lb = hashes.lower_bound(geonode(ghash));
	set<geonode>::const_iterator ub = hashes.upper_bound(geonode(ghash));
	for(;lb != ub; ++lb) {
		tmp.push_back(*lb);
	}
	return tmp;
}
