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

	geopoint(void) : lat(0.0), lon(0.0) {}

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
	struct node {
		uint64_t osmid;
		geopoint gpoint;
		binarygeohash ghash;
		std::vector<uint64_t> adjlist;

		node(const uint64_t & id, const double & latitude, const double & longitude)
		: osmid(id), gpoint(latitude, longitude), adjlist({}) {
			ghash = gpoint.bgeohash(prec);
		}

		node(const uint64_t & id, const double & latitude, const double & longitude, const std::vector<uint64_t> & alist)
		: osmid(id), gpoint(latitude, longitude), adjlist(alist) {
			ghash = gpoint.bgeohash(prec);
		}

		// dummy for a search key
		node(const binarygeohash & hash) : osmid(0), gpoint(), ghash(hash), adjlist({}) { }

		~node() {
			adjlist.clear();
		}

		uint64_t id() const { return osmid; }

		friend std::ostream & operator<<(std::ostream & out, const node & n) {
			out << "(" << std::dec << std::setw(10) << n.id() << " " << n.ghash << " "
					<< " (" << std::fixed << std::setprecision(7) << n.gpoint.lat << ","
					<< std::setprecision(7) << n.gpoint.lon << "), ";
			out << "{" << std::dec;
			if ( n.adjlist.size() > 0 ) {
				for(unsigned int i = 0; i+1 < n.adjlist.size(); ++i) {
					out << n.adjlist[i] << ", ";
				}
				out << n.adjlist[n.adjlist.size() - 1] << "} ";
			}
			out << ") ";
			return out;
		}
	};

	std::vector<node> nodes;

private:
	static constexpr int prec = 40;

public:
	unsigned int size() const { return nodes.size(); }


	void push_back(const uint64_t & id, const double & lat, const double & lon, const std::vector<uint64_t> & alist) {
		nodes.push_back(node(id, lat, lon, alist));
	}

    void sort() {
    	std::sort(nodes.begin(), nodes.end(),
    			[](const node & a, const node & b) { return a.ghash < b.ghash; }
    	);
    }

    // all the nodes being adjacent to id.
    std::set<uint64_t> adjacents(const uint64_t & id) const {
    	std::set<uint64_t> adjset;
    	for(auto & n: nodes) {
    		if (n.id() == id) {
    			for(const auto & adjid : n.adjlist) {
    				adjset.insert(adjid);
    			}
    		} else {
    			const auto & list = n.adjlist;
    			if (find(list.begin(), list.end(), id) != list.end()) {
    				adjset.insert(n.id());
    			}
    		}
    	}
    	return adjset;
    }

    // all the edges having id as an end point.
    std::set<std::pair<uint64_t,uint64_t>> adjacent_edges(const uint64_t & id) const {
    	std::set<std::pair<uint64_t, uint64_t>> edgeset;
    	for(auto & n: nodes) {
    		if (n.id() == id) {
    			for(const auto & adjid : n.adjlist) {
    				if (id < adjid) {
    					edgeset.insert(std::pair<uint64_t,uint64_t>(id, adjid));
    				} else {
    					edgeset.insert(std::pair<uint64_t,uint64_t>(adjid, id));
    				}
    			}
    		} else {
    			const auto & list = n.adjlist;
    			if (find(list.begin(), list.end(), id) != list.end()) {
    				if (id < n.id()) {
    					edgeset.insert(std::pair<uint64_t,uint64_t>(id, n.id()));
    				} else {
    					edgeset.insert(std::pair<uint64_t,uint64_t>(n.id(),id));
    				}
    			}
    		}
    	}
    	return edgeset;
    }

	std::pair<int,int> range(const binarygeohash & gbin) {
		node key(gbin);
		vector<node>::iterator lb = lower_bound(nodes.begin(), nodes.end(),
				key,
				[](const node & a, const node &b){ return a.ghash < b.ghash; } );
		vector<node>::iterator ub = upper_bound(lb, nodes.end(),
				key,
				[](const node & a, const node &b){ return a.ghash < b.ghash; } );
		return std::pair<int,int>(lb - nodes.begin(), ub - nodes.begin());
	}

	friend std::ostream & operator<<(std::ostream & out, const geograph & gg) {
		for(const node & n : gg.nodes) {
			out << n << endl;
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
        ggraph.push_back(id, lat, lon, adjacents);
        adjacents.clear();
    }
    csvf.close();
    ggraph.sort();

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
			for(auto & i : vec) {
				geograph::node key(i);
				range = ggraph.range(i);
				for(unsigned int i = range.first; i < range.second; ++i) {
					edges.merge(ggraph.adjacent_edges(ggraph.nodes[i].id()));
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
