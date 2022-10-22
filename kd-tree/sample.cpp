#include <iostream>
#include <array>
#include <vector>

//#include <opencv2/opencv.hpp>
//Using SDL
#include <SDL2/SDL.h>
#include <SDL2/SDL2_gfxPrimitives.h>

#include "kdtree.h"

using namespace std;

// user-defined point type
// inherits std::array in order to use operator[]
class MyPoint : public std::array<double, 2>
{
public:

	// dimension of space (or "k" of k-d tree)
	// KDTree class accesses this member
	static const int DIM = 2;

	// the constructors
	MyPoint() {}
	MyPoint(double x, double y)
	{ 
		(*this)[0] = x;
		(*this)[1] = y;
	}

	// conversion to OpenCV Point2d
	//operator cv::Point2d() const { return cv::Point2d((*this)[0], (*this)[1]); }
	int x() const { return at(0); }
	int y() const { return at(1); }
};

int main(int argc, char **argv)
{
	const int seed = argc > 1 ? stoi(argv[1]) : 0;
	srand(seed);

	// generate space
	const int width = 500;
	const int height = 500;

	// generate points
	const int npoints = 100;
	vector<MyPoint> points(npoints);
	for (int i = 0; i < npoints; i++)
	{
		const int x = rand() % width;
		const int y = rand() % height;
		points[i] = MyPoint(x, y);
	}

	// build k-d tree
	kdt::KDTree<MyPoint> kdtree(points);

	SDL_Window* window = NULL;
	if( SDL_Init( SDL_INIT_VIDEO ) < 0 ) {
		cerr << "Error: Initializing SDL failed! " << SDL_GetError() << endl;
		return EXIT_FAILURE;
	}
	//Create window
	window = SDL_CreateWindow( "kd-tree",
			SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
			width, height, SDL_WINDOW_SHOWN );
	if( !window ) {
		cerr << "Error: Window could not be created! " << SDL_GetError() << endl;
		return EXIT_FAILURE;
		SDL_Quit();
	}
	SDL_Renderer * renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);
	if ( !renderer ) {
		cerr << "Error: Could not create renderer! " << SDL_GetError() << endl;
		SDL_DestroyWindow( window );
		SDL_Quit();
		return EXIT_FAILURE;
	}

	int quit = 0;
	SDL_Event event;
	while (!quit) {
		SDL_Delay(10);
		SDL_PollEvent(&event);

		switch (event.type)	{
			case SDL_QUIT:
				quit = 1;
				break;
			// TODO input handling code goes here
			case SDL_MOUSEBUTTONDOWN:
				break;
			case SDL_MOUSEMOTION:
				break;
			case SDL_MOUSEBUTTONUP:
				break;
		}

		// clear window
		SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
		SDL_RenderClear(renderer);

		// TODO rendering code goes here
		//cv::Mat img = cv::Mat::zeros(cv::Size(width, height), CV_8UC3);
		for (const auto& pt : points) {
			//cv::circle(img, cv::Point2d(pt), 1, cv::Scalar(0, 255, 255), -1);
			circleColor(renderer, pt.x(), pt.y(), 1, 0xffffff00);// 0xAABBGGRR
		}

		// generate query (center of the space)
		const MyPoint query(0.5 * width, 0.5 * height);
		//cv::circle(img, cv::Point2d(query), 1, cv::Scalar(0, 0, 255), -1);
		circleColor(renderer, query.x(), query.y(), 1, 0xffff0000);// 0xAABBGGRR

		// nearest neigbor search
		//const cv::Mat I0 = img.clone();
		const int idx = kdtree.nnSearch(query);
		//cv::circle(I0, cv::Point2d(points[idx]), 1, cv::Scalar(255, 255, 0), -1);
		circleColor(renderer, points[idx].x(), points[idx].y(), 1, 0xff00ffff);
		//cv::line(I0, cv::Point2d(query), cv::Point2d(points[idx]), cv::Scalar(0, 0, 255));
		lineColor(renderer, query.x(), query.y(), points[idx].x(), points[idx].y(), 0xffff0000);

		// k-nearest neigbors search
		//const cv::Mat I1 = img.clone();
		const int k = 10;
		const vector<int> knnIndices = kdtree.knnSearch(query, k);
		for (int i : knnIndices) {
			//cv::circle(I1, cv::Point2d(points[i]), 1, cv::Scalar(255, 255, 0), -1);
			circleColor(renderer, points[i].x(), points[i].y(), 1, 0xff00ffff);
			//cv::line(I1, cv::Point2d(query), cv::Point2d(points[i]), cv::Scalar(0, 0, 255));
			lineColor(renderer, query.x(), query.y(), points[i].x(), points[i].y(), 0xffff0000);
		}

		/*
		// radius search
		const cv::Mat I2 = img.clone();
		const double radius = 50;
		const std::vector<int> radIndices = kdtree.radiusSearch(query, radius);
		for (int i : radIndices)
			cv::circle(I2, cv::Point2d(points[i]), 1, cv::Scalar(255, 255, 0), -1);
		cv::circle(I2, cv::Point2d(query), cvRound(radius), cv::Scalar(0, 0, 255));

		// show results
		cv::imshow("Nearest neigbor search", I0);
		cv::imshow("K-nearest neigbors search (k = 10)", I1);
		cv::imshow("Radius search (radius = 50)", I2);

		cv::waitKey(0);
		*/

		// render window

		SDL_RenderPresent(renderer);
	}

	SDL_DestroyRenderer(renderer);
	SDL_DestroyWindow( window );
	SDL_Quit();

	return 0;
}
