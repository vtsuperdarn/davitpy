# Master Makefile

# Declare DaViTpy working directory
DAVITDIR = $(DAVITPY)

# Declare local compilers, or use system defaults
FC   = gfortran
F77  = gfortran
MPI  = mpif90
F2PY = f2py

# If you have problems compiling certain routines, your system may not support
# some of these flags.  However, it is not recommended to change them.
FC_FLAGS = -O2 -fPIC
F77_FLAGS = $(FC_FLAGS) -fbacktrace -fno-automatic
MPI_FLAGS = -O2 -fbacktrace -fno-automatic

# Declare directories which contain C or Fortran code that must be compiled
# NOTE: IRGR and MSIS are currently pre-compiled and so not included here
IRIDIR = $(DAVITPY)/models/iri
TSYDIR = $(DAVITPY)/models/tsyganenko
HWMDIR = $(DAVITPY)/models/hwm
RAYDIR = $(DAVITPY)/models/raydarn

all: clean build

build:
	(cd $(IRIDIR); make F77=$(F77) F2PY=$(F2PY) OPT_FLAGS="$(F77_FLAGS)")
	(cd $(TSYDIR); make F77=$(F77) F2PY=$(F2PY) OPT_FLAGS="$(F77_FLAGS)")
	(cd $(HWMDIR); make FC=$(FC) F2PY=$(F2PY) OPT_FLAGS="$(FC_FLAGS)")
	(cd $(RAYDIR); make FC=$(MPI) OPT_FLAGS="$(MPI_FLAGS)")

clean:
	(cd $(IRIDIR); make clean)
	(cd $(TSYDIR); make clean)
	(cd $(HWMDIR); make clean)
	(cd $(RAYDIR); make clean)
test:
	(cd $(IRIDIR); make test)
	(cd $(TSYDIR); make test)
	(cd $(HWMDIR); make test)
test_clean:
	(cd $(IRIDIR); make test_clean)
	(cd $(TSYDIR); make test_clean)
	(cd $(HWMDIR); make test_clean)
