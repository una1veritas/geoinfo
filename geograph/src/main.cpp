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

int show_in_sdl_window(const geograph & gg);

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
    geograph roadgraph;
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
							roadgraph.insert_node(a_node);
							roadgraph.insert_node(ggraph.node(b));
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
    		roadgraph.insert_edge(an_edge);
    		cout << "(" << an_edge.first << " - " << an_edge.second << "), ";
    	}
    	cout << endl;
    }
    cout << "finished." << endl;
    show_in_sdl_window(roadgraph);

    return EXIT_SUCCESS;
}

int show_in_sdl_window(const geograph & gg) {
	int exit_value = EXIT_SUCCESS;
	SDL_Window* window = NULL;
	double hscale = double(1024) / gg.width();
	double vscale = double(768) / gg.height();

	int mx0 = -1, my0 = -1, mx1 = -1, my1 = -1;
	//Initialize SDL
	if( SDL_Init( SDL_INIT_VIDEO ) < 0 ) {
		cerr << "Error: Initializing SDL failed! " << SDL_GetError() << endl;
		exit_value = EXIT_FAILURE;
	} else {
		//Create window
		window = SDL_CreateWindow( "SDL Tutorial",
				SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
				1024, 768, SDL_WINDOW_SHOWN );
		if( !window ) {
			cerr << "Error: Window could not be created! " << SDL_GetError() << endl;
			exit_value = EXIT_FAILURE;
		} else {
			SDL_Renderer * renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);
			if ( !renderer ) {
				cerr << "Error: Could not create renderer! " << SDL_GetError() << endl;
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
					}

					// TODO rendering code goes here
					if ( update ) {
						// clear window
						SDL_SetRenderDrawColor(renderer, 242, 242, 242, 255);
						SDL_RenderClear(renderer);

						int cnt = 0;
						for(auto itr = gg.cbegin(); itr != gg.cend(); ++itr ) {
							const geopoint & pt = itr->second.point();
							int x = (pt.lon - gg.left()) * hscale;
							int y = (pt.lat - gg.bottom()) * vscale;
							filledCircleColor(renderer, x, y, 2, 0xff7f0000);
						}

						// render window
						SDL_RenderPresent(renderer);
						update = false;
					}
					//filledCircleColor(renderer, mx1, my1, 2, 0xff7f0000);


				}

				SDL_DestroyRenderer(renderer);
			}
			SDL_DestroyWindow( window );
		}
	}
	SDL_Quit();

	return exit_value;
}
