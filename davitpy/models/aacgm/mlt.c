/* mlt.c
   =====
   Author R.J.Barnes
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

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "rtime.h"
#include "aacgm.h"
#include "AstAlg.h"


static double sol_dec_old=0;
static double told=1e12;
static double mslon1=0;
static double mslon2=0;


int convert_geo_coord(double lat_in,double  lon_in,
                      double height_in,double *lat_out,
                      double *lon_out,int flag,int order);



double astmlt1(int t0,double solar_dec,double mlon,double *mslon) {
 
  double ret_val;

  /* double r; */

  double mslat1,mslat2,slon1,slon2,height;
  int err;
 
  if ((fabs(solar_dec-sol_dec_old)>0.1) || (sol_dec_old==0)) told=1e12;
  if (fabs(mslon2-mslon1)>10) told=1e12;
    
   if ((t0>=told) && (t0<(told+600))) {
    *mslon=mslon1+(t0-told)*(mslon2-mslon1)/600.0;
   } else {
    told=t0;
    sol_dec_old=solar_dec;

    slon1 = (43200.0-t0)*15.0/3600.0;
    slon2 = (43200.0-t0-600)*15.0/3600.0;

    height = 450;
    /*
    
      Should use the top AACGM conversion functions, but the 
      order of expansion is lower in the old version, so for now
      duplicate the old calculation using the internal call to 
      convert_geo_coord
    
      err=AACGMConvert(solar_dec,slon1,height,&mslat1,&mslon1,&r,0);
      err=AACGMConvert(solar_dec,slon2,height,&mslat2,&mslon2,&r,0);
    */

    err=convert_geo_coord(solar_dec,slon1,height,&mslat1,&mslon1,0,4);
    err=convert_geo_coord(solar_dec,slon2,height,&mslat2,&mslon2,0,4);

    *mslon=mslon1;
  }
  
  ret_val = (mlon - *mslon) /15.0 + 12.0;
  if (ret_val >=24) ret_val -=24;
  if (ret_val <0) ret_val+=24;  
  return ret_val;
} 

double astmlt(int yr,int mo,int dy,int hr,int mt,int sc,double mlon,
            double *mslong) {

  double jd,dd,eqt,dec,ut,at,ret_val;
  dd=AstAlg_dday(dy-1,hr,mt,sc);
  jd=AstAlg_jde(yr,mo,dd);
  eqt=AstAlg_equation_of_time(jd);
  dec=AstAlg_solar_declination(jd);
  ut=hr*3600+mt*60+sc;
  at = ut + eqt*60.0;
  ret_val = astmlt1(at, dec, mlon, mslong);
  return ret_val;
}

double MLTConvertYMDHMS(int yr,int mo,int dy,int hr,int mt,int sc,
                        double mlon) {
  double mslon;
  return astmlt(yr,mo,dy,hr,mt,sc,mlon,&mslon);
}

double MLTConvertYrsec(int yr,int yr_sec,double mlon) {
  int mo,dy,hr,mt,sc;
  double mslon;
  TimeYrsecToYMDHMS(yr_sec,yr,&mo,&dy,&hr,&mt,&sc);
  return astmlt(yr,mo,dy,hr,mt,sc,mlon,&mslon);
}

double MLTConvertEpoch(double epoch,double mlon) {
  int yr,mo,dy,hr,mt;
  double sc;
  double mslon;
  TimeEpochToYMDHMS(epoch,&yr,&mo,&dy,&hr,&mt,&sc);
  return astmlt(yr,mo,dy,hr,mt,(int) sc,mlon,&mslon);
}

