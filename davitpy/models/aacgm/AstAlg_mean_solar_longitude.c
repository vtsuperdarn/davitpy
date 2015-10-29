/* AstAlg_mean_solar_longitude.c
   =============================
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
  
/* This function calculates the mean solar longitude for a given Julian day (see function AstAlg_jde.c).

 Calling Sequence:
   slong = AstAlg_mean_solar_longitude(double jd);

   The returned value is in degrees and ranges from 0 to 360

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

double AstAlg_mean_solar_longitude( double jd ) {

/* the mean solar longitude gets called from several other functions
   and we don't want to have to recalculate the value every time, so
   the last calculated value is saved as a static value */

    static double last_jd, last_sl;

    static const double coefs[] = {280.4664567, 360007.6982779,
		      0.03032028, 2.00276381406e-5,
		      -6.53594771242e-5, -0.50e-6 };
    double tau, sl;

    int i;

    if (jd == last_jd) return last_sl;

/* calculate the difference between the requested Julian day and the
   reference Julian day, J2000, in terms of milennia */

    tau = (jd - J2000)/365250.0;

/* now calculate the solar longitude using the delta-time tau and the
   coefficients */

    sl = 0.0;

    for (i=5; i>=0; i--) {
	sl = tau * sl + coefs[i];
    }


/* make sure the result is between 0 and 360 degrees */

    sl = dmod(sl, 360);

    if (sl < 0.0) sl = sl + 360.0;

    last_jd = jd;
    last_sl = sl;

    return sl;
}
