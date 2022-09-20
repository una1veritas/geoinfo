/*
 * geograph.h
 *
 *  Created on: 2022/08/30
 *      Author: sin
 */

#ifndef GEOGRAPH_H_
#define GEOGRAPH_H_

#include <utility>

#include "bgeohash.h"
//#include <cmath>
//#include "geodistance.h"

struct geopoint {
	double lat, lon;

	geopoint(const double & lattitude, const double & longitude)
	: lat(lattitude), lon(longitude) { }

	geopoint() : lat(0), lon(0) {}

	geopoint(const geopoint & p, const geopoint & q) : lat(q.lat - p.lat), lon(q.lon - p.lon) {	}

	bgeohash geohash(const int & precision = 40) const {
		return  bgeohash(lat, lon, precision);
	}

	geopoint operator+(const geopoint & q) const {
		return geopoint(lat+q.lat, lon+q.lon);
	}
	geopoint operator-(const geopoint & q) const {
		return geopoint(lat-q.lat, lon-q.lon);
	}

	double distance_to(const geopoint & q) const;
	double distance_to(const geopoint &q1, const geopoint &q2) const;

	double inner_prod(const geopoint & a, const geopoint & b) const;
	double outer_prod_norm(const geopoint & a, const geopoint & b) const;
	double projection(const geopoint & a, const geopoint & b) const;


	double vector_norm() const { return geopoint().distance_to(*this); }

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
		bgeohash geohash;

		static constexpr int prec = 40;

		geonode(void) : osmid(0), gpoint(0, 0) { geohash = gpoint.geohash(prec); }

		geonode(const geonode & gn) : osmid(gn.osmid), gpoint(gn.gpoint), geohash(gn.geohash) {}

		geonode(const uint64_t & id, const double & latitude, const double & longitude)
		: osmid(id), gpoint(latitude, longitude) {
			geohash = gpoint.geohash(prec);
		}

		// dummy for a search key
		geonode(const bgeohash & hash) : osmid(0), gpoint(0,0), geohash(hash) { }

		//~geonode() {}

		const uint64_t & id() const { return osmid; }
		const geopoint & point() const { return gpoint; }
		const bgeohash & bingeohash() const { return geohash; }

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

private:
	struct geohash_compare {
		bool operator() (geonode * a, geonode * b) const {
			return a->bingeohash() < b->bingeohash();
		}
	};

private:
	geopoint topleft, bottomright;
	map<uint64_t, geonode> nodes;
	map<uint64_t,std::set<uint64_t>> adjacents;
	set<geonode *,geohash_compare> hashes;

public:
	geograph() : topleft(-100,200), bottomright(100,-200), nodes(), adjacents(), hashes() {}

	unsigned int size() const { return nodes.size(); }
	const geonode & node(const uint64_t & id) const { return nodes.at(id); }
	const geopoint & point(const uint64_t & id) const { return nodes.at(id).point(); }
	//double width() const { return bottomright.lon - topleft.lon; }
	//double height() const { return topleft.lat - bottomright.lat; }
	//double south() const { return bottomright.lat; }
	//double east() const { return topleft.lon; }
	//double north() const { return topleft.lat; }
	//double west() const { return bottomright.lon; }
	//double eastwest() const;
	//double northsouth() const;

	std::map<uint64_t,geonode>::const_iterator cbegin() const { return nodes.cbegin(); }
	std::map<uint64_t,geonode>::const_iterator cend() const { return nodes.cend(); }
	std::map<uint64_t,geonode>::iterator begin() { return nodes.begin(); }
	std::map<uint64_t,geonode>::iterator end() { return nodes.end(); }

	const map<uint64_t, geonode> & nodemap() const { return nodes;}
	void insert(const uint64_t & id, const double & lat, const double & lon, const vector<uint64_t> & alist);
	void insert_node(const geonode & gnode);
	void insert_node(const uint64_t & id, const double & lat, const double & lon) {
		insert_node(geonode(id,lat,lon));
	}
	void insert_edge_between(const uint64_t & id0, const uint64_t & id1);

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
    const std::set<uint64_t> & adjacent_nodes(const uint64_t & id) const;

    // all the edges having id as an end point.
    std::set<std::pair<uint64_t,uint64_t>> adjacent_edges(const uint64_t & id) const;

    std::vector<geonode> geohash_range(const bgeohash & ghash);

	friend std::ostream & operator<<(std::ostream & out, const geograph & gg) {
		for(const auto & a_pair : gg.nodes) {
			out << a_pair.first << ", " << endl;
		}
		return out;
	}
};

#endif /* GEOGRAPH_H_ */
