/* astalglib.c
 *
 * collection of Astronomical Algorithms see LICENSE.txt
 *
 * minor reformatting by SGS for including in AACGM-v2 software
 *
 */

/* ----------------- REFERENCE ------------------------

The software contained herein is derived from algorithms published
in the book _Astronomical Algorithms_, Second Edition, by Jean Meeus,
publisher: Willman-Bell, Inc., Richmond, Virginia, 1998 (corrections
dated 2005).

The book will be referred to as "Meeus" for short.

*/

#include <stdio.h>
#include <math.h>
#include "astalg.h"

/* AstAlg_apparent_obliquity
   =========================
   Author: Kile Baker
*/

/* This function calculates the apparent obliquity (angle between
   the earth's spin axis and the ecliptic).  It uses the
   mean obliquity and the effect of the lunar position.

   Calling sequence:
     eps = AstAlg_apparent_obliquity(double julian_day)

   The value is returned in degrees.
*/

double AstAlg_apparent_obliquity(double jd) {

  static double last_jd, last_eps;

  /* if we've already calculated the value just return it */

  if (jd == last_jd) return (last_eps);

  last_jd = jd;
  last_eps = AstAlg_mean_obliquity(jd) + 
              0.00256 * cos(AstAlg_DTOR * AstAlg_lunar_ascending_node(jd));

  return (last_eps);
}

/* AstAlg_apparent_solar_longitude
   ===============================
   Author: Kile Baker
*/

/* This function calculates the apparent solar longitude for a given
   Julian Day using the geometric solar longitude along with 
   the effect of the position of the moon.

   Calling Sequence:
     asl = AstAlg_apparent_solar_longitude(double jd)

     The returned value is in degrees.
*/

double AstAlg_apparent_solar_longitude(double jd) {

  static double last_jd, last_asl;
    
  /* if we've already calculated the value simply return it */

  if (jd == last_jd) return (last_asl);

  last_jd = jd;
  last_asl = AstAlg_geometric_solar_longitude(jd) - 0.00569 -
              0.00478*sin(AstAlg_DTOR * AstAlg_lunar_ascending_node(jd));

  return (last_asl);
}

/* AstAlg_dday
   =============
   Author: Kile Baker
*/

/* This routine is a fairly trivial one.  In the AstAlg software
   it is commonly necessary to know the decimal day (i.e. day of month
   and fraction thereof.  This routine simply calculates the decimal
   day as a double precision number from the day, hour, minute, and second.

   No attempt is made to check the validity of the arguments so you can
   create a garbage result if you give it nonsense values like setting
   the day to 1000 or the hour to 50, etc.
*/

double AstAlg_dday(int day, int hour, int minute, int second) {

/* SGS Changed */
/* Kile, this is WRONG! Nathanial found this bug */
/*  return (double) (day + hour/24.0 + minute/60.0 + second/3600.0);*/
  return ((double) (day + (hour + minute/60.0 + second/3600.0)/24.));
}

/* AstAlg_equation_of_time
   =========================
   Author: Kile Baker
*/

/* This function returns the equation of time for a given
   Julian date.

   The returned value is the difference between the apparent time and the
   mean solar time.  The correction is returned in minutes and is always
   between + and - 20.

   A positive value menas that the true sun crosses the observer's meridian
   before the mean sun (i.e. mean time is lagging).

   Calling sequence:

   eqt = AstAlg_equation_of_time(double jd)

   This routine calls AstAlg_mean_solar_longitude,
   AstAlg_solar_right_ascension, AstAlg_mean_obliquity,
   and AstAlg_nutation_corr.
*/

double AstAlg_equation_of_time(double jd) {

  static double last_jd, last_eqt;

  double eqt;
  double dpsi, deps, sml, sra, obliq;

  /* if we've already calculated the value, simply return it */

  if (jd == last_jd) return (last_eqt);

  /* first get all the separate pieces */
  sml = AstAlg_mean_solar_longitude(jd);
  sra = AstAlg_solar_right_ascension(jd);
  obliq = AstAlg_mean_obliquity(jd);
  AstAlg_nutation_corr(jd, &dpsi, &deps);

  /* now put it all together */

  eqt = sml - 0.0057183 - sra + dpsi*cos(AstAlg_DTOR*(obliq + deps));

  eqt = dmod(eqt,360.0);

  /* now convert from degrees to minutes */
  eqt = 4.0 * eqt;

  if (eqt > 20.0) eqt = eqt - 24.0*60.0; /*wrap back 24 hours*/
  if (eqt < -20.0) eqt = 24.0*60.0 + eqt; /*wrap forward 24 hours */

  last_jd = jd;
  last_eqt = eqt;

  return (eqt);
}

/* AstAlg_geometric_solar_longitude
   ================================
   Author: Kile Baker
*/

/* This function calculates the geometric_solar_longitude.

  Calling sequence:
   gsl = AstAlg_geometric_solar_longitude(julian_day)

   The returned value is in degrees from 0 to 360

   The function requires the mean solar longitude and the
   mean solar anomaly.

*/

double AstAlg_geometric_solar_longitude(double jd) {

  static double last_jd, last_gsl;

  double sml, sma, tau, gc;

  /* if we've already calculated the value for this Julian Day just
     return it */

  if (last_jd == jd) return (last_gsl);

  /* compute the delta-tau in centuries from the reference time J2000 */
  tau = (jd - J2000)/36525.0;

  sml = AstAlg_mean_solar_longitude(jd);

  /* we need the mean solar anomaly in radians because it's used in some
     sine functions */
  sma = AstAlg_DTOR * AstAlg_mean_solar_anomaly(jd);

  gc = (1.914602 - 0.004817*tau - 0.000014*(tau*tau)) * sin(sma)
      + (0.019993 - 0.000101*tau) * sin(2.0*sma)
      + 0.000289 * sin(3.0*sma);

  sml += gc;
/*  sml = sml + gc;*/

  /* make sure the value is between 0 and 360 degrees */
  sml = dmod(sml, 360.0);

  if (sml < 0.0) sml += 360.0;

  last_jd = jd;
  last_gsl = sml;

  return (sml);
}

/* AstAlg_jde2calendar
   ===================
   Author: Kile Baker
*/

/* This routine converts Julian Day to calendar year, month, day,
   hour, minute and second */

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

  jd +=  0.5;

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
}

/* AstAlg_jde
   ==========
   Author: Kile Baker
*/

/* This routine returns the Julian Day as a double precision value

   Calling sequence:

   jd = AstAlg_jde( int year, int month, double day)

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

double AstAlg_jde(int year, int month, double day) {

/* NOTE: the value of 'year' must be the full 4-digit year */

  int a;
  double b;

/* if the month is January or February, treat it as belonging
   to the previous year.  This makes the leap year correction
   easier to handle */

  if (month <= 2) {
    year--;
    month += 12;
  }

/* the next few lines perform the leap year correction.  It deals
   with the centuries correctly */

  a = (int) (year/100);
  b = (double) (2 - a + a/4);

/* ideally, the constant 30.6001 could simply be 30.6, but adding the
   additional .0001 to it ensures that truncation error doesn't result
   in an incorrect calculation */

  return ((double) ( (long) (365.25*(year + 4716)) +
          (double) ( (long) (30.6001 * (month + 1)))) + day + b - 1524.5);
}

/* AstAlg_lunar_ascending_node
   ===========================
   Author: Kile Baker
*/

/* This function calculates the location of the moon's ascending node.
   This value affects the nutation of the Earth's spin axis.
   
   Calling Sequence:
     asc_node = AstAlg_lunar_ascending_node(double jd)

     where jd is the Julian Day
*/

double AstAlg_lunar_ascending_node(double jd) {

  static double last_jd, last_ascn;
  double tau, omega;

/* if we've already calculated the value just return it */

  if (jd == last_jd) return (last_ascn);

/* calculate the delta-time in centuries with respect to 
   the reference time J2000 */

  tau = (jd - J2000)/36525.0;

/* omega = 125 - 1934 * tau + .002*tau^2 + t^3/4.5e5 */

  omega = (((tau/4.50e5 + 2.0708e-3)*tau - 1.934136261e3)*tau) + 125.04452;

/* now make sure omega is between 0 and 360 */

  omega = dmod(omega, 360.0);

  if (omega < 0.0) omega += 360.0;

  last_jd = jd;
  last_ascn = omega;

  return (omega);
}
     
/* AstAlg_mean_lunar_longitude
   ===========================
   Author: Kile Baker
*/

/* This function calculates the mean lunar longitude for a given
   Julian Day.

   Calling Sequence:

   lunlong = AstAlg_mean_lunar_longitude(double jd)

*/

double AstAlg_mean_lunar_longitude(double jd) {

  static double last_jd, last_llong;
  double tau, llong;

/* simply return the value if we've already calculated it */

  if (jd == last_jd) return (last_llong);

/* calculate the detla-time from the reference time J2000 in centuries */

  tau = (jd - J2000)/36525.0;

  llong = 218.3165 + 481267.8813 * tau;

/* make sure the resulting value is between 0 and 360 */

  llong = dmod(llong, 360.0);

  if (llong < 0) llong += 360.0;

  last_jd = jd;
  last_llong = llong;

  return (llong);
}

/* AstAlg_apparent_solar_longitude
   ===============================
   Author: Kile Baker
*/

/* This function calcules the mean obliquity of the earth.  That is
   the inclination of the rotation axis relative to the ecliptic plane.

   Calling Sequence:

    e0 = AstAlg_mean_obliquity(julian_date)

    The returned value is in degrees.

*/

double AstAlg_mean_obliquity(double jd) {

  static double last_jd, last_e0;
  double tau;
  const double coefs[] = {23.439291111111, -0.0130041666667, -1.638888889e-7,
                          5.036111111e-7};

/* if we've already calculated this value for this date simply return it */

  if (jd == last_jd) return (last_e0);

    /* the coefficients in Meeus are given in degrees, minutes and seconds
       so I have to convert them to double precision degrees first.
       Although this could be done before compilation it would make
       it hard to check the code with the book.  I therefore do 
       the calculation here but only the first time the routine is called.
    */

/*    if (coeffs[3] != 0.001813/3600.0) {
  coeffs[3] = 0.001813/3600.0;
  coeffs[2] = -0.00059/3600.0;
  coeffs[1] = -46.8150/3600.0;
  coeffs[0] = 23.0 + 26.0/60.0 + 21.448/3600.0;
    }
*/

  tau = (jd - J2000)/36525.0;

/* Now calculate the value of e0 */
  last_e0 = ((((coefs[3]*tau) + coefs[2]) * tau) + coefs[1]) * tau + coefs[0];
  last_jd = jd;

  return (last_e0);
}

/* AstAlg_apparent_solar_anomaly
   =============================
   Author: Kile Baker
*/

/* This function calculates the mean solar anomaly for a given Julian day 
(see function AstAlg_jde.c).

 Calling Sequence:
   slong = AstAlg_mean_solar_anomaly(double jd);

   The returned value is in degrees and ranges from 0 to 360

*/

double AstAlg_mean_solar_anomaly( double jd ) {

/* last calculated value for this function is saved.  This is done
   to avoid recalculating the value multiple times, since it is used
   in several other functions in the AstAlg library */

  static double last_jd, last_sma;

  double tau, sma;

  if (jd == last_jd) return (last_sma);

/* calculate the difference between the requested Julian Day and
    the reference value, J2000, in centuries */

  tau = (jd - J2000)/36525.0;
  sma = 357.5291130 + 35999.05029 * tau - 0.0001537 * (tau*tau);

/* make sure the value is between 0 and 360 */

  sma = dmod(sma, 360);

  if (sma < 0.0) sma += 360.0;

  last_jd = jd;
  last_sma = sma;

  return (sma);
}

/* AstAlg_mean_solar_longitude
   ===========================
   Author: Kile Baker
*/

/* This function calculates the mean solar longitude for a given Julian day (see function AstAlg_jde.c).

 Calling Sequence:
   slong = AstAlg_mean_solar_longitude(double jd);

   The returned value is in degrees and ranges from 0 to 360

*/

double AstAlg_mean_solar_longitude( double jd ) {

/* the mean solar longitude gets called from several other functions
   and we don't want to have to recalculate the value every time, so
   the last calculated value is saved as a static value */

  static double last_jd, last_sl;

  static const double coefs[] = {280.4664567, 360007.6982779,
                                  0.03032028, 2.00276381406e-5,
                                  -6.53594771242e-5, -0.50e-6 };
  double tau, sl;
  int i;

  if (jd == last_jd) return (last_sl);

/* calculate the difference between the requested Julian day and the
   reference Julian day, J2000, in terms of milennia */

  tau = (jd - J2000)/365250.0;

/* now calculate the solar longitude using the delta-time tau and the
   coefficients */

  sl = 0.0;
  for (i=5; i>=0; i--) {
    sl = tau * sl + coefs[i];
  }

/* make sure the result is between 0 and 360 degrees */

  sl = dmod(sl, 360);

  if (sl < 0.0) sl += 360.0;

  last_jd = jd;
  last_sl = sl;

  return (sl);
}

/* AstAlg_nutation_corr
   ====================
   Author: Kile Baker
*/

/* This routine calculates the corrections to the solar longitude and
   obliquity that arize due to the nutation of the earth's spin.
   
   Calling Sequence:

   void AstAlg_nutation_corr(double jd, double *slong_corr, double *obliq_corr)

*/

void AstAlg_nutation_corr(double jd, double *slong_corr, double *obliq_corr)
{
  double slong, lunlong, omega;
  static double last_jd, last_slcorr, last_oblcorr;

/* just return the values if they've already been calculated */

  if (jd == last_jd) {
    *slong_corr = last_slcorr;
    *obliq_corr = last_oblcorr;
    return;   /* SGS added */
  }

/* get the mean solar longitude and mean lunar longitude in radians */

  slong = AstAlg_DTOR * AstAlg_mean_solar_longitude(jd);
  lunlong = AstAlg_DTOR * AstAlg_mean_lunar_longitude(jd);
  omega = AstAlg_DTOR * AstAlg_lunar_ascending_node(jd);

/* the next line computes the correction to the solar longitude in arcsecs */

  *slong_corr = -17.20 * sin(omega) - 1.32 * sin(2.0*slong) -
                  0.23 * sin(2.0*lunlong) + 0.21 * sin(2.0*omega);

/* convert from arcsec to degrees */
  *slong_corr = *slong_corr/3600.0;

/* Next we calculate the correction to the obliquity in arcsecs */

  *obliq_corr = 9.20 * cos(omega) + 0.57 * cos(2.0*slong) +
                0.10 * cos(2.0*lunlong) - 0.09 * cos(2.0*omega);

  *obliq_corr = *obliq_corr/3600.0;

/* save the calculated values in case their needed again */
  last_jd = jd;
  last_slcorr = *slong_corr;
  last_oblcorr = *obliq_corr;
}

/* AstAlg_apparent_solar_declination
   =================================
   Author: Kile Baker
*/

/* This function returns the apparent declination of the sun for a given
   Julian Day.  It uses the apparent_obliquity and the apparent solar
   longitude.

   Calling sequence:

    sdec = AstAlg_solar_declination(double jd)

    The value is returned in degrees.
*/

double AstAlg_solar_declination(double jd) {

  static double last_jd, last_sdec;
  double sindec;

/* if we've already calculated the value simply return it */

  if (jd == last_jd) return (last_sdec);

  sindec = sin(AstAlg_DTOR * AstAlg_apparent_obliquity(jd)) *
            sin(AstAlg_DTOR * AstAlg_apparent_solar_longitude(jd));

  last_jd = jd;
  last_sdec = asin(sindec)/AstAlg_DTOR;

  return (last_sdec);
}

/* AstAlg_solar_right_ascension
   ============================
   Author: Kile Baker
*/

/* This function returns the right ascension of the sun for a given
   Julian date.

   Calling sequence:
     ra = AstAlg_solar_right_ascension(double jd)

   The value is returned in DEGREES, not in the more traditional
   hours.  Convert to hour angle by dividing degrees by 15.

   The function calls the functions AstAlg_apparent_solar_longitude
   and AstAlg_apparent_obliquity

*/

double AstAlg_solar_right_ascension(double jd) {

  static double last_jd, last_ra;
  double eps, slong, alpha;

/* if we've already calculated the value, simply return it. */

  if (jd == last_jd) return (last_ra);

  /* get the solar longitude in radians */
  slong = AstAlg_DTOR * AstAlg_apparent_solar_longitude(jd);

  /* get the obliquity in radians */
  eps = AstAlg_DTOR * AstAlg_apparent_obliquity(jd);

  alpha = atan2(cos(eps)*sin(slong),cos(slong));

  last_ra = alpha/AstAlg_DTOR;
  last_jd = jd;

  return (last_ra);
}

