
CFLAGS += -g
INCLUDEDIRS = 
LIBDIRS = -L/usr/local/lib
LIBRARIES = -lSDL2main -lSDL2 -lSDL2_gfx
CXXFLAGS += -std=c++2b

TARGET = geograph.exe
OBJS = SDL_gfx_test.o

all:	$(TARGET)

$(TARGET):	$(OBJS)
	$(CXX) -o $@ $^  $(LIBDIRS) $(LIBRARIES)

%.o:	$(PROJECT_ROOT)src/%.cpp
	$(CXX) -c $(CFLAGS) $(CXXFLAGS) $(CPPFLAGS) -o $@ $< $(INCLUDEDIRS) 

%.o:	$(PROJECT_ROOT)%.c
	$(CC) -c $(CFLAGS) $(CPPFLAGS) -o $@ $<

clean:
	rm -fr geograph.exe $(OBJS)
