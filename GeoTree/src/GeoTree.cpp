//============================================================================
// Name        : GeoTree.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <vector>
#include <fstream>
#include <set>
#include "bgeohash.h"
#include "geograph.h"

using namespace std;

//ノードのデータ構造を定義
struct GeoNode {
private:
	bgeohash geohash;  	// 深さ，およびこのノードが対応する領域，geohash の精度が深さを表す
	enum {
		TYPE_SETNODE = 0,
		TYPE_DIVIDERNODE,
	} node_type;

	union {
		struct {
			double threshold;  	// 分割する緯度または経度, どちらかは geohash の精度が偶数（経度）か奇数（緯度）で判別
			GeoNode * left, * right;
		};
		struct {
			set<geopoint> * points;
		};
	};

public:
	GeoNode(const bgeohash & ghash, const vector<geopoint> & pointseq) {
		// 葉の場合のコンストラクタ．
		// 点は vector から set に移すだけ．
		geohash = bgeohash;
		node_type = TYPE_SETNODE;
		points = new set<geopoint>();
		for(const auto & gp : pointseq) {
			points->insert(gp);
		}
	}

	~GeoNode() {
		if ( node_type == TYPE_SETNODE ) {
			points->clear();
			delete points;
		}
	}
};

int main(int argc, char * argv[]){

	if (argc < 2) {
		cerr << "usage: command map-file_name]" << endl;
		exit(EXIT_FAILURE);
	}

	vector<geopoint> points = read_geopoints(argv[1]);

	return 0;
}

vector<string> split(string& input, char delimiter) {
    istringstream stream(input);
    string field;
    vector<string> result;
    while (getline(stream, field, delimiter)) {
        result.push_back(field);
    }
    return result;
}

vector<geopoint> read_geopoints(const string & filename) {
	ifstream csvf;
	vector<geopoint> points;
	csvf.open(filename);
	if (!csvf) {
		cerr << "open a geograph file " << filename << " failed." << endl;
		return points; // returning empty point sequence.
	}

    string line;
    while (getline(csvf, line)) {
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 4) {
        	cerr << "insufficient parameters to define a node_edge." << endl;
        	continue;
        }
		//uint64_t id = stoull(strvec[0]);
		double lat = stod(strvec[1]);
		double lon = stod(strvec[2]);
        points.push_back(geopoint(lat, lon));
    }
    csvf.close();
	return points;
}
