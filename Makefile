# OpenDict Makefile
#

DESTDIR     = /usr
bindir	    = $(DESTDIR)/bin
icondir	    = $(DESTDIR)/share/icons/hicolor
opendictdir = $(DESTDIR)/share/opendict
mandir      = $(DESTDIR)/share/man/man1

install:
	mkdir -p $(opendictdir)/lib/extra
	mkdir -p $(opendictdir)/lib/gui
	cp -r lib/*.py $(opendictdir)/lib
	cp -r lib/extra/*.py $(opendictdir)/lib/extra
	cp -r lib/gui/*.py $(opendictdir)/lib/gui
	chmod -R a+rX $(opendictdir)/lib
	mkdir -p $(opendictdir)/pixmaps
	cp pixmaps/*.png $(opendictdir)/pixmaps
	chmod -R a+rX $(opendictdir)/pixmaps
	mkdir -p $(icondir)/24x24/apps
	mkdir -p $(icondir)/32x32/apps
	mkdir -p $(icondir)/48x48/apps
	mkdir -p $(icondir)/96x96/apps
	mkdir -p $(icondir)/scalable/apps
	cp pixmaps/icon-24x24.png $(icondir)/24x24/apps/opendict.png
	cp pixmaps/icon-32x32.png $(icondir)/32x32/apps/opendict.png
	cp pixmaps/icon-48x48.png $(icondir)/48x48/apps/opendict.png
	cp pixmaps/icon-96x96.png $(icondir)/96x96/apps/opendict.png
	cp pixmaps/SVG/icon-rune.svg $(icondir)/scalable/apps/opendict.svg

	$(MAKE) -C po install prefix=$(DESTDIR)

	cp opendict.py $(opendictdir)
	chmod a+rx $(opendictdir)/opendict.py
	cp copying.html $(opendictdir)
	chmod a+r $(opendictdir)/copying.html
	mkdir -p $(bindir)
	ln -sf $(opendictdir)/opendict.py $(bindir)/opendict
	mkdir -p $(DESTDIR)/share/applications
	cp misc/opendict.desktop $(DESTDIR)/share/applications
	chmod a+r $(DESTDIR)/share/applications/opendict.desktop
	mkdir -p $(mandir)
	cp opendict.1 $(mandir)

uninstall:
	rm -f $(DESTDIR)/share/applications/opendict.desktop
	rm -f $(bindir)/opendict
	rm -f $(opendictdir)/copying.html
	rm -f $(opendictdir)/opendict.py

	$(MAKE) -C po uninstall prefix=$(DESTDIR)

	rm -f $(icondir)/24x24/apps/opendict.png
	rm -f $(icondir)/32x32/apps/opendict.png
	rm -f $(icondir)/48x48/apps/opendict.png
	rm -f $(icondir)/96x96/apps/opendict.png
	rm -f $(icondir)/scalable/apps/opendict.svg
	rm -f $(opendictdir)/pixmaps/*.png
	rmdir $(opendictdir)/pixmaps
	rm -f $(opendictdir)/lib/gui/*.py*
	rm -f $(opendictdir)/lib/extra/*.py*
	rm -f $(opendictdir)/lib/*.py*
	rmdir $(opendictdir)/lib/extra
	rmdir $(opendictdir)/lib/gui
	rmdir $(opendictdir)/lib
	rmdir $(opendictdir)
	rm -f $(mandir)/opendict.*

clean:
	for f in `find . -name '*.pyc'`; do rm $$f; done
	for f in `find . -name '*.pyo'`; do rm $$f; done
	for f in `find . -name '*.py~'`; do rm $$f; done
	for f in `find . -name '*~'`; do rm $$f; done

	$(MAKE) -C po clean
