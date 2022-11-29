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

#include "bgeohash.h"
#include "geograph.h"

using namespace std;

//ノードのデータ構造を定義
struct GeoNode{
	int depth；
	static constexpr char * char_map_geohash = (char *) "0123456789bcdefghjkmnpqrstuvwxyz";
	static constexpr char * char_map_16 = (char *) "0123456789ABCDEF";

	bool leaf {}；

	//内部ノードの場合
	bool lon {};
	//int 区切る緯度または経度の値
	int lon = 0;

	GeoNode* left;
	GeoNode* right;

	//葉ノードの場合
	set<uint64_t> points;
};
/*
//make_GeoTreeを完成させる
make_GeoTree(点の集合,精度){
	根ノード(=葉)を返す
}*/


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
