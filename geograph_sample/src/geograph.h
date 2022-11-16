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

struct georect {
	double north, east, south, west;

	georect(const double & n, const double e, const double s, const double w) :
		north(n), east(e), south(s), west(w) { }

	georect(const georect & georect) :
		north(georect.north),
		east(georect.east),
		south(georect.south),
		west(georect.west) { }

	georect(const vector<geopoint> & vec) {
		if (vec.size() == 0) {
			north = 0, east = 0, south = 0, west = 0;
		} else {
			north = vec[0].lat, east = vec[0].lon, south = vec[0].lat, west = vec[0].lon;
		}
		for(const auto & p : vec) {
			east = std::min(east, p.lon);
			west = std::max(west, p.lon);
			south = std::min(south, p.lat);
			north = std::max(north, p.lat);
		}
	}

	georect & operator()(const double & n, const double e, const double s, const double w) {
		north = n;
		east = e;
		south = s;
		west = w;
		return *this;
	}

	georect & shift(const double & lat, const double & lon) {
		north += lat; south += lat;
		east += lon; west += lon;
		return * this;
	}

	double width_degree() const {
		return west - east;
	}

	double height_degree() const {
		return north - south;
	}

	double width_meter() const {
		return geopoint((north+south)/2, east).distance_to(geopoint((north+south)/2,west));
	}

	double height_meter() const {
		return geopoint(south, east).distance_to(geopoint(north,east));
	}

	geopoint center() const {
		return geopoint((north+south)/2, (east+west)/2);
	}

	double aspect_ratio() const {
		return width_meter()/height_meter();
	}

	bool contains(const geopoint & p) const {
		return  (p.lat >= south) and (p.lat <= north)
				and (p.lon >= east) and (p.lon <= west);
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

	const geonode & node_nearest_to(const geopoint & pt);

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
