#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
	double time, lat, lon;
} gpspos;

typedef struct {
	gpspos * array;
	unsigned int array_size;
	unsigned int count;
} varray_gpspos;

int init_varray_gpspos(varray_gpspos * varray, unsigned int array_size) {
	varray->array = (gpspos *) malloc(sizeof(gpspos)*array_size);
	if ( varray->array == NULL )
		return 0; // failed
	varray->array_size = array_size;
	varray->count = 0;
	return 1; // succeeded
}

int discard_varray_gpspos(varray_gpspos * varray) {
	free(varray->array);
	return 1; // succeed
}

int varray_gpspos_resize(varray_gpspos * varray) {
	gpspos * newarray = (gpspos*) malloc(sizeof(gpspos) * (varray->array_size<<1) );
	if ( newarray == NULL ) {
		fprintf(stderr, "varray_gpspos_resize failed.\n");
		return 0; // failed
	}
	varray->array_size = varray->array_size<<1;
	for(int i = 0; i < varray->count; ++i) {
		newarray[i] = varray->array[i];
	}
	free(varray->array);
	varray->array = newarray;
	return 1; // succeeded
}

int varray_gpspos_append(varray_gpspos * varray, gpspos pos) {
	if ( !(varray->count < varray->array_size) ) {
		if ( !varray_gpspos_resize(varray) ) {
			fprintf(stderr, "varray_gpspos_resize failed.\n");
			return 0; // failed
		}
	}
	varray->array[varray->count] = pos;
	++varray->count;
	return 1; // succeeded
}

int read_gpspos_csv(char * filename, varray_gpspos * array) {
	char buff[1024];
	FILE * fp = fopen(filename, "r");
	if (fp == NULL) {
		fprintf(stderr, "file open failed.\n");
		return 0; // failed
	}
	gpspos pos;
	while (fgets(buff, 1024, fp) != NULL) {
		sscanf(buff,"%lf,%lf,%lf",&pos.time, &pos.lat, &pos.lon);
		if ( !varray_gpspos_append(array, pos) ) {
			fprintf(stderr, "varray_gpspos_append: size overflow!\n");
		}
	}
	fclose(fp);
	return 1; // succeeded
}

#define DEG2RAD(x)  ((M_PI / 180.0) * (x))

double gpspos_distance(gpspos * p, gpspos * q) {
	//http://dtan4.hatenablog.com/entry/2013/06/10/013724
	//https://en.wikipedia.org/wiki/Geographical_distance#Ellipsoidal_Earth_projected_to_a_plane
	//https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
	//const int mode = 1;
    // 緯度，経度をラジアンに
	double  plat = DEG2RAD(p->lat),
			plon = DEG2RAD(p->lon),
			qlat = DEG2RAD(q->lat),
			qlon = DEG2RAD(q->lon);
    // 緯度と経度の差
    //double latdiff = plat - qlat, londiff = plon - qlon;
    // 平均緯度
    double latavr = (plat + qlat) / 2.0;

    // 測地系による値の違い
    double a = 6378137.0; //mode ? 6378137.0 : 6377397.155; // 赤道半径
    double b = 6356752.314140356; //mode ? 6356752.314140356 : 6356078.963; // 極半径
    //$e2 = ($a*$a - $b*$b) / ($a*$a);
    double e2 = 0.00669438002301188; //mode ? 0.00669438002301188 : 0.00667436061028297; // 第一離心率^2
    //$a1e2 = $a * (1 - $e2);
    double a1e2 = 6335439.32708317; // mode ? 6335439.32708317 : 6334832.10663254; // 赤道上の子午線曲率半径

    double sin_latavr = sin(latavr);
    double W2 = 1.0 - e2 * (sin_latavr*sin_latavr);
    double M = a1e2 / (sqrt(W2)*W2); // 子午線曲率半径M
    double N = a / sqrt(W2); // 卯酉線曲率半径

    double t1 = M * (plat - qlat); //latdiff;
    double t2 = N * cos(latavr) * (plon - qlon); //londiff;
    return sqrt((t1*t1) + (t2*t2));
}

int main(int argc, char **argv) {
	varray_gpspos posarray;
	init_varray_gpspos(&posarray, 128);
	read_gpspos_csv(argv[1], &posarray);
	for(int i = 0; i < posarray.count; ++i) {
		printf("%d: %lf, %lf, %lf",
				i, posarray.array[i].time,
				posarray.array[i].lat,
				posarray.array[i].lon);
		if ( i > 0 )
			printf("; (%lf)", gpspos_distance(&posarray.array[i-1], &posarray.array[i]));
		printf("\n");
	}
	discard_varray_gpspos(&posarray);
	return 0;
}
