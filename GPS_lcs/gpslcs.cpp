#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <cmath>
#include <chrono>

#include <vector>
#include "gpspoint.h"

//#define SHOW_SEQ
#define FRAC(x)  ((x) - (int)(x))

int read_gpspoint_csv(char *filename, std::vector<gpspoint> &array) {
	char buff[1024];
	FILE *fp = fopen(filename, "r");
	if (fp == NULL) {
		fprintf(stderr, "file open failed.\n");
		return 0; // failed
	}
	char tstr[1024];
	double t, la, lo;
	while (fgets(buff, 1024, fp) != NULL) {
		sscanf(buff, "%[^,],%lf,%lf", tstr, &la, &lo);
		t = atof(tstr);
		array.push_back(gpspoint(t, la, lo));
	}
	fclose(fp);
	return 1; // succeeded
}

int main(int argc, char **argv) {
	if (!(argc > 2)) {
		fprintf(stderr, "two file names requested.\n");
		return EXIT_FAILURE;
	}
	std::vector<gpspoint> parray, qarray;
	read_gpspoint_csv(argv[1], qarray);
	read_gpspoint_csv(argv[2], parray);

	printf("\n%s:\n", argv[1]);
	printf("%lu points.\n", (unsigned long) qarray.size());
#ifdef SHOW_SEQ
	for(int i = 0; i < qarray.size(); ++i) {
		printf("%d: %lf, %lf, %lf",
				i, qarray[i].time, qarray[i].lat, qarray[i].lon);
		if ( i > 0 )
			printf("; (%lf)", qarray[i-1].distanceTo(qarray[i]));
		printf("\n");
	}
#endif
	printf("%s:\n", argv[2]);
	printf("%lu points.\n", (unsigned long) parray.size());
#ifdef SHOW_SEQ
	for(int i = 0; i < parray.size(); ++i) {
		printf("%d: %lf, %lf, %lf", i, parray[i].time, parray[i].lat, parray[i].lon);
		if ( i > 0 )
			printf("; (%lf)", parray[i-1].distanceTo(parray[i]));
		printf("\n");
	}
#endif

	auto sw = std::chrono::system_clock::now();
	std::vector<std::pair<float,float>> result = gpspoint::lcs(parray, qarray, 30);
	auto dur = std::chrono::system_clock::now() - sw;

	double similarity = 0;
	std::cout << "took " << std::chrono::duration_cast<std::chrono::milliseconds>(dur).count() << " millis." << std::endl;
	printf("\nthe length of a lcs: %ld\n\n", (unsigned long)result.size());
	for (auto i = result.begin(); i != result.end(); ++i) {
		float iq = i->first, ip = i->second;
		if ( FRAC(iq) != 0 ) {
			printf("%.1lf ([%lf, %lf]-[%lf, %lf]) ", iq, qarray[(int)iq].lat, qarray[(int)iq].lon, qarray[1+(int)iq].lat, qarray[1+(int)iq].lon);
		} else {
			printf("%d ([%lf, %lf]) ",  (int)iq, qarray[iq].lat, qarray[iq].lon);
		}
		if ( FRAC(ip) != 0 ) {
			printf(", %.1lf ([%lf, %lf]-[%lf, %lf]) ", ip, parray[ip].lat, parray[ip].lon, parray[1+(int)ip].lat, parray[1+(int)ip].lon);
		} else {
			printf(", %d ([%lf, %lf]) ",  (int)ip, parray[ip].lat, parray[ip].lon);
		}
		if ( FRAC(iq) == 0 && FRAC(ip) == 0 ) {
			printf("%lf", qarray[iq].distanceTo(parray[ip]) );
			similarity += 1;
		} else if ( FRAC(iq) == 0 && FRAC(ip) != 0 ) {
			printf("%lf", qarray[(int)iq].distanceTo(parray[(int)ip],parray[1+(int)ip]) );
			similarity += 0.5;
		} else if ( FRAC(iq) != 0 && FRAC(ip) == 0 ) {
			printf("%lf", parray[ip].distanceTo(qarray[(int)iq],qarray[1+(int)iq]) );
			similarity += 0.5;
		} else {
			printf("error!");
		}
		printf("\n");
	}
	printf("similarity = %.1lf\n\n", similarity);

	/* write in csv format */
	/*
	for (auto i = result.second.begin(); i != result.second.end(); ++i) {
		gpspoint p = parray[i->first];
		printf("%lf,%lf,%lf\n", p.time, p.lat, p.lon);
	}
	printf("\n");
	*/
	return EXIT_SUCCESS; // return 0;
}
