POFILES=$(wildcard *.po)
MOFILES=$(POFILES:.po=.mo)

all: opendict.pot $(MOFILES)

install: all
	for file in $(MOFILES); do \
		lang=`echo $$file | sed 's/\.mo//'`; \
		install -d $(prefix)/share/locale/$$lang/LC_MESSAGES/; \
		install -m 0644 $$file $(prefix)/share/locale/$$lang/LC_MESSAGES/opendict.mo; \
	done

opendict.pot:
	@echo "Rebuilding the pot file"
	rm -f *.pot
	test -f /usr/bin/xgettext && /usr/bin/xgettext ../opendict.py ../lib/*.py ../lib/gui/*.py || echo
	cp messages.po opendict.pot
	rm -f messages.po

%.mo: %.po
	msgfmt --verbose --check -o $@ $<

%.po: opendict.pot
	@echo -n "Merging opendict.pot and $@"
	@msgmerge $@ opendict.pot -o $@.new
	@if [ "`diff $@ $@.new | grep '[<>]' | wc -l`" -ne 2 ]; then \
		mv -f $@.new $@; \
	else \
		rm -f $@.new; \
	fi
	@msgfmt --statistics $@

clean:
	rm -f $(MOFILES) messages messages.mo

uninstall:
	for file in $(MOFILES); do \
		lang=`echo $$file | sed 's/\.mo//'`; \
		rm -f $(prefix)/share/locale/$$lang/LC_MESSAGES/opendict.mo; \
	done
