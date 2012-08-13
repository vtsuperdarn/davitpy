FCC = gfortran
FFLAGS = -w -ffixed-line-length-132 -g -fno-automatic -fno-align-commons

check:
	$(FCC) $(FFLAGS) igrf_run.for igrf.for -o igrf_run

clean:
	find . -name "*~" -o -name "*.o" | xargs rm -f igrf_run