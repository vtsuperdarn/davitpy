#!/bin/bash
# Compile with f2py

all:
	f2py nrlmsise00_sub.for -m msisFort -h nrlmsis.pyf
	f2py --f77flags="-w" -c nrlmsis.pyf nrlmsise00_sub.for

clean:
	find . -type f -name "*.so" | xargs rm -f
	find . -type f -name "*.pyf" | xargs rm -f
