/* convert_geo_coord.c
   ===================
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
#include <math.h>
#include "math.h"

#include "altitude_to_cgm.h"
#include "cgm_to_altitude.h"
#include "rylm.h"

extern struct {
  double coef[121][3][5][2];
} sph_harm_model;

static double cint[121][3][2]; 

/* Table of constant values */

static double height_old[2]={-1,-1};
static double first_coeff_old=-1;

int convert_geo_coord(double lat_in,double  lon_in,
		      double height_in,double *lat_out,
		      double *lon_out,int flag,
		      int order) {

    
    int i, j, l, m, k;
    int i_err64;

    extern int rylm();
    double ylmval[121];
    double colat_temp;
    double lon_output;
    
    double lat_adj=0;
    double lat_alt=0;
    double colat_input; 
   
    double alt_var_cu=0, lon_temp=0, alt_var_sq=0, alt_var_qu=0;
    double colat_output=0, r=0, x=0, y=0, z=0;
    double alt_var=0;
    double lon_input=0;

    if (lon_in<0) lon_in+=360.0;  

    if (first_coeff_old != sph_harm_model.coef[0][0][0][0]) {
	height_old[0] = -1.0;
	height_old[1] = -1.0;
    }
    first_coeff_old= sph_harm_model.coef[0][0][0][0];

    if ((height_in < 0) || (height_in > 7200)) return -2;
    else if ((flag < 0) || (flag > 1)) return -4; 
    else if (fabs(lat_in) >90.) return -8;
    else if ((lon_in<0) || (lon_in >360)) return -16;
       
    if (height_in != height_old[flag]) {
	alt_var= height_in/7200.0;
	alt_var_sq = alt_var * alt_var;
	alt_var_cu = alt_var * alt_var_sq;
	alt_var_qu = alt_var * alt_var_cu;

	for (i=0; i<3; i++) {
	    for (j=0; j<121;j++) {
		cint[j][i][flag] =sph_harm_model.coef[j][i][0][flag]+
                sph_harm_model.coef[j][i][1][flag]*alt_var+
                sph_harm_model.coef[j][i][2][flag]*alt_var_sq+
                sph_harm_model.coef[j][i][3][flag]*alt_var_cu+
                sph_harm_model.coef[j][i][4][flag]*alt_var_qu;
	    }
	}
	height_old[flag] = height_in;
    
    }

    x = 0;
    y = 0;
    z = 0;

    lon_input =lon_in*PI/180.0;

    if (flag == 0) colat_input = (90-lat_in)*PI/180.0;
    else {
      i_err64=cgm_to_altitude(height_in, lat_in, &lat_adj);
	       
      if (i_err64 != 0) return -64;
      colat_input= (90. - lat_adj)*PI/180;

    }
    rylm(colat_input,lon_input,order,ylmval);

    for (l = 0; l <= order; l++) {
      for (m = -l; m <= l; m++) {

	    k = l * (l+1) + m+1;
	    x += cint[k-1][0][flag]*ylmval[k-1];
            y += cint[k-1][1][flag]*ylmval[k-1];
            z += cint[k-1][2][flag]*ylmval[k-1];
	}
    }
    r = sqrt(x * x + y * y + z * z);
    if ((r< 0.9) || (r > 1.1)) return -32;
   
    z /= r;
    x /= r;
    y /= r;

    if (z > 1.) colat_temp=0;
    else if (z< -1.) colat_temp =PI;
    else colat_temp= acos(z);
  
    if ((fabs(x) < 1e-8) && (fabs(y) < 1e-8)) lon_temp =0;
    else lon_temp = atan2(y,x);

    lon_output = lon_temp;

    if (flag == 0) {

	lat_alt =90 - colat_temp*180/PI;

	altitude_to_cgm(height_in, lat_alt,&lat_adj);
	colat_output = (90. - lat_adj) * PI/180;

    } else colat_output = colat_temp;


    *lat_out = (double) (90 - colat_output*180/PI);
    *lon_out  = (double) (lon_output*180/PI);

    return 0;
} 




