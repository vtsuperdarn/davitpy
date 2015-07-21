/* AstAlg_equation_of_time.c
   =========================
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
  
/* This function returns the equation of time for a given
   Julian date.

   The returned value is the difference between the apparent time and the
   mean solar time.  The correction is returned in minutes and is always
   between + and - 20.

   A positive value menas that the true sun crosses the observer's meridian
   before the mean sun (i.e. mean time is lagging).

   Calling sequence:

   eqt = AstAlg_equation_of_time(double jd)

   This routine calls AstAlg_mean_solar_longitude,
   AstAlg_solar_right_ascension, AstAlg_mean_obliquity,
   and AstAlg_nutation_corr.
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

double AstAlg_equation_of_time(double jd) {

    static double last_jd, last_eqt;

    double eqt;
    double dpsi, deps, sml, sra, obliq;

/* if we've already calculated the value, simply return it */

    if (jd == last_jd) return last_eqt;

/* first get all the separate pieces */

    sml = AstAlg_mean_solar_longitude(jd);
    sra = AstAlg_solar_right_ascension(jd);
    obliq = AstAlg_mean_obliquity(jd);
    AstAlg_nutation_corr(jd, &dpsi, &deps);

/* now put it all together */

    eqt = sml - 0.0057183 - sra + dpsi*cos(AstAlg_DTOR*(obliq + deps));

    eqt = dmod(eqt,360.0);

/* now convert from degrees to minutes */

    eqt = 4.0 * eqt;

    if (eqt > 20.0) eqt = eqt - 24.0*60.0; /*wrap back 24 hours*/
    if (eqt < -20.0) eqt = 24.0*60.0 + eqt; /*wrap forward 24 hours */

    last_jd = jd;
    last_eqt = eqt;

    return eqt;
}

    
