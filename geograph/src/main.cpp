//============================================================================
// Name        : geograph.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <iomanip>
#include <algorithm>

#include <stdexcept>
#include <cinttypes>

using std::pair;
using std::vector;
using std::cout;
using std::cerr;
using std::endl;

#include "bingeohash.h"
#include "geograph.h"

#include <cmath>
#include "geodistance.h"

#include <SDL.h>
#include <SDL2_gfxPrimitives.h>

vector<string> split(string& input, char delimiter) {
    istringstream stream(input);
    string field;
    vector<string> result;
    while (getline(stream, field, delimiter)) {
        result.push_back(field);
    }
    return result;
}

struct SDLWindow {
	SDL_Window * window;
	SDL_Renderer * renderer;

	int status;
	std::string err_msg;

	enum STATUS_CODE{
		NO_ERR = 0,
		SDL_INIT_ERR,
		SDL_CREATEWINDOW_ERR,
		SDL_CREATERENDERER_ERR,
	};

	union Color {
		struct {
			uint8_t red;
			uint8_t grn;
			uint8_t blu;
			uint8_t alpha;
		};
		uint32_t color;

		Color(void)	: red(0), grn(0), blu(0), alpha(0) { }
		Color(uint8_t r, uint8_t g, uint8_t b, uint8_t a = 0xff)
		: red(r), grn(g), blu(b), alpha(a) { }

		Color & operator()(uint8_t r, uint8_t g, uint8_t b, uint8_t a = 0xff) {
			red = r; grn = g; blu = b; alpha = a;
			return *this;
		}
	};

	SDLWindow() : window(NULL), renderer(NULL), status(NO_ERR), err_msg() {
		init();
	}

	~SDLWindow() {
		if (renderer) {
			SDL_DestroyRenderer(renderer);
			renderer = NULL;
		}
		if (window) {
			SDL_DestroyWindow(window);
			window = NULL;
		}
		SDL_Quit();
	}

	bool operator()(void) const {
		return status == NO_ERR;
	}

	bool init() {
		if (SDL_Init( SDL_INIT_VIDEO ) < 0) {
			err_msg = SDL_GetError();
			status = SDL_INIT_ERR;
			return false;
		}
		return true;
	}

	bool open(const std::string & title, const int & w, const int & h) {
		window = SDL_CreateWindow( title.c_str(),
				SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, w, h, SDL_WINDOW_SHOWN );
		if( !window ) {
			err_msg = SDL_GetError();
			status = SDL_CREATEWINDOW_ERR;
			return false;
		}
		return true;
	}

	bool create_renderer() {
		renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);
		if ( !renderer ) {
			err_msg = SDL_GetError();
			status = SDL_CREATERENDERER_ERR;
			return false;
		}
		return true;
	}

	void render_clear(const Color & c) {
		SDL_SetRenderDrawColor(renderer, c.red, c.grn, c.blu, c.alpha);
		SDL_RenderClear(renderer);
	}

	void render_present() {
		SDL_RenderPresent(renderer);
	}

	void draw_line(const int & x0, const int & y0, const int & x1, const int & y1, const uint8_t & w, const Color & c) {
		if (w <= 1) {
			lineColor(renderer, x0, y0, x1, y1, c.color);
		} else {
			thickLineColor(renderer, x0, y0, x1, y1, w, c.color);
		}
	}

	void draw_filledCircle(const int & x, const int & y, const int & r, const Color & c) {
		filledCircleColor(renderer, x, y, r, c.color);
	}

	void draw_circle(const int & x, const int & y, const int & r, const Color & c) {
		circleColor(renderer, x, y, r, c.color);
	}

	const std::string & last_error() const {
		return err_msg;
	}
};

int show_in_sdl_window(const geograph & map, const std::vector<geopoint> & track);

int main(int argc, char * argv[]) {
	ifstream csvf;

	if (argc != 3) {
		cerr << "usage: command [geograph csv file name] [GPS trajectory csv file name]" << endl;
		exit(EXIT_FAILURE);
	}

	cout << "reading geograph file." << endl;
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

    // collect road segments on the map along with the points in the GPS trajectory.
    std::vector<std::set<uint64pair>> proxedges;
    for(unsigned int i = 0; i < mytrack.size(); ++i) {
    	proxedges.push_back(std::set<uint64pair>());
    	const geopoint & curr = mytrack[i];
    	const geopoint & prev = (i > 0) ? mytrack[i-1] : mytrack[i];
    	const geopoint & next = (i+1 < mytrack.size()) ? mytrack[i+1] : mytrack[i];
    	bingeohash gid = bingeohash(curr.lat, curr.lon,37);
    	//cout << curr << " ";
    	std::set<geograph::geonode> prox_nodes;
    	for(unsigned int z = 0; z < 2; ++z) {
			vector<bingeohash> vec = gid.neighbors(z);
			for(const bingeohash & ghash : vec) {
				const vector<geograph::geonode> & r = ggraph.geohash_range(ghash);
				prox_nodes.insert(r.begin(), r.end());
			}
    	}
    	const double delta = 21.0;
    	for(auto a : prox_nodes) {
			for(auto & b_id : ggraph.adjacent_nodes(a.id())) {
				const geograph::geonode & b = ggraph.node(b_id);
				geopoint currvec(curr.lat - prev.lat, curr.lon - prev.lon);
				geopoint abvec(b.point().lat - a.point().lat, b.point().lon - a.point().lon);
				geopoint nextvec(next.lat - curr.lat, next.lon - curr.lon);
				double proj0 = geopoint().projection(currvec, abvec);
				double proj1 = geopoint().projection(nextvec, abvec);
				cout << proj0 << ", " << proj1 << endl;
				if (curr.distance_to(a.point()) <= delta and curr.distance_to(b.point()) <= delta) {
					proxedges[i].insert(uint64pair(a.id(),b.id()));
					continue;
				}
				if (curr.distance_to(a.point(), b.point()) <= delta and (abs(proj0) >= 0.7 or abs(proj1) >= 0.7) ) {
					proxedges[i].insert(uint64pair(a.id(),b.id()));
				}
			}
    	}
    	//cout << dec << edges.size() << " ";
    	//cout << endl;
    }
    cout << "finished." << endl;
    show_in_sdl_window(ggraph, mytrack);

    return EXIT_SUCCESS;
}

int show_in_sdl_window(const geograph & map, const std::vector<geopoint> & track) {
	int exit_value = EXIT_SUCCESS;
	SDLWindow sdlwin;
	int winwidth = 1024, winheight = 1024;
	struct {
		double north, south, east, west;
	} track_bbox {track[0].lat, track[0].lat, track[0].lon, track[0].lon};
	double bbox_width;
	double bbox_height;
	double aspect = route.eastwest()/route.northsouth();
	double hscale, vscale;
	if (aspect > 1.0) {
		hscale = double(winwidth) / route.width();
		winheight /= aspect;
		vscale = double(winheight) / route.height();
	} else {
		vscale = double(winheight) / route.height();
		winwidth *= aspect;
		hscale = double(winwidth) / route.width();
	}
	if ( !sdlwin() or !sdlwin.open("Geograph", winwidth, winheight)
			or !sdlwin.create_renderer() ) {
		cerr << "Error: " << sdlwin.last_error() << endl;
		exit_value = EXIT_FAILURE;
} else {
		bool quit = false;
		bool update = true;
		SDL_Event event;
		while (!quit) {
			SDL_Delay(10);
			SDL_PollEvent(&event);

			switch (event.type)	{
				case SDL_QUIT:
					quit = true;
					break;
				// TODO input handling code goes here
					/*
				case SDL_MOUSEBUTTONDOWN:
					mx0 = event.button.x;
					my0 = event.button.y;
					break;
				case SDL_MOUSEMOTION:
					mx1 = event.button.x;
					my1 = event.button.y;
					break;
				case SDL_MOUSEBUTTONUP:
					mx0 = my0 = mx1 = my1 = -1;
					update = true;
					break;
					*/
			}

			// TODO rendering code goes here
			if ( update ) {
				// clear window
				SDLWindow::Color c;
				c(242, 242, 242);
				sdlwin.render_clear(c);

				for(auto itr = map.cbegin(); itr!= map.cend(); ++itr) {
					const geopoint & p = itr->second.point();
					if (p.lat > route.south() and p.lat < route.north()
							and p.lon > route.east() and p.lon < route.west() ) {
						int x0 = (p.lon - route.east()) * hscale;
						int y0 = (route.north() - p.lat) * vscale;
						c(128,128,128);
						sdlwin.draw_filledCircle(x0, y0, 1, c);
						for(auto & adjid : map.adjacent_nodes(itr->first)) {
							int x1 = (map.node(adjid).point().lon - route.east()) * hscale;
							int y1 = (route.north() - map.node(adjid).point().lat) * vscale;
							sdlwin.draw_filledCircle(x1, y1, 1, c);
							sdlwin.draw_line(x0, y0, x1, y1, 1, c);
						}
					}
				}
				for(auto itr = track.cbegin(); itr != track.cend(); ++itr ) {
					const geopoint & p = itr->second.point();
					int x0 = (p.lon - route.east()) * hscale;
					int y0 = (route.north() - p.lat) * vscale;
					c(0,0,0x7f);
					sdlwin.draw_filledCircle(x0, y0, 2, c);
					for(auto & adjid : track.adjacent_nodes(itr->first)) {
						int x1 = (track.node(adjid).point().lon - route.east()) * hscale;
						int y1 = (route.north() - track.node(adjid).point().lat) * vscale;
						sdlwin.draw_filledCircle(x1, y1, 2, c);
						sdlwin.draw_line(x0, y0, x1, y1, 1, c);
					}
				}
				for(auto itr = route.cbegin(); itr != route.cend(); ++itr ) {
					const geopoint & pt = itr->second.point();
					int x0 = (pt.lon - route.east()) * hscale;
					int y0 = (route.north() - pt.lat) * vscale;
					c(192,64,0,64);
					sdlwin.draw_filledCircle(x0, y0, 2, c);
					for(auto & adjid : route.adjacent_nodes(itr->first)) {
						int x1 = (route.node(adjid).point().lon - route.east()) * hscale;
						int y1 = (route.north() - route.node(adjid).point().lat) * vscale;
						sdlwin.draw_filledCircle(x1, y1, 2, c);
						sdlwin.draw_line(x0, y0, x1, y1, 3, c);
					}
				}
				sdlwin.render_present();
				update = false;
			}
		}
	}
	return exit_value;
}
