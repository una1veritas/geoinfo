PROJECT_ROOT = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

BUILD_MODE = debug

TARGET = geograph.exe
OBJS = main.o geograph.o

ifeq ($(BUILD_MODE),debug)
	CFLAGS += -g
	CXXFLAGS += -std=c++20
else ifeq ($(BUILD_MODE),run)
	CFLAGS += -O2
	CXXFLAGS += -std=c++20
else
	$(error Specify correct build mode $(BUILD_MODE) not supported by this Makefile)
endif

all:	$(TARGET)

$(TARGET):	$(OBJS)
	$(CXX) -o $@ $^  $(LIBDIRS) $(LIBRARIES)

INCLUDEDIRS = -I/usr/local/include/SDL2
LIBDIRS = 
LIBRARIES = -lSDL2main -lSDL2 -lSDL2_gfx

%.o:	$(PROJECT_ROOT)src/%.cpp
	$(CXX) -c $(CFLAGS) $(CXXFLAGS) $(CPPFLAGS) -o $@ $< $(INCLUDEDIRS) 

%.o:	$(PROJECT_ROOT)%.c
	$(CC) -c $(CFLAGS) $(CPPFLAGS) -o $@ $<

clean:
	rm -fr geograph.exe $(OBJS)
