#!/bin/bash
# Compile with f2py

all:
#	f2py igrf11.f90 -m igrf -h igrf11.pyf
	f2py --fcompiler=gnu95 -c igrf11.pyf igrf11.f90

clean:
	find . -type f -name "*.so" | xargs rm -f
#	find . -type f -name "*.pyf" | xargs rm -f
