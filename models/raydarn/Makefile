# 
FC := mpif90
FFLAGS := -w -O2 -fbacktrace

EXEC := raydarn

IRIDIR := ../iri/
IRIOBJS := $(IRIDIR)irisub.o $(IRIDIR)irifun.o $(IRIDIR)iritec.o $(IRIDIR)iridreg.o $(IRIDIR)iriflip.o $(IRIDIR)cira.o $(IRIDIR)igrf.o
RTOBJS := constants.o MPIutils.o

%.o: %.for
	$(FC) $(FFLAGS) -g -fno-automatic -c $< -o $@

%.o: %.f90
	$(FC) $(FFLAGS) -g -fno-automatic -c $< -o $@

all: $(EXEC)
	 find . -name "*.o" | xargs rm -f

raydarn: $(IRIOBJS) $(IGRFOBJS) $(RTOBJS) raytrace_mpi.o

$(EXEC):
	$(FC) -o $@ $^


.PHONY: all clean

clean:
	find . -name "*~" -o -name "*.o" -o -name "*.mod" | xargs rm -f $(EXEC)
	find ../iri -name "*~" -o -name "*.o" | xargs rm -f $(EXEC)
