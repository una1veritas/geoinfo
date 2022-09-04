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

#include <SDL2/SDL.h>
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

int show_in_sdl_window(const geograph & gg, const geograph & map, const geograph & track);

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
	geograph mytrack;
    while (getline(csvf, line)) {
        vector<string> strvec = split(line, ',');
        if (strvec.size() < 2) {
        	cerr << "insufficient parameters for a point." << endl;
        	continue;
        }
        mytrack.insert_node(mytrack.size(), stod(strvec[2]), stod(strvec[3]));
        if (mytrack.size() > 1)
        	mytrack.insert_edge_between(mytrack.size()-2, mytrack.size()-1);
    }
    csvf.close();

    // collect road segments on the map along with the points in the GPS trajectory.
    geograph roadgraph;
    for(unsigned int i = 0; i < mytrack.size(); ++i) {
    	const geopoint & gp = mytrack.node(i).point();
    	bingeohash gid = bingeohash(gp.lat, gp.lon,37);
    	//cout << gp << " ";
    	for(unsigned int z = 0; z < 2; ++z) {
			vector<bingeohash> vec = gid.neighbors(z);
			//cout << vec.size() << " ";
			for(const bingeohash & ghash : vec) {
				// binary search algorithm std::range
				for(auto & a_node : ggraph.geohash_range(ghash)) {
					for(auto & b : ggraph.adjacent_nodes(a_node.id())) {
						if (gp.distance_to(a_node.point(), ggraph.node(b).point()) <= 21.0) {
							roadgraph.insert_node(a_node);
							roadgraph.insert_node(ggraph.node(b));
							roadgraph.insert_edge_between(a_node.id(),b);
						}
					}
				}
			}
    	}
    	//cout << dec << edges.size() << " ";
    	//cout << endl;
    }
    cout << "finished." << endl;
    show_in_sdl_window(roadgraph, ggraph, mytrack);

    return EXIT_SUCCESS;
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

	void render_clear(uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
		SDL_SetRenderDrawColor(renderer, g, g, b, a);
		SDL_RenderClear(renderer);
	}

	void render_present() {
		SDL_RenderPresent(renderer);
	}
	const std::string & last_error() const {
		return err_msg;
	}
};

int show_in_sdl_window(const geograph & route, const geograph & map, const geograph & path) {
	int exit_value = EXIT_SUCCESS;
	SDLWindow sdlwin;
	int winwidth = 1024, winheight = 1024;
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
				sdlwin.render_clear(242,242,242,255);

				for(auto itr = map.cbegin(); itr!= map.cend(); ++itr) {
					const geopoint & p = itr->second.point();
					if (p.lat > route.south() and p.lat < route.north()
							and p.lon > route.east() and p.lon < route.west() ) {
						int x0 = (p.lon - route.east()) * hscale;
						int y0 = (route.north() - p.lat) * vscale;
						filledCircleColor(sdlwin.renderer, x0, y0, 1, 0xff000000);
						for(auto & adjid : map.adjacent_nodes(itr->first)) {
							int x1 = (map.node(adjid).point().lon - route.east()) * hscale;
							int y1 = (route.north() - map.node(adjid).point().lat) * vscale;
							filledCircleColor(sdlwin.renderer, x1, y1, 1, 0xff000000);
							lineColor(sdlwin.renderer, x0, y0, x1, y1, 0xff000000);
						}
					}
				}
				for(auto itr = path.cbegin(); itr != path.cend(); ++itr ) {
					const geopoint & p = itr->second.point();
					int x0 = (p.lon - route.east()) * hscale;
					int y0 = (route.north() - p.lat) * vscale;
					filledCircleColor(sdlwin.renderer, x0, y0, 2, 0xff7f0000);
					for(auto & adjid : path.adjacent_nodes(itr->first)) {
						int x1 = (path.node(adjid).point().lon - route.east()) * hscale;
						int y1 = (route.north() - path.node(adjid).point().lat) * vscale;
						filledCircleColor(sdlwin.renderer, x1, y1, 2, 0x7f0000);
						thickLineColor(sdlwin.renderer, x0, y0, x1, y1, 1, 0xff7f0000);
					}
				}
				for(auto itr = route.cbegin(); itr != route.cend(); ++itr ) {
					const geopoint & pt = itr->second.point();
					int x0 = (pt.lon - route.east()) * hscale;
					int y0 = (route.north() - pt.lat) * vscale;
					filledCircleColor(sdlwin.renderer, x0, y0, 2, 0x7f00007f);
					for(auto & adjid : route.adjacent_nodes(itr->first)) {
						int x1 = (route.node(adjid).point().lon - route.east()) * hscale;
						int y1 = (route.north() - route.node(adjid).point().lat) * vscale;
						filledCircleColor(sdlwin.renderer, x1, y1, 2, 0x7f00007f);
						thickLineColor(sdlwin.renderer, x0, y0, x1, y1, 3, 0x7f0000f7);
					}
				}
				sdlwin.render_present();
				update = false;
			}
		}
	}
	return exit_value;
}
