include Makefile.inc

all:
	$(PYTHON) setup.py build --build-platlib=`pwd`

install:
	$(PYTHON) setup.py install --install-lib=$(DESTDIR)/$(PYDIR)

depend:

clean:
	rm -fr *.pyc *.so build/
