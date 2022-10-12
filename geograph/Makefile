#PROJECT_ROOT = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

BUILD_MODE = debug

TARGET = geograph.exe
OBJS = main.o geograph.o

ifeq ($(BUILD_MODE),debug)
	CFLAGS += -g
else ifeq ($(BUILD_MODE),run)
	CFLAGS += -O2
else
	$(error Specify correct build mode $(BUILD_MODE) not supported by this Makefile)
endif

ifeq ($(PLATHOME),macos)
#	INCLUDEDIRS = -I/usr/local/include/SDL2
	LIBDIRS = -L/usr/local/lib
	LIBRARIES = -lSDL2main -lSDL2 -lSDL2_gfx
	CXXFLAGS += -std=c++20
else ifeq ($(PLATHOME),mingw64)
	LIBRARIES = -lmingw32 -lSDL2main -lSDL2 -lSDL2_gfx
	CXXFLAGS += -std=c++2a
else ifeq ($(PLATHOME),ubuntu22)
	INCLUDEDIRS = 
	LIBDIRS = 
	LIBRARIES = -lSDL2main -lSDL2 -lSDL2_gfx
	CXXFLAGS += -std=c++2b
endif

showcomment:
	@echo "Use make PLATHOME=ubuntu22 or =mingw64 or=macos command to build executable."
	@echo "commands: clean, all"
	@echo
	
all:	$(TARGET)

$(TARGET):	$(OBJS)
	$(CXX) -o $@ $^  $(LIBDIRS) $(LIBRARIES)

%.o:	$(PROJECT_ROOT)src/%.cpp
	$(CXX) -c $(CFLAGS) $(CXXFLAGS) $(CPPFLAGS) -o $@ $< $(INCLUDEDIRS) 

%.o:	$(PROJECT_ROOT)%.c
	$(CC) -c $(CFLAGS) $(CPPFLAGS) -o $@ $<

clean:
	rm -fr geograph.exe $(OBJS)
