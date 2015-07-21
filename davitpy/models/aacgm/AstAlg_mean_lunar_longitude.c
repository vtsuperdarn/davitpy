/* AstAlg_mean_lunar_longitude.c
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
  
/* This function calculates the mean lunar longitude for a given
   Julian Day.

   Calling Sequence:

   lunlong = AstAlg_mean_lunar_longitude(double jd)

*/

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.

*/

#include "AstAlg.h"

double AstAlg_mean_lunar_longitude(double jd) {

    static double last_jd, last_llong;
    double tau, llong;

/* simply return the value if we've already calculated it */

    if (jd == last_jd) return last_llong;

/* calculate the detla-time from the reference time J2000 in centuries */

    tau = (jd - J2000)/36525.0;

    llong = 218.3165 + 481267.8813 * tau;

/* make sure the resulting value is between 0 and 360 */

    llong = dmod(llong, 360.0);

    if (llong < 0) llong = llong + 360.0;

    last_jd = jd;
    last_llong = llong;

    return llong;
}
