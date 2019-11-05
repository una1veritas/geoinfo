#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
		return -1; // error
	varray->array_size = array_size;
	varray->count = 0;
	return 0; // no error
}

int discard_varray_gpspos(varray_gpspos * varray) {
	free(varray->array);
	return 0; // no error
}

int varray_gpspos_resize(varray_gpspos * varray) {
	gpspos * newarray = (gpspos*) malloc(sizeof(gpspos) * (varray->array_size<<1) );
	if ( newarray == NULL ) {
		fprintf(stderr, "varray_gpspos_resize failed.\n");
		return -1; //error
	}
	varray->array_size = varray->array_size<<1;
	for(int i = 0; i < varray->count; ++i) {
		newarray[i] = varray->array[i];
	}
	free(varray->array);
	varray->array = newarray;
	return 0;
}

int varray_gpspos_append(varray_gpspos * varray, gpspos pos) {
	if ( !(varray->count < varray->array_size) ) {
		if ( varray_gpspos_resize(varray) ) {
			fprintf(stderr, "varray_gpspos_resize failed.\n");
			return -1; // error
		}
	}
	varray->array[varray->count] = pos;
	++varray->count;
	return 0; // no error
}

int read_gpspos_csv(char * filename, varray_gpspos * array) {
	char buff[1024];
	FILE * fp = fopen(filename, "r");
	if (fp == NULL) {
		fprintf(stderr, "file open failed.\n");
		return -1; // error
	}
	gpspos pos;
	while (fgets(buff, 1024, fp) != NULL) {
		sscanf(buff,"%lf,%lf,%lf",&pos.time, &pos.lat, &pos.lon);
		if ( varray_gpspos_append(array, pos) ) {
			fprintf(stderr, "varray_gpspos_append: size overflow!\n");
		}
	}
	fclose(fp);
	return 0; // no error
}

int main(int argc, char **argv) {
	varray_gpspos posarray;
	init_varray_gpspos(&posarray, 64);
	read_gpspos_csv(argv[1], &posarray);
	printf("posarray capacity = %d\n", posarray.array_size);
	for(int i = 0; i < posarray.count; ++i) {
		printf("%d: %lf, %lf, %lf\n", i, posarray.array[i].time, posarray.array[i].lat, posarray.array[i].lon);
	}
	discard_varray_gpspos(&posarray);
	return 0;
}
