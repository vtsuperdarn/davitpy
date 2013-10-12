/* cgm_to_altitude.c
   =================
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




#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "math.h"


int cgm_to_altitude(double r_height_in,double r_lat_in,double *r_lat_adj) {
    double eradius = 6371.2;
    double unim=1;
    double  r1;
    double ra;
    int error=0;

   /* Compute the corresponding altitude adjusted dipole latitude. */
   /* Computing 2nd power */

    r1 = cosd(r_lat_in);
    ra = (r_height_in/ eradius+1)*(r1*r1);
    if (ra > unim) {
	ra = unim;
        error=1;
    }

    r1 = acos(sqrt(ra));
    *r_lat_adj = sgn(r1,r_lat_in)*180/PI;
    return error;
}

