/* AstAlg_geometric_solar_longitude.c
   ==================================
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
  
/* This function calculates the geometric_solar_longitude.

  Calling sequence:
   gsl = AstAlg_geometric_solar_longitude(julian_day)

   The returned value is in degrees from 0 to 360

   The function requires the mean solar longitude and the
   mean solar anomaly.

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

double AstAlg_geometric_solar_longitude(double jd) {

    static double last_jd, last_gsl;

    double sml, sma, tau, gc;

/* if we've already calculated the value for this Julian Day just
   return it */

    if (last_jd == jd) return last_gsl;

/* compute the delta-tau in centuries from the reference time J2000 */

    tau = (jd - J2000)/36525.0;

    sml = AstAlg_mean_solar_longitude(jd);

/* we need the mean solar anomaly in radians because it's used in some
   sine functions */

    sma = AstAlg_DTOR * AstAlg_mean_solar_anomaly(jd);

    gc = (1.914602 - 0.004817*tau - 0.000014*(tau*tau)) * sin(sma)
	+ (0.019993 - 0.000101*tau) * sin(2.0*sma)
	+ 0.000289 * sin(3.0*sma);

    sml = sml + gc;

/* make sure the value is between 0 and 360 degrees */

    sml = dmod(sml, 360.0);

    if (sml < 0.0) sml = sml + 360.0;

    last_jd = jd;
    last_gsl = sml;

    return sml;
}

