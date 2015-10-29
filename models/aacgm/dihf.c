/* dihf.c
   ======
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
#include "rmath.h"

int dihf(float x, float y, float z, float *d, float *i, 
          float *h, float *f) {
   
    float h2;
    float sn, hpx;

    sn = (float)1e-4;

    h2 = x * x + y * y;
    *h = sqrt(h2);
    *f = sqrt(h2 + z * z);
    if (*f < sn) {
	*d = (float)999.;
	*i = (float)999.;
    } else {
	*i = atan2d(z,*h);

	if (*h < sn) {
	    *d = (float)999.;
	} else {
	    hpx = *h + x;
	    if (hpx < sn) {
		*d = (float) 180.;
	    } else {
		*d = atan2d(y,hpx) * (float)2.;
	    }
	}
    }
    return 0;
} 


