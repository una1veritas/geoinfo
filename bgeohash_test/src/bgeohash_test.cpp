//============================================================================
// Name        : bgeohash_test.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <iomanip>
#include "bgeohash.h"
#include "geohash.h"

using namespace std;

int main() {
	cout << "!!!Hello World!!!" << endl; // prints !!!Hello World!!!

	double lat = 33.59494018554690, lon = 130.4036063702130;
	cout << "encoding cordinate: " << lat << ", " << lon << endl;

	string hashcode = geohash::encode(lat, lon, 7);
	cout << "geohash code: " << hashcode << endl;
	cout << "string binary form: " << geohash::bincode(hashcode) << endl;
	cout << "int (binary) value: " << hex << geohash::binvalue(hashcode) << endl;

	bgeohash bhash(geohash::binvalue(hashcode), 7*5);
	cout << "bgeohash code: " << bhash << endl;
	cout << "geohash in binary: " << hex << bhash.location() << endl;
	uint64_t intval = bhash.location();
	for(int i = 0; i < bhash.precision(); ++i) {
		cout << ( (intval >> (63-i)) & 1)  << " ";
	}
	cout << endl;

	return 0;
}
