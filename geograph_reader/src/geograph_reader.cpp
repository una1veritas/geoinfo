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

	ifstream csvfile;

	cout << "reading..." << endl;
	csvfile.open(argv[1]);
	if (! csvfile ) {
		cerr << "opening the file " << argv[1] << " failed." << endl;
		exit(EXIT_FAILURE);
	}

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
	} graph;

    string line;
    while (getline(csvfile, line)) {
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 4) {
        	cerr << "insufficient parameters to define a node_edge." << endl;
        	continue;
        }
		unsigned long id = stoull(strvec[0]);
		double lat = stod(strvec[1]);
		double lon = stod(strvec[2]);
        graph.nodes.insert(id);
        graph.nodecoord[id] = pair<double,double>(lat,lon);
        graph.adjacents[id] = vector<unsigned long>();
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	graph.adjacents[id].push_back(stoull(strvec[i]));
    }
    cout << "finished." << endl;
    csvfile.close();

    long cnt;
    cout << "node id (lattitude, longitude):" << endl;
    cnt = 0;
    for(const auto & an_id : graph.nodes) {
    	cout << an_id << " (" << graph.nodecoord[an_id].first << ", "
    			<< graph.nodecoord[an_id].second << "), " ;
    	if (++cnt > 100)
    		break;
    }
    cout << endl;
    cout << endl << "edges: " << endl;
    cnt = 0;
    for(const auto & a_pair : graph.adjacents) {
    	for(const auto & endpoint : a_pair.second) {
			cout << "(" << a_pair.first << ", " << endpoint << "), ";
    	}
    	cout << endl;
		if (++cnt > 100)
			break;
    }
    cout << endl;
	return 0;
}
