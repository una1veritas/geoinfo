//============================================================================
// Name        : geograph_reader.cpp
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

#include "geograph.h"

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

int main(const int argc, const char * argv[]) {
	ifstream csvfile;

	if (! (argc > 0) ) {
		cerr << "give an input file name." << endl;
		exit(EXIT_FAILURE); // terminates with error.
	}
	cout << "input file name = " << argv[1] << endl;

	csvfile.open(argv[1]);
	if (! csvfile ) {
		cerr << "opening the file " << argv[1] << " failed." << endl;
		exit(EXIT_FAILURE);
	}

	geograph graph;
	vector<uint64_t> adjlist;

	cout << "reading..." << endl;
    string line;
    unsigned int count = 0;
    while (getline(csvfile, line)) {
    	++count;
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 4) {
        	cerr << count << ": insufficient parameters to define a node_edge. " << endl;
        	continue;
        }
		unsigned long id = stoull(strvec[0]);
		double lat = stod(strvec[1]);
		double lon = stod(strvec[2]);
		adjlist.clear();
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	adjlist.push_back(stoull(strvec[i]));
        graph.insert(id, lat, lon, adjlist);
    }
    cout << count << "lines finished." << endl;
    csvfile.close();
	cout << " finished." << endl;

    cout << "node id (lattitude, longitude):" << endl;
    count = 0;
    for(const auto & a_pair : graph ) {
    	cout << a_pair.first << " (" << a_pair.second << "), " ;
    	if (++count > 100)
    		break;
    }
    cout << endl;
    cout << graph.size() << " nodes." << endl << endl;

    cout << endl << "edges: " << endl;
    count = 0;
    for(const auto & id : graph.node_ids() ) {
    	for(const auto & another : graph.adjacents(id) ) {
			if (count < 100) {
				for(const auto & endpoint : a_pair.second) {
					cout << "(" << a_pair.first << ", " << endpoint << "), ";
				}
				cout << endl;
			}
			count += a_pair.second.size();
    	}
    }
    cout << endl;
    cout << count << " edges." << endl;
	return 0;
}
