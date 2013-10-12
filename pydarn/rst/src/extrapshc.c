/* extrapshc.c
   ===========
   Author: R.J.Barnes
*/

/*
 LICENSE AND DISCLAIMER
 
 Copyright (c) 2012 The Johns Hopkins University/Applied Physics Laboratory
 
 This file is part of the Radar Software Toolkit (RST).
 
 RST is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 any later version.
 
 RST is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.
 
 You should have received a copy of the GNU Lesser General Public License
 along with RST.  If not, see <http://www.gnu.org/licenses/>.
 
 
 
*/



#include <math.h>

int extrapshc(double date, double dte1, int nmax1, 
               double *gh1, int nmax2, double *gh2, int *nmax, double *gh) {
   
    int i, k, l;
    double factor;

    --gh;
    --gh2;
    --gh1;

    factor = date - dte1;
    if (nmax1 == nmax2) {
	k = nmax1 * (nmax1 + 2);
	*nmax = nmax1;
    } else if (nmax1 > nmax2) {
	k = nmax2 * (nmax2 + 2);
	l = nmax1 * (nmax1 + 2);
     
	for (i = k + 1; i <= l; ++i) {
	    gh[i] = gh1[i];
	}
	*nmax = nmax1;
    } else {
	k = nmax1 * (nmax1 + 2);
	l = nmax2 * (nmax2 + 2);
       
	for (i = k + 1; i <= l; ++i) {
	    gh[i] = factor * gh2[i];
	}
	*nmax = nmax2;
    }
    
    for (i = 1; i <= k; ++i) {
	gh[i] = gh1[i] + factor * gh2[i];
    }
    return 0;
} 

