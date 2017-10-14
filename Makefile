# Master Makefile

# Declare DaViTpy working directory
DAVITDIR = $(DAVITPY)

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
	$(MAKE) -C $(IRIDIR) OPT_FLAGS="$(F77_FLAGS)"
	$(MAKE) -C $(TSYDIR) OPT_FLAGS="$(F77_FLAGS)"
	$(MAKE) -C $(HWMDIR) OPT_FLAGS="$(FC_FLAGS)"
	$(MAKE) -C $(RAYDIR) OPT_FLAGS="$(MPI_FLAGS)"

clean:
	$(MAKE) -C $(IRIDIR) $@
	$(MAKE) -C $(TSYDIR) $@
	$(MAKE) -C $(HWMDIR) $@
	$(MAKE) -C $(RAYDIR) $@
test:
	$(MAKE) -C $(IRIDIR) $@
	$(MAKE) -C $(TSYDIR) $@
	$(MAKE) -C $(HWMDIR) $@
test_clean:
	$(MAKE) -C $(IRIDIR) $@
	$(MAKE) -C $(TSYDIR) $@
	$(MAKE) -C $(HWMDIR) $@
