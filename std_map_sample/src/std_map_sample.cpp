//============================================================================
// Name        : std_map_sample.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <map>
#include <unordered_map>
#include <cinttypes>

using namespace std;

typedef uint64_t uint64;

struct uint64pair {
	uint64 first, second;

	uint64pair(const uint64 & a, const uint64 & b) {
		if ( a > b ) {
			first = b;
			second = a;
		} else {
			first = a;
			second = b;
		}
	}

	uint64pair(const unsigned int a[]) : uint64pair(a[0], a[1]) { }

	// compare *this and right
	bool operator==(const uint64pair & right) const {
		return first == right.first and second == right.second;
	}

	bool operator!=(const uint64pair & right) const {
		return first != right.first or second != right.second;
	}

	bool operator<(const uint64pair & right) const {
		if (first < right.first) {
			return true;
		} else if (first == right.first) {
			return second < right.second;
		}
		return false;
	}

	// hash function
	struct hash {
		size_t operator()(const uint64pair & p) const {
			return size_t(p.first ^ p.second);
		}
	};

	friend std::ostream & operator<<(ostream & out, const uint64pair & p) {
		out << '(' << p.first << ", " << p.second << ") ";
		return out;
	}
};

int main() {
	uint64pair a(1, 3), b(3, 1), c(2,2);
	uint64pair d = {3, 0};
	unsigned int array[] = {9, 4, 2, 6, };
	d = array;
	cout << "!!!Hello World!!!" << endl; // prints !!!Hello World!!!

	cout << (a < b) << (a < c) << (a == b) << (b != c) << endl;
	cout << d << endl << endl;

	map<uint64pair, double> adjmatrix;
	adjmatrix[{5,2}] = 1.0;
	adjmatrix[{3,4}] = 2.0;
	adjmatrix[{2,5}] = 3.8;
	adjmatrix[{1,4}] = 2.0;
	for(const auto & keyval: adjmatrix) {
		cout << keyval.first << ": " << keyval.second << endl;
	}
	cout << endl;

	unordered_map<uint64pair, double, uint64pair::hash> hashmatrix;
	hashmatrix[{5,2}] = 1.0;
	hashmatrix[{3,4}] = 2.0;
	hashmatrix[{2,5}] = 3.7;
	hashmatrix[{1,4}] = 2.0;
	cout << hashmatrix.count({4,3}) << ", " <<  hashmatrix.count({2,3}) << endl;
	for(const auto & keyval: hashmatrix) {
		cout << keyval.first << ": " << keyval.second << endl;
	}
	cout << endl;

	return 0;
}
