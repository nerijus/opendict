WX_CONFIG_PATH=wx-config
#WX_CONFIG_PATH=/usr/local/wxWindows.22/bin/wx-config

CC = $(shell $(WX_CONFIG_PATH) --cxx)
CFLAGS = $(shell $(WX_CONFIG_PATH) --cxxflags) -g -Wall
LIBS = $(shell $(WX_CONFIG_PATH) --libs) -g -Wall

all: opendict

WebAlkonasPlugin.o:
	cd plugins/WebAlkonasPlugin/ && make && cd ../..

DictParser.o: DictParser.h DictParser.cc
	$(CC) -c DictParser.cc -o DictParser.o $(CFLAGS)

SlowoParser.o: SlowoParser.h SlowoParser.cc
	$(CC) -c SlowoParser.cc -o SlowoParser.o $(CFLAGS)

MovaParser.o: MovaParser.h MovaParser.cc
	$(CC) -c MovaParser.cc -o MovaParser.o $(CFLAGS)

DictText.o: DictText.h DictText.cc
	$(CC) -c DictText.cc -o DictText.o $(CFLAGS)

DictWordList.o: DictWordList.h DictWordList.cc
	$(CC) -c DictWordList.cc -o DictWordList.o $(CFLAGS)

DictLetterList.o: DictLetterList.h DictLetterList.cc
	$(CC) -c DictLetterList.cc -o DictLetterList.o $(CFLAGS)

About.o: About.h About.cc
	$(CC) -c About.cc -o About.o $(CFLAGS)

MainWindow.o: MainWindow.h MainWindow.cc Fonts.h images/clear.xpm
	$(CC) -c MainWindow.cc -o MainWindow.o $(CFLAGS)

OpenDict.o: OpenDict.h OpenDict.cc
	$(CC) -c OpenDict.cc -o OpenDict.o $(CFLAGS)

opendict: DictParser.o SlowoParser.o DictText.o DictWordList.o \
	DictLetterList.o About.o MainWindow.o OpenDict.o \
	MovaParser.o \
	plugins/WebAlkonasPlugin/WebAlkonasPlugin.o
	$(CC) DictParser.o SlowoParser.o DictText.o DictWordList.o \
		DictLetterList.o About.o MainWindow.o OpenDict.o \
		MovaParser.o \
		plugins/WebAlkonasPlugin/WebAlkonasPlugin.o \
	-o opendict $(CFLAGS) $(LIBS)

clean:
	rm -f *.o *~ core opendict
