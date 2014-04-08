POFILES=$(wildcard *.po)
MOFILES=$(POFILES:.po=.mo)

all: messages.pot $(MOFILES)

install: all
	for file in $(MOFILES); do \
		lang=`echo $$file | sed 's/\.mo//'`; \
		install -d $(prefix)/share/locale/$$lang/LC_MESSAGES/; \
		install -m 0644 $$file $(prefix)/share/locale/$$lang/LC_MESSAGES/opendict.mo; \
	done

messages.pot:
	@echo "Rebuilding the pot file"
	rm -f *.pot
	test -f /usr/bin/pygettext && /usr/bin/pygettext -v ../opendict.py ../lib/*.py ../lib/gui/*.py || echo
	test -f /usr/bin/pygettext.py && /usr/bin/pygettext.py -v ../opendict.py ../lib/*.py ../lib/gui/*.py || echo
	test -f /usr/share/doc/packages/python/Tools/i18n/pygettext.py && python /usr/share/doc/packages/python/Tools/i18n/pygettext.py -v ../opendict.py ../lib/*.py ../lib/gui/*.py  || echo
	cp messages.pot opendict.pot
	rm -f messages.pot

%.mo: %.po
	msgfmt --verbose --check -o $@ $<

%.po: messages.pot
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
