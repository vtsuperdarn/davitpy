/* AstAlg_dday.c
   =============
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
    
/* This routine is a fairly trivial one.  In the AstAlg software
   it is commonly necessary to know the decimal day (i.e. day of month
   and fraction thereof.  This routine simply calculates the decimal
   day as a double precision number from the day, hour, minute, and second.

   No attempt is made to check the validity of the arguments so you can
   create a garbage result if you give it nonsense values like setting
   the day to 1000 or the hour to 50, etc.
*/

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.


*/

#include "AstAlg.h"

double AstAlg_dday(int day, int hour, int minute, int second) {

    return (double) (day + hour/24.0 + minute/60.0 + second/3600.0);
}
