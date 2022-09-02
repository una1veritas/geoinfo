/*This source code copyrighted by Lazy Foo' Productions (2004-2022)
and may not be redistributed without written permission.*/

//Using SDL and standard IO
#include <SDL.h>
#include <SDL2_gfxPrimitives.h>
//#include <iostream>
#include <stdio.h>

//Screen dimension constants
const int SCREEN_WIDTH = 640;
const int SCREEN_HEIGHT = 480;

int main( int argc, char* args[] ) {
	SDL_Window* window = NULL;

	int mx0 = -1, my0 = -1, mx1 = -1, my1 = -1;
	//Initialize SDL
	if( SDL_Init( SDL_INIT_VIDEO ) < 0 ) {
		printf( "Error %s: SDL couldn't initialize! \n", SDL_GetError() );
		return -1;
	}
	//Create window
	window = SDL_CreateWindow( "SDL Tutorial",
			SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
			SCREEN_WIDTH, SCREEN_HEIGHT, SDL_WINDOW_SHOWN );
	if( !window ) {
		printf( "Window could not be created! SDL_Error: %s\n", SDL_GetError() );
		return -1;
		SDL_Quit();
	}
	SDL_Renderer * renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);
	if ( !renderer ) {
		printf("Error %s: Could not create renderer\n", SDL_GetError());
		SDL_DestroyWindow( window );
		SDL_Quit();
		return -1;
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
		}

		// clear window

		SDL_SetRenderDrawColor(renderer, 242, 242, 242, 255);
		SDL_RenderClear(renderer);

		// TODO rendering code goes here
		if ( mx0 != -1 and mx1 != -1 ) {
			filledCircleColor(renderer, mx0, my0, 2, 0xffff0000); // 0xAABBGGRR --- endianness differs?
		    filledCircleColor(renderer, mx1, my1, 2, 0xffff0000);
			lineColor(renderer, mx0, my0, mx1, my1, 0xffff0000);
		}
		// render window

		SDL_RenderPresent(renderer);
	}

	SDL_DestroyRenderer(renderer);
	SDL_DestroyWindow( window );
	SDL_Quit();

	return 0;
}
