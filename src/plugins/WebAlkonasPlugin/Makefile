WX_CONFIG_PATH=wx-config
#WX_CONFIG_PATH=/usr/local/wxWindows.22/bin/wx-config

CC = $(shell $(WX_CONFIG_PATH) --cxx)
CFLAGS = $(shell $(WX_CONFIG_PATH) --cflags) -g -Wall

all: WebAlkonasPlugin.o

WebAlkonasPlugin.o: WebAlkonasPlugin.h WebAlkonasPlugin.cc
	$(CC) -c WebAlkonasPlugin.cc -o WebAlkonasPlugin.o $(CFLAGS)

clean:
	rm -f *.o *~

