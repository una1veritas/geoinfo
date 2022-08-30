/*
 * geograph.h
 *
 *  Created on: 2022/08/30
 *      Author: sin
 */

#ifndef GEOGRAPH_H_
#define GEOGRAPH_H_


#include "bgeohash.h"
//#include <cmath>
//#include "geodistance.h"

struct geopoint {
	double lat, lon;

	geopoint(const double & lattitude, const double & longitude)
	: lat(lattitude), lon(longitude) { }

	binarygeohash bgeohash(const int & precision = 40) {
		return  binarygeohash(lat, lon, precision);
	}

	friend ostream & operator<<(ostream & out, const geopoint & p) {
		out << " (" << fixed << setprecision(7) << p.lat << ","
				<< setprecision(7) << p.lon << ") ";
		return out;
	}
};

struct geograph {

public:
	struct geonode {
		uint64_t osmid;
		geopoint gpoint;
		binarygeohash geohash;

		geonode(const geonode & gn) : osmid(gn.osmid), gpoint(gn.gpoint), geohash(gn.geohash) {}

		geonode(const uint64_t & id, const double & latitude, const double & longitude)
		: osmid(id), gpoint(latitude, longitude) {
			geohash = gpoint.bgeohash(prec);
		}

		geonode(const uint64_t & id) : osmid(id), gpoint(0,0), geohash(gpoint.bgeohash(prec)) {	}

		// dummy for a search key
		geonode(const binarygeohash & hash) : osmid(0), gpoint(0,0), geohash(hash) { }

		//~geonode() {}

		uint64_t id() const { return osmid; }

		bool operator<(const geonode & b) const {
			return osmid < b.osmid;
		}

		bool operator==(const geonode & b) const {
			return osmid == b.osmid;
		}

		friend std::ostream & operator<<(std::ostream & out, const geonode & n) {
			out << "(" << std::dec << std::setw(10) << n.id() << " " << n.geohash << " "
					<< " (" << std::fixed << std::setprecision(7) << n.gpoint.lat << ","
					<< std::setprecision(7) << n.gpoint.lon << ") ";
			out << ") ";
			return out;
		}
	};

	struct geohash_compare {
		bool operator() (geonode & a, geonode & b) const {
			return a.geohash < b.geohash;
		}
	};

	map<uint64_t, geonode> nodes;
	map<uint64_t,std::set<uint64_t>> adjacents;
	set<geonode,geohash_compare> hashes;

private:
	static constexpr int prec = 40;

public:
	unsigned int size() const { return nodes.size(); }

	void insert(const uint64_t & id, const double & lat, const double & lon, const vector<uint64_t> & alist);

	/*
    vector<pair<binarygeohash,uint64_t>> hashtoid() {
    	vector<pair<binarygeohash,uint64_t>> hash2id;
    	for(auto itr = nodes.begin(); itr != nodes.end(); ++itr) {
    		hash2id.push_back(pair<binarygeohash,uint64_t>(itr->geohash,itr->osmid));
    	}
    	std::sort(hash2id.begin(), hash2id.end(),
    			[](const pair<binarygeohash,uint64_t> & a, const pair<binarygeohash,uint64_t> & b)
				{ return a.first < b.first; }
    	);
    	return hash2id;
    }
    */

    // all the nodes being adjacent to id.
    std::set<uint64_t> adjacent_nodes(const uint64_t & id);

    // all the edges having id as an end point.
    std::set<pair<uint64_t,uint64_t>> adjacent_edges(const uint64_t & id);

    vector<const geograph::geonode> geohash_range(const binarygeohash & ghash);

	friend std::ostream & operator<<(std::ostream & out, const geograph & gg) {
		for(const auto & a_pair : gg.nodes) {
			out << a_pair.first << ", " << endl;
		}
		return out;
	}
};

#endif /* GEOGRAPH_H_ */
