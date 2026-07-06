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
#include "convexhull.h"

using std::cout;
using std::endl;
using std::string;
using std::vector;


int csv_reader(const std::string& filename, std::vector<Point2D> & tbl) {
    // 1. Open the CSV file
    std::ifstream file(filename);
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
	vector<Point2D> pointseq; // = { {0, 0}, {1, 1}, {2, -1}, {2.0, -1.5}, {-4, -4}, {0, 0}, {1, 1}, {2, -2} };
	csv_reader("test.csv", pointseq);
	for (const auto & elem : pointseq ) {
		cout << elem << ", ";
	}
	cout << endl;
	cout << "point sequence size = " << pointseq.size() << endl << endl;

	//ringarray<Point2D> ring(127);

	ConvexHull cvx(pointseq);
	double cvx_dia;
	cvx.add(0);
	cvx.add(1);
	cvx.add(2);
	cout << "cvx = " << cvx << endl;
	cout << "cvx first point, last point " << cvx[0] << ",  " << cvx[-1] << endl;
	cvx_dia = cvx[0].distance_to(cvx[-1]);
	cout << "cvx dia = " << cvx_dia << endl;
	cvx.add(3);
	cvx.add(4);
	cout << "cvx = " << cvx << endl;
	cvx_dia = cvx[0].distance_to(cvx[-1]);
	cout << "cvx dia = " << cvx_dia << endl;
	
	cout << "Convex Hull = " << cvx << std::endl;
	cout << "Finished." << endl;

    return 0;
}
