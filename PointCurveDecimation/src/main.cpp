//============================================================================
// Name        : PointCurveDecimation.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cmath>

#include "point2d.h"
#include "ringarray.h"
using namespace std;

int csv_reader(const std::string& filename, std::vector<Point2D> & tbl) {
    // 1. Open the CSV file
    std::ifstream file("data.csv");
    if (!file.is_open()) {
        std::cerr << "Error opening file!" << std::endl;
        return 1;
    }

    std::string line;
    // 2. Read the file line by line
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string xstr, ystr;

        // 3. Split each line by commas
        if ( std::getline(ss, xstr, ',') && std::getline(ss, ystr, ',') ) {
        	// 4. Convert the split strings to the appropriate data types
			Point2D pt;
			pt.x = std::stod(xstr);
			pt.y = std::stod(ystr);
			tbl.push_back(pt);
        } else {
        	break;
        }
    }

    // 5. Close the file
    file.close();

    return 0;
}

int main() {
	cout << "CSV reader!!" << endl; // prints !!!Hello World!!!
	std::vector<Point2D> seqs = { {0, 0}, {1, 1}, {2, -1}, {2.0, -1.0}, {-4, -4}, {0, 0}, {1, 1}, {2, -2} };
	for (int i = 0; i + 2 < seqs.size() ; ++i) {
		std::cout << seqs[i] << ", " << seqs[i+1] << ", " << seqs[i+2] << std::endl;
		std::cout << " + " << seqs[i] + seqs[i+1] << std::endl;
		std::cout << " == " << (seqs[i] == seqs[i+1]) << std::endl;
		std::cout << " != " << (seqs[i] != seqs[i+1]) << std::endl;
		std::cout << " dot " << seqs[i].dot(seqs[i+1]) << std::endl;
		std::cout << " cross_norm " << seqs[i].cross_norm(seqs[i+1]) << std::endl;
		std::cout << " rhombus " << seqs[i].rhombus(seqs[i+1], seqs[i+2]) << std::endl;
		std::cout << " distance " << seqs[i].distance_to(seqs[i+1]) << std::endl;
		std::cout << " distance to line " << seqs[i].distance_to(seqs[i+1], seqs[i+2]) << std::endl;
		std::cout << " vector " << Point2D::vector(seqs[i], seqs[i+1]) << std::endl;
		std::cout << " perpendicular vector "  << Point2D::perpvector(seqs[i], seqs[i+1]) << std::endl;
	}

	std::cout << Point2D(0, 0).rhombus(Point2D(1, 1), Point2D(0.8, 0.6)) << endl;
    return 0;
}
