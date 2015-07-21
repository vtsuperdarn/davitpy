/* AstAlg_jde.c
   ============
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
  
/* This routine returns the Julian Day as a double precision value

   Calling sequence:

   jd = AstAlg_jde( int year, int month, double day)

*/

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.


*/

/* NOTE: Meeus uses Terrestrial Dynamic (TD) time, sometimes referred to
   as Ephemeris Time.  The 'E' in the name of this function (jde) is
   a reminder that the time is Julian Day in Ephemeris time.

   All of the rest of the algorithms provided in this set of software
   calculate their values with reference to Jan 1, 2000 at noon TD. 
   This reference time is referred to as J2000 and is a defined constant
   in AstAlg.h.

   Since all the calculations involve differences between the JDE value
   and J2000, the difference between TD at UT can safely be ignored.
   The only difference comes from any leaap seconds that have been applied
   between the reference time and the time of interest.  Those differences
   are sufficiently small (a few seconds) so that we ignore them.

   If you want to have higher accuracy you probably need to calculate the
   decimal day in terms of TD rather than UT.  Meeus has details of how
   to do this.
*/

#include "AstAlg.h"

double AstAlg_jde(int year, int month, double day) {

/* NOTE: the value of 'year' must be the full 4-digit year */

    int a;
    double b;

/* if the month is January or February, treat it as belonging
   to the previous year.  This makes the leap year correction
   easier to handle */

    if (month <= 2) {
	year = year - 1;
	month = month + 12;
    }

/* the next few lines perform the leap year correction.  It deals
   with the centuries correctly */

    a = (int) (year/100);
    b = (double) (2 - a + a/4);

/* ideally, the constant 30.6001 could simply be 30.6, but adding the
   additional .0001 to it ensures that truncation error doesn't result
   in an incorrect calculation */

    return ((double) ( (long) (365.25*(year + 4716)) +
		      (double) ( (long) (30.6001 * (month + 1)))) +
	day + b - 1524.5);
}
