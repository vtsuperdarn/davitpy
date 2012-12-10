#!/bin/bash


all:
#	f2py geopack08.for -m tsygFort -h geopack08.pyf T96.f T02.f
	gfortran -w -O2 -fbacktrace -fno-automatic -fPIC -c geopack08.for T96.f T02.f
	f2py --f77flags="-w" -c geopack08.pyf geopack08.for T96.f T02.f

clean:
	find . -type f -name "*.o" | xargs rm -f
	find . -type f -name "*.so" | xargs rm -f
#	find . -type f -name "*.pyf" | xargs rm -f
