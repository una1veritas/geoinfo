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
#include <stdio.h>
#include <time.h>
#include <chrono>

#include <stdexcept>
#include <cinttypes>

#include "geograph.h"
#include "bgeohash.h"

#include <cmath>
#include "geodistance.h"
#include "cartcoord.h"

//#include <SDL2/SDL.h>
//#include <SDL2/SDL2_gfxPrimitives.h>

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

//int show_in_sdl_window(const geograph & map, const std::vector<uint64_t> & d_track);

int main(int argc, char * argv[]) {
	ifstream csvf;

	if (argc < 2) {
		cerr << "usage: command map-file_name]" << endl;
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
        vector<uint64_t> adjacents;
        for(unsigned int i = 3; i < strvec.size(); ++i)
        	adjacents.push_back(stoull(strvec[i]));
        ggraph.insert(id, lat, lon, adjacents);
        adjacents.clear();
    }
    csvf.close();





    cout << "goegraph node size = " << dec << ggraph.size() << endl;
    cout << endl;

    double start_horizon, start_vartical;
	//double goal_horizon, goal_vartical;
	double distance;
	double target_horizon, target_vartical;
	string distination;

	cout << "start_coord = ?" << endl;
	cin >> start_horizon >> start_vartical;
	//cout << "goal_coord = ?" << endl;
	//cin >> goal_horizon >> goal_vartical;

	geopoint start_coord(start_horizon, start_vartical);
	//geopoint goal_coord(goal_horizon, goal_vartical);

	uint64_t osmid_start = ggraph.node_nearest_to(start_coord).id();
	//uint64_t osmid_goal = ggraph.node_nearest_to(goal_coord).id();

	cout << "start point = " << ggraph.node(osmid_start) << " id " << std::dec << osmid_start << endl;
	//cout << "goal point = " << ggraph.node(osmid_goal) << " id " << std::dec << osmid_goal << endl;

	cout << endl;

    uint64_t start_id = osmid_start;
    //uint64_t goal_id = osmid_goal;

    cout << "distance = ?" << endl;
    cin >> distance;

    if(distance < 0){
    	cout << "Error:Distance is incorrect" << endl;
    	exit(1);
    }

    cout << "Do you have a distination?" << endl;
    cout << "yes or no" << endl;
    cin >> distination;

    uint64_t target_id;
    if(distination == "yes" || distination == "Yes" || distination == "YES"){
    	cout << "target_coord = ?" << endl;
    	cin >> target_horizon >> target_vartical;

    	geopoint target_coord(target_horizon, target_vartical);
    	uint64_t osmid_target = ggraph.node_nearest_to(target_coord).id();
        cout << "target point = " << ggraph.node(osmid_target) << " id " << std::dec << osmid_target << endl;
        cout << endl;

        target_id = osmid_target;

    }

    /* 学校正門前
     * geopoint start_coord(33.651759, 130.672120);
     * 新飯塚駅
     * geopoint goal_coord(33.644224, 130.693827);
     */

    std::set<uint64_t> VP1, VP2;
    std::map<uint64_t, double> l1, l2;
    std::chrono::system_clock::time_point start_clock, end_clock;

    start_clock = std::chrono::system_clock::now();

    for(auto itr = ggraph.begin(); itr != ggraph.end(); ++itr){
    	VP1.insert(itr->first);
    	l1[itr->first] = std::numeric_limits<double>::infinity();
    }

    l1[start_id] = 0;

    cout << "calculate now..." << endl;
    cout << endl;

    while ( VP1.size() > 0) {
    	uint64_t u1 = 0;
    	double nearest = std::numeric_limits<double>::infinity();

    	for(auto & id : VP1) {
    		if (l1[id] < nearest) {
    			u1 = id;
    			nearest = l1[id];
    		}
    	}

    	if(nearest == std::numeric_limits<double>::infinity()){
    		break;
    	}

    	VP1.erase(u1);

    	for(auto itr = ggraph.adjacent_nodes(u1).cbegin();
    			itr != ggraph.adjacent_nodes(u1).cend(); ++itr) {
    		uint64_t v1 = *itr;

    		if(VP1.contains(v1) && l1[v1] > l1[u1] + ggraph.point(u1).distance_to(ggraph.point(v1))){
    			l1[v1] = l1[u1] + ggraph.point(u1).distance_to(ggraph.point(v1));
    		}

    	}
    }

    if(distination == "yes" || distination == "Yes" || distination == "YES"){
    	for(auto itr = ggraph.begin(); itr != ggraph.end(); ++itr){
    		VP2.insert(itr->first);
    		l2[itr->first] = std::numeric_limits<double>::infinity();
    	}

    	l2[target_id] = 0;

    	cout << "calculate now..." << endl;
    	cout << endl;

    	while ( VP2.size() > 0) {
    		uint64_t u2 = 0;
    		double nearest = std::numeric_limits<double>::infinity();

    		for(auto & id : VP2) {
    		    if (l2[id] < nearest) {
    		    	u2 = id;
    		    	nearest = l2[id];
    		    }
    		}

    		if(nearest == std::numeric_limits<double>::infinity()){
    		    	break;
    		}

    		VP2.erase(u2);

    		for(auto itr = ggraph.adjacent_nodes(u2).cbegin();
    		    	itr != ggraph.adjacent_nodes(u2).cend(); ++itr) {
    		    uint64_t v2 = *itr;

    		    if(VP2.contains(v2) && l2[v2] > l2[u2] + ggraph.point(u2).distance_to(ggraph.point(v2))){
    		    	l2[v2] = l2[u2] + ggraph.point(u2).distance_to(ggraph.point(v2));
    		    }

    		}
    	}
    }

    //cout << "distance = " << l[goal_id] << endl;
    //cout << endl;

    if(distination == "yes" || distination == "Yes" || distination == "YES"){
    	std::vector<uint64_t> Q, R, S, X, Y;
    	uint64_t s, t1, t2, t3, min_id;
    	double difference, half_difference, fifty = 25;
    	int i = 1, check = 0;

    	t1 = target_id;

    	S.push_back(t1);

    	while(t1 != start_id) {
    		double min = 10000;
    	    uint64_t m1 = 0;
    	    for(auto itr = ggraph.adjacent_nodes(t1).cbegin();
    	    		itr != ggraph.adjacent_nodes(t1).cend(); ++itr) {
    	    	s = *itr;

    	    	if(l1[s] - (l1[t1] - ggraph.point(t1).distance_to(ggraph.point(s))) < min){
    	    		min = l1[s] - (l1[t1] - ggraph.point(t1).distance_to(ggraph.point(s)));
    	    		m1 = s;
    	    	}
    	    }

    	    t1 = m1;
    	    S.push_back(t1);
    	}

    	cout << "calculate now..." << endl;
    	cout << endl;

    	difference = distance - l1[target_id];

    	half_difference = difference / 2;

    	if(difference < l1[t1]){
    		cout << "Error:Root not found" << endl;
    		exit(1);
    	}

    	while(check == 0){
    		double min = 10000;

    		for(auto itr = l1.cbegin(); itr != l1.cend(); ++itr){
    			if(fabs(itr->second - half_difference) < fifty){
    				X.push_back(itr->first);
    			}
    		}

    		for(auto itr = l2.cbegin(); itr != l2.cend(); ++itr){
    			if(fabs(itr->second - half_difference) < fifty){
    				Y.push_back(itr->first);
    			}
    		}

    		for(auto itr1 = X.cbegin(); itr1 != X.cend(); ++itr1){
    			for(auto itr2 = Y.cbegin(); itr2 != Y.cend(); ++itr2){
    				if(*itr1 == *itr2){
    					if(fabs(l1[*itr1] + l2[*itr2] - difference) < min){
    						min = l1[*itr1] + l2[*itr2];
    						min_id = *itr1;
    						check = 1;
    					}
    				}
    			}
    		}

    		fifty = fifty + 25;
    	}

    	cout << "calculate now..." << endl;
    	cout << endl;

    	t2 = min_id;

    	Q.push_back(t2);

    	while(t2 != start_id) {
    		double min = 10000;
    	    uint64_t m2 = 0;
    	    for(auto itr = ggraph.adjacent_nodes(t2).cbegin();
    	    		itr != ggraph.adjacent_nodes(t2).cend(); ++itr) {
    	    	s = *itr;

    	    	if(l1[s] - (l1[t2] - ggraph.point(t2).distance_to(ggraph.point(s))) < min){
    	    	    min = l1[s] - (l1[t2] - ggraph.point(t2).distance_to(ggraph.point(s)));
    	    	    m2 = s;
    	    	}
    	    }

    	    t2 = m2;
    	    Q.push_back(t2);
    	}

    	cout << "calculate now..." << endl;
    	cout << endl;

    	t3 = min_id;

    	R.push_back(t3);

    	while(t3 != target_id) {
    	    double min = 10000;
    	    uint64_t m3 = 0;
    	    for(auto itr = ggraph.adjacent_nodes(t3).cbegin();
    	    		itr != ggraph.adjacent_nodes(t3).cend(); ++itr) {
    	    	s = *itr;

    	    	if(l2[s] - (l2[t3] - ggraph.point(t3).distance_to(ggraph.point(s))) < min){
    	    	    min = l2[s] - (l2[t3] - ggraph.point(t3).distance_to(ggraph.point(s)));
    	    	    m3 = s;
    	    	}
    	    }

    	    t3 = m3;
    	    R.push_back(t3);
    	}

    	cout << "calculate now..." << endl;
    	cout << endl;

    	std::reverse(Q.begin(), Q.end());

    	Q.insert(Q.cend(), R.cbegin(), R.cend());
    	Q.insert(Q.cend(), S.cbegin(), S.cend());

    	cout << "start" << endl;

    	for(auto itr = Q.cbegin(); itr != Q.cend(); ++itr) {
    		cout << i <<" id:" << dec << *itr << endl;
    	    i++;
    	}

    	cout << "goal" << endl;

    	cout << "real_distance = " << l1[min_id] + l2[min_id] + l1[target_id] << endl;

    	end_clock = std::chrono::system_clock::now();

    	cout << "caluculation_time = " << std::chrono::duration_cast<std::chrono::milliseconds>(end_clock - start_clock).count() << endl;

    	//show_in_sdl_window(ggraph, Q);

    } else {
    	double half_distance, difference;
    	uint64_t min_id;

    	half_distance = distance / 2;
    	difference = std::numeric_limits<double>::infinity();

    	for(auto itr = l1.cbegin(); itr != l1.cend(); ++itr){
    		if(fabs(itr->second - half_distance) < difference){
    			difference = fabs(itr->second - half_distance);
    			min_id = itr->first;
    		}
    	}

    	std::vector<uint64_t> Q, R;
    	uint64_t s, t = min_id;
    	int i = 1;

    	Q.push_back(t);

    	while(t != start_id) {
    	double min = 10000;
    	uint64_t m = 0;
    	for(auto itr = ggraph.adjacent_nodes(t).cbegin();
    			itr != ggraph.adjacent_nodes(t).cend(); ++itr) {
    		s = *itr;

    	    if(l1[s] - (l1[t] - ggraph.point(t).distance_to(ggraph.point(s))) < min){
    	    	min = l1[s] - (l1[t] - ggraph.point(t).distance_to(ggraph.point(s)));
    	    	m = s;
    	    }
    	}

    	t = m;

    	Q.push_back(t);

    	}

    	R = Q;

    	std::reverse(Q.begin(), Q.end());

    	Q.insert(Q.cend(), R.cbegin(), R.cend());

    	cout << "start" << endl;

    	for(auto itr = Q.cbegin(); itr != Q.cend(); ++itr) {
    		cout << i <<" id:" << dec << *itr << endl;
    		i++;
    	}

    	cout << "goal" << endl;

    	cout << "real_distance = " << l1[min_id] * 2 << endl;

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
