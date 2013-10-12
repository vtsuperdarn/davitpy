/* AstAlg_lunar_ascending_node.c
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
  
/* This function calculates the location of the moon's ascending node.
   This value affects the nutation of the Earth's spin axis.
   
   Calling Sequence:
     asc_node = AstAlg_lunar_ascending_node(double jd)

     where jd is the Julian Day
*/

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.


*/

#include "AstAlg.h"

double AstAlg_lunar_ascending_node(double jd) {

    static double last_jd, last_ascn;
    double tau, omega;

/* if we've already calculated the value just return it */

    if (jd == last_jd) return last_ascn;

/* calculate the delta-time in centuries with respect to 
   the reference time J2000 */

    tau = (jd - J2000)/36525.0;

/* omega = 125 - 1934 * tau + .002*tau^2 + t^3/4.5e5 */

    omega = (((tau/4.50e5 + 2.0708e-3)*tau - 1.934136261e3)*tau) + 125.04452;

/* now make sure omega is between 0 and 360 */

    omega = dmod(omega, 360.0);

    if (omega < 0.0) omega = omega + 360.0;

    last_jd = jd;
    last_ascn = omega;

    return omega;
}
     
