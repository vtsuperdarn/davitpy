#
# define destination locations
#

PYTHON = python`python -c 'import sys; print "%d.%d" % sys.version_info[:2]'`
PYTHONINCLUDE = /usr/include/$(PYTHON)
DATADIR=/usr/share/pydmap
PYDIR=${PYTHONLIBDIR}/pydmap
ARCH := $(patsubst i%86,i386,$(shell uname -m))
ARCH := $(patsubst sparc%,sparc,$(ARCH))

ifneq (,$(filter ppc64 x86_64 s390x,$(shell uname -m)))
LIBDIR = lib64
else
LIBDIR = lib
endif

PYTHONLIBDIR = /usr/$(LIBDIR)/$(PYTHON)/site-packages
