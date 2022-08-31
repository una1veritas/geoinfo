PROJECT_ROOT = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

OBJS = gpslcs.o gpspoint.o
HEADERS = gpspoint.h

ifeq ($(BUILD_MODE),debug)
	CXXFLAGS += -std=c++1z -g
else ifeq ($(BUILD_MODE),run)
	CXXFLAGS += -std=c++1z -O2
else 
	CXXFLAGS += -std=c++1z -g -Wall
#	$(error Build mode $(BUILD_MODE) not supported by this Makefile)
endif

TARGET = gpslcs.exe

all:	$(TARGET)

TESTOBJ = test.o

test.exe:   $(TESTOBJ)
	$(CXX) -o $@ $^

gpslcs.exe:	$(OBJS)
	$(CXX) -o $@ $^


%.o:	$(PROJECT_ROOT)%.cpp $(HEADERS)
	$(CXX) -c $(CXXFLAGS) -o $@ $<

%.o:	$(PROJECT_ROOT)%.c 
	$(CC) -c $(CFLAGS) -o $@ $<

clean:
	rm -fr *.exe $(OBJS) $(TESTOBJ)
