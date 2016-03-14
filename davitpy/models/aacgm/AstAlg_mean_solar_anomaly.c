/* AstAlg_apparent_solar_anomaly.c
   ===============================
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
  
/* This function calculates the mean solar anomaly for a given Julian day 
(see function AstAlg_jde.c).

 Calling Sequence:
   slong = AstAlg_mean_solar_anomaly(double jd);

   The returned value is in degrees and ranges from 0 to 360

*/

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.

*/

#include "AstAlg.h"

double AstAlg_mean_solar_anomaly( double jd ) {

/* last calculated value for this function is saved.  This is done
   to avoid recalculating the value multiple times, since it is used
   in several other functions in the AstAlg library */

       static double last_jd, last_sma;

       double tau, sma;

       if (jd == last_jd) return last_sma;

       /* calculate the difference between the requested Julian Day and
	  the reference value, J2000, in centuries */

       tau = (jd - J2000)/36525.0;

       sma = 357.5291130 + 35999.05029 * tau
	   - 0.0001537 * (tau*tau);

       /* make sure the value is between 0 and 360 */

       sma = dmod(sma, 360);

       if (sma < 0.0) sma = sma + 360.0;

       last_jd = jd;
       last_sma = sma;

       return sma;
   }

