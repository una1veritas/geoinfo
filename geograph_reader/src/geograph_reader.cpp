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
private:
	set<unsigned long> nodes;
	map<unsigned long, pair<double, double> > node_coordinate;
	map<unsigned long, vector<unsigned long> > node_adjacents;

public:
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

	unsigned long size() const {
		return nodes.size();
	}

	// insert/register a new node.
	void insert_node(const unsigned long & id, const double & lat, const double & lon) {
		nodes.insert(id);
        node_coordinate[id] = pair<double,double>(lat,lon);
        node_adjacents[id] = vector<unsigned long>();
	}

	// add an edge. *** an adjacent node can be added more than once! ***
	void add_edge(const unsigned long & id, const unsigned long & another) {
		if ( id < another ) {
			if ( ! node_adjacents.contains(id) ) {
				node_adjacents[id] = vector<unsigned long>();
			}
        	node_adjacents[id].push_back(another);
		} else {
			if ( ! node_adjacents.contains(another) ) {
				node_adjacents[another] = vector<unsigned long>();
			}
        	node_adjacents[another].push_back(id);
		}
	}

	double latitude(const unsigned long & id) {
		return node_coordinate[id].first;
	}

	double longitude(const unsigned long & id) {
		return node_coordinate[id].second;
	}

	const set<unsigned long> & node_ids() const {
		return nodes;
	}

	const vector<unsigned long> & adjacents(const unsigned long & id) const {
		return node_adjacents[id];
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
        graph.insert_node(id, lat, lon);
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	graph.add_edge(id, stoull(strvec[i]));
    }
    cout << count << "lines finished." << endl;
    csvfile.close();
	cout << " finished." << endl;

    cout << "node id (lattitude, longitude):" << endl;
    count = 0;
    for(const auto & an_id : graph.node_ids() ) {
    	cout << an_id << " (" << graph.latitude(an_id) << ", "
    			<< graph.longitude(an_id) << "), " ;
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
