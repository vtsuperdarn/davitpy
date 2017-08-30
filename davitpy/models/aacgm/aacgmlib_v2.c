/*-----------------------------------------------------------------------------
; AACGM library
;
; a collection of C routines intended to fully exploit the functionality of
; the AACGM coordinates [Shepherd, 2014] including use of the AACGM
; coefficients and field line tracing
;
; 20140611 SGS v0.0  Modification to existing AACGM C and IDL software, but
;                    includes additional features: linear interpolation and
;                    fieldline tracing.
; 20140702 SGS v0.1  Made operational, moved globals to library, fixed bug
;                    in malloc.
; 20140703 SGS v0.2  Added AACGM_GetDateTime() function to provide capability
;                    of getting date and time used in calculations (Jeff).
;                    Changed behavior to abort (with message) if not data/time
;                    is set.
;                    Variable fact changed to double from unsigned long which
;                    is not big enought on some 32-bit systems.
;                    Switched from NAN to HUGE_VAL for undefined result
; 20140918 SGS v1.0  change function names to _v2 for wider distribution
; 20150810 SGS v1.1  added code to default to geodetic coordinates for inverse
;                    transformation. This code was left out in the C version.
; 20170308 SGS v1.2  Added static to global variables in order to work with RST
;                    library.
;
; Functions:
;
; AACGM_v2_Rylm
; AACGM_v2_Alt2CGM  - not used
; AACGM_v2_CGM2Alt
; AACGM_v2_Sgn
; convert_geo_coord_v2
; AACGM_v2_LoadCoefFP
; AACGM_v2_LoadCoef
; AACGM_v2_LoadCoefs
; AACGM_v2_Convert
; AACGM_v2_SetDateTime
; AACGM_v2_GetDateTime
; AACGM_v2_SetNow
; AACGM_v2_errmsg
;

; AACGM_v2_Dayno
; AACGM_v2_Trace
; AACGM_v2_Trace_inv
;
;------------------------------------------------------------------------------
*/


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "aacgmlib_v2.h"
#include "igrflib.h"
#include "genmag.h"

#define DEBUG 0

/* put these in the library header file when you figure out how to do so... */
static struct {
  int year;
  int month;
  int day;
  int hour;
  int minute;
  int second;
  int dayno;
  int daysinyear;
} aacgm_date = {-1,-1,-1,-1,-1,-1,-1,-1};

static int myear = 0;       /* model year: 5-year epoch */
static double fyear = 0.;   /* floating point year */

static int myear_old = -1;
static double fyear_old = -1.;

static double height_old[2] = {-1,-1};

static struct {
  double coef[AACGM_KMAX][NCOORD][POLYORD][NFLAG];      /* interpolated coefs */
  double coefs[AACGM_KMAX][NCOORD][POLYORD][NFLAG][2];  /* bracketing coefs */
} sph_harm_model;

/* SGS added for MSC compatibility */
#ifndef complex
struct complex {
  double x;
  double y;
};
#endif


/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_Rylm
;
; PURPOSE:
;       Computes an array of real spherical harmonic function values
;       Y_lm(phi,theta) for a given colatitiude (phi) and longitude (theta)
;       for all the values up to l = order, which is typically 10. The
;       values are stored in a 1D array of dimension (order+1)^2. The
;       indexing scheme used is:
;
;        l    0  1  1  1  2  2  2  2  2  3  3  3  3  3  3  3  4  4  4  4  4 ...
;        m    0 -1  0  1 -2 -1  0  1  2 -3 -2 -1  0  1  2  3 -4 -3 -2 -1  0 ...
;C & IDL j    0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 ...
;FORTRAN j    1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 ...
; 
; CALLING SEQUENCE:
;       AACGM_v2_Rylm, colat,lon,order, ylmval
;
;     Input Arguments:  
;       colat         - The colatitude of the point for which the spherical
;                       harmonic Y_lm is to be calculated
;
;       lon           - The longitude of the point for which the spherical
;                       harmonic Y_lm is to be calculated
;
;       order         - The order of the spherical harmonic function expansion.
;                       The total number of terms computed will be (order+1)^2
;
;     Output Argument:
;       ylmval        - 1D array of spherical harmonic functions at the point
;                       (colat,lon)
;
; HISTORY:
;
; Revision 1.1  94/10/12  15:24:21  15:24:21  baker (Kile Baker S1G)
; Initial revision
;
; subsequent revisions, porting to C and IDL by baker, wing and barnes.
;
; NOTES by SGS:
;
; It is likely that the original version was taken from FORTRAN and used array
; indexing that begins with 1. Indexing is somewhat more natural using the
; zeros-based indexing of C/IDL. Indices have thus been changed from the
; original version.
;
; It appears that the original version used unnormalized spherical harmonic
; functions. I suspect this might be better, but realized it too late. The
; coefficients I derived are for orthonormal spherical harmonic functions
; which then require the same for evaluation. I believe that the original
; authors used orthogonal spherical harmonic functions which eliminate the
; need for computing the normalization factors. I suspect this is just fine,
; but have not tested it.
; 
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_Rylm(double colat, double lon, int order, double *ylmval)
{
  struct complex z1, z2;
  struct complex q_fac, q_val;
  int k, l, m, kk;
  int ia,ib,ic,id;
  double cos_theta, sin_theta;  
  double cos_lon, sin_lon;
  double l2, tl, fac;
  double ca, cb, d1;
  double *ffff;
  /* long unsigned *fact;    not big enough for 32-bit machines */
  double *fact;

  cos_theta = cos(colat);
  sin_theta = sin(colat);

  cos_lon = cos(lon);
  sin_lon = sin(lon);

  d1 = -sin_theta;
  z2.x = cos_lon;
  z2.y = sin_lon;

  z1.x = d1 * z2.x;
  z1.y = d1 * z2.y;
  q_fac = z1;

  /*
   * Generate Zonal Harmonics (P_l^(m=0) for l = 1,order) using recursion
   * relation (6.8.7), p. 252, Numerical Recipes in C, 2nd. ed., Press. W.
   * et al. Cambridge University Press, 1992) for case where m = 0.
   *
   * l Pl = cos(theta) (2l-1) Pl-1 - (l-1) Pl-2          (6.8.7)
   *
   * where Pl = P_l^(m=0) are the associated Legendre polynomials
   *
   */

  ylmval[0] = 1;            /* l = 0, m = 0 */
  ylmval[2] = cos_theta;    /* l = 1, m = 0 */

  for (l=2; l<=order; l++) {
    /* indices for previous two values: k = l * (l+1) + m with m=0 */
    ia = (l-2)*(l-1);
    ib = (l-1)*l;
    ic = l * (l+1);

    ylmval[ic] = (cos_theta * (2*l-1) * ylmval[ib] - (l-1)*ylmval[ia])/l;
  }

  /*
   * Generate P_l^l for l = 1 to (order+1)^2 using algorithm based upon (6.8.8)
   * in Press et al., but incorporate longitude dependence, i.e., sin/cos (phi)
   *
   * Pll = (-1)^l (2l-1)!! (sin^2(theta))^(l/2)
   *
   * where Plm = P_l^m are the associated Legendre polynomials
   *
   */

  q_val = q_fac;
  ylmval[3] = q_val.x;    /* l = 1, m = +1 */
  ylmval[1] = -q_val.y;   /* l = 1, m = -1 */
  for (l=2; l<=order; l++) {
    d1    = l*2 - 1.;
    z2.x  = d1 * q_fac.x;
    z2.y  = d1 * q_fac.y;
    z1.x  = z2.x * q_val.x - z2.y * q_val.y;
    z1.y  = z2.x * q_val.y + z2.y * q_val.x;
    q_val = z1;

    /* indices for previous two values: k = l * (l+1) + m */
    ia = l*(l+2);   /* m = +l */
    ib = l*l;       /* m = -l */

    ylmval[ia] =  q_val.x;
    ylmval[ib] = -q_val.y;
  }

  /*
   * Generate P_l,l-1 to P_(order+1)^2,l-1 using algorithm based upon (6.8.9)
   * in Press et al., but incorporate longitude dependence, i.e., sin/cos (phi)
   *
   * Pl,l-1 = cos(theta) (2l-1) Pl-1,l-1
   *
   */

  for (l=2; l<=order; l++) {

    l2 = l*l;
    tl = 2*l;
    /* indices for Pl,l-1; Pl-1,l-1; Pl,-(l-1); Pl-1,-(l-1) */
    ia = l2 - 1;
    ib = l2 - tl + 1;
    ic = l2 + tl - 1;
    id = l2 + 1;

    fac = tl - 1;
    ylmval[ic] = fac * cos_theta * ylmval[ia];      /* Pl,l-1   */
    ylmval[id] = fac * cos_theta * ylmval[ib];      /* Pl,-(l-1) */
  }

  /*
   * Generate remaining P_l+2,m to P_(order+1)^2,m for each m = 1 to order-2
   * using algorithm based upon (6.8.7) in Press et al., but incorporate
   * longitude dependence, i.e., sin/cos (phi).
   *
   * for each m value 1 to order-2 we have P_mm and P_m+1,m so we can compute
   * P_m+2,m; P_m+3,m; etc.
   *
   */

  for (m=1; m<=order-2; m++) {
    for (l=m+2; l<=order; l++) {
      ca = ((double) (2*l-1))/(l-m);
      cb = ((double) (l+m-1))/(l-m);

      l2 = l*l;
      ic = l2 + l + m;
      ib = l2 - l + m;
      ia = l2 - l - l - l + 2 + m;
      /* positive m */
      ylmval[ic] = ca * cos_theta * ylmval[ib] - cb * ylmval[ia];

      ic -= (m+m);
      ib -= (m+m);
      ia -= (m+m);
      /* negative m */
      ylmval[ic] = ca * cos_theta * ylmval[ib] - cb * ylmval[ia];
    }
  }

  /*
   * Normalization added here (SGS)
   * 
   * Note that this is NOT the standard spherical harmonic normalization factors
   * 
   * The recursive algorithms above treat positive and negative values of m in
   * the same manner. In order to use these algorithms the normalization must
   * also be modified to reflect the symmetry.
   * 
   * Output values have been checked against those obtained using the internal
   * IDL legendre() function to obtain the various associated legendre
   * polynomials.
   * 
   * As stated above, I think that this normalization may be unnecessary. The
   * important thing is that the various spherical harmonics are orthogonal,
   * rather than orthonormal.
   * 
   */

  /* determine array of factorials */
  /*fact = (long unsigned *)malloc(sizeof(long unsigned)*(2*order+2));*/
  fact = (double *)malloc(sizeof(double)*(2*order+2));
  if (fact == NULL) return (-1);
  fact[0] = fact[1] = 1;
  for (k=2; k <= 2*order+1; k++) fact[k] = k*fact[k-1];

  ffff = (double *)malloc(sizeof(double)*(order+1)*(order+1));
  if (ffff == NULL) return (-1);

  /* determine normalization factors */
  for (l=0; l<=order; l++) {
    for (m=0; m<=l; m++) {
      k = l * (l+1) + m;      /* 1D index for l,m */
      ffff[k] = sqrt((2*l+1)/(4*M_PI) * fact[l-m]/fact[l+m]);
      ylmval[k] *= ffff[k];
    }
    for (m=-l; m<0; m++) {
      k  = l * (l+1) + m;     /* 1D index for l,m */
      kk = l * (l+1) - m;
      ylmval[k] *= ffff[kk] * ((-m % 2) ? -1 : 1);
    }
  }

  #if DEBUG > 1
  for (k=0; k<2*order+1; k++)
    /*printf("%03d %lu\n", k, fact[k]);*/
    printf("%03d %lf\n", k, fact[k]);
  #endif

  free(fact);
  free(ffff);

  #if DEBUG > 10
  for (l=0; l<=order; l++) {
    for (m=0; m<=l; m++) {
      k = l * (l+1) + m;      /* 1D index for l,m */
      printf("%03d %lf\n", k, ylmval[k]);
    }
  }
  #endif

  return (0);
} 

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_Alt2CGM
;
; PURPOSE:
;       Transformation from so-called 'at-altitude' coordinates to AACGM.
;       The purpose of this function is to scale the latitudes in such a
;       way so that there is no gap. The problem is that for non-zero
;       altitudes (h) are range of latitudes near the equator lie on dipole
;       field lines that near reach the altitude h, and are therefore not
;       accessible. This is the inverse transformation.
;
;       cos (lat_aacgm) = sqrt( Re/(Re + h) ) cos (lat_at-alt)
;       
;
; CALLING SEQUENCE:
;       AACGM_v2_Alt2CGM,r_height_in,r_lat_alt,r_lat_adj
;
;     Input Arguments:  
;       r_height_in   - The altitude (h)
;       r_lat_alt     - The 'at-altitude' latitude
;
;     Output Arguments:  
;       r_lat_adj     - The corrected latitude, i.e., AACGM latitude
;
; HISTORY:
;
; This function is unchanged from its original version (Baker ?)
;     
;+-----------------------------------------------------------------------------
*/

void AACGM_v2_Alt2CGM(double r_height_in, double r_lat_alt, double *r_lat_adj)
{
  double eps =1e-9;
  double unim =0.9999999;

  double r1;
  double r0, ra;

  #if DEBUG > 0
  printf("AACGM_v2_Alt2CGM\n");
  #endif

  /* Computing 2nd power */
  r1 = cos(r_lat_alt*DTOR);
  ra = r1 * r1;
  if (ra < eps) ra = eps;

  r0 = (r_height_in/RE + 1.) / ra;
  if (r0 < unim) r0 = unim;
  
  r1 = acos(sqrt(1/r0));
  *r_lat_adj = AACGM_v2_Sgn(r1, r_lat_alt)/DTOR;
} 

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_CGM2Alt
;
; PURPOSE:
;       Transformation from AACGM to so-called 'at-altitude' coordinates.
;       The purpose of this function is to scale the latitudes in such a
;       way so that there is no gap. The problem is that for non-zero
;       altitudes (h) are range of latitudes near the equator lie on dipole
;       field lines that near reach the altitude h, and are therefore not
;       accessible. This mapping closes the gap.
;
;       cos (lat_at-alt) = sqrt( (Re + h)/Re ) cos (lat_aacgm)
;       
;
; CALLING SEQUENCE:
;       AACGM_v2_CGM2Alt,r_height_in,r_lat_in,r_lat_adj, error
;
;     Input Arguments:  
;       r_height_in   - The altitude (h)
;       r_lat_in      - The AACGM latitude
;
;     Output Arguments:  
;       r_lat_adj     - The 'at-altitude' latitude
;       error         - variable is set if latitude is below the value that
;                       is mapped to the origin
;
; HISTORY:
;
; This function is unchanged from its original version (Baker ?)
;     
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_CGM2Alt(double r_height_in, double r_lat_in, double *r_lat_adj)
{
  double unim=1;
  double r1;
  double ra;
  int error=0;

  #if DEBUG > 0
  printf("AACGM_v2_CGM2Alt\n");
  #endif

  /* convert from AACGM to at-altitude coordinates */
  r1 = cos(r_lat_in*DTOR);
  ra = (r_height_in/RE + 1)*(r1*r1);
  if (ra > unim) {
    ra = unim;
    error = 1;
  }

  r1 = acos(sqrt(ra));
  *r_lat_adj = AACGM_v2_Sgn(r1,r_lat_in)/DTOR;

  return (error);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_Sgn
;
; PURPOSE:
;       return the signed quantity of a variable where the magnitude is given
;       by the first argument and the sign is given by the second argument.
;
; CALLING SEQUENCE:
;       AACGM_v2_Sgn, a, b
;     
;     Input Arguments:  
;       a             - magnitude
;       b             - sign
;
;     Return Value:
;       signed quantity
;
;+-----------------------------------------------------------------------------
*/

double AACGM_v2_Sgn(double a, double b)
{
  double x=0;
  x = (a >= 0) ? a : -a;
  return (b >= 0) ? x: -x;
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       convert_geo_coord_v2
;
; PURPOSE:
;       Second-level function used to determine the lat/lon of the input
;       coordinates.
;
; CALLING SEQUENCE:
;       err = convert_geo_coord_v2(in_lat,in_lon,height, out_lat,out_lon,
;                               code,order, igrf_filename);
;     
;     Input Arguments:  
;       in_lat        - latitude in degrees
;       in_lon        - longitude in degrees
;       height        - height above Earth in km
;       code          - bitwise code for passing options into converter
;                       G2A         - geographic (geodetic) to AACGM-v2
;                       A2G         - AACGM-v2 to geographic (geodetic)
;                       TRACE       - use field-line tracing, not coefficients
;                       ALLOWTRACE  - use trace only above 2000 km
;                       BADIDEA     - use coefficients above 2000 km
;       order         - integer order of spherical harmonic expansion
;
;     Output Arguments:
;       out_lat       - pointer to output latitude in degrees
;       out_lon       - pointer to output longitude in degrees
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int convert_geo_coord_v2(double lat_in, double lon_in, double height_in,
			 double *lat_out, double *lon_out, int code, int order,
			 char *igrf_filename) {

/*  int i,j,k,l,m,f,a,t,flag;*/
  int i,j,k,l,m,flag;
  int i_err64, err;

/*  extern int rylm(); */
  double ylmval[AACGM_KMAX];
  double colat_temp;
  double lon_output;
    
  double lat_adj=0;
/*  double lat_alt=0; */
  double colat_input; 
   
  double alt_var_cu=0, lon_temp=0, alt_var_sq=0, alt_var_qu=0;
  double colat_output=0, r=0, x=0, y=0, z=0;
  double ztmp, fac;
  double alt_var=0;
  double lon_input=0;

  static double cint[AACGM_KMAX][NCOORD][NFLAG];

  #if DEBUG > 0
  printf("convert_geo_coord_v2\n");
  #endif

  /* no date/time set so use current time */
  if (aacgm_date.year < 0) {    /* AACGM_v2_SetNow();*/
    AACGM_v2_errmsg(0);
    return -128;
  }

  /* TRACE */ /* call tracing functions here and return */
  if ((code & TRACE) || (height_in > MAXALT && (code & ALLOWTRACE))) {
    if (A2G & code) {   /* AACGM-v2 to geographic */
      err = AACGM_v2_Trace_inv(lat_in,lon_in,height_in, lat_out,lon_out,
			       igrf_filename);

      /* v2.3 moved to AACGM_v2_Convert
      if ((code & GEOCENTRIC) == 0) {
        geoc2geod(*lat_out,*lon_out,(RE+height_in)/RE, llh);
        *lat_out = llh[0];
      } */
    } else {
      err = AACGM_v2_Trace(lat_in,lon_in,height_in, lat_out,lon_out,
			   igrf_filename);
    }

    return (err);
  }

  /* determine the altitude dependence of the coefficients */
  flag = (A2G & code);    /* 0 for G2A; 1 for A2G */
  if (height_in != height_old[flag]) {
    alt_var = height_in/(double)MAXALT;
    alt_var_sq = alt_var * alt_var;
    alt_var_cu = alt_var * alt_var_sq;
    alt_var_qu = alt_var * alt_var_cu;

    #if DEBUG > 1
    printf("alt_var = %lf\n", alt_var);
    printf("alt_var_qu = %lf\n", alt_var_qu);
    #endif

    #if DEBUG > 0
    printf("** HEIGHT INTERPOLATION **\n");
    #endif

    for (i=0; i<NCOORD; i++) {
      for (j=0; j<AACGM_KMAX;j++) {
        /* change to allow general polynomial approximation */
        cint[j][i][flag] =  sph_harm_model.coef[j][i][0][flag] +
                            sph_harm_model.coef[j][i][1][flag]*alt_var+
                            sph_harm_model.coef[j][i][2][flag]*alt_var_sq+
                            sph_harm_model.coef[j][i][3][flag]*alt_var_cu+
                            sph_harm_model.coef[j][i][4][flag]*alt_var_qu;
        #if DEBUG > 10
        printf("%35.30lf %35.30lf\n", cint[j][i][flag],
                            sph_harm_model.coef[j][i][0][flag]);
        #endif

      }
    }

    height_old[flag] = height_in;
  }
  #if DEBUG > 1
  printf("cint[0][0][%d] = %lf\n", flag, cint[0][0][flag]);
  printf("cint[%d][0][%d] = %lf\n",
            AACGM_KMAX-1, flag, cint[AACGM_KMAX-1][0][flag]);
  printf("cint[%d][%d][%d] = %lf\n", AACGM_KMAX-1, NCOORD-1, flag,
                                      cint[AACGM_KMAX-1][NCOORD-1][flag]);
  #endif

  x = y = z = 0;

  lon_input = lon_in*DTOR;

  if (flag == 0) {
    colat_input = (90.-lat_in)*DTOR;
  } else {
    /* use intermediate "at-altitude" coordinates for inverse trans. */
    i_err64 = AACGM_v2_CGM2Alt(height_in, lat_in, &lat_adj);

    if (i_err64 != 0) return -64;
    colat_input= (90. - lat_adj)*DTOR;
  }

  /* Compute the values of the spherical harmonic functions.
   * NOTE: this function was adapted to use orthonormal SH functions */
  AACGM_v2_Rylm(colat_input, lon_input, order, ylmval);

  for (l=0; l<=order; l++) {
    for (m=-l; m<=l; m++) {
      k = l * (l+1) + m;      /* SGS: changes indexing */

      x += cint[k][0][flag]*ylmval[k];
      y += cint[k][1][flag]*ylmval[k];
      z += cint[k][2][flag]*ylmval[k];
    }
  }
 
  /* COMMENT: SGS
   * 
   * This answers one of my questions about how the coordinates for AACGM are
   * guaranteed to be on the unit sphere. Here they compute xyz indpendently
   * using the SH coefficients for each coordinate. They reject anything that
   * is +/- .1 Re from the surface of the Earth. They then scale each xyz
   * coordinate by the computed radial distance. This is a TERRIBLE way to do
   * things... but necessary for the inverse transformation.
   */

  /* SGS - new method that ensures position is on unit sphere and results in a
   *       much better fit. Uses z coordinate only for sign, i.e., hemisphere.
   */
  if (flag == 0) {
    fac = x*x + y*y;
    if (fac > 1.) {
      /* we are in the forbidden region and the solution is undefined */
      *lat_out = HUGE_VAL;
      *lon_out = HUGE_VAL;

      return -64;
    }

    ztmp = sqrt(1. - fac);
    z = (z < 0) ? -ztmp : ztmp;

    colat_temp = acos(z);
  } else {
  /* SGS - for inverse the old normalization produces lower overall errors...*/
    r = sqrt(x*x + y*y + z*z);
    if ((r< 0.9) || (r > 1.1)) return -32;

    z /= r;
    x /= r;
    y /= r;

    if (z > 1.) colat_temp = 0;
    else if (z < -1.) colat_temp = M_PI;
    else colat_temp = acos(z);
  }
  
  if ((fabs(x) < 1e-8) && (fabs(y) < 1e-8)) lon_temp = 0;
  else lon_temp = atan2(y,x);

  lon_output = lon_temp;

  /* SGS - not used for forward transformation */
  /*
  if (flag == 0) {
    lat_alt =90 - colat_temp*180/PI;
    altitude_to_cgm(height_in, lat_alt,&lat_adj);
    colat_output = (90. - lat_adj) * PI/180;
  } else colat_output = colat_temp;
  */
  colat_output = colat_temp;

  *lat_out = (double) (90. - colat_output/DTOR);
  *lon_out = (double) (lon_output/DTOR);

  /* v2.3 moved to AACGM_v2_Convert
  if ((code & GEOCENTRIC) == 0 && (code & A2G)) {
    geoc2geod(*lat_out,*lon_out,(RE+height_in)/RE, llh);
    *lat_out = llh[0];
  } */

  return 0;
} 


/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_LoadCoefFP
;
; PURPOSE:
;       Load a set of spherical harmonic coefficients.
;
; CALLING SEQUENCE:
;       err = AACGM_v2_LoadCoefFP(fp, code);
;     
;     Input Arguments:  
;       fp            - FILE pointer to open coefficient file
;       code          - 0 for 1st set; 1 for 2nd set
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_LoadCoefFP(FILE *fp, int code)
{
  /*  char tmp[64]; */
  double tmp;
  int f,l,a,t;

  #if DEBUG > 0
  printf("AACGM_v2_LoadCoefFP\n");
  #endif

  if (fp==NULL) {
    #if DEBUG > 0
    printf("NULL file pointer in AACGM_v2_LoadCoefFP\n");
    #endif
    return -1;
  }

  for (f=0;f<NFLAG;f++) { 
    for (l=0;l<POLYORD;l++) {
      for (a=0;a<NCOORD;a++) { 
        for (t=0;t<AACGM_KMAX;t++) {
          if (fscanf(fp, "%lf", &tmp) != 1) {
            #if DEBUG > 0
            printf("FILE error, aborting\n");
            #endif
            fclose(fp);
            return -1;
          }

          sph_harm_model.coefs[t][a][l][f][code] = tmp;
        }
      }
    }
  }

  #if DEBUG > 10
  for (f=0;f<NFLAG;f++) { 
    for (l=0;l<POLYORD;l++) {
      for (a=0;a<NCOORD;a++) { 
        for (t=0;t<AACGM_KMAX;t++) {
          printf("%lf ", sph_harm_model.coefs[t][a][l][f][code]);
        }
        printf("\n");
      }
      printf("\n");
    }
    printf("\n");
  }
  #endif

return 0;
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_LoadCoef
;
; PURPOSE:
;       Load a set of spherical harmonic coefficients.
;
; CALLING SEQUENCE:
;       ret = AACGM_v2_LoadCoef(fname,code);
;     
;     Input Arguments:  
;       fname         - filename containing the AACGM coefficient set
;       code          - 0 for 1st set; 1 for 2nd set
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_LoadCoef(char *fname, int code)
{
  FILE *fp=NULL;
  int err=-2;

  #if DEBUG > 0
  printf("loading %s\n", fname);
  #endif

  fp = fopen(fname,"r");
  if (fp==NULL) {
    #if DEBUG > 0
    printf("NULL file pointer in AACGM_v2_LoadCoef\n");
    #endif
    return -1;
  }

  err = AACGM_v2_LoadCoefFP(fp, code);
  if (err != 0) {
    #if DEBUG > 0
    printf("error in AACGM_v2_LoadCoefFP\n");
    #endif
    return -2;
  }
  fclose(fp);

  return 0;
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_LoadCoefs
;
; PURPOSE:
;       Load two sets of spherical harmonic coefficients.
;
; CALLING SEQUENCE:
;       err = AACGM_v2_LoadCoefs(myear, root);
;     
;     Input Arguments:  
;       myear         - 5-year epoch year prior to desired time; bracketing
;                       set is +5 years.
;       root          - directory and file root for AACGM coefficient files
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_LoadCoefs(int year, char *root)
{
  char fname[256];
  char yrstr[5];  
  int ret=0;

  #if DEBUG > 0
  printf("AACGM_v2_LoadCoefs\n");
  #endif
  /* default location of coefficient files */
  if(strlen(root) == 0 && getenv("AACGM_v2_DAT_PREFIX") != (char *)(NULL))
    strcpy(root,getenv("AACGM_v2_DAT_PREFIX"));

  if (strlen(root)==0) {
    AACGM_v2_errmsg(2);
    return -1;
  }

  if (year <= 0) return -1;
  sprintf(yrstr,"%4.4d",year);  

  strcpy(fname,root);
  strcat(fname,yrstr);
  strcat(fname,".asc");
  #if DEBUG > 0
  printf("AACGM_v2_LoadCoefs: %s\n", fname);
  #endif
  ret = AACGM_v2_LoadCoef(fname,G2A);   /* forward coefficients */
  if (ret != 0) return ret;

  sprintf(yrstr,"%4.4d",year+5);  
  strcpy(fname,root);
  strcat(fname,yrstr);
  strcat(fname,".asc");
  #if DEBUG > 0
  printf("AACGM_v2_LoadCoefs: %s\n", fname);
  #endif
  ret += AACGM_v2_LoadCoef(fname,A2G);  /* inverse coefficients */

  myear_old = year;

  return ret;
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_Convert
;
; PURPOSE:
;       Main function called by many SD plotting routines that are written
;       in C.
;
; CALLING SEQUENCE:
;       err = AACGM_v2_Convert(in_lat, in_lon, height,
;                 out_lat, out_lon, r, code, igrf_filename);
;     
;     Input Arguments:  
;       int_lat       - double precision input latitude in degrees
;       int_lon       - double precision input longitude in degrees
;       height        - altitude in km
;       code          - bitwise code for passing options into converter
;                       G2A         - geographic (geodetic) to AACGM-v2
;                       A2G         - AACGM-v2 to geographic (geodetic)
;                       TRACE       - use field-line tracing, not coefficients
;                       ALLOWTRACE  - use trace only above 2000 km
;                       BADIDEA     - use coefficients above 2000 km
;                       GEOCENTRIC  - assume inputs are geocentric w/ RE=6371.2
;
;     Output Arguments:  
;       out_lat       - output latitude in degrees
;       out_lon       - output longitude in degrees
;       r             - geocentric radial distance in Re
;
;     Return Value:
;       error code
;
;
; NOTES:
;
;       All AACGM-v2 conversions are done in geocentric coordinates using a
;           value of 6371.2 km for the Earth radius.
;
;       For G2A conversion inputs are geographic latitude, longitude and
;           height (glat,glon,height), specified as either geocentric or
;           geodetic (default). For geodetic inputs a conversion to geocentric
;           coordinates is performed, which changes the values of
;           glat,glon,height. The output is AACGM-v2 latitude, longitude and
;           the geocentric radius (mlat,mlon,r) using the geocentric height
;           in units of RE.
;
;        For A2G conversion inputs are AACGM-v2 latitude, longitude and the
;            geocentric height (mlat,mlon,height). The latter can be obtained
;            from the r output of the G2A conversion. The output is geographic
;            latitude, longitude and height (glat,glon,height). If the
;            gedodetic option is desired (default) a conversion of the outputs
;            is performed, which changes the values of glat,glon,height.
;
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_Convert(double in_lat, double in_lon, double height,
		     double *out_lat, double *out_lon, double *r, int code,
		     char *igrf_filename)
{
  int err;
  int order=10;   /* pass in so a lower order would be allowed? */
  double rtp[3];
  double llh[3];

  #if DEBUG > 0
  printf("AACGM_v2_Convert\n");
  #endif

  /* height < 0 km */
  if (height < 0) {
    fprintf(stderr, "WARNING: coordinate transformations are not intended "
                    "for altitudes < 0 km: %lf\n", height);
  /*  return -2; */
  }

  /* height > 2000 km not allowed for coefficients */
  if (height > MAXALT && !(code & (TRACE|ALLOWTRACE|BADIDEA))) {
    fprintf(stderr, "ERROR: coefficients are not valid for altitudes "
                    "above %d km: %lf.\n", MAXALT, height);
    fprintf(stderr, "       You must either use field-line tracing "
                    "(TRACE or ALLOWTRACE) or\n"
                    "       indicate that you know this is a very bad idea "
                    "(BADIDEA)\n\n");
    return -4;
  }

  /* latitude out of bounds */
  if (fabs(in_lat) > 90.) {
    fprintf(stderr, "ERROR: latitude must be in the range -90 to +90 degrees: "
                    "%lf\n", in_lat);
    return -8;
  }

  /* longitude out of bounds */
/* SGS v2.3 removing requirement that longitude be -180 to 180. Does not seems
 *          to matter and is inconsistent with IDL version: -180 to 180.

  if ((in_lon < -180) || (in_lon > 180)) {
    fprintf(stderr, "ERROR: longitude must be in the range -180 to 180 "
                    "degrees: %lf\n", in_lon);
    return -16;
  }
 */

  /* if forward calculation (G2A) and input coordinates are given in geodetic
     coordinates (default) then must first convert to geocentric coordinates */
  if ((code & GEOCENTRIC) == 0 && (code & A2G) == 0) {
    geod2geoc(in_lat,in_lon,height, rtp);

    /* modify lat/lon/alt to geocentric values */
    in_lat = 90. - rtp[1]/DTOR;
    in_lon = rtp[2]/DTOR;
    height = (rtp[0]-1.)*RE;
  }

  /* all inputs are geocentric */
  err = convert_geo_coord_v2(in_lat,in_lon,height, out_lat,out_lon, code,order,
			     igrf_filename);
  /* all outputs are geocentric */

  if ((code & A2G) == 0) {    /* forward: G2A */
    *r = (height + RE)/RE;    /* geocentric radial distance in RE */
  } else {                    /* inverse: A2G */
    if ((code & GEOCENTRIC) == 0) { /* geodetic outputs */
      geoc2geod(*out_lat,*out_lon,(RE+height)/RE, llh);
      *out_lat = llh[0];
      height = llh[2];
    }
    *r = height;              /* height in km */
  }

  if (err !=0) return -1;
  return 0;
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_SetDateTime
;
; PURPOSE:
;       Function to set date and time. MUST be called at least once BEFORE
;       any calls to AACGM_v2_Convert.
;
; CALLING SEQUENCE:
;       err = AACGM_v2_SetDateTime(year, month, day, hour, minute, second, root)
;     
;     Input Arguments:  
;       year          - year [1900-2020)
;       month         - month of year [01-12]
;       day           - day of month [01-31]
;       hour          - hour of day [00-24]
;       minute        - minute of hour [00-60]
;       second        - second of minute [00-60]
;       root          - directory and file root of AACGM coefficient file
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_SetDateTime(int year, int month, int day,
			 int hour, int minute, int second, char *root)
{
  int err, doy, ndays;
  double fyear;

  doy = dayno(year,month,day,&ndays);
  fyear = year + ((doy-1) + (hour + (minute + second/60.)/60.)/24.) / ndays;

  if ((fyear < IGRF_FIRST_EPOCH) || (fyear >= IGRF_LAST_EPOCH + 5.)) {
    AACGM_v2_errmsg(1);
    return (-1);
  }

  aacgm_date.year   = year;
  aacgm_date.month  = month;
  aacgm_date.day    = day;
  aacgm_date.hour   = hour;
  aacgm_date.minute = minute;
  aacgm_date.second = second;
  aacgm_date.dayno  = doy;
  aacgm_date.daysinyear = ndays;

  #if DEBUG > 0
  printf("AACGM_v2_SetDateTime\n");
  printf("%03d: %04d%02d%02d %02d%02d:%02d\n",
        aacgm_date.dayno, aacgm_date.year, aacgm_date.month, aacgm_date.day,
        aacgm_date.hour, aacgm_date.minute, aacgm_date.second);
  #endif

  err = AACGM_v2_TimeInterp(root);

  return err;
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_GetDateTime
;
; PURPOSE:
;       Function to get date and time.
;
; CALLING SEQUENCE:
;       err = AACGM_v2_GetDateTime(year, month, day, hour, minute, second, dayno);
;     
;     Output Arguments (integer pointers):  
;       year          - year [1965-2014]
;       month         - month of year [01-12]
;       day           - day of month [01-31]
;       hour          - hour of day [00-24]
;       minute        - minute of hour [00-60]
;       second        - second of minute [00-60]
;       dayno         - day of year [01-366]
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_GetDateTime(int *year, int *month, int *day,
                      int *hour, int *minute, int *second, int *dayno)
{
  *year   = aacgm_date.year;
  *month  = aacgm_date.month;
  *day    = aacgm_date.day;
  *hour   = aacgm_date.hour;
  *minute = aacgm_date.minute;
  *second = aacgm_date.second;
  *dayno  = aacgm_date.dayno;

  return 0;
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_SetNow
;
; PURPOSE:
;       Function to set date and time to current computer time in UT.
;
; CALLING SEQUENCE:
;       err = AACGM_v2_SetNow(root);
;     
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_SetNow(char *root)
{
  /* current time */
  int err, doy,ndays;
  double fyear;
  time_t now;
  struct tm *tm_now;

  time(&now);
  tm_now = gmtime(&now);    /* right now in UT */

  doy = dayno(1900 + tm_now->tm_year,tm_now->tm_mon,tm_now->tm_mday,&ndays);
  fyear = 1900 + tm_now->tm_year + ((doy-1) + (tm_now->tm_hour +
                (tm_now->tm_min + tm_now->tm_sec/60.)/60.)/24.) / ndays;

  if ((fyear < IGRF_FIRST_EPOCH) || (fyear >= IGRF_LAST_EPOCH + 5.)) {
    fprintf(stderr, "\nDate range for AACGM-v2 is [%4d - %4d)\n\n",
                      IGRF_FIRST_EPOCH, IGRF_LAST_EPOCH + 5);
    fprintf(stderr, "%04d%02d%02d %02d%02d:%02d\n", tm_now->tm_year,
                     tm_now->tm_mon, tm_now->tm_mday, tm_now->tm_hour,
                     tm_now->tm_min, tm_now->tm_sec);
    return (-1);
  }

  aacgm_date.year   = (*tm_now).tm_year + 1900;
  aacgm_date.month  = (*tm_now).tm_mon  + 1;
  aacgm_date.day    = (*tm_now).tm_mday;
  aacgm_date.hour   = (*tm_now).tm_hour;
  aacgm_date.minute = (*tm_now).tm_min;
  aacgm_date.second = (*tm_now).tm_sec;
  aacgm_date.dayno  = (*tm_now).tm_yday + 1;
  aacgm_date.daysinyear = ndays;

  #if DEBUG > 0
  printf("AACGM_v2_SetNow\n");
  printf("%03d: %04d%02d%02d %02d%02d:%02d\n",
        aacgm_date.dayno, aacgm_date.year, aacgm_date.month, aacgm_date.day,
        aacgm_date.hour, aacgm_date.minute, aacgm_date.second);
  #endif

  err = AACGM_v2_TimeInterp(root);

  return err;
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_errmsg
;
; PURPOSE:
;       Display error message because no date and time have been set.
;
; CALLING SEQUENCE:
;       AACGM_v2_errmsg(code);
;     
;+-----------------------------------------------------------------------------
*/

void AACGM_v2_errmsg(int ecode)
{

  fprintf(stderr, "\n"
  "**************************************************************************"
  "\n");

  switch (ecode) {
    case 0: /* no Date/Time set */
  fprintf(stderr,
  "* AACGM-v2 ERROR: No Date/Time Set                                       *\n"
  "*                                                                        *\n"
  "* You must specifiy the date and time in order to use AACGM coordinates, *\n"
  "* which depend on the internal (IGRF) magnetic field. Before calling     *\n"
  "* AACGM_v2_Convert() you must set the date and time to the integer values*\n"
  "* using the function:                                                    *\n"
  "*                                                                        *\n"
  "*   AACGM_v2_SetDateTime(year,month,day,hour,minute,second);             *\n"
  "*                                                                        *\n"
  "* or to the current computer time in UT using the function:              *\n"
  "*                                                                        *\n"
  "*   AACGM_v2_SetNow(root);                                               *\n"
  "*                                                                        *\n"
  "* subsequent calls to AACGM_v2_Convert() will use the last date and time *\n"
  "* that was set, so update to the actual date and time that is desired.   *"
  "\n");
    break;

    case 1: /* Date/Time out of bounds */
  fprintf(stderr,
  "* AACGM-v2 ERROR: Date out of bounds                                     *\n"
  "*                                                                        *\n"
  "* The current date range for AACGM-v2 coordinates is [1990-2020), which  *\n"
  "* corresponds to the date range for the IGRF12 model, including the      *\n"
  "* 5-year secular variation.                                              *"
  "\n");
    break;

    case 2: /* COEF Path not set */
  fprintf(stderr,
  "* AACGM-v2 ERROR: AACGM_v2_DAT_PREFIX path not set *\n"
  "*                                                                        *\n"
  "* You must set the environment variable AACGM_v2_DAT_PREFIX to the       *\n"
  "\n");
    break;
  }
  fprintf(stderr,
  "**************************************************************************"
  "\n\n");
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_TimeInterp
;
; PURPOSE:
;       Interpolate coefficients between adjacent 5-year epochs
;
; CALLING SEQUENCE:
;       err = AACGM_v2_TimeInterp(root);
;     
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_TimeInterp(char *root)
{
  int myear,f,l,a,t,err;
  double fyear;

  /* myear is the epoch model year */
  myear = aacgm_date.year/5*5;
  if (myear != myear_old) {   /* load the new coefficients, if needed */
    err = AACGM_v2_LoadCoefs(myear, root);
    if (err != 0) return err;
    fyear_old = -1;           /* force time interpolation */
    height_old[0] = -1.;      /* force height interpolation */
    height_old[1] = -1.;
  }

  /* fyear is the floating point time */
  fyear = aacgm_date.year + ((aacgm_date.dayno-1) + (aacgm_date.hour +
                    (aacgm_date.minute + aacgm_date.second/60.)/60.)/24.)/
                    aacgm_date.daysinyear;

  /* time interpolation right here */
  if (fyear != fyear_old) {
    #if DEBUG > 0
    printf("** TIME INTERPOLATION **\n");
    #endif

    for (f=0;f<NFLAG;f++)
    for (l=0;l<POLYORD;l++)
    for (a=0;a<NCOORD;a++)
    for (t=0;t<AACGM_KMAX;t++)
      sph_harm_model.coef[t][a][l][f] = sph_harm_model.coefs[t][a][l][f][0] +
          (fyear - myear) * (sph_harm_model.coefs[t][a][l][f][1] -
                            sph_harm_model.coefs[t][a][l][f][0])/5;

    height_old[0] = -1.;      /* force height interpolation because coeffs */
    height_old[1] = -1.;      /* have changed */

    fyear_old = fyear;
  }

  return (0);
}


int AACGM_v2_Trace(double lat_in, double lon_in, double alt,
		   double *lat_out, double *lon_out, char *igrf_filename)
{
  int err, kk, idir;
  unsigned long k,niter;
  double ds, dsRE, dsRE0, eps, Lshell;
  double rtp[3],xyzg[3],xyzm[3],xyzc[3],xyzp[3];

  /* set date for IGRF model */
  IGRF_SetDateTime(aacgm_date.year, aacgm_date.month, aacgm_date.day,
		   aacgm_date.hour, aacgm_date.minute, aacgm_date.second,
		   igrf_filename);

  /* Q: these could eventually be command-line options */
  ds    = 1.;
  dsRE  = ds/RE;
  dsRE0 = dsRE;
  eps   = 1.e-4/RE;

  /* for the model we are doing the tracing in geocentric coordinates */
  rtp[0] = (RE+alt)/RE;       /* distance in RE; 1.0 is surface of sphere */
  rtp[1] = (90.-lat_in)*DTOR;   /* colatitude in radians */
  rtp[2] = lon_in*DTOR;         /* longitude in radians */

  k = 0L;
  /* convert position to Cartesian coords */
  sph2car(rtp, xyzg);

  /* convert to magnetic Dipole coordinates */
  geo2mag(xyzg, xyzm);

  idir = (xyzm[2] > 0.) ? -1 : 1;   /* N or S hemisphere */

  dsRE = dsRE0;

  /*
  ; trace to magnetic equator
  ;
  ; Note that there is the possibility that the magnetic equator lies
  ; at an altitude above the surface of the Earth but below the starting
  ; altitude. I am not certain of the definition of CGM, but these
  ; fieldlines map to very different locations than the solutions that
  ; lie above the starting altitude. I am considering the solution for
  ; this set of fieldlines as undefined; just like those that lie below
  ; the surface of the Earth.
  */
  while (idir*xyzm[2] < 0.) {

    for (kk=0;kk<3;kk++) xyzp[kk] = xyzg[kk]; /* save as previous */

    AACGM_v2_RK45(xyzg, idir, &dsRE, eps, 1); /* set to 0 for RK4: /noadapt) */

    /* convert to magnetic Dipole coordinates */
    geo2mag(xyzg, xyzm);

    k++;
  }
  niter = k;

  if (niter > 1) {
    /* now bisect stepsize (fixed) to land on magnetic equator w/in 1 m */
    for (k=0;k<3;k++) xyzc[k] = xyzp[k];
    kk = 0L;
    while (dsRE > 1e-3/RE) {
      dsRE *= .5;
      for (k=0;k<3;k++) xyzp[k] = xyzc[k];
      AACGM_v2_RK45(xyzc, idir, &dsRE, eps, 0);  /* using RK4 */
      geo2mag(xyzc,xyzm);

      /* Is it possible that resetting here causes a doubling of the tol? */
      if (idir * xyzm[2] > 0)
      for (k=0;k<3;k++) xyzc[k] = xyzp[k];

      kk++;
    }
    niter += kk;
  }

  /* 'trace' back to reference surface along Dipole field lines */
  Lshell = sqrt(xyzc[0]*xyzc[0] + xyzc[1]*xyzc[1] + xyzc[2]*xyzc[2]);
  if (Lshell < (RE+alt)/RE) { /* magnetic equator is below ... */
    *lat_out = NAN;
    *lon_out = NAN;

    err = -1;
  } else {
    geo2mag(xyzc, xyzm);  /* geographic to magnetic */
    car2sph(xyzm, rtp);

    *lat_out = -idir*acos(sqrt(1./Lshell))/DTOR;
    *lon_out = rtp[2]/DTOR;
    if (*lon_out > 180) *lon_out -= 360.;

    err = 0;
  }

  return (err);
}

int AACGM_v2_Trace_inv(double lat_in, double lon_in, double alt,
		       double *lat_out, double *lon_out, char *igrf_filename)
{
  int err, kk, idir;
  unsigned long k,niter;
  double ds, dsRE, dsRE0, eps, Lshell;
  double rtp[3],xyzg[3],xyzm[3],xyzc[3],xyzp[3];

  /* set date for IGRF model */
  IGRF_SetDateTime(aacgm_date.year, aacgm_date.month, aacgm_date.day,
		   aacgm_date.hour, aacgm_date.minute, aacgm_date.second,
		   igrf_filename);

  /* Q: these could eventually be command-line options */
  ds    = 1.;
  dsRE  = ds/RE;
  dsRE0 = dsRE;
  eps   = 1.e-4/RE;

  /* Q: Test this */
  /* poles map to infinity */
  if (fabs(fabs(lat_in) - 90.) < 1e-6)
    lat_in += (lat_in > 0) ? -1e-6 : 1e-6;

  Lshell = 1./(cos(lat_in*DTOR)*cos(lat_in*DTOR));
  if (Lshell <(RE+alt)/RE) { /* solution does not exist; the starting
                              * position at the magnetic equator is below
                              * the altitude of interest */
    *lat_out = NAN;
    *lon_out = NAN;
    err = -1;
  } else {
    /* magnetic Cartesian coordinates of fieldline trace starting point */
    xyzm[0] = Lshell*cos(lon_in*DTOR);
    xyzm[1] = Lshell*sin(lon_in*DTOR);
    xyzm[2] = 0.;

    /* geographic Cartesian coordinates of starting point */
    mag2geo(xyzm, xyzg);

    /* geographic spherical coordinates of starting point */
    car2sph(xyzg,rtp);

    k = 0L;

    /* direction of trace is determined by the starting hemisphere? */
    idir = (lat_in > 0) ? 1 : -1;

    dsRE = dsRE0;

    /* trace back to altitude above Earth */
    while (rtp[0] >  (RE + alt)/RE) {
      for (kk=0;kk<3;kk++) xyzp[kk] = xyzg[kk]; /* save as previous */

      AACGM_v2_RK45(xyzg, idir, &dsRE, eps, 1); /* set to 0 for RK4: /noadapt)*/

      car2sph(xyzg, rtp);

      k++;
    }
    niter = k;

    if (niter > 1) {
      /* now bisect stepsize (fixed) to land on magnetic equator w/in 1 m */
      for (k=0;k<3;k++) xyzc[k] = xyzp[k];
      kk = 0L;
      while (dsRE > 1e-3/RE) {
        dsRE *= .5;
        for (k=0;k<3;k++) xyzp[k] = xyzc[k];
        AACGM_v2_RK45(xyzc, idir, &dsRE, eps, 0);  /* using RK4 */

        car2sph(xyzc, rtp);

        if (rtp[0] < (RE + alt)/RE)
          for (k=0;k<3;k++) xyzc[k] = xyzp[k];

        kk++;
      }
      niter += kk;
    }

    *lat_out = 90. - rtp[1]/DTOR;
    *lon_out = rtp[2]/DTOR;
    if (*lon_out > 180) *lon_out -= 360.;
    err = 0;
  }

  return (err);
}

