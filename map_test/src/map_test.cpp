//============================================================================
// Name        : map_test.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <set>

using namespace std;

struct geonode {
	unsigned int osmid;
	double lat, lon;

public:
	geonode(unsigned int id) : osmid(id), lat(0), lon(0) {}

	bool operator<(const geonode & another) const {
		return osmid < another.osmid;
	}

	bool operator<=(const geonode & another) const {
		return osmid <= another.osmid;
	}

	bool operator==(const geonode & another) const {
		return osmid == another.osmid;
	}
};

int main() {
	cout << "!!!Hello World!!!" << endl; // prints !!!Hello World!!!

	set<geonode> ex;

	for(unsigned int id = 0; id < 10; ++id) {
		ex.insert(geonode(id));
	}

	for(auto & elem : ex) {
		cout << elem.osmid << endl;
	}
	cout << endl << "finished." << endl;
	return 0;
}
