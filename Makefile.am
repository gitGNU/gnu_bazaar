SUBDIRS = src

EPYDOC_OPTIONS = -n "Bazaar $(VERSION) API Documentation" $(srcdir)/src/bazaar

doc/pdf/api.pdf:
	rm -rf $(srcdir)/doc/pdf
	install -d $(srcdir)/doc/pdf
	epydoc --pdf -o $(srcdir)/doc/pdf $(EPYDOC_OPTIONS)

doc/html:
	rm -rf $(srcdir)/doc/html
	install -d $(srcdir)/doc/html
	epydoc --html -o $(srcdir)/doc/html $(EPYDOC_OPTIONS)

doc: doc/html doc/pdf/api.pdf

EXTRA_DIST = doc/pdf/api.pdf doc/html
MAINTAINERCLEANFILES = -r doc
