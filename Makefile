# OpenDict Makefile
# Copyright (c) 2003-2005 Martynas Jocius <mjoc at akl.lt>

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
	cp copying.html $(HOME)
	chmod ugo+r $(HOME)/copying.html
	ln -sf $(HOME)/opendict.py /usr/bin/opendict
	chmod ugo+rx /usr/bin/opendict
	cp misc/opendict.desktop /usr/share/applications/
	chmod ugo+r /usr/share/applications/opendict.desktop

uninstall:
	rm -rf $(HOME)/*.*
	rm -rf $(HOME)/lib/
	rm -rf $(HOME)/pixmaps/
	rm -f /usr/bin/opendict
	rm -f /usr/share/locale/lt/LC_MESSAGES/opendict.mo
	rm -f /usr/share/applications/opendict.desktop

clean:
	for f in `find . -name '*.pyc'`; do rm $$f; done
	for f in `find . -name '*.pyo'`; do rm $$f; done
	for f in `find . -name '*.py~'`; do rm $$f; done
	for f in `find . -name '*~'`; do rm $$f; done
