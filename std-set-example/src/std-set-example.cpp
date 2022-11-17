//============================================================================
// Name        : std-set-example.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>

#include <set>

using namespace std;

int main(int argc, char * argv[]) {
	cout << "!!!Hello World!!!" << endl; // prints !!!Hello World!!!

	set<int> s;
	int val;
	for(int i = 1; i < argc; ++i) {
		try {
			val = stoi(argv[i], nullptr, 10);
		} catch(std::invalid_argument const & exc) {
			cout << "invalid argument error " << exc.what() << endl;
		} catch(...) {
			cout << "skip argument " << argv[i] << endl;
		}
		s.insert(val);

		cout << "argv[" << i << "] = " << argv[i] << endl;
		for(auto & i : s) {
			cout << i << ", ";
		}
		cout << endl;
	}

	return 0;
}
