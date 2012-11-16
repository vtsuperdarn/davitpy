#!/bin/bash
# Compile with f2py


all:
	f2py *.f90 -m raydarn -h raydarn.pyf
	gfortran -w -O2 -fbacktrace -fno-automatic -fPIC -c ../iri/*.for
	mpif90 -w -O2 -fbacktrace -fno-automatic -fPIC -c *.f90
	f2py --f90flags="-w" --f77flags="-w" --f90exec=mpif90 --f77exec=gfortran -c raydarn.pyf *.f90 ../iri/*.for

clean:
	find . -type f -name "*.o" | xargs rm -f
	find . -type f -name "*.so" | xargs rm -f
	find . -type f -name "*.pyf" | xargs rm -f
