//============================================================================
// Name        : geograph.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <iomanip>
#include <algorithm>

#include <cmath>
#include <numbers>

using std::cout;
using std::endl;

#include "bgeohash.h"
#include "geograph.h"

#define DEG2RAD(x)  ((std::numbers::pi / 180.0) * (x))
double geopoint::distance_to(const geopoint & q) const {
	//http://dtan4.hatenablog.com/entry/2013/06/10/013724
	//https://en.wikipedia.org/wiki/Geographical_distance#Ellipsoidal_Earth_projected_to_a_plane
	//https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
	//const int mode = 1;
    // 緯度，経度をラジアンに
	double plat = DEG2RAD(lat);
	double plon = DEG2RAD(lon);
	double qlat = DEG2RAD(q.lat);
	double qlon = DEG2RAD(q.lon);
    // 緯度と経度の差
    //double latdiff = plat - qlat, londiff = plon - qlon;
    // 平均緯度
    double latavr = (plat + qlat) / 2.0;

    // 測地系による値の違い
    constexpr double a = 6378137.0; //mode ? 6378137.0 : 6377397.155; // 赤道半径
    //double b = 6356752.314140356; //mode ? 6356752.314140356 : 6356078.963; // 極半径
    //$e2 = ($a*$a - $b*$b) / ($a*$a);
    constexpr double e2 = 0.00669438002301188; //mode ? 0.00669438002301188 : 0.00667436061028297; // 第一離心率^2
    //$a1e2 = $a * (1 - $e2);
    constexpr double a1e2 = 6335439.32708317; // mode ? 6335439.32708317 : 6334832.10663254; // 赤道上の子午線曲率半径

    double sin_latavr = sin(latavr);
    double W2 = 1.0 - e2 * (sin_latavr*sin_latavr);
    double M = a1e2 / (sqrt(W2)*W2); // 子午線曲率半径M
    double N = a / sqrt(W2); // 卯酉線曲率半径

    double t1 = M * (plat - qlat); //latdiff;
    double t2 = N * cos(latavr) * (plon - qlon); //londiff;
    return sqrt((t1*t1) + (t2*t2));
}

double geopoint::inner_prod(const geopoint & a, const geopoint & b) const {
	double ax = distance_to(geopoint(lat, a.lon));
	double ay = distance_to(geopoint(a.lat, lon));
	double bx = distance_to(geopoint(lat, b.lon));
	double by = distance_to(geopoint(b.lat, lon));
	if (a.lon < lon) ax = -ax;
	if (a.lat < lat) ay = -ay;
	if (b.lon < lon) bx = -bx;
	if (b.lat < lat) by = -by;
	return (ax * bx) + (ay * by);
}

double geopoint::projection(const geopoint & a, const geopoint & b) const {
	double ax = distance_to(geopoint(lat, a.lon));
	double ay = distance_to(geopoint(a.lat, lon));
	double bx = distance_to(geopoint(lat, b.lon));
	double by = distance_to(geopoint(b.lat, lon));
	if (a.lon < lon) ax = -ax;
	if (a.lat < lat) ay = -ay;
	if (b.lon < lon) bx = -bx;
	if (b.lat < lat) by = -by;
	double anorm = ax*ax + ay*ay;
	double bnorm = bx*bx + by*by;
	if (anorm == 0 or bnorm == 0)
		return 0;
	return (ax*bx + ay*by)/sqrt(anorm*bnorm);
}

double geopoint::outer_prod_norm(const geopoint & a, const geopoint & b) const {
	double ax = distance_to(geopoint(lat, a.lon));
	double ay = distance_to(geopoint(a.lat, lon));
	double bx = distance_to(geopoint(lat, b.lon));
	double by = distance_to(geopoint(b.lat, lon));
	if (a.lon < lon) ax = -ax;
	if (a.lat < lat) ay = -ay;
	if (b.lon < lon) bx = -bx;
	if (b.lat < lat) by = -by;
	return (ax * by) - (ay * bx);
}


double geopoint::distance_to(const geopoint &q1, const geopoint &q2) const {
	if ( q1.inner_prod(*this, q2) <= 0.0 ) { // < 0.0
		return distance_to(q1);
	}
	if ( q2.inner_prod(q1, *this) < 0.0 ) { // < 0.0
		return distance_to(q2);
	}
	return abs(q1.outer_prod_norm(q2, *this)) / q1.distance_to(q2);
}

/*
double geograph::eastwest() const {
	const geopoint bottomleft(bottomright.lat,topleft.lon);
	return bottomleft.distance_to(bottomright);
}
double geograph::northsouth() const {
	const geopoint bottomleft(bottomright.lat,topleft.lon);
	return bottomleft.distance_to(topleft);
}
*/
void geograph::insert(const uint64_t & id, const double & lat, const double & lon, const vector<uint64_t> & alist) {
	nodes[id] = geonode(id,lat,lon);
	topleft.lat = std::max(topleft.lat, lat);
	topleft.lon = std::min(topleft.lon, lon);
	bottomright.lat = std::min(bottomright.lat, lat);
	bottomright.lon = std::max(bottomright.lon, lon);
	if (adjacents.find(id) == adjacents.end()) {
		adjacents[id] = std::set<uint64_t>(alist.begin(),alist.end());
	} else {
		for(const uint64_t & adj_id : alist) {
			//if (adj_id != id)
			adjacents[id].insert(adj_id);
		}
	}
	hashes.insert(&nodes[id]);

	for(const uint64_t & xid : alist) {
		if (adjacents.find(xid) == adjacents.end()) {
			adjacents[xid] = std::set<uint64_t>();
		}
		adjacents[xid].insert(id);
	}
}

void geograph::insert_node(const geograph::geonode & gnode) {
	nodes[gnode.id()] = gnode;
	topleft.lat = std::max(topleft.lat, gnode.gpoint.lat);
	topleft.lon = std::min(topleft.lon, gnode.gpoint.lon);
	bottomright.lat = std::min(bottomright.lat, gnode.gpoint.lat);
	bottomright.lon = std::max(bottomright.lon, gnode.gpoint.lon);
	if (adjacents.find(gnode.id()) == adjacents.end()) {
		adjacents[gnode.id()] = std::set<uint64_t>();
	}
	hashes.insert(&nodes[gnode.id()]);
}

void geograph::insert_edge_between(const uint64_t & id0, const uint64_t & id1) {
	if (nodes.find(id0) == nodes.end() or nodes.find(id1) == nodes.end()) {
		cerr << "tried to add the edge with undefined end-point(s) " << id0 << ", " << id1 << ". "  << endl;
		return;
	}
	adjacents[id0].insert(id1);
	adjacents[id1].insert(id0);
}

const std::set<uint64_t> & geograph::adjacent_nodes(const uint64_t & id) const {
	static std::set<uint64_t> emptyset;
	if (adjacents.contains(id)) {
		return adjacents.at(id);
	}
	return emptyset;
}


// all the edges having id as an end point.
std::set<std::pair<uint64_t,uint64_t>> geograph::adjacent_edges(const uint64_t & id) const {
	std::set<std::pair<uint64_t, uint64_t>> edgeset;
	for(auto & adjid : adjacents.at(id) ) {
		if (id < adjid) {
			edgeset.insert(std::pair<uint64_t,uint64_t>(id, adjid));
		} else {
			edgeset.insert(std::pair<uint64_t,uint64_t>(adjid, id));
		}
	}
	return edgeset;
}


std::vector<geograph::geonode> geograph::geohash_range(const bgeohash & ghash) {
	vector<geograph::geonode> tmp;
	geograph::geonode key(ghash);
	set<geograph::geonode*>::const_iterator lb = hashes.lower_bound(&key);
	set<geograph::geonode*>::const_iterator ub = hashes.upper_bound(&key);
	for(;lb != ub; ++lb) {
		tmp.push_back(**lb);
	}
	return tmp;
}
const geograph::geonode & geograph::node_nearest_to(const geopoint & pt) {
    double dist = std::numeric_limits<double>::infinity();
    geograph::geonode & nearest = nodes.begin()->second;
    for (const auto & a_pair : nodes) {
    	const geopoint & a_point = a_pair.second.point();
    	double d = a_point.distance_to(pt);
    	if (d < dist) {
    		dist = d;
    		nearest = a_pair.second;
    	}
    }
    return nearest;
}
