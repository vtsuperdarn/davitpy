#!/bin/bash
# Compile with f2py

all:
#	f2py hwm07e.f90 -m hwm07 -h hwm07.pyf
	gfortran -w -O2 -fPIC -c *.f90
	f2py --fcompiler=gnu95 --f90flags="-w" -c hwm07.pyf *.f90

clean:
	find . -type f -name "*.so" | xargs rm -f
#	find . -type f -name "*.pyf" | xargs rm -f
