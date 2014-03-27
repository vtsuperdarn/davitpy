#!/bin/bash
# Compile with f2py
SOURCES='irisub.for irifun.for iriflip.for iritec.for igrf.for cira.for iridreg.for'


all:
	#f2py2.6 irisub.for -m iri -h iri.pyf
	gfortran -w -O2 -fno-automatic -c *.for
	f2py2.6 --fcompiler=gnu95 --f77flags="" -c iri.pyf *.for

clean:
	find . -type f -name "*.so" | xargs rm -f
	#find . -type f -name "*.pyf" | xargs rm -f
