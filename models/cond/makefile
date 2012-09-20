# ***********************************************
# Compile IRI, NRLMSIS and conductivities
FC := gfortran
FFLAGS := -w -O2 -ffixed-line-length-132

EXEC := sigp

IRIDIR := ../iri/
IRIOBJS := $(IRIDIR)irisub.o $(IRIDIR)irifun.o $(IRIDIR)iritec.o $(IRIDIR)iridreg.o
#$(IRIDIR)cira.o
IGRFOBJS := ../igrf/igrf.o
MSISOBJS := ../nrlmsis/nrlmsise00_sub.o

%.o: %.for
	$(FC) $(FFLAGS) -g -fno-automatic -c $< -o $@

%.o: %.f90
	$(FC) $(FFLAGS) -g -fno-automatic -c $< -o $@

all: $(EXEC)

sigp: $(IRIOBJS) $(IGRFOBJS) $(MSISOBJS) conductivities.o

$(EXEC):
	$(FC) -o $@ $^

.PHONY: all clean

clean:
	find . -name "*~" -o -name "*.o" | xargs rm -f $(EXEC)
	find ../iri -name "*~" -o -name "*.o" | xargs rm -f $(EXEC)
	find ../igrf -name "*~" -o -name "*.o" | xargs rm -f $(EXEC)
	find ../nrlmsis -name "*~" -o -name "*.o" | xargs rm -f $(EXEC)