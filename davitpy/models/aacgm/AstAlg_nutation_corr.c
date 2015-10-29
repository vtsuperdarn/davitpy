/* AstAlg_nutation_corr.c
   ======================
   Author: Kile Baker
*/

/*
 Copyright and License Information 
 
    This source file is part of a library of files implementing
    portions of the algorithms given in the book _Astronomical
    Algorithms_ by Jean Meeus.
 
    Software Copyright (C) 2006, U.S. Government
    Author: Kile B. Baker
            National Science Foundation
 	   4201 Wilson Blvd,
 	   Arlington, VA 22230
 	   email: kbaker@nsf.gov
 
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
 
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
 
    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 
 
 
 
*/
  
/* This routine calculates the corrections to the solar longitude and
   obliquity that arize due to the nutation of the earth's spin.
   
   Calling Sequence:

   void AstAlg_nutation_corr(double jd, double *slong_corr, double *obliq_corr)

*/

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.


*/

#include <math.h>
#include "AstAlg.h"

void AstAlg_nutation_corr(double jd, double *slong_corr, double *obliq_corr)
{
    double slong, lunlong, omega;
    static double last_jd, last_slcorr, last_oblcorr;

/* just return the values if they've already been calculated */

    if (jd == last_jd) {
	*slong_corr = last_slcorr;
	*obliq_corr = last_oblcorr;
    }

/* get the mean solar longitude and mean lunar longitude in radians */

    slong = AstAlg_DTOR * AstAlg_mean_solar_longitude(jd);
    lunlong = AstAlg_DTOR * AstAlg_mean_lunar_longitude(jd);
    omega = AstAlg_DTOR * AstAlg_lunar_ascending_node(jd);

/* the next line computes the correction to the solar longitude in arcsecs */

    *slong_corr = -17.20 * sin(omega) - 1.32 * sin(2.0*slong) -
	0.23 * sin(2.0*lunlong) + 0.21 * sin(2.0*omega);

/* convert from arcsec to degrees */
    *slong_corr = *slong_corr/3600.0;

/* Next we calculate the correction to the obliquity in arcsecs */

    *obliq_corr = 9.20 * cos(omega) + 0.57 * cos(2.0*slong) +
	0.10 * cos(2.0*lunlong) - 0.09 * cos(2.0*omega);

    *obliq_corr = *obliq_corr/3600.0;

/* save the calculated values in case their needed again */
    last_jd = jd;
    last_slcorr = *slong_corr;
    last_oblcorr = *obliq_corr;

    return;
}
