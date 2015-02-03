/* rmath.h
   =======
   Author: R.J.Barnes
*/


/*
 LICENSE AND DISCLAIMER
 
 Copyright (c) 2012 The Johns Hopkins University/Applied Physics Laboratory
 
 This file is part of the Radar Software Toolkit (RST).
 
 RST is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 any later version.
 
 RST is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.
 
 You should have received a copy of the GNU Lesser General Public License
 along with RST.  If not, see <http://www.gnu.org/licenses/>.
 
 
 
*/




#ifndef _RMATH_H
#define _RMATH_H

#ifndef _COMPLEX
struct complex {
    double x,y;
};
#define cabs(a) sqrt((a.x*a.x)+(a.y*a.y))
#endif

#define C 2.997e+8
#define LN_TO_LOG 4.342944819

#ifndef HUGE_VAL
#define HUGE_VAL 1.0e36                /* default value of HUGE */
#endif
 
#ifndef PI
#define PI 3.14159265358979323846
#endif

#define asind(x) asin(x)*180/PI
#define acosd(x) acos(x)*180/PI
#define cosd(x) cos(PI*(x)/180.0)
#define sind(x) sin(PI*(x)/180.0)
#define tand(x) tan(PI*(x)/180.0)
#define atand(x) atan(x)*180.0/PI
#define atan2d(x,y) atan2(x,y)*180.0/PI
#endif













