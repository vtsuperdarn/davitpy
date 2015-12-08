# Makefile for building hwm-2007 and compliling it with f2py

# Declare default compilers
LOCAL_F2PY = f2py
LOCAL_FC   = gfortran
# Use default compilers unless specified by command line input
#echo 'Use F2PY and F77 to specify the fortran-to-python and fortran complilers'
F2PY = $(LOCAL_F2PY)
FC   = $(LOCAL_FC)

# Declare optional and required compilation flags
OPT_FLAGS = -O2 -fPIC
REQ_FLAGS = -w

# Declare source code
SOURCES = hwm14.f90
OBJ = $(SOURCES:.f90=.o)

PYF = hwm14.pyf
PYO = $(PYF:.pyf=.so)

# Define operations
all:
	$(FC) $(REQ_FLAGS) $(OPT_FLAGS) -c $(SOURCES)
	$(F2PY) --f90flags="$(REQ_FLAGS)" -c $(PYF) $(SOURCES)

clean:
	rm -f $(PYO) $(OBJ)

# Define test operations
test:
	$(F2PY) $(SOURCES) -m hwm14 -h hwm14_test.pyf

test_clean:
	rm -f hwm14_test.pyf
