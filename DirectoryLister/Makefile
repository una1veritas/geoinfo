CC  = cc
CXX = c++

CFLAGS   =
CXXFLAGS = 

ifeq ($(BUILD_MODE),run)
	CFLAGS += -O2
	CXXFLAGS += -std=c++11
else
	CFLAGS += -g
	CXXFLAGS += -std=c++11
endif

OBJS = main.o
DEPHEADERS = DirectoryLister.h
TARGET = DirectoryLister.exe

all:	$(TARGET)

$(TARGET):	$(OBJS)
	$(CXX) -o $@ $^

%.o: 	%.cpp $(DEPHEADERS)
	$(CXX) -c $(CFLAGS) $(CXXFLAGS) -o $@ $<

#%.o:	$(PROJECT_ROOT)%.cpp
#	$(CXX) -c $(CFLAGS) $(CXXFLAGS) -o $@ $<
#

%.o: 	%.c
	$(CC) -c $(CFLAGS) $(CPPFLAGS) -o $@ $<

clean:
	rm -fr $(TARGET) build $(OBJS)
	
demo: $(TARGET)
	./$(TARGET) ../data_example
	