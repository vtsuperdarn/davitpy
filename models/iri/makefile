#!/bin/bash
# Compile with f2py
SOURCES='irisub.for irifun.for iriflip.for iritec.for igrf.for cira.for iridreg.for'


all:
	#f2py irisub.for -m iri -h iri.pyf
	#f2py --fcompiler=gnu95 -c iri.pyf *.for
	#gfortran -w -O2 -fno-automatic -c -ffixed-line-length-0 -std=legacy *.for
	f77 -w -c *.for


clean:
	find . -type f -name "*.so" | xargs rm -f
	#find . -type f -name "*.pyf" | xargs rm -f
