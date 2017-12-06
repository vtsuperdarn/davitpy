/* rtime.c
   =======
   Author: R.J.Barnes
*/

/*
 (c) 2010 JHU/APL & Others - Please Consult LICENSE.superdarn-rst.3.2-beta-4-g32f7302.txt for more information.
 
*/

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "rtime.h"

#define DAY_SEC 86400

int TimeYMDHMSToYrsec(int yr,int mo,int dy,int hr,int mn,int sc) {

  time_t clock;
  struct tm tm;
  char *tz;

  memset(&tm,0,sizeof(struct tm));
  tm.tm_year=yr-1900;
  tm.tm_mon=0;
  tm.tm_mday=1;
  tm.tm_hour=0;
  tm.tm_min=0;
  tm.tm_sec=0;

  tz = getenv("TZ");
  setenv("TZ", "", 1);
  tzset();
  clock=mktime(&tm);

  memset(&tm,0,sizeof(struct tm));
  tm.tm_year=yr-1900;
  tm.tm_mon=mo-1;
  tm.tm_mday=dy;
  tm.tm_hour=hr;
  tm.tm_min=mn;
  tm.tm_sec=sc;
  clock=mktime(&tm)-clock;
  

  if (tz) setenv("TZ", tz, 1);
  else unsetenv("TZ");
  tzset();

  return (int) clock;
}

void TimeYrsecToYMDHMS(int yrsec,int yr,int *mo,int *dy,int *hr,int *mn,
                  int *sc) {


  time_t clock;
  struct tm tmyr;
  struct tm *tm;
  char *tz;

  memset(&tmyr,0,sizeof(struct tm));
  tmyr.tm_year=yr-1900;
  tmyr.tm_mon=0;
  tmyr.tm_mday=1;
  tmyr.tm_hour=0;
  tmyr.tm_min=0;
  tmyr.tm_sec=0;

  tz = getenv("TZ");
  setenv("TZ", "", 1);
  tzset();
 
  clock=mktime(&tmyr);
  if (tz) setenv("TZ", tz, 1);
  else unsetenv("TZ");
  tzset();

  clock=clock+yrsec;
  tm=gmtime(&clock);
  
  *mo=tm->tm_mon+1;
  *dy=tm->tm_mday;
  *hr=tm->tm_hour; 
  *mn=tm->tm_min;
  *sc=tm->tm_sec;
}


double TimeYMDHMSToEpoch(int yr,int mo,int dy,int hr,int mn,double sc) {
 
  time_t clock;
  struct tm tm;
  char *tz;

  memset(&tm,0,sizeof(struct tm));
  tm.tm_year=yr-1900;
  tm.tm_mon=mo-1;
  tm.tm_mday=dy;
  tm.tm_hour=hr;
  tm.tm_min=mn;
  tm.tm_sec=floor(sc);

  tz = getenv("TZ");
  setenv("TZ", "", 1);
  tzset();
  clock=mktime(&tm);
  if (tz) setenv("TZ", tz, 1);
  else unsetenv("TZ");
  tzset();
               
  return clock+(sc-floor(sc));
}

void TimeEpochToYMDHMS(double tme,int *yr,int *mo,int *dy,int *hr,int *mn,
         double *sc) {
  time_t clock;
  struct tm *tm;

  clock=floor(tme);
  tm=gmtime(&clock);
  
  *yr=tm->tm_year+1900;
  *mo=tm->tm_mon+1;
  *dy=tm->tm_mday;
  *hr=tm->tm_hour; 
  *mn=tm->tm_min;
  *sc=tm->tm_sec+(tme-floor(tme));
}

double TimeYMDHMSToJulian(int yr,int mo,int dy,int hr,int mt,double sc) {

  int A,B,i;
  double jdoy;
  double dfrac;
  yr=yr-1;
  i=yr/100;
  A=i;
  i=A/4;
  B=2-A+i;
  i=365.25*yr;
  i+=30.6001*14;
  jdoy=i+1720994.5+B;

  
  dfrac=1+TimeYMDHMSToYrsec(yr+1,mo,dy,hr,mt,sc)/DAY_SEC;
   
  return jdoy+dfrac; 

}


int TimeJulianToYMDHMS(double jd,int *yr,int *mo,
                 int *dy,int *hr,int *mt,double *sc) {

  int Z,month;
  int hour,minute;

  double A,B,C,D,E,F,alpha,day,year,factor,second;

  factor=0.5/DAY_SEC/1000; 
  F=(jd+0.5)-floor(jd+0.5);
  if ((F+factor)>=1.0) {
    jd=jd+factor;
    F=0.0;
  }

  Z=floor(jd+0.5);

  if (Z<2299161) A=Z;
  else {
    alpha=floor((Z-1867216.25)/36524.25);
    A=Z+1+alpha-floor(alpha/4);
  }

  B=A+1524;
  C=floor((B-122.1)/365.25);
  D=floor(365.25*C);
  E=floor((B-D)/30.6001);
  day=B-D-floor(30.6001*E)+F;

  if (E<13.5) month=floor(E-0.5);
  else month=floor(E-12.5);
  if (month>2.5) year=C-4716;
  else year=C-4715;
  


  *yr=(int) year;
  *mo=month;
  *dy=(int) floor(day);

  /* okay now use the residual of the day to work out the time */

  A=(day-floor(day))*DAY_SEC;

  hour=(int) (A/3600.0);
  minute=(int) ((A-hour*3600)/60);
  second=A-hour*3600-minute*60;
    
  *hr=hour;
  *mt=minute;
  *sc=second;
  return 0;
}

