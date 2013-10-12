/* AstAlg_apparent_solar_longitude.c
   =================================
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
  
/* This function calcules the mean obliquity of the earth.  That is
   the inclination of the rotation axis relative to the ecliptic plane.

   Calling Sequence:

    e0 = AstAlg_mean_obliquity(julian_date)

    The returned value is in degrees.

*/

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.


*/

#include "AstAlg.h"

double AstAlg_mean_obliquity(double jd) {

    static double last_jd, last_e0;
    double tau;
    const double coefs[] = 
	{23.439291111111,
	 -0.0130041666667,
	 -1.638888889e-7,
	 5.036111111e-7};

/* if we've already calculated this value for this date simply return it */

    if (jd == last_jd) return last_e0;

    /* the coefficients in Meeus are given in degrees, minutes and seconds
       so I have to convert them to double precision degrees first.
       Although this could be done before compilation it would make
       it hard to check the code with the book.  I therefore do 
       the calculation here but only the first time the routine is called.
    */

/*    if (coeffs[3] != 0.001813/3600.0) {
	coeffs[3] = 0.001813/3600.0;
	coeffs[2] = -0.00059/3600.0;
	coeffs[1] = -46.8150/3600.0;
	coeffs[0] = 23.0 + 26.0/60.0 + 21.448/3600.0;
    }
*/

    tau = (jd - J2000)/36525.0;

/* Now calculate the value of e0 */
    last_e0 = ((((coefs[3]*tau) + coefs[2])
		* tau) + coefs[1]) * tau + coefs[0];
    last_jd = jd;

    return last_e0;
}
