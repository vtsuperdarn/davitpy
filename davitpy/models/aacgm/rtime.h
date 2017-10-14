/* rtime.h
   +======
   Author: R.J.Barnes
*/

/*
 (c) 2010 JHU/APL & Others - Please Consult LICENSE.superdarn-rst.3.2-beta-4-g32f7302.txt for more information.
*/

#ifndef _RTIME_H
#define _RTIME_H

void   TimeYrsecToYMDHMS(int time,int yr,
                        int *mo,int *dy, int *hr,int *mn,int *sc);
int    TimeYMDHMSToYrsec(int yr, int mo, int dy, int hr, int mn, int sc);
double TimeYMDHMSToEpoch(int yr,int mo,int dy,int hr,int mn,double sc);
void   TimeEpochToYMDHMS(double tme,
                        int *yr,int *mo,int *dy,int *hr,int *mn, double *sc);
double TimeYMDHMSToJulian(int yr,int mo,int dy,int hr,int mt,double sc);
int    TimeJulianToYMDHMS(double jd,
                        int *yr,int *mo, int *dy,int *hr,int *mt,double *sc);
void   TimeReadClock(int *yr, int *mo, int *dy, int *hr, int *mn, int *sc,
                        int *usc);

#endif

