opendict:
	cd src/plugins/WebAlkonasPlugin/ && make && cd ../../..
	cd src && make

clean:
	cd src/plugins/WebAlkonasPlugin/ && make clean && cd ../../..
	cd src && make clean
