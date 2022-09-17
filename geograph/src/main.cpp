//============================================================================
// Name        : geograph.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <algorithm>

#include <stdexcept>
#include <cinttypes>

using std::pair;
using std::vector;
using std::cout;
using std::cerr;
using std::endl;

#include "bgeohash.h"
#include "geograph.h"

#include <cmath>
#include "geodistance.h"

#include <SDL2/SDL.h>
#include <SDL2/SDL2_gfxPrimitives.h>

vector<string> split(string& input, char delimiter) {
    istringstream stream(input);
    string field;
    vector<string> result;
    while (getline(stream, field, delimiter)) {
        result.push_back(field);
    }
    return result;
}

int show_in_sdl_window(const geograph & map, const std::vector<geopoint> & track, const std::vector<std::set<std::pair<uint64_t,uint64_t>>> & roadsegs);

int main(int argc, char * argv[]) {
	ifstream csvf;

	if (argc != 3) {
		cerr << "usage: command [geograph csv file name] [GPS trajectory csv file name]" << endl;
		exit(EXIT_FAILURE);
	}

	cout << "reading geograph file " << argv[1] << ". " << endl;
	csvf.open(argv[1]);
	if (! csvf ) {
		cerr << "open a geograph file " << argv[1] << " failed." << endl;
		exit(EXIT_FAILURE);
	}
	geograph ggraph;
    string line;
    while (getline(csvf, line)) {
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 4) {
        	cerr << "insufficient parameters to define a node_edge." << endl;
        	continue;
        }
		uint64_t id = stoull(strvec[0]);
		double lat = stod(strvec[1]);
		double lon = stod(strvec[2]);
        std::vector<uint64_t> adjacents;
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	adjacents.push_back(stoull(strvec[i]));
        ggraph.insert(id, lat, lon, adjacents);
        adjacents.clear();
    }
    csvf.close();

    /*
	// show some entries.
    int count = 0;
    for(const auto & a_pair : ggraph.nodemap()) {
    	cout << a_pair.second << endl;
    	count += 1;
    	if (count > 100) {
    		cout << "..." << endl;
    		break;
    	}
    }
    cout << endl;
    */

    cout << "goegraph size = " << std::dec << ggraph.size() << endl;

    cout << "reading GPS trajectory file." << endl;
	csvf.open(argv[2]);
	if (! csvf ) {
		cerr << "open a trajectory file '" << argv[2] << "' failed." << endl;
		exit(EXIT_FAILURE);
	}

	std::vector<geopoint> mytrack;
    while (getline(csvf, line)) {
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 2) {
        	cerr << "insufficient parameters for a point." << endl;
        	continue;
        }
        mytrack.push_back(geopoint(stod(strvec[2]), stod(strvec[3])));
    }
    csvf.close();


    // collect a sequence of road segments along with the points of the track.
    std::vector<std::set<std::pair<uint64_t,uint64_t>>> roadsegseq;
    for(unsigned int i = 0; i < mytrack.size(); ++i) {
    	roadsegseq.push_back(std::set<std::pair<uint64_t,uint64_t>>());
    	const geopoint & curr = mytrack[i];
    	const geopoint & prev = (i > 0) ? mytrack[i-1] : mytrack[i];
    	const geopoint & next = (i+1 < mytrack.size()) ? mytrack[i+1] : mytrack[i];
    	bgeohash ghash = curr.geohash(37);
		vector<bgeohash> ghashes = ghash.neighbors(1);
		std::set<geograph::geonode> neighbors;
		for(const bgeohash & ghash : ghashes) {
			//cout << ghash << ", ";
			const vector<geograph::geonode> & r = ggraph.geohash_range(ghash);
			neighbors.insert(r.begin(), r.end());
		}
    	const double delta = 21.0;
    	for(auto a : neighbors) {
			for(auto & b_id : ggraph.adjacent_nodes(a.id())) {
				const geograph::geonode & b = ggraph.node(b_id);
				geopoint currvec(prev, curr);
				geopoint abvec(a.point(), b.point());
				geopoint nextvec(curr, next);
				// 経路の断片と道の断片の擬似的な射影（なす角）
				double proj0 = prev.projection(curr, prev+(b.point() - a.point()));
				double proj1 = curr.projection(next, curr+(b.point() - a.point()));
				//cout << proj0 << ", " << proj1 << endl;
				if ((curr.distance_to(a.point()) <= delta and prev.distance_to(b.point()) <= delta)
						or (curr.distance_to(a.point()) <= delta and next.distance_to(b.point()) <= delta)) {
					if (a.id() < b.id())
						roadsegseq[i].insert(std::pair<uint64_t,uint64_t>(a.id(),b.id()));
					else if (b.id() < a.id())
						roadsegseq[i].insert(std::pair<uint64_t,uint64_t>(b.id(),a.id()));
					//cout << a.id() << ", " << b.id() << endl;
				}
				if (curr.distance_to(a.point(), b.point()) <= delta and (abs(proj0) >= 0.7 or abs(proj1) >= 0.7) ) {
					if (a.id() < b.id())
						roadsegseq[i].insert(std::pair<uint64_t,uint64_t>(a.id(),b.id()));
					else if (b.id() < a.id())
						roadsegseq[i].insert(std::pair<uint64_t,uint64_t>(b.id(),a.id()));
				}

			}
    	}
    	//cout << roadsegseq[i].size() << endl;
    }
    cout << "finished." << endl;
    show_in_sdl_window(ggraph, mytrack, roadsegseq);

    return EXIT_SUCCESS;
}

struct GeoRect {
	double north, east, south, west;

	GeoRect(const double & n, const double e, const double s, const double w) :
		north(n), east(e), south(s), west(w) { }

	GeoRect(const GeoRect & georect) :
		north(georect.north),
		east(georect.east),
		south(georect.south),
		west(georect.west) { }

	GeoRect & operator()(const double & n, const double e, const double s, const double w) {
		north = n;
		east = e;
		south = s;
		west = w;
		return *this;
	}

	GeoRect & shift(const double & lat, const double & lon) {
		north += lat; south += lat;
		east += lon; west += lon;
		return * this;
	}

	double width() const {
		return west - east;
	}

	double height() const {
		return north - south;
	}

	double width_meter() const {
		return geopoint((north+south)/2, east).distance_to(geopoint((north+south)/2,west));
	}

	double height_meter() const {
		return geopoint(south, east).distance_to(geopoint(north,east));
	}

	geopoint center() const {
		return geopoint((north+south)/2, (east+west)/2);
	}

	void include_inside(const geopoint & p) {
		east = std::min(east, p.lon);
		west = std::max(west, p.lon);
		south = std::min(south , p.lat);
		north = std::max(north, p.lat);
	}

	bool contains(const geopoint & p) const {
		return  (p.lat >= south) and (p.lat <= north)
				and (p.lon >= east) and (p.lon <= west);
	}
};

int show_in_sdl_window(const geograph & map, const std::vector<geopoint> & track, const std::vector<std::set<std::pair<uint64_t,uint64_t>>> & roadsegs) {
	SDL_Window * window = NULL;
	SDL_Renderer * renderer = NULL;
	union Color {
		struct {
			uint8_t r;
			uint8_t g;
			uint8_t b;
			uint8_t a;
		};
		uint32_t color;

		Color() : r(0), g(0), b(0), a(0xff) {}
		Color(uint8_t red, uint8_t grn, uint8_t blu, uint8_t alpha = 0xff) : r(red), g(grn), b(blu), a(alpha) {}
		Color & operator()(uint8_t red, uint8_t grn, uint8_t blu, uint8_t alpha = 0xff) {
			r = red; g = grn; b = blu; a = alpha;
			return *this;
		}
	} c, c2;
	int exit_value = EXIT_SUCCESS;
	constexpr unsigned int WINDOWSIZE = 1024;
	SDL_Rect winrect = { 0, 0, WINDOWSIZE, WINDOWSIZE };
	SDL_Rect worldrect = { 0, 0, 0, 0 };

	GeoRect maprect = { track[0].lat,track[0].lon,track[0].lat,track[0].lon };
	GeoRect viewrect = { 0,0,0,0 };

	for(auto & p : track)
		maprect.include_inside(p);

	cout << maprect.width_meter() << ", " << maprect.height_meter() << endl;
	double aspect = maprect.width_meter() / maprect.height_meter();
	double hscale, vscale;
	if (aspect > 1.0) {
		worldrect.h = WINDOWSIZE;
		worldrect.w = WINDOWSIZE * aspect;
	} else {
		worldrect.h = WINDOWSIZE;
		worldrect.w = WINDOWSIZE * aspect;
	}
	// pixel per degree
	vscale = double(worldrect.h) / (maprect.north - maprect.south);
	hscale = double(worldrect.w) / (maprect.west - maprect.east);
	viewrect(maprect.north, maprect.east,
			maprect.north - double(worldrect.h) / vscale,
			maprect.east + double(worldrect.w) / hscale);
	cout << "hscale = " << hscale << ", vscale = " << vscale << endl;
	if ( (SDL_Init( SDL_INIT_VIDEO ) < 0)
			or !(window = SDL_CreateWindow( "Geograph", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
					winrect.w, winrect.h, SDL_WINDOW_SHOWN ))
			or !(renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE)) ) {
		cerr << "Error: " << SDL_GetError() << endl;
		exit_value = EXIT_FAILURE;
	} else {
		int mx0 = 0, my0 = 0, mx1 = 0, my1 = 0;
		double diff_h = 0, diff_v = 0;
		Color c, c2;
		bool quit = false;
		bool update = true;
		bool show_track = true;
		bool dragging = false;
		SDL_Event event;
		while (!quit) {
			SDL_Delay(10);
			SDL_PollEvent(&event);
			switch (event.type)	{
				case SDL_QUIT:
					quit = true;
					break;
				// TODO input handling code goes here
				case SDL_MOUSEMOTION:
					if (dragging and
							(mx1 != event.button.x or my1 != event.button.y)) {
						mx1 = event.button.x;
						my1 = event.button.y;
						update = true;
						//cout << mx1 << ",  " << my1 << endl;
					}
					break;
				case SDL_MOUSEBUTTONDOWN:
					if (show_track == true ) {
						show_track = false;
						update = true;
					}
					dragging = true; // start dragging
					mx0 = event.button.x;
					my0 = event.button.y;
					mx1 = mx0; my1 = my0;
					break;
				case SDL_MOUSEBUTTONUP:
					if (mx0 != mx1 or my0 != my1) {
						diff_h = (mx1 - mx0) / hscale;
						diff_v = (my1 - my0) / vscale;
						mx0 = mx1; my0 = my1;
						viewrect.shift(diff_v, -diff_h);
						update = true;
					}
					if ( show_track == false ) {
						show_track = true;
						update = true;
					}
					dragging = false; // finish dragging
					break;
			}

			// TODO rendering code goes here
			if ( update ) {
				// clear window
				Color c, c2;
				c(242, 242, 242);
				SDL_SetRenderDrawColor(renderer, c.r, c.g, c.b, c.a);
				SDL_RenderClear(renderer);
				//cout << mx0 << ", " << my0 << "; " << mx1 << ", " << my1 << endl;
				// tweak the view rect
				diff_h = (mx1 - mx0) / hscale;
				diff_v = (my1 - my0) / vscale;
				GeoRect drawrect(viewrect);
				drawrect.shift(diff_v, -diff_h);

				for(auto itr = map.cbegin(); itr!= map.cend(); ++itr) {
					const geopoint & p = itr->second.point();
					if ( drawrect.contains(p) ) {
						int x0 = (p.lon - drawrect.east) * hscale;
						int y0 = (drawrect.north - p.lat) * vscale;
						//cout << p << " " << hscale << " " << vscale << endl;
						c(192,192,192);
						c2(64,64,64);
						filledCircleColor(renderer, x0, y0, 1, c.color);
						for(auto & adjid : map.adjacent_nodes(itr->first)) {
							int x1 = (map.node(adjid).point().lon - drawrect.east) * hscale;
							int y1 = (drawrect.north - map.node(adjid).point().lat) * vscale;
							filledCircleColor(renderer, x1, y1, 1, c2.color);
							lineColor(renderer, x0, y0, x1, y1, c.color);
							//cout << x0 << ", " << y0 << "; " << x1 << ", " << y1 << endl;
						}
					}
				}

				if ( show_track ) {
					for(unsigned int i = 0; i < track.size(); ++i ) {
						if ( drawrect.contains(track[i]) ) {
							int x0 = (track[i].lon - drawrect.east) * hscale;
							int y0 = (drawrect.north - track[i].lat) * vscale;
							c(0,0,0x7f);
							filledCircleColor(renderer, x0, y0, 2, c.color);
							if (i != 0) {
								int x1 = (track[i-1].lon - drawrect.east) * hscale;
								int y1 = (drawrect.north - track[i-1].lat) * vscale;
								filledCircleColor(renderer, x0, y0, 2, c.color);
								lineColor(renderer, x0, y0, x1, y1, c.color);
							}
							for(auto & e : roadsegs[i]) {
								const geopoint & a = map.point(e.first), & b = map.point(e.second);
								//cout << a << ", " << b << endl;
								int x0 = (a.lon - drawrect.east) * hscale;
								int y0 = (drawrect.north - a.lat) * vscale;
								int x1 = (b.lon - drawrect.east) * hscale;
								int y1 = (drawrect.north - b.lat) * vscale;
								c(160,128,0,96);
								thickLineColor(renderer, x0, y0, x1, y1, 3, c.color);
							}
						}
					}
				}

				SDL_RenderPresent(renderer);
				update = false;
			}
		}
	}
	if (renderer) {
		SDL_DestroyRenderer(renderer);
		renderer = NULL;
	}
	if (window) {
		SDL_DestroyWindow(window);
		window = NULL;
	}
	SDL_Quit();
	return exit_value;
}
