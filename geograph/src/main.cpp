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

int show_in_sdl_window(const geograph & map, const std::vector<geopoint> & track, const std::vector<std::set<std::pair<uint64_t,uint64_t>>> & roadsegs);

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

int show_in_sdl_window(const geograph & map, const std::vector<geopoint> & track, const std::vector<std::set<std::pair<uint64_t,uint64_t>>> & roadsegs) {
	int exit_value = EXIT_SUCCESS;
	SDLWindow sdlwin;
	SDL_Rect winrect = { 0, 0, 1024, 1024 };
	//int winwidth = 1024, winheight = 1024;

	struct {
		double east, west, south, north;

		double width() const {
			return geopoint(south, east).distance_to(geopoint(south,west));
		}
		double height() const {
			return geopoint(south, east).distance_to(geopoint(north,east));
		}
		bool contains(const geopoint & p) const {
			return  (p.lat >= south) and (p.lat <= north)
					and (p.lon >= east) and (p.lon <= west);
		}
	} maprect = { track[0].lon,track[0].lon,track[0].lat,track[0].lat },
	  viewrect = { 0,0,0,0 };

	for(auto & p : track) {
		maprect.east = std::min(maprect.east, p.lon);
		maprect.west = std::max(maprect.west, p.lon);
		maprect.south = std::min(maprect.south , p.lat);
		maprect.north = std::max(maprect.north, p.lat);
	}
	double aspect = maprect.width() / maprect.height();
	double hscale, vscale;
	if (aspect > 1.0) {
		hscale = double(winrect.w) / (maprect.west - maprect.east);
		winrect.h /= aspect;
		vscale = double(winrect.h) / (maprect.north - maprect.south);
	} else {
		vscale = double(winrect.h) / (maprect.north - maprect.south);
		winrect.w *= aspect;
		hscale = double(winrect.w) / (maprect.west - maprect.east);
	}
	cout << hscale << ", " << vscale << endl;
	if ( !sdlwin() or !sdlwin.open("Geograph", winrect.w, winrect.h)
			or !sdlwin.create_renderer() ) {
		cerr << "Error: " << sdlwin.last_error() << endl;
		exit_value = EXIT_FAILURE;
	} else {
		bool quit = false;
		bool update = true;
		bool show_track = true;
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
					if (show_track == true ) {
						show_track = false;
						update = true;
					}
					break;
				case SDL_MOUSEMOTION:
					break;
				case SDL_MOUSEBUTTONUP:
					if ( show_track == false ) {
						show_track = true;
						update = true;
					}
					break;
			}

			// TODO rendering code goes here
			if ( update ) {
				// clear window
				SDLWindow::Color c, c2;
				c(242, 242, 242);
				sdlwin.render_clear(c);

				for(auto itr = map.cbegin(); itr!= map.cend(); ++itr) {
					const geopoint & p = itr->second.point();
					if ( maprect.contains(p) ) {
						int x0 = (p.lon - maprect.east) * hscale;
						int y0 = (maprect.north - p.lat) * vscale;
						//cout << p << " " << hscale << " " << vscale << endl;

						c(192,192,192);
						c2(64,64,64);
						sdlwin.draw_filledCircle(x0, y0, 1, c2);
						for(auto & adjid : map.adjacent_nodes(itr->first)) {
							int x1 = (map.node(adjid).point().lon - maprect.east) * hscale;
							int y1 = (maprect.north - map.node(adjid).point().lat) * vscale;
							sdlwin.draw_filledCircle(x1, y1, 1, c2);
							sdlwin.draw_line(x0, y0, x1, y1, 1, c);
							//cout << x0 << ", " << y0 << "; " << x1 << ", " << y1 << endl;
						}
					}
				}

				if ( show_track ) {
					for(unsigned int i = 0; i < track.size(); ++i ) {
						int x0 = (track[i].lon - maprect.east) * hscale;
						int y0 = (maprect.north - track[i].lat) * vscale;
						c(0,0,0x7f);
						sdlwin.draw_filledCircle(x0, y0, 2, c);
						if (i != 0) {
							int x1 = (track[i-1].lon - maprect.east) * hscale;
							int y1 = (maprect.north - track[i-1].lat) * vscale;
							sdlwin.draw_filledCircle(x1, y1, 2, c);
							sdlwin.draw_line(x0, y0, x1, y1, 1, c);
						}
						for(auto & e : roadsegs[i]) {
							const geopoint & a = map.point(e.first), & b = map.point(e.second);
							//cout << a << ", " << b << endl;
							int x0 = (a.lon - maprect.east) * hscale;
							int y0 = (maprect.north - a.lat) * vscale;
							int x1 = (b.lon - maprect.east) * hscale;
							int y1 = (maprect.north - b.lat) * vscale;
							c(160,128,0,96);
							sdlwin.draw_line(x0, y0, x1, y1, 3, c);
						}
					}
				}

				sdlwin.render_present();
				update = false;
			}
		}
	}
	return exit_value;
}
