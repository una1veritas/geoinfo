#include <iostream>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include <vector>
#include "gpspoint.h"
#include <cctype>

int read_gpspoint_csv(char *filename, std::vector<gpspoint> &array) {
	char buff[1024], datetime[1024];
	FILE *fp = fopen(filename, "r");
	if (fp == NULL) {
		fprintf(stderr, "file open failed.\n");
		return 0; // failed
	}
	double dt, la, lo;
	char * strptr;
	while (fgets(buff, 1024, fp) != NULL) {
		sscanf(buff, "%[^,],%lf,%lf", datetime, &la, &lo);
		strptr = datetime;
		dt = strtod(strptr, &strptr);
		if ( dt > 10000.0 ) {
			printf("Julian ? = %f\n", dt);
		} else {
			int year = dt;
			for(; !std::isdigit(*strptr); strptr++);
			int month = strtod(strptr, &strptr);
			for(; !std::isdigit(*strptr); strptr++);
			int date = strtod(strptr, &strptr);
			for(; !std::isdigit(*strptr); strptr++);
			int hour = strtod(strptr, &strptr);
			for(; !std::isdigit(*strptr); strptr++);
			int minu = strtod(strptr, &strptr);
			for(; !std::isdigit(*strptr); strptr++);
			int sec = strtod(strptr, &strptr);
			//for(; !std::isdigit(*strptr); strptr++);
			int tzhour = strtod(strptr, &strptr);
			for(; !std::isdigit(*strptr); strptr++);
			int tzmin = strtod(strptr, &strptr);
			for(; !std::isdigit(*strptr); strptr++);
			printf("Gregorian? = %d %d %d %d %d %d %d %d\n", year, month, date, hour, minu, sec, tzhour, tzmin);
		}
		array.push_back(gpspoint(dt, la, lo));
	}
	fclose(fp);
	return 1; // succeeded
}

int main(int argc, char **argv) {

	if ( argc == 1 ) {
		fprintf(stderr, "One file names requested.\n");
		return EXIT_FAILURE;
	}
	std::vector<gpspoint> parray;
	if ( !read_gpspoint_csv(argv[1], parray) ) {
		return EXIT_FAILURE;
	}

	for (unsigned int i = 0; i < parray.size() - 1; ++i) {
		std::cout << i << ": " << parray[i] << std::endl;
	}
	std::cout << std::endl;

/*
	gpspoint a(58800.125671,33.59401617667972,130.361561738076),
			b(58800.125162,33.59297388702034,130.3625824024252),
			c(58793.167049,33.59515380859375,130.403928989666);
			//c(58800.125324,33.59385855499058,130.3594693635873);

	std::cout << a << std::endl << b << std::endl << c << std::endl;
	std::cout << a.distanceTo(b) << std::endl;
	std::cout << a.distanceTo(c) << std::endl;
	std::cout << "inner prod ab.ac " << gpspoint::inner_prod(a, b, c) << std::endl;
	std::cout << "inner prod ba.bc " << gpspoint::inner_prod(b, a, c) << std::endl;
	std::cout << "outer prod abxbc " << gpspoint::norm_outer_prod(a, b, c) << std::endl;
*/
	return EXIT_SUCCESS; // return 0;
}

