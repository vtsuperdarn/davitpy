/* altitude_to_cgm.c
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




#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "math.h"

void altitude_to_cgm(double r_height_in,double  r_lat_alt,
		     double *r_lat_adj) {
   
  double eradius =6371.2;
  double eps =1e-9;
  double unim =0.9999999;

  double r1;
  double r0, ra;

   /* Computing 2nd power */
  r1 = cosd(r_lat_alt);
  ra = r1 * r1;
  if (ra < eps) ra = eps;
  r0 = (r_height_in/eradius+1) / ra;
  if (r0 < unim) r0 = unim;
  
  r1 = acos(sqrt(1/r0));
  *r_lat_adj= sgn(r1, r_lat_alt)*180/PI;

} 

