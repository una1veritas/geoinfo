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
//#include <SDL2_gfxPrimitives.h>

struct SDL2Window {
//private:
	SDL_Window* window;
	SDL_Renderer * renderer;

	static constexpr int SCREEN_WIDTH = 1024;
	static constexpr int SCREEN_HEIGHT = 768;

public:
	SDL2Window(const string & title,
			const int & width = SCREEN_WIDTH,
			const int & height = SCREEN_HEIGHT)
	: window(NULL), renderer(NULL) {
		if ( SDL_Init( SDL_INIT_VIDEO ) < 0 ) {
			cerr << "SDL Error: Initialize failed! " << SDL_GetError() << endl;
		} else {
			create_window(title, width, height);
			create_renderer();
		}
	}

	~SDL2Window() {
		if (renderer)
			SDL_DestroyRenderer(renderer);
		if (window)
			SDL_DestroyWindow( window );
		SDL_Quit();
	}

	void create_window(const string & title, const int & width, const int & height) {
		window = SDL_CreateWindow( title.c_str(),
				SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
				width, height, SDL_WINDOW_SHOWN );
		if( !window ) {
			cerr << "Error: Window could not be created! " << SDL_GetError() << endl;
		}
	}

	void create_renderer() {
		SDL_Renderer * renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);
		if ( !renderer ) {
			cerr << "Error: Could not create renderer! " << SDL_GetError() << endl;
		}
	}

};

vector<string> split(string& input, char delimiter) {
    istringstream stream(input);
    string field;
    vector<string> result;
    while (getline(stream, field, delimiter)) {
        result.push_back(field);
    }
    return result;
}

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
	vector<geopoint> mytrack;
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
    geograph roadsegs;
    for(unsigned int i = 0; i < mytrack.size(); ++i) {
    	geopoint & gp = mytrack[i];
    	bingeohash gid = bingeohash(gp.lat, gp.lon,37);
    	cout << gp << " ";
		std::set<std::pair<uint64_t,uint64_t>> edges;
    	for(unsigned int z = 0; z < 2; ++z) {
			vector<bingeohash> vec = gid.neighbors(z);
			cout << vec.size() << " ";
			edges.clear();
			for(const bingeohash & ghash : vec) {
				// binary search algorithm std::range
				for(auto & a_node : ggraph.geohash_range(ghash)) {
					for(auto & b : ggraph.adjacent_nodes(a_node.id())) {
						if (gp.distance_to(a_node.point(), ggraph.node(b).point()) <= 30.0) {
							roadsegs.insert_node(a_node);
							roadsegs.insert_node(ggraph.node(b));
							if (a_node.id() < b)
								edges.insert(std::pair<uint64_t,uint64_t>(a_node.id(),b));
							else
								edges.insert(std::pair<uint64_t,uint64_t>(b,a_node.id()));
						}
					}
				}
			}
    	}
    	cout << dec << edges.size() << " ";
    	for(auto & an_edge : edges) {
    		roadsegs.insert_edge(an_edge);
    		cout << "(" << an_edge.first << " - " << an_edge.second << "), ";
    	}
    	cout << endl;
    }
    cout << "finished." << endl;

    SDL2Window sdl2win("geograph", 1024, 768);
	bool quit = false;
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
				break;
				*/
		}
		// clear window

		SDL_SetRenderDrawColor(sdl2win.renderer, 192, 192, 192, 255);
		SDL_RenderClear(sdl2win.renderer);

		// TODO rendering code goes here
		/*
		if ( mx0 != -1 and mx1 != -1 ) {
			filledCircleColor(renderer, mx0, my0, 2, 0xffff0000); // 0xAABBGGRR --- endianness differs?
		    filledCircleColor(renderer, mx1, my1, 2, 0xffff0000);
			lineColor(renderer, mx0, my0, mx1, my1, 0xffff0000);
		}
		*/
		// render window

		SDL_RenderPresent(sdl2win.renderer);
	}

    return EXIT_SUCCESS;
}
