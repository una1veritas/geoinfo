//============================================================================
// Name        : geograph_read_sample.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <set>
#include <map>

using namespace std;

struct Graph {
	set<unsigned long> nodes;
	map<unsigned long, pair<double, double> > nodecoord;
	map<unsigned long, vector<unsigned long> > adjacents;

	Graph() {}

	~Graph() {
		nodes.clear();
		nodecoord.clear();
		for(auto & nodelistpair : adjacents) {
			nodelistpair.second.clear();
		}
	}
};

// 文字列を文字 delimiter で区切って文字列の配列 vector<string> にして
// 返す関数．コンマやタブ区切り形式のテキスト一行を処理するのに使用する．
vector<string> split(string& input, char delimiter) {
    istringstream stream(input);
    string field;
    vector<string> result;
    while (getline(stream, field, delimiter)) {
        result.push_back(field);
    }
    return result;
}


int main(const int argc, const char argv[]) {
	cout << "!!!Hello World!!!" << endl; // prints !!!Hello World!!!
	if (! (argc > 0) ) {
		cerr << "give an input file name." << endl;
		exit(EXIT_FAILURE); // terminates with error.
	}
	cout << "input file name = " << argv[1] << endl;

	ifstream csvfile;

	cout << "reading..." << endl;
	csvfile.open(argv[1]);
	if (! csvfile ) {
		cerr << "opening the file " << argv[1] << " failed." << endl;
		exit(EXIT_FAILURE);
	}

	Graph graph;

	return 0;
}
