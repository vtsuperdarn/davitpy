/* AstAlg_jde2calendar.c
   =====================
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
  
/* This routine converts Julian Day to calendar year, month, day,
   hour, minute and second */

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.

*/

#include "AstAlg.h"

void AstAlg_jde2calendar(double jd,
			 int *year,
			 int *month,
			 int *day,
			 int *hour,
			 int *minute,
			 int *second) {

    long a,b,c,d,e, z;
    long alpha;
    double f;
    double dday, resid;

/* this is a rather complicated calculation and uses some clever tricks
   that I (Kile Baker) don't really understand.  It all comes out of
   Meeus (chapter 7) and it all seems to work. */

    jd = jd + 0.5;

/* z is the integer part of jd+.5 and f is the remaining fraction of a day */

    z = (long) jd;
    f = jd - z;
    
    if (z < 2299161) a = z;
    else {
	alpha = (long) ((z - 1867216.25)/36524.25);
	a = z + 1 + alpha - (long)(alpha/4);
    }

    b = a + 1524;
    c = (long) ((b - 122.1)/365.25);
    d = (long) (365.25 * c);
    e = (long) ((b - d)/30.6001);
/* NOTE: Meeus states emphatically that the constant 30.6001 must be used
   to avoid calculating dates such as Feb. 0 instead of Jan. 31. */

/* the value of e is basically giving us the month */

    if (e < 14) *month = e-1;
    else *month = e-13;

/* the value of c is basically giving us the year */

    if (*month > 2) *year = c - 4716;
    else *year = c - 4715;

/* now calclulate the decimal day */

    dday = b - d - (double) ((long) (30.6001 * e)) + f;

/* extract the integer part of the day and get the left over residual
   in hours */

    *day = (int) dday;
    resid = (dday - *day) * 24.0;

/* extract the integer part of the hours and get the left over minutes */
    
    *hour = (int) resid;
    resid = (resid - *hour)*60.0;

/* extract the integer part of the minutes and get the left over seconds */
    *minute = (int) resid;
    resid = (resid - *minute)*60.0;
    /* round of the value of second to the nearest second */

    *second = (int)(resid + 0.5);
    return;
}
