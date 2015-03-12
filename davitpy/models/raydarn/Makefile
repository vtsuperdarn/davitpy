# Makefile for building RayDARN

# Declare default compilers
LOCAL_FC = mpif90
# Use default compilers unless specified by command line input
FC = $(LOCAL_FC)

# Declare optional and required compilation flags
OPT_FLAGS = -O2 -fbacktrace -fno-automatic
REQ_FLAGS = -w -g

# Declare non-local directories that contain source files
IRIDIR = $(DAVITPY)/davitpy/models/iri

# Declare source, object, and executable files
RTSRC = constants.f90 \
	MPIutils.f90

IRISRC = $(IRIDIR)/irisub.o \
         $(IRIDIR)/irifun.for \
         $(IRIDIR)/iriflip.for \
         $(IRIDIR)/iritec.for \
         $(IRIDIR)/igrf.for \
         $(IRIDIR)/cira.for \
         $(IRIDIR)/iridreg.for

RTOBJS = $(RTSRC:.f90=.o)
IRIOBJS = $(IRISRC:.for=.o)

EXEC = rtFort

%.o: %.for
	$(FC) $(REQ_FLAGS) $(OPT_FLAGS) -c $< -o $@

%.o: %.f90
	$(FC) $(REQ_FLAGS) $(OPT_FLAGS) -c $< -o $@

all: $(EXEC)
	rm -f $(IRIOBJS) $(RTOBJS)

rtFort: $(IRIOBJS) $(RTOBJS) raytrace_mpi.o

$(EXEC):
	$(FC) -o $@ $^

.PHONY: all clean

clean:
	find . -name "*~" -o -name "*.o" -o -name "*.mod" | xargs rm -f $(EXEC)
	rm -f $(EXEC) $(IRIOBJS)
