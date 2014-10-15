# Makefile for building iri-2007 and compliling it with f2py

# Declare default compilers
LOCAL_F2PY = f2py
LOCAL_F77  = gfortran
# Use default compilers unless specified by command line input
F2PY = $(LOCAL_F2PY)
F77  = $(LOCAL_F77)

# Declare optional and required compilation flags
REQ_FLAGS = -w
OPT_FLAGS = -O2 -fbacktrace -fno-automatic -fPIC

# Declare source, object, and executable files
SOURCES = irisub.for \
          irifun.for \
          iriflip.for \
          iritec.for \
          igrf.for \
          cira.for \
          iridreg.for
OBJ = $(SOURCES:.for=.o)

PYF = iri.pyf
PYO = $(PYF:.pyf=.so)

# Define operations
all:
	$(F77) $(REQ_FLAGS) $(OPT_FLAGS) -c $(SOURCES)
	$(F2PY) --f77flags="$(REQ_FLAGS)" -c $(PYF) $(SOURCES)

clean:
	rm -f $(PYO) $(OBJ)

# Declare testing operations
test:
	f2py irisub.for -m iri -h iri_test.pyf

test_clean:
	rm -f iri_test.pyf
