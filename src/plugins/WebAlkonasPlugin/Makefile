CC = g++
CFLAGS = $(shell wx-config --cflags) -g -Wall

all: WebAlkonasPlugin.o

WebAlkonasPlugin.o: WebAlkonasPlugin.h WebAlkonasPlugin.cc
	$(CC) -c WebAlkonasPlugin.cc -o WebAlkonasPlugin.o $(CFLAGS)

clean:
	rm -f *.o *~

