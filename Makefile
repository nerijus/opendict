# OpenDict Makefile
# 

DESTDIR     =
bindir	    = /usr/bin
datadir	    = /usr/share
opendictdir = $(datadir)/opendict

install:
	mkdir -p $(DESTDIR)$(opendictdir)
	cp -r lib/ $(DESTDIR)$(opendictdir)
	chmod ugo+rx $(DESTDIR)$(opendictdir)/lib
	chmod ugo+rx $(DESTDIR)$(opendictdir)/lib/*
	cp -r pixmaps/ $(DESTDIR)$(opendictdir)	
	chmod ugo+rx $(DESTDIR)$(opendictdir)/pixmaps
	chmod ugo+rx $(DESTDIR)$(opendictdir)/pixmaps/*

	$(MAKE) -C po install prefix=$(DESTDIR)

	cp opendict.py $(DESTDIR)$(opendictdir)
	chmod ugo+rx $(DESTDIR)$(opendictdir)/opendict.py
	cp copying.html $(DESTDIR)$(opendictdir)
	chmod ugo+r $(DESTDIR)$(opendictdir)/copying.html
	ln -sf $(DESTDIR)$(opendictdir)/opendict.py $(DESTDIR)$(bindir)/opendict
	chmod ugo+rx $(DESTDIR)$(bindir)/opendict
	cp misc/opendict.desktop $(DESTDIR)$(datadir)/applications/
	chmod ugo+r $(DESTDIR)$(datadir)/applications/opendict.desktop

uninstall:
	rm -rf $(DESTDIR)$(opendictdir)/*.*
	rm -rf $(DESTDIR)$(opendictdir)/lib/
	rm -rf $(DESTDIR)$(opendictdir)/pixmaps/
	rm -f $(DESTDIR)$(bindir)/opendict

	$(MAKE) -C po uninstall prefix=$(DESTDIR)

	rm -f $(DESTDIR)$(datadir)/applications/opendict.desktop
	
clean:
	for f in `find . -name '*.pyc'`; do rm $$f; done
	for f in `find . -name '*.pyo'`; do rm $$f; done
	for f in `find . -name '*.py~'`; do rm $$f; done
	for f in `find . -name '*~'`; do rm $$f; done

	$(MAKE) -C po clean
