
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "aacgmlib_v2.h"
#include "rtime.h"
#include "astalg.h"

/*-----------------------------------------------------------------------------
  MLT functions for use with AACGM-v2
;
; C user functions intended to compute the magnetic local time at a given
; time and location given by AACGM-v2 coordinates.
;
; Code based on legacy routines authored by Kile Baker, Simon Wing and Robin
; Barnes.
;
; Significant changes include:
;
; - discontinued use of common block used for interpolation between two values
;   separated by 10 minutes.
;
; - MLT is based on the relative AACGM-v2 longitudes of the desired location to
;   that of a reference location. The reference location is taken to be the
;   subsolar point at 700 km altitude. The reference AACGM-v2 longitude is
;   computed using AACGM-v2 coefficients, which act to interpolate through
;   regions where AACGM coordinates are undefined, thereby providing a
;   mechanism for defining the reference longitude in a consistent manner.
;   Differences with values determined at 0 km altitude (where defined) are
;   typically <1 minute and always <5 minutes (in MLT).

; 20170601 SGS v1.2  MLTConvert_v2 now calls AACGM_v2_SetDateTime() if the
;                    AACGM-v2 date/time is not currently set OR if the
;                    date/time passed into one of the public functions differs
;                    from the AACGM-v2 date/time by more than 30 days. In each
;                    case the AACGM-v2 coefficients are loaded and interpolated
;                    which could impact other calls to AACGM_v2_Convert() if
;                    the date/time is not reset.

; Changes

   Combined MLTAst and MLTAst1

   Removed *mlson variable since it is only used for doing linear
     interpolation between two periods separated by 10 minutes.

;
; Public Functions:
; -----------------
;
; mlt  = MLTConvertYMDHMS_v2(yr,mo,dy,hr,mt,sc, mlon, igrf_filename);
; mlon = inv_MLTConvertYMDHMS_v2(yr,mo,dy,hr,mt,sc, mlt, igrf_filename);
;
; mlt  = MLTConvertEpoch_v2(epoch, mlon, igrf_filename);
; mlon = inv_MLTConvertEpoch_v2(epoch, mlt, igrf_filename);
;
; mlt  = MLTConvertYrsec_v2(yr,yrsec, mlon, igrf_filename);
; mlon = inv_MLTConvertYrsec_v2(yr,yrsec, mlt, igrf_filename);
;
; Private Functions:
; ------------------
;
; mlt  = MLTConvert_v2(yr,mo,dy,hr,mt,sc, mlon, root, igrf_filename);
; mlon = inv_MLTConvert_v2(yr,mo,dy,hr,mt,sc, mlt, root, igrf_filename);
; 
;
*/

double mlon_ref = -1;

struct {
  int yr;
  int mo;
  int dy;
  int hr;
  int mt;
  int sc;
} mlt_date = {-1,-1,-1,-1,-1,-1};

/*
 * Accepts scalars but only recomputes mlon_ref if time has changed from last
 * call so computation is fast(er) for multiple calls at same date/time
 *
 * No options here. Use IDL version for development
 *
 */
double MLTConvert_v2(int yr, int mo, int dy, int hr, int mt ,int sc,
		     double mlon, char *root, char *igrf_filename)
{
  int err;
  int ayr,amo,ady,ahr,amt,asc,adyn;
  double dd,jd,eqt,dec,ut,at;
  double slon,mlat,r;
  double hgt,aacgm_mlt;
  double ajd;

  err = 0;
  AACGM_v2_GetDateTime(&ayr, &amo, &ady, &ahr, &amt, &asc, &adyn);
  if (ayr < 0) { 
    /* AACGM date/time not set so set it to the date/time passed in */
    err = AACGM_v2_SetDateTime(yr,mo,dy,hr,mt,sc, root);
    if (err != 0) return (err);
  } else {
    /* If date/time passed into function differs from AACGM data/time by more
     * than 30 days, recompute the AACGM-v2 coefficients */
    ajd = TimeYMDHMSToJulian(ayr,amo,ady,ahr,amt,asc);
    jd =  TimeYMDHMSToJulian(yr,mo,dy,hr,mt,sc);
    if (fabs(jd-ajd) > 30.0) {
      err = AACGM_v2_SetDateTime(yr,mo,dy,hr,mt,sc, root);
    }
    if (err != 0) return (err);
  }

/* check for bad input, which can come from undefined region, and return NAN */
  if (!isfinite(mlon)) {
    return (NAN);
  }

  hgt = 700.;   /* AACGM-v2 coefficients are defined everywhere above this
                 * altitude. */

  if (mlt_date.yr != yr || mlt_date.mo != mo || mlt_date.dy != dy ||
      mlt_date.hr != hr || mlt_date.mt != mt || mlt_date.sc != sc) {
    /* date/time has changed so recompute */
    mlt_date.yr = yr;
    mlt_date.mo = mo;
    mlt_date.dy = dy;
    mlt_date.hr = hr;
    mlt_date.mt = mt;
    mlt_date.sc = sc;

    /* compute corrected time */
    dd  = AstAlg_dday(dy,hr,mt,sc);
    jd  = AstAlg_jde(yr,mo,dd);
    eqt = AstAlg_equation_of_time(jd);
    dec = AstAlg_solar_declination(jd);
    ut  = hr*3600. + mt*60. + sc;
    at  = ut + eqt*60.;

    /* comparision with IDL version is exact
    printf("\n\n");
    printf("dd  = %20.12lf\n", dd);
    printf("jd  = %20.12lf\n", jd);
    printf("eqt = %20.12lf\n", eqt);
    printf("dec = %20.12lf\n", dec);
    printf("\n\n");
    */

    /* compute reference longitude */
    slon = (43200.-at)*15./3600.;         /* subsolar point  */

    /* compute AACGM-v2 coordinates of reference point */
    err = AACGM_v2_Convert(dec, slon, hgt, &mlat, &mlon_ref, &r, G2A,
			   igrf_filename);

    /* check for error: this should NOT happen... */
    if (err != 0) {
      err = -99;
      return (NAN);
    }
  }
/*printf("** %lf\n", mlon_ref);*/

  aacgm_mlt = 12. + (mlon - mlon_ref)/15.;  /* MLT based on subsolar point */

  /* comparision with IDL version is exact */

  while (aacgm_mlt > 24.) aacgm_mlt -= 24.;
  while (aacgm_mlt <  0.) aacgm_mlt += 24.;

  return (aacgm_mlt);
}

/* inverse function: MLT to AACGM-v2 magnetic longitude */
double inv_MLTConvert_v2(int yr, int mo, int dy, int hr, int mt ,int sc,
			 double mlt, char *igrf_filename)
{
  int err;
  double dd,jd,eqt,dec,ut,at;
  double slon,mlat,r;
  double hgt,aacgm_mlon;

/* check for bad input, which should not happen for MLT, and return NAN */
  if (!isfinite(mlt)) {
    return (NAN);
  }

  hgt = 700.;   /* AACGM-v2 coefficients are defined everywhere above this
                 * altitude. */

  if (mlt_date.yr != yr || mlt_date.mo != mo || mlt_date.dy != dy ||
      mlt_date.hr != hr || mlt_date.mt != mt || mlt_date.sc != sc) {
    /* date/time has changed so recompute */
    mlt_date.yr = yr;
    mlt_date.mo = mo;
    mlt_date.dy = dy;
    mlt_date.hr = hr;
    mlt_date.mt = mt;
    mlt_date.sc = sc;

    /* compute corrected time */
    dd  = AstAlg_dday(dy,hr,mt,sc);
    jd  = AstAlg_jde(yr,mo,dd);
    eqt = AstAlg_equation_of_time(jd);
    dec = AstAlg_solar_declination(jd);
    ut  = hr*3600. + mt*60. + sc;
    at  = ut + eqt*60.;

    /* compute reference longitude */
    slon = (43200.-at)*15./3600.;         /* subsolar point  */

    /* compute AACGM-v2 coordinates of reference point */
    err = AACGM_v2_Convert(dec, slon, hgt, &mlat, &mlon_ref, &r, G2A,
			   igrf_filename);

    /* check for error: this should NOT happen... */
    if (err != 0) {
      err = -99;
      return (NAN);
    }
  }

  aacgm_mlon = (mlt - 12.)*15. + mlon_ref;  /* mlon based on subsolar point */

  while (aacgm_mlon >  180.) aacgm_mlon -= 360.;
  while (aacgm_mlon < -180.) aacgm_mlon += 360.;

  return (aacgm_mlon);
}

double MLTConvertYMDHMS_v2(int yr, int mo, int dy, int hr, int mt, int sc,
			   double mlon, char *root, char *igrf_filename)
{
  return (MLTConvert_v2(yr,mo,dy,hr,mt,sc,mlon,root,igrf_filename));
}

double inv_MLTConvertYMDHMS_v2(int yr, int mo, int dy, int hr, int mt, int sc,
			       double mlt, char *igrf_filename)
{
  return (inv_MLTConvert_v2(yr,mo,dy,hr,mt,sc,mlt,igrf_filename));
}

double MLTConvertYrsec_v2(int yr,int yr_sec, double mlon, char *root,
			  char *igrf_filename)
{
  int mo,dy,hr,mt,sc;

  TimeYrsecToYMDHMS(yr_sec,yr,&mo,&dy,&hr,&mt,&sc);

  return (MLTConvert_v2(yr,mo,dy,hr,mt,sc,mlon,root,igrf_filename));
}

double inv_MLTConvertYrsec_v2(int yr, int yr_sec, double mlt,
			      char *igrf_filename)
{
  int mo,dy,hr,mt,sc;

  TimeYrsecToYMDHMS(yr_sec,yr,&mo,&dy,&hr,&mt,&sc);

  return (inv_MLTConvert_v2(yr,mo,dy,hr,mt,sc,mlt,igrf_filename));
}

double MLTConvertEpoch_v2(double epoch, double mlon, char *root,
			  char *igrf_filename)
{
  int yr,mo,dy,hr,mt;
  double sc;

  TimeEpochToYMDHMS(epoch,&yr,&mo,&dy,&hr,&mt,&sc);

  return (MLTConvert_v2(yr,mo,dy,hr,mt,(int)sc, mlon, root, igrf_filename));
}

double inv_MLTConvertEpoch_v2(double epoch, double mlt, char *igrf_filename)
{
  int yr,mo,dy,hr,mt;
  double sc;

  TimeEpochToYMDHMS(epoch,&yr,&mo,&dy,&hr,&mt,&sc);

  return (inv_MLTConvert_v2(yr,mo,dy,hr,mt,(int)sc, mlt, igrf_filename));
}

