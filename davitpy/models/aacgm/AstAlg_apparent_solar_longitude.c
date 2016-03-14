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
  
/* This function calculates the apparent solar longitude for a given
   Julian Day using the geometric solar longitude along with 
   the effect of the position of the moon.

   Calling Sequence:
     asl = AstAlg_apparent_solar_longitude(double jd)

     The returned value is in degrees.
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

double AstAlg_apparent_solar_longitude(double jd) {

    static double last_jd, last_asl;
    
/* if we've already calculated the value simply return it */

    if (jd == last_jd) return last_asl;

    last_jd = jd;
    last_asl = AstAlg_geometric_solar_longitude(jd) - 0.00569 -
	0.00478*sin(AstAlg_DTOR * AstAlg_lunar_ascending_node(jd));

    return last_asl;
}
