# OpenDict Makefile
# Copyright (c) 2003 Martynas Jocius <mjoc@akl.lt>

HOME=/usr/share/opendict

install:
	mkdir -p $(HOME)
	cp -r lib/ $(HOME)
	chmod ugo+rx $(HOME)/lib
	chmod ugo+rx $(HOME)/lib/*
	cp -r pixmaps/ $(HOME)	
	chmod ugo+rx $(HOME)/pixmaps
	chmod ugo+rx $(HOME)/pixmaps/*
	cp po/lt/opendict.mo /usr/share/locale/lt/LC_MESSAGES/
	chmod ugo+r /usr/share/locale/lt/LC_MESSAGES/opendict.mo
	cp opendict.py $(HOME)
	chmod ugo+rx $(HOME)/opendict.py
	cp copying.txt $(HOME)
	chmod ugo+r $(HOME)/copying.txt
	ln -sf $(HOME)/opendict.py /usr/bin/opendict
	chmod ugo+rx /usr/bin/opendict
	cp misc/opendict.desktop /usr/share/applications/
	chmod ugo+r /usr/share/applications/opendict.desktop

uninstall:
	rm -rf $(HOME)
	rm -f /usr/bin/opendict
	rm -f /usr/share/locale/lt/LC_MESSAGES/opendict.mo
	rm -f /usr/share/applications/opendict.desktop
	
clean:
	rm -f lib/*.pyc
	rm -f lib/gui/*.pyc
	rm -f lib/extra/*.pyc 
