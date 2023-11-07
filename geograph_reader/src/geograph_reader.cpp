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

struct Graph {
	set<unsigned long> nodes;
	map<unsigned long, pair<double, double> > node_coordinate;
	map<unsigned long, vector<unsigned long> > node_adjacents;

	// make as an empty graph
	Graph() {}

	// dispose the graph
	~Graph() {
		nodes.clear();
		node_coordinate.clear();
		for(auto & nodelistpair : node_adjacents) {
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

int main(const int argc, const char * argv[]) {
	if (! (argc > 0) ) {
		cerr << "give an input file name." << endl;
		exit(EXIT_FAILURE); // terminates with error.
	}
	cout << "input file name = " << argv[1] << endl;

	ifstream csvfile(argv[1]);

	if (! csvfile ) {
		cerr << "opening the file " << argv[1] << " failed." << endl;
		exit(EXIT_FAILURE);
	}

	Graph graph;

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
        graph.nodes.insert(id);
        graph.node_coordinate[id] = pair<double,double>(lat,lon);
        graph.node_adjacents[id] = vector<unsigned long>();
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	graph.node_adjacents[id].push_back(stoull(strvec[i]));
    }
    cout << count << "lines finished." << endl;
    csvfile.close();
	cout << " finished." << endl;

    cout << "node id (lattitude, longitude):" << endl;
    count = 0;
    for(const auto & an_id : graph.nodes) {
    	cout << an_id << " (" << graph.node_coordinate[an_id].first << ", "
    			<< graph.node_coordinate[an_id].second << "), " ;
    	if (++count > 100)
    		break;
    }
    cout << endl;
    cout << graph.nodes.size() << " nodes." << endl << endl;

    cout << endl << "edges: " << endl;
    count = 0;
    for(const auto & a_pair : graph.node_adjacents) {
    	if (count < 100) {
			for(const auto & endpoint : a_pair.second) {
				cout << "(" << a_pair.first << ", " << endpoint << "), ";
			}
			cout << endl;
    	}
    	count += a_pair.second.size();
    }
    cout << endl;
    cout << count << " edges." << endl;
	return 0;
}
