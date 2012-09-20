# compiles all fortran models on davit
# 
FC := gfortran
FFLAGS := -w -O2 -fbacktrace

EXEC := iri/iri igrf/igrf_run cond/sigp hwm/hwm_run

IRIDIR := iri/
IRIOBJS := $(IRIDIR)irisub.o $(IRIDIR)irifun.o $(IRIDIR)iritec.o $(IRIDIR)iridreg.o $(IRIDIR)iriflip.for $(IRIDIR)cira.o
IGRFDIR := igrf/
IGRFOBJS := $(IGRFDIR)igrf.o 
MSISDIR := msis/
MSISOBJS := $(MSISDIR)cira.o
HWMDIR := hwm/
HWMOBJS := $(HWMDIR)hwm07e.o $(HWMDIR)dwm07b.o $(HWMDIR)apexcord.o
RTDIR := raydarn/
RTOBJS := $(RTDIR)constants.o $(RTDIR)MPIutils.o

%.o: %.for
	$(FC) $(FFLAGS) -ffixed-line-length-132 -g -fno-automatic -c $< -o $@

%.o: %.f
	$(FC) $(FFLAGS) -ffixed-line-length-132 -g -fno-automatic -c $< -o $@

%.o: %.f90
	$(FC) $(FFLAGS) -g -fno-automatic -c $< -o $@


all: 	$(EXEC)
	mpif90 $(FFLAGS) -g -fno-automatic -c $(RTDIR)constants.f90 -o $(RTDIR)constants.o
	mpif90 $(FFLAGS) -g -fno-automatic -c $(RTDIR)MPIutils.f90 -o $(RTDIR)MPIutils.o
	mpif90 $(FFLAGS) -g -fno-automatic -c $(RTDIR)raytrace_mpi.f90 -o $(RTDIR)raytrace_mpi.o
	mpif90 -o $(RTDIR)raydarn $(IGRFOBJS) $(IRIOBJS) $(RTOBJS) $(RTDIR)raytrace_mpi.o
	cp -f constants.mod rtmpi/
	cp -f mpiutils.mod rtmpi/
	rm -f constants.mod MPIutils.mod
	cp -f *.mod hwm/
	rm -f *.mod

iri/iri: $(IRIOBJS) $(IGRFOBJS) iri/iri_run.o
igrf/igrf_run: $(IRIOBJS) $(IGRFOBJS) igrf/igrf_run.o
cond/sigp: $(IRIOBJS) $(IGRFOBJS) cond/conductivities.o
hwm/hwm_run: $(HWMOBJS) hwm/hwm_run.o

$(EXEC):
	$(FC) -o $@ $^


.PHONY: all clean

clean:
	find . -name "*~" -o -name "*.o" -name "*.mod"| xargs rm -f $(EXEC)
	find ./rtmpi -name "*~" -o -name "*.o" -o -name "*.mod"| xargs rm -f $(EXEC)
	find ./iri -name "*~" -o -name "*.o" | xargs rm -f $(EXEC)
	find ./igrf -name "*~" -o -name "*.o" | xargs rm -f $(EXEC)
	find ./nrlmsis -name "*~" -o -name "*.o" | xargs rm -f $(EXEC)
	find ./hwm -name "*~" -o -name "*.o" -o -name "*.mod" | xargs rm -f $(EXEC)
