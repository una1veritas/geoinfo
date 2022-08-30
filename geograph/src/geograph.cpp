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

		// dummy for a search key
		geonode(const binarygeohash & hash) : osmid(0), gpoint(0,0), geohash(hash) { }

		//~geonode() {}

		uint64_t id() const { return osmid; }

		bool operator<(const geonode & another) const {
			return geohash < another.geohash;
		}

		bool operator==(const geonode & another) const {
			return geohash == another.geohash;
		}

		friend std::ostream & operator<<(std::ostream & out, const geonode & n) {
			out << "(" << std::dec << std::setw(10) << n.id() << " " << n.geohash << " "
					<< " (" << std::fixed << std::setprecision(7) << n.gpoint.lat << ","
					<< std::setprecision(7) << n.gpoint.lon << ") ";
			out << ") ";
			return out;
		}
	};

	set<geonode> nodes;
	map<uint64_t,set<uint64_t>> adjacent;

private:
	static constexpr int prec = 40;

public:
	unsigned int size() const { return nodes.size(); }


	void insert(const uint64_t & id, const double & lat, const double & lon, const vector<uint64_t> & alist) {
		nodes.insert(geonode(id, lat, lon));
		auto itr = adjacent.find(id);
		if (itr == adjacent.end()) {
			adjacent[id] = std::set<uint64_t>(alist.begin(),alist.end());
		}
		adjacent[id].insert(alist.begin(),alist.end());

		for(auto & xid : alist) {
			if (adjacent.find(xid) == adjacent.end()) {
				adjacent[xid] = std::set<uint64_t>();
			}
			adjacent[xid].insert(id);
		}
	}

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
    std::set<uint64_t> adjacents(const uint64_t & id) {
    	return adjacent[id];
    }

    // all the edges having id as an end point.
    std::set<pair<uint64_t,uint64_t>> adjacent_edges(const uint64_t & id) {
    	std::set<pair<uint64_t, uint64_t>> edgeset;
    	for(auto & adjid : adjacent[id]) {
			if (id < adjid) {
				edgeset.insert(pair<uint64_t,uint64_t>(id, adjid));
			} else {
				edgeset.insert(pair<uint64_t,uint64_t>(adjid, id));
			}
    	}
    	return edgeset;
    }

    /*
	pair<int,int> range(const vector<pair<binarygeohash,uint64_t>> & h2idvec, const binarygeohash & ghash) {
		geonode key(ghash);
		vector<geonode>::iterator lb = lower_bound(ghashtoid.begin(), ghashtoid.end(),
				key,
				[](const geonode & a, const geonode &b){ return a.geohash < b.geohash; } );
		vector<geonode>::iterator ub = upper_bound(lb, ghashtoid.end(),
				key,
				[](const geonode & a, const geonode &b){ return a.geohash < b.geohash; } );
		return pair<int,int>(lb - ghashtoid.begin(), ub - ghashtoid.begin());
	}
	*/

	friend std::ostream & operator<<(std::ostream & out, const geograph & gg) {
		for(const auto & a_node : gg.nodes) {
			out << a_node << ", " << endl;
		}
		return out;
	}
};



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

    // construct the node table sorted by geohash
    vector<const geograph::geonode *> hash2id;
    for(auto & a_node : ggraph.nodes) {
    	hash2id.push_back(&a_node);
    }
	std::sort(hash2id.begin(), hash2id.end(), [ ](const geograph::geonode * a, const geograph::geonode * b) { return a->geohash < b->geohash; }
	);

	// show some entry
    int count = 0;
    for(auto i = ggraph.nodes.begin(); i != ggraph.nodes.end(); ++i) {
    	cout << *i << endl;
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
				geograph::geonode key(ghash); // dummy node with geohash code
				auto lb = lower_bound(hash2id.begin(), hash2id.end(), &key,
							[](const geograph::geonode * a, const geograph::geonode * b)
							{ return a->geohash < b->geohash; } );
				auto ub = upper_bound(lb, hash2id.end(), &key,
							[](const geograph::geonode * a, const geograph::geonode * b)
							{ return a->geohash < b->geohash; } );
				range.first = lb - hash2id.begin();
				range.second = ub - hash2id.begin();
				//cout << dec << range.first << " : " << range.second << " ";

				for(unsigned int i = range.first; i < range.second; ++i) {
					edges.merge(ggraph.adjacent_edges(hash2id[i]->id()));
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
