//============================================================================
// Name        : geograph_dijkstra.cpp
// Author      : 
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <fstream>
#include <iomanip>
#include <map>
#include <set>
#include <limits>
#include <vector>
#include <algorithm>
#include <cstdio>
#include <chrono>

#include <stdexcept>
#include <cinttypes>

#include "geograph.h"
#include "bgeohash.h"

#include <cmath>
#include "geodistance.h"
#include "cartcoord.h"

using namespace std;

vector<string> split(string& input, char delimiter) {
    istringstream stream(input);
    string field;
    vector<string> result;
    while (getline(stream, field, delimiter)) {
        result.push_back(field);
    }
    return result;
}

bool getfromcsv(const string & filename, geograph & ggraph) {
	ifstream csvf;
	csvf.open(filename);
	if (! csvf ) {
		cerr << "open a geograph file " << filename << " failed." << endl;
		return false;
	}
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
        vector<uint64_t> adjacents;
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	adjacents.push_back(stoull(strvec[i]));
        ggraph.insert(id, lat, lon, adjacents);
        adjacents.clear();
    }
    csvf.close();
    return true;
}
/*
 *
 *
#include <SDL2/SDL.h>
#include <SDL2/SDL2_gfxPrimitives.h>
 *
int show_in_sdl_window(const geograph & map, const std::vector<uint64_t> & d_track);
*/

std::map<uint64_t,double> dijkstra_dist_table(const geograph & graph, const uint64_t & start_id, const double & limit = std::numeric_limits<double>::infinity()) {
    std::set<uint64_t> R;
    std::map<uint64_t, double> dist;

    for(const auto & p : graph.nodemap() ){
    	R.insert(p.first);
    	//dist[p.first] = std::numeric_limits<double>::infinity();
    }

    dist[start_id] = 0;

    while ( R.size() > 0) {
    	uint64_t u = 0;
    	double nearest = std::numeric_limits<double>::infinity();

    	for(const auto & id : R) {
    		//if (dist[id] < nearest) {
        	if (dist.contains(id) and dist[id] < nearest) {
    			u = id;
    			nearest = dist[id];
    		}
    	}

    	if ( nearest == std::numeric_limits<double>::infinity() )
    		break;

    	if ( nearest > limit )
    		break;

    	R.erase(u);

    	for(const auto & adjid : graph.adjacent_nodes(u) ) {
    		double adjdist = graph.point(u).distance_to(graph.point(adjid));
    		if( R.contains(adjid) and (!dist.contains(adjid) or dist[adjid] > dist[u] + adjdist) ){
    			dist[adjid] = dist[u] + adjdist;
    		}

    	}
    }
    return dist;
}

std::vector<uint64_t> dijkstra_find_path(const geograph & graph,
		std::map<uint64_t, double> & dist, const uint64_t & start_id, const uint64_t & goal_id) {

	std::vector<uint64_t> path;
	path.push_back(goal_id);
	uint64_t current = goal_id;
	cout << start_id << ", " << dist[start_id] << ", " << goal_id << ", " << dist[goal_id] << endl;
	while( current != start_id ) {
		double mindist = std::numeric_limits<double>::infinity();
	    uint64_t minid = 0;
	    for(const auto & adjid : graph.adjacent_nodes(current) ) {
	    	double adjdist = graph.point(current).distance_to(graph.point(adjid));
	    	if(dist[adjid] - (dist[current] - adjdist) < mindist) {
	    		mindist = dist[adjid] - (dist[current] - adjdist);
	    		minid = adjid;
	    	}
	    }
	    //cout << mindist << endl;
	    current = minid;
	    path.push_back(current);
	}
	return path;
}

bool comp_by_second(const std::pair<uint64_t,double> & a, const std::pair<uint64_t,double> & b) {
		return a.second < b.second;
}

int main(int argc, char * argv[]) {
	enum {
		ROUND_TRIP = 0,
		DROP_BY = 1,
	} mode = ROUND_TRIP;

	if (argc < 5) {
		cerr << "usage: command [map-file_name] [start point lattitude] [longitude] [distance (m)] [drop-by point latitude] [longitude]" << endl;
		exit(EXIT_FAILURE);
	}

	string mapfilename = argv[1];
	geopoint startpt(std::stod(argv[2]), std::stod(argv[3]));
	double distance = std::stod(argv[4]);
	cout << mapfilename << " " << startpt << " " << distance << endl;
	geopoint dropbypt;
	if (argc >= 7) {
		mode = DROP_BY;
		dropbypt.lat = std::stod(argv[5]);
		dropbypt.lon = std::stod(argv[6]);
	}

	cout << "reading geograph file " << mapfilename << ". " << endl;
	geograph ggraph;
	getfromcsv(mapfilename, ggraph);
    cout << "goegraph size = " << dec << ggraph.size() << endl << endl;

    /* 学校正門前
     * geopoint start_coord(33.651759, 130.672120);
     * 新飯塚駅
     * geopoint goal_coord(33.644224, 130.693827);
     */

	uint64_t start_id = ggraph.node_nearest_to(startpt).id();
	uint64_t dropby_id = ggraph.node_nearest_to(dropbypt).id();

    std::map<uint64_t, double> d_from_start, d_from_dropby;
    std::chrono::system_clock::time_point start_clock, end_clock;

    start_clock = std::chrono::system_clock::now();

    cout << "calculate dists from start_id..." << endl;
    d_from_start = dijkstra_dist_table(ggraph, start_id, distance * 0.51);

	if (mode == DROP_BY) {
		cout << "calculate dists from dropby_id... " << endl;
		d_from_dropby = dijkstra_dist_table(ggraph, dropby_id, distance * 0.51);
	}
    end_clock = std::chrono::system_clock::now();
    cout << "time = " << std::chrono::duration_cast<std::chrono::milliseconds>(end_clock - start_clock).count() << " millis." << endl << endl;

    cout << "searching for a turning point..." << endl << endl;
    start_clock = std::chrono::system_clock::now();

    if(mode == DROP_BY){
    	std::vector<uint64_t> Q, R, path_start_to_dropby;
    	std::vector<std::pair<uint64_t,double>> d_from_start_vec, d_from_dropby_vec;
    	uint64_t t2, t3, min_id;
    	double difference, half_difference, fifty = 25;
    	int i = 1, check = 0;

    	cout << "dist of drop by point " << d_from_start[dropby_id] << endl;

    	path_start_to_dropby = dijkstra_find_path(ggraph, d_from_start, start_id, dropby_id);

    	cout << "found path." << endl;

    	difference = distance - d_from_start[dropby_id];

    	half_difference = difference / 2;

    	if(difference < d_from_start[dropby_id]){
    		cout << "Error: impossible distance." << endl;
    		exit(1);
    	}

    	cout << d_from_start.size() << endl << d_from_dropby.size() << endl;
    	for(auto & kv : d_from_start) {
    		d_from_start_vec.push_back(kv);
    	}

    	for(auto & kv : d_from_dropby) {
    		d_from_dropby_vec.push_back(kv);
    	}



		std::sort (d_from_start_vec.begin(), d_from_start_vec.end(), comp_by_second);
		std::sort (d_from_dropby_vec.begin(), d_from_dropby_vec.end(), comp_by_second);

    	for(const auto & a : d_from_start_vec) {
    		cout << "(" << a.first <<", " << a.second << "), ";
    	}
    	cout << endl;

		/*
    	while(check == 0){
    		double min = 10000;

			for(auto itr = d_from_start.cbegin(); itr != d_from_start.cend(); ++itr) {
				if(fabs(itr->second - half_difference) < fifty){
					X.push_back(itr->first);
				}
			}

			for(auto itr = d_from_dropby.cbegin(); itr != d_from_dropby.cend(); ++itr) {
				if(fabs(itr->second - half_difference) < fifty){
					Y.push_back(itr->first);
				}
			}

    		for(auto itr1 = X.cbegin(); itr1 != X.cend(); ++itr1){
    			for(auto itr2 = Y.cbegin(); itr2 != Y.cend(); ++itr2){
    				if(*itr1 == *itr2){
    					if(fabs(d_from_start[*itr1] + d_from_dropby[*itr2] - difference) < min){
    						min = d_from_start[*itr1] + d_from_dropby[*itr2];
    						min_id = *itr1;
    						check = 1;
    					}
    				}
    			}
    		}

    		fifty = fifty + 25;
    	}
    	*/

    	cout << "calculate now..." << endl;
    	cout << endl;

    	/*
    	t2 = min_id;

    	Q = dijkstra_find_path(ggraph, d_from_start, start_id, t2);

    	cout << "calculate now..." << endl;
    	cout << endl;

    	t3 = min_id;

    	R =  dijkstra_find_path(ggraph, d_from_start, dropby_id, t3);

    	cout << "calculate now..." << endl;
    	cout << endl;

    	std::reverse(Q.begin(), Q.end());

    	Q.insert(Q.cend(), R.cbegin(), R.cend());
    	Q.insert(Q.cend(), path_start_to_dropby.cbegin(), path_start_to_dropby.cend());

    	cout << "start" << endl;

    	for(auto itr = Q.cbegin(); itr != Q.cend(); ++itr) {
    		cout << i <<" id:" << dec << *itr << endl;
    	    i++;
    	}

    	cout << "goal" << endl;

    	cout << "real_distance = " << d_from_start[min_id] + d_from_dropby[min_id] + d_from_start[dropby_id] << endl;
    	 */
    	end_clock = std::chrono::system_clock::now();

    	cout << "caluculation_time = " << std::chrono::duration_cast<std::chrono::milliseconds>(end_clock - start_clock).count() << endl;

    	//show_in_sdl_window(ggraph, Q);

    } else {
    	double half_distance, difference;
    	uint64_t min_id;

    	half_distance = distance / 2;
    	difference = std::numeric_limits<double>::infinity();

    	for(auto itr = d_from_start.cbegin(); itr != d_from_start.cend(); ++itr){
    		if(fabs(itr->second - half_distance) < difference){
    			difference = fabs(itr->second - half_distance);
    			min_id = itr->first;
    		}
    	}

    	std::vector<uint64_t> Q, R;
    	uint64_t t = min_id;
    	int i = 1;

    	Q = dijkstra_find_path(ggraph, d_from_start, start_id, t);

    	R = Q;

    	std::reverse(Q.begin(), Q.end());

    	Q.insert(Q.cend(), R.cbegin(), R.cend());

    	cout << "start" << endl;

    	for(auto itr = Q.cbegin(); itr != Q.cend(); ++itr) {
    		cout << i <<" id:" << dec << *itr << endl;
    		i++;
    	}

    	cout << "goal" << endl;

    	cout << "real_distance = " << d_from_start[min_id] * 2 << endl;

    	end_clock = std::chrono::system_clock::now();

    	cout << "caluculationtime = " << std::chrono::duration_cast<std::chrono::milliseconds>(end_clock - start_clock).count() << endl;

    	//show_in_sdl_window(ggraph, Q);
    }

    return EXIT_SUCCESS;
}

/*
int show_in_sdl_window(const geograph & map, const std::vector<uint64_t> & d_track) {
	constexpr unsigned int WINDOW_MIN_WIDTH = 1024;
	constexpr unsigned int WINDOW_MIN_HEIGHT = 768;
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

	struct {
		unsigned int w, h;
	} winrect = {WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT};

	//georect area(d_track);
	georect area;
	geopoint gp = map.point(d_track[0]);

	area.north = gp.lat, area.east = gp.lon, area.south = gp.lat, area.west = gp.lon;

	for(const auto & i : d_track) {
		gp = map.point(i);

		area.east = std::min(area.east, gp.lon);
		area.west = std::max(area.west, gp.lon);
		area.south = std::min(area.south, gp.lat);
		area.north = std::max(area.north, gp.lat);
	}

	//cout << traj_area.width_meter() << ", " << traj_area.height_meter() << endl;
	// pixel per degree
	double vscale = 0.5 * double(WINDOW_MIN_HEIGHT) / (area.north - area.south);
	double hscale = 0.5 * double(WINDOW_MIN_HEIGHT) * area.aspect_ratio() / (area.west - area.east);
	georect viewarea(area);
	cout << "hscale = " << hscale << ", vscale = " << vscale << endl;
	if ( (SDL_Init( SDL_INIT_VIDEO ) < 0)
			or !(window = SDL_CreateWindow( "Geograph", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
					winrect.w, winrect.h, SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE))
			or !(renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE)) ) {
		cerr << "Error: " << SDL_GetError() << endl;
		return EXIT_FAILURE;
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
						viewarea.shift(diff_v, -diff_h);
						update = true;
					}
					if ( show_track == false ) {
						show_track = true;
						update = true;
					}
					dragging = false; // finish dragging
					break;
				case SDL_WINDOWEVENT:
					// resize function is still incomplete;
					// map-drawing of enlarged area is postponed
					// after the succeeding resize.
					switch (event.window.event) {
					case SDL_WINDOWEVENT_SIZE_CHANGED:
						winrect.w = event.window.data1;
						winrect.h = event.window.data2;
						//cout << "CHANGED " << winrect.h << ", " << winrect.w << endl;
						//break;
					//case SDL_WINDOWEVENT_RESIZED:
						update = true;
						//cout << "RESIZED" << endl;
						viewarea.south = viewarea.north - double(winrect.h) / vscale;
						viewarea.west = viewarea.east + double(winrect.w) / hscale;
						break;
					}
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
				georect drawrect(viewarea);
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
					for(unsigned int i = 0; i < d_track.size() - 1; ++i ) {
						const geopoint P = map.point(d_track[i]), Q = map.point(d_track[i+1]);
						if ( drawrect.contains(P) ) {
							int x0 = (P.lon - drawrect.east) * hscale;
							int y0 = (drawrect.north - P.lat) * vscale;
							c(0,0,0x7f);
							filledCircleColor(renderer, x0, y0, 2, c.color);
							int x1 = (Q.lon - drawrect.east) * hscale;
							int y1 = (drawrect.north - Q.lat) * vscale;
							filledCircleColor(renderer, x0, y0, 2, c.color);
							lineColor(renderer, x0, y0, x1, y1, c.color);
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
	return EXIT_SUCCESS;
}
*/
