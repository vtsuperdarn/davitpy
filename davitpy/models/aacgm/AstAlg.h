/* Astalg.h
   ========
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



/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.


*/

#ifndef _AstAlg_H
#define _AstAlg_H

#define J2000 (2451545.0)
/* The reference time for all the algorithms in Meeus. The reference
   date is January 1, 2000 at UT (actually TD) noon (i.e. day 1.5 of 2000).

   The zero time for Julian Day is noon on the beginning of the year in
   -4712.
*/
/* I need the value of PI, so include the math.h definitions */

#include <math.h>

#define AstAlg_DTOR (M_PI/180.0)
 
/* we need a floating point version of the % binary operator */

#define dmod(a,b) ((double) ((((long) a) % ((long) b)) + (a - (long) a)))

double AstAlg_apparent_obliquity(double jd);
double AstAlg_apparent_solar_longitude(double jd);
double AstAlg_dday(int day, int hour, int minute, int second);
double AstAlg_equation_of_time(double jd); 
double AstAlg_geometric_solar_longitude(double jd);
double AstAlg_jde(int year, int month, double day);
void AstAlg_jde2calendar(double jd, 
			 int *year,
			 int *month,
			 int *day,
			 int *hour,
			 int *minute,
			 int *second);
double AstAlg_lunar_ascending_node(double jd);
double AstAlg_mean_lunar_longitude(double jd);
double AstAlg_mean_obliquity(double jd);
double AstAlg_mean_solar_anomaly( double jd );
double AstAlg_mean_solar_longitude( double jd );
void AstAlg_nutation_corr(double jd, double *slong_corr, double *obliq_corr);
double AstAlg_solar_declination(double jd);
double AstAlg_solar_right_ascension(double jd);

#endif
