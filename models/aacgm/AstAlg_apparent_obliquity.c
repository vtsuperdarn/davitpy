/* AstAlg_apparent_obliquity.c
   ===========================
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
  
#include <math.h>
#include "AstAlg.h"

/* This function calculates the apparent obliquity (angle between
   the earth's spin axis and the ecliptic).  It uses the
   mean obliquity and the effect of the lunar position.

   Calling sequence:
     eps = AstAlg_apparent_obliquity(double julian_day)

   The value is returned in degrees.
*/

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.

*/

double AstAlg_apparent_obliquity(double jd) {

    static double last_jd, last_eps;

/* if we've already calculated the value just return it */

    if (jd == last_jd) return last_eps;

    last_jd = jd;
    last_eps = AstAlg_mean_obliquity(jd) + 
	0.00256 * cos(AstAlg_DTOR * AstAlg_lunar_ascending_node(jd));

    return last_eps;
}
