include $(top_srcdir)/Makefile.rules

SUBDIRS = src test

EPYDOC_OPTIONS = -n "Bazaar $(VERSION) API Documentation" $(DOCSOURCES)

doc/pdf/api.pdf: $(DOCSOURCES)
	rm -rf $(srcdir)/doc/pdf
	install -d $(srcdir)/doc/pdf
	epydoc --pdf -o $(srcdir)/doc/pdf $(EPYDOC_OPTIONS)

doc/html: $(DOCSOURCES)
	rm -rf $(srcdir)/doc/html
	install -d $(srcdir)/doc/html
	epydoc --html -o $(srcdir)/doc/html $(EPYDOC_OPTIONS)

doc: doc/html doc/pdf/api.pdf

EXTRA_DIST = doc/pdf/api.pdf doc/html
MAINTAINERCLEANFILES = -r doc
