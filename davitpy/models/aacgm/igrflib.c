#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>
#include "igrflib.h"
#include "genmag.h"
#include "astalg.h"

/*#define DEBUG 1*/
/* TO DO: should these stuff go in igrflib.h? */

static struct {
  int year;
  int month;
  int day;
  int hour;
  int minute;
  int second;
  int dayno;
  int daysinyear;
} igrf_date = {-1,-1,-1,-1,-1,-1,-1,-1};

static struct {
  double ctcl;
  double ctsl;
  double stcl;
  double stsl;
  double ct0;
  double st0;
  double cl0;
  double sl0;
} geopack = {0.,0.,0.,0.,0.,0.,0.,0.};

static double IGRF_coef_set[MAXNYR][IGRF_MAXK]; /* all the coefficients */
static double IGRF_svs[IGRF_MAXK];              /* secular variations */
static double IGRF_coefs[IGRF_MAXK];            /* interpolated coefficients */
static int    nmx;                          /* order of expansion */

/*-----------------------------------------------------------------------------
; for debugging
;+-----------------------------------------------------------------------------
*/
void pause(void)
{
  char ch;

  fprintf(stdout, "(Hit Enter to coninue...");
  scanf("%c", &ch);
  fprintf(stdout, "\n");
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       IGRF_loadcoeffs
;
; PURPOSE:
;       Load the entire set of spherical harmonic coefficients from the given
;       file.
; 
;  Read the in the coefficients. Note that I am using the same ordering as
;  is used in the AACGM code. That is,
; 
;   l    0  1  1  1  2  2  2  2  2  3  3  3  3  3  3  3  4  4  4  4  4 ...
;   m    0 -1  0  1 -2 -1  0  1  2 -3 -2 -1  0  1  2  3 -4 -3 -2 -1  0 ...
; 
;  C & IDL index: k = l * (l+1) + m
; 
;   k    0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 ...
;
; CALLING SEQUENCE:
;       err = IGRF_loadcoeffs();
;     
;     Input Arguments:  
;       filename      - name of file which contains IGRF coefficients; default
;                       is current IGRF model: igrf12coeffs.txt
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int IGRF_loadcoeffs(char *filename)
{
  int k,l,m,n, ll,mm;
  int fac, len;
  int iyear, nyear;
  int dgrf[MAXNYR];
  int epoch[MAXNYR];
  char jnk;
/*  char header[2][MAXSTR];*/
  char line[MAXSTR];
  double fyear;
  double coef, sv;
  double Slm[IGRF_MAXK], fctrl[2*IGRF_ORDER+1], dfc[2*IGRF_ORDER];
  FILE *fp;

  #if DEBUG > 0
  printf("IGRF_loadceoffs\n");
  #endif

  /* file containing the IGRF coefficients */
  if(strlen(filename) == 0 && getenv("IGRF_COEFFS") != (char *)(NULL))
    filename = getenv("IGRF_COEFFS");

  if(strlen(filename) == 0)
    {
      printf("\n");
      printf("*************************************************************\n");
      printf("* You MUST set the environment variable IGRF_COEFFS \n");
      printf("*************************************************************\n");
      return (-99);
    }
/*  strcpy(filename,getenv("IGRF_COEFFS")); */

  #if DEBUG > 1
  printf("Schmidt quasi-normalization factors\n");
  printf("===================================\n\n");
  #endif

  /* factorial */
  fctrl[0] = fctrl[1] = 1.;
  for (k=2; k<= 2*IGRF_ORDER; k++)
    fctrl[k] = k*fctrl[k-1];

  /*for(k=0; k<=2*IGRF_ORDER; k++) printf("%lf\n", fctrl[k]); */

  /* double factorial */
  dfc[1] = 1;
  for (k=3; k<2*IGRF_ORDER; k+=2)
    dfc[k] = dfc[k-2]*k;

  for (l=0; l<=IGRF_ORDER; l++) {
    for (m=0; m<=l; m++) {
      k = l * (l+1) + m;      /* 1D index for l,m */
      n = l * (l+1) - m;      /* 1D index for l,m */

      fac = (m) ? 2 : 1;
      /* Davis 2004; Wertz 1978 recursion
      Slm[k] = Slm[n] = sqrt(fac*fctrl[l-m]/fctrl[l+m])*dfc[2*l-1]/fctrl[l-m];
      */
      /* Winch 2004 */
      Slm[k] = Slm[n] = sqrt(fac*fctrl[l-m]/fctrl[l+m]);

      #if DEBUG > 1
      printf("$ %2d %2d %2d %e %e %e\n", l, m, k, fctrl[l-m],fctrl[l+m],Slm[k]);
      printf("$ %2d %2d %2d %e %e %e\n", l,-m, n, fctrl[l-m],fctrl[l+m],Slm[n]);
      #endif
    }
  }

  /* get the coefficients */
  fp = fopen(filename, "r");
  if (fp == NULL) {
    fprintf(stderr, "File not found: %s\n", filename);
    return (-1);
  }

  /* read first two header lines */
  for (k=0; k<2; k++) {
    jnk = ' ';
    m = 0;
    while (jnk != '\n') {
      fscanf(fp, "%c", &jnk);
/*      header[k][m] = (jnk == '\n') ? (char)0 : jnk;*/
      m++;
    }
  }

  /* get next line */
  jnk = ' ';
  m = 0;
  while (jnk != '\n') {
    fscanf(fp, "%c", &jnk);
    line[m] = (jnk == '\n') ? (char)0 : jnk;
    m++;
  }
  len = m;
  #if DEBUG > 1
  fprintf(stderr, "%s\n", line);
  #endif

  /* count how many D/IGRF years */
  nyear = 0;
  for (m=0; m<len; m++)
    if (line[m] == 'G') nyear++;

  if (nyear > MAXNYR) {
    fprintf(stderr, "Too many years in file: %d\n", nyear);
    return (-2);
  }
  #if DEBUG > 1
  fprintf(stderr, "%d years\n", nyear);
  #endif

  iyear = 0;
  for (m=0; m<len; m++) {
    switch (line[m]) {
      case 'I': dgrf[iyear] = 0; break;
      case 'D': dgrf[iyear] = 1; break;
      case 'G': iyear++; break;
    }
  }
  #if DEBUG > 1
  for (m=0; m<nyear; m++) fprintf(stderr, "%d\n", dgrf[m]);
  #endif

  /* get next line, which should have the following format:
   *
   * "g/h n m 1900.0 1905.0 ... 2010.0 2010-15"
   */
  jnk = ' ';
  while (jnk != 'm') fscanf(fp, "%c", &jnk);

  /* read the years, which should be 5-year integer epochs... */
  for (m=0; m<nyear; m++) {
    fscanf(fp, "%lf", &fyear);
    epoch[m] = (int)floor(fyear);
    #if DEBUG > 1
    fprintf(stderr, "%8.2lf\n", fyear);
    #endif
  }

  #if DEBUG > 1
  for (m=0; m<nyear; m++) fprintf(stderr, "%4d\n", epoch[m]);
  #endif

  jnk = ' ';
  while (jnk != '\n') fscanf(fp, "%c", &jnk);

  /* read in the coefficients */
  /* NOTE that for IGRF there is no l=0 term in the coefficient file */
  for (l=1; l<=IGRF_ORDER; l++) {
    k = l * (l+1);                  /* 1D index for l,m=0 */
    fscanf(fp, "%c", &jnk);         /* g or h */
    fscanf(fp, "%d %d", &ll, &mm);  /* l amd m */
    for (n=0; n<nyear; n++) {
      fscanf(fp, "%lf", &coef);     /* coefficient */
      IGRF_coef_set[n][k] = coef * Slm[k];    /* NORMALIZE */
      #if DEBUG > 1
      fprintf(stderr, "%d %d %d %d %f\n", k, l, n, 0, IGRF_coef_set[n][k]);
      #endif
    }
    fscanf(fp, "%lf", &sv);         /* secular variation */
    IGRF_svs[k] = sv * Slm[k];      /* NORMALIZE */
    fscanf(fp, "%c", &jnk);         /* <CR> */

    for (m=1; m<=l; m++) {
      k = l * (l+1) + m;            /* 1D index for l,m */
      fscanf(fp, "%c", &jnk);         /* g or h */
      fscanf(fp, "%d %d", &ll, &mm);  /* l amd m */

      for (n=0; n<nyear; n++) {
        fscanf(fp, "%lf", &coef);     /* coefficient */
        IGRF_coef_set[n][k] = coef * Slm[k];    /* NORMALIZE */
        #if DEBUG > 1
        fprintf(stderr, "%d %d %d %d %f\n", k, l, n, m, IGRF_coef_set[n][k]);
        #endif
      }
      fscanf(fp, "%lf", &sv);         /* secular variation */
      IGRF_svs[k] = sv * Slm[k];      /* NORMALIZE */
      fscanf(fp, "%c", &jnk);         /* <CR> */

      k = l * (l+1) - m;            /* 1D index for l,m */
      fscanf(fp, "%c", &jnk);         /* g or h */
      fscanf(fp, "%d %d", &ll, &mm);  /* l amd m */
      for (n=0; n<nyear; n++) {
        fscanf(fp, "%lf", &coef);     /* coefficient */
        IGRF_coef_set[n][k] = coef * Slm[k];    /* NORMALIZE */
        #if DEBUG > 1
        fprintf(stderr, "%d %d %d %d %f\n", k, l, n, -m, IGRF_coef_set[n][k]);
        #endif
      }
      fscanf(fp, "%lf", &sv);         /* secular variation */
      IGRF_svs[k] = sv * Slm[k];      /* NORMALIZE */

      /* note, some files end each line with <CR><LF> while others are <LF> */
      fscanf(fp, "%c", &jnk);                 /* <LF or CR> */
      if (jnk == 13) fscanf(fp, "%c", &jnk);  /* <LF> */
    }

    #if DEBUG > 2
    pause();
    #endif
  }
  fclose(fp);

  #if DEBUG > 1
  for (n=0; n<nyear; n++)
    fprintf(stderr, "%04d %f\n", epoch[n], IGRF_coef_set[n][0]);
  pause();
  #endif

  #if DEBUG > 1
  fprintf(stderr, "%d\n", (2000-1900)/5);
  /* print coefficients in order */
  for (l=0; l<=IGRF_ORDER; l++) {
    for (m=-l; m<=l; m++) {
      k = l * (l+1) + m;
      fprintf(stderr, "%2d %3d %3d: %e\n", l,m,k,
                      IGRF_coef_set[(1980-1900)/5][k]);
    }
  }
  pause();
  #endif

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       IGRF_Plm
;
; PURPOSE:
;       Internal function to compute array of Gaussian Normalized Associated
;       Legendre functions and the corresponding derivatives.
;
; CALLING SEQUENCE:
;       err = IGRF_Plm(theta, order, plmval, dplmval);
;     
;     Input Arguments: 
;       theta         - co-latitude in radians
;       order         - order of expansion, should NOT exceed IGRF_ORDER
;
;     Output Arguments:
;       plmval        - pointer to array for storage of values
;       dplmval       - pointer to array for storage of derivative values
;
;     Return Value:
;       error code
;
;     Notes: I am using array indexing similar to that used for m=-l to l,
;            but here m=0 to l, so the arrays are too big and there are no
;            values stored in locations for m<0. Probably should fix that...
;
;       values are stored in a 1D array of dimension (order+1)^2. The
;       indexing scheme used is:
;
;             g  h  g  g  h  h  g  g  g  h  h  h  g  g  g  g  h  h  h  h  h ...
;        l    0  1  1  1  2  2  2  2  2  3  3  3  3  3  3  3  4  4  4  4  4 ...
;        m    0 -1  0  1 -2 -1  0  1  2 -3 -2 -1  0  1  2  3 -4 -3 -2 -1  0 ...
;C & IDL j    0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 ...
;FORTRAN j    1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 ...
; 
;+-----------------------------------------------------------------------------
*/

int IGRF_Plm(double theta, int order, double *plmval, double *dplmval) {
  int l,m,k,n,p;
  double a,b;       /* factors */
  double st,ct;

  if (order > IGRF_ORDER) return (-1);

  st = sin(theta);
  ct = cos(theta);

  plmval[0]  = 1.;   /* 0,0 */
  dplmval[0] = 0.;   /* 0,0 */
  /* compute values of P^{l,l} and dP^{l,l}/dtheta */
  for (l=1; l<=order; l++) {
    k = l * (l+1) + l;    /* l = m */
    n = (l-1) * l + l-1;  /* l-1 = m-l, i.e., previous l=m */
    /* Davis 2004; Wertz 1978 recursion
    plmval[k]  = plmval[n]*st;
    dplmval[k] = dplmval[n]*st + plmval[n]*ct;
    */
    /* numerical recipies in C */
    /* a = 1-2*l;*/   /* reverse order to remove Condon-Shortley phase */
    a = 2*l-1;
    plmval[k]  = a*plmval[n]*st;
    dplmval[k] = a*(dplmval[n]*st + plmval[n]*ct);

    #if DEBUG > 1
    printf("%2d %3d %e %e\n", l, k, plmval[k], dplmval[k]);
    #endif
  }

  plmval[2]  =  ct; /* 1,0 */
  dplmval[2] = -st; /* 1,0 */
  /* compute values of P^{l,m} and dP^{l,m}/dtheta */
  for (l=2; l<=order; l++) {
    for (m=0; m<l; m++) {
      k = l * (l+1) + m;        /* l,m */
      n = (l-1) * l + m;        /* l-1,m */
      p = (l-2) * (l-1) + m;    /* l-2,m */
      /* Davis 2004; Wertz 1978 recursion
      kfac = ((l-1)*(l-1) - m*m)/((double)(2*l-1)*(2*l-3));
      plmval[k]  = ct*plmval[n] - kfac*plmval[p];
      dplmval[k] = ct*dplmval[n] -st*plmval[n] - kfac*dplmval[p];
      */

      /* numerical recipies in C */
      a = 2*l-1;
      /* This works but NOT if plmval[p] is NAN!!!!
       *
      b = (m == l-1) ? 0 : l+m-1;
      plmval[k]  = (a*ct*plmval[n] - b*plmval[p])/(l-m);
      dplmval[k] = (a*(ct*dplmval[n] - st*plmval[n]) - b*dplmval[p])/(l-m);
      */
      if (m == l-1) {
        plmval[k]  = a*ct*plmval[n]/(l-m);
        dplmval[k] = a*(ct*dplmval[n] - st*plmval[n])/(l-m);
      } else {
        b = l+m-1;
        plmval[k]  = (a*ct*plmval[n] - b*plmval[p])/(l-m);
        dplmval[k] = (a*(ct*dplmval[n] - st*plmval[n]) - b*dplmval[p])/(l-m);
      }
      #if DEBUG > 1
      printf("%2d %2d %3d %e %e\n", l, m, k, plmval[k], dplmval[k]);
      #endif
    }
  }

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       IGRF_compute
;
; PURPOSE:
;       User function to compute IGRF magnetic field at lat/lon and distance.
;
; CALLING SEQUENCE:
;       err = IGRF_compute(r, theta, phi, Br, Btheta, Bphi);
;     
;     Input Arguments: 
;       r             - geocentric distance in km
;       theta         - co-latitude in radians
;       phi           - longitude in radians
;
;     Output Arguments:
;       Br            - pointer to field in radial direction
;       Btheta        - pointer to field in co-latitude direction
;       Bphi          - pointer to field in longtitude direction
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int IGRF_compute(const double rtp[], double brtp[]) {

  int k,l,m,n;
/*  double brr,btt,bpp; */
  double tbrtp[3], st, theta;
  double aor, afac;
  double dplmval[IGRF_MAXK], plmval[IGRF_MAXK];
  double cosm_arr[IGRF_ORDER+1], sinm_arr[IGRF_ORDER+1];

  #if DEBUG > 0
  printf("IGRF_compute\n");
  #endif

  /* no date/time set so bail */
  if (igrf_date.year < 0) {
    IGRF_msg_notime();
    return -128;
  }

  /* Must avoid singularit at the poles (dividing by sin(theta) later) */
  theta = rtp[1];
  st = sin(theta);
  if (fabs(st) < 1e-15) theta += (st < 0.) ? 1e-15 : -1e-15;

  /* Compute the values of the Legendre Polynomials, and derivatives */
  IGRF_Plm(theta,nmx,plmval,dplmval);

/*  aor  = RE/r;*/      /* a/r, where RE = a */
/*  aor  = RE/rtp[0];*/   /* a/r, where RE = a */
  aor = 1./rtp[0];    /* r is in units of RE to be consistent with geopack, */
                      /* we want RE/r */

  /*printf("aor = %lf\n", aor);*/
  afac = aor*aor;

  /* array of trig functions in phi for faster computation */
  for (k=0; k<=IGRF_ORDER; k++) {
    cosm_arr[k] = cos(k*rtp[2]);
    sinm_arr[k] = sin(k*rtp[2]);
  }

  for (k=0;k<3;k++) brtp[k] = 0;

  for (l=1; l<=nmx; l++) {  /* no l = 0 term in IGRF */
    for (k=0;k<3;k++) tbrtp[k] = 0;
    for (m=0; m<=l; m++) {
      k = l*(l+1) + m;  /* g */
      n = l*(l+1) - m;  /* h */

      tbrtp[0] += (IGRF_coefs[k]*cosm_arr[m] + IGRF_coefs[n]*sinm_arr[m]) *
              plmval[k];
      tbrtp[1] += (IGRF_coefs[k]*cosm_arr[m] + IGRF_coefs[n]*sinm_arr[m]) *
              dplmval[k];
      tbrtp[2] += (-IGRF_coefs[k]*sinm_arr[m] + IGRF_coefs[n]*cosm_arr[m]) *
              m*plmval[k];

/*      printf("%2d %2d %e %e %e\n", l,m, IGRF_coefs[k],IGRF_coefs[n], plmval[k]);
//      printf("[]: %e %e %e\n", tbrtp[0], tbrtp[1], tbrtp[2]);
//      printf("  %2d: brr=%lf, coef[k]=%lf, coef[n]=%lf, plmval[k]=%lf\n",
//            m,brr,IGRF_coefs[k],IGRF_coefs[n],plmval[k]);
//      printf("  %2d: brr=%lf, cosm=%lf, sinm=%lf\n", m,brr,cosm_arr[m],sinm_arr[m]);*/
    }
/*    printf("%2d brr = %lf\n", l,brr);*/
    afac *= aor;

/*    *br     += afac*(l+1)*brr;
//    *btheta -= afac*btt;
//    *bphi   -= afac*bpp; */
    brtp[0] += afac*(l+1)*tbrtp[0];
    brtp[1] -= afac*tbrtp[1];
    brtp[2] -= afac*tbrtp[2];
  }

/*  *bphi /= sin(theta);
//printf("*** %e %e\n", brtp[2], sin(rtp[1]));
//printf("*** %e %e %e\n", brtp[0], brtp[1], brtp[2]); */
  brtp[2] /= sin(theta);
/*  if (sin(rtp[1]) > 1.e-19) { *//* from geopack ... */
/*    brtp[2] /= sin(rtp[1]);
//  } else {
//    if (cos(rtp[1]) < 0.) brtp[2] = -brtp[2];
//  }
//printf("*** %e %e %e\n", brtp[0], brtp[1], brtp[2]); */

  return (0);
} 

/*-----------------------------------------------------------------------------
;
; NAME:
;       IGRF_interpolate_coefs
;
; PURPOSE:
;       Function to compute interpolated coefficients.
;
; CALLING SEQUENCE:
;       err = IGRF_interpolate_coefs();
;     
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/
int IGRF_interpolate_coefs(void) {

  int i,k,l,m, myear;
  double fyear;
  double g10,g11,h11,sq,sqq,sqr;

  #if DEBUG > 0
  printf("** TIME INTERPOLATION **\n");
  #endif

  /* fyear is the floating point time */
  fyear = igrf_date.year + ((igrf_date.dayno-1) + (igrf_date.hour +
                    (igrf_date.minute + igrf_date.second/60.)/60.)/24.)/
                    igrf_date.daysinyear;

  /* NOTE: FORTRAN code allows 10-year extrapolation beyond last epoch.
   * Here we are limiting to only 5 */
  if (fyear < IGRF_FIRST_EPOCH || fyear > IGRF_LAST_EPOCH + 5) {
    /* reset date */
    igrf_date.year = igrf_date.month = igrf_date.day = -1;
    igrf_date.hour = igrf_date.minute = igrf_date.second = -1;
    igrf_date.dayno = igrf_date.daysinyear = -1;

    fprintf(stdout, "Date range for current IGRF model is: %4d to %4d\n\n",
                      IGRF_FIRST_EPOCH, IGRF_LAST_EPOCH+5);
    return (-3);
  }

  myear = igrf_date.year/5*5;                 /* epoch year */
  nmx   = (igrf_date.year < 1995) ? 10 : 13;  /* order of expansion */
  i     = (myear - IGRF_FIRST_EPOCH)/5;       /* index of first set of coefs */

  if (fyear < IGRF_LAST_EPOCH) {
    /* interpolate bounding coefficients */
    for (l=1; l<=nmx; l++) {  /* no l = 0 term in IGRF */
      for (m=-l; m<=l; m++) {
        k = l * (l+1) + m;      /* SGS: changes indexing */
        IGRF_coefs[k] = IGRF_coef_set[i][k] + (fyear-myear)*
                        (IGRF_coef_set[i+1][k]-IGRF_coef_set[i][k])/5;
      }
    }
  } else {
    /* use secular varation */
    for (l=1; l<=nmx; l++) {  /* no l = 0 term in IGRF */
      for (m=-l; m<=l; m++) {
        k = l * (l+1) + m;      /* SGS: changes indexing */
        IGRF_coefs[k] = IGRF_coef_set[i][k] + (fyear-myear)*IGRF_svs[k];
      }
    }
  }

  /* compute the components of the unit vector EzMag in geographic coordinates:
   * sin(theta0)*cos(lambda0), sin(theta0)*sin(lambda0)
   */

/* C & IDL index: k = l * (l+1) + m */
  g10 = -IGRF_coefs[2]; /* 1*2+0 = 2 */
  g11 =  IGRF_coefs[3]; /* 1*2+1 = 3 */
  h11 =  IGRF_coefs[1]; /* 1*2-1 = 1 */

  sq  = g11*g11 + h11*h11;

  sqq = sqrt(sq);
  sqr = sqrt(g10*g10 + sq);

  geopack.sl0  = -h11/sqq;
  geopack.cl0  = -g11/sqq;
  geopack.st0  = sqq/sqr;
  geopack.ct0  = g10/sqr;

  geopack.stcl = geopack.st0*geopack.cl0;
  geopack.stsl = geopack.st0*geopack.sl0;
  geopack.ctsl = geopack.ct0*geopack.sl0;
  geopack.ctcl = geopack.ct0*geopack.cl0;

  #if DEBUG > 0
  printf("sl0  = %lf\n", geopack.sl0);
  printf("cl0  = %lf\n", geopack.cl0);
  printf("st0  = %lf\n", geopack.st0);
  printf("ct0  = %lf\n", geopack.ct0);
  printf("stcl = %lf\n", geopack.stcl);
  printf("stsl = %lf\n", geopack.stsl);
  printf("ctsl = %lf\n", geopack.ctsl);
  printf("ctcl = %lf\n", geopack.ctcl);
  #endif

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       IGRF_SetDateTime
;
; PURPOSE:
;       Function to set date and time. MUST be called at least once BEFORE
;       any calls to IGRF functions.
;
; CALLING SEQUENCE:
;       err = IGRF_SetDateTime(year, month, day, hour, minute, second, filename)
;     
;     Input Arguments:  
;       year          - year [1965-2014]
;       month         - month of year [01-12]
;       day           - day of month [01-31]
;       hour          - hour of day [00-24]
;       minute        - minute of hour [00-60]
;       second        - second of minute [00-60]
;       filename      - file with IGRF coefficients
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int IGRF_SetDateTime(int year, int month, int day,
		     int hour, int minute, int second, char *filename)
{
  int err = 0;

  /* load coefficients if not already loaded */
  if (igrf_date.year < 0)
    err = IGRF_loadcoeffs(filename);

  if (err) return (err);

  if (igrf_date.year != year || igrf_date.month != month ||
      igrf_date.day != day || igrf_date.hour != hour ||
      igrf_date.minute != minute || igrf_date.second != second) {

    igrf_date.year   = year;
    igrf_date.month  = month;
    igrf_date.day    = day;
    igrf_date.hour   = hour;
    igrf_date.minute = minute;
    igrf_date.second = second;
    igrf_date.dayno  = dayno(year,month,day,&(igrf_date.daysinyear));

    #if DEBUG > 0
    printf("IGRF_SetDateTime\n");
    printf("%03d: %04d%02d%02d %02d%02d:%02d\n",
          igrf_date.dayno, igrf_date.year, igrf_date.month, igrf_date.day,
          igrf_date.hour, igrf_date.minute, igrf_date.second);
    #endif

    err = IGRF_interpolate_coefs();
  }

  return (err);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       IGRF_GetDateTime
;
; PURPOSE:
;       Function to get date and time.
;
; CALLING SEQUENCE:
;       err = IGRF_GetDateTime(year, month, day, hour, minute, second, dayno);
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

int IGRF_GetDateTime(int *year, int *month, int *day,
                      int *hour, int *minute, int *second, int *dayno)
{
  *year   = igrf_date.year;
  *month  = igrf_date.month;
  *day    = igrf_date.day;
  *hour   = igrf_date.hour;
  *minute = igrf_date.minute;
  *second = igrf_date.second;
  *dayno  = igrf_date.dayno;

  return 0;
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       IGRF_SetNow
;
; PURPOSE:
;       Function to set date and time to current computer time in UT.
;
; CALLING SEQUENCE:
;       err = IGRF_SetNow(filename);
;     
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int IGRF_SetNow(char *filename)
{
  /* current time */
  int err = 0;
  int dyno;
  time_t now;
  struct tm *tm_now;

  /* load coefficients if not already loaded */
  if (igrf_date.year < 0)
    err = IGRF_loadcoeffs(filename);

  if (err) return (err);

  now = time(NULL);
  tm_now = gmtime(&now);    /* right now in UT */

  igrf_date.year   = (*tm_now).tm_year + 1900;
  igrf_date.month  = (*tm_now).tm_mon  + 1;
  igrf_date.day    = (*tm_now).tm_mday;
  igrf_date.hour   = (*tm_now).tm_hour;
  igrf_date.minute = (*tm_now).tm_min;
  igrf_date.second = (*tm_now).tm_sec;
  igrf_date.dayno  = (*tm_now).tm_yday + 1;
  dyno = dayno(igrf_date.year,0,0,&(igrf_date.daysinyear));

  #if DEBUG > 0
  printf("IGRF_SetNow\n");
  printf("%03d: %04d%02d%02d %02d%02d:%02d\n",
        igrf_date.dayno, igrf_date.year, igrf_date.month, igrf_date.day,
        igrf_date.hour, igrf_date.minute, igrf_date.second);
  #endif

  fprintf(stderr, "\nIGRF: No date/time specified, using current time: ");
  fprintf(stderr, "%04d%02d%02d %02d%02d:%02d\n\n",
        igrf_date.year, igrf_date.month, igrf_date.day,
        igrf_date.hour, igrf_date.minute, igrf_date.second);

  err = IGRF_interpolate_coefs();

  return (err);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       IGRF_Tilt
;
; PURPOSE:
;       Function to return dipole tilt angle for the given UT time.
;
; CALLING SEQUENCE:
;       tilt = IGRF_Tilt(year,month,day, hour,minute,second);
;     
;     Return Value:
;       dipole tilt angle in degrees
;
;+-----------------------------------------------------------------------------
*/

double IGRF_Tilt(int yr, int mo, int dy, int hr, int mt, int sc, char *filename)
{
  double sps,s1,s2,s3,q;
  double d1,d2,d3;
  double dd,jd,dec,sras;
  double dyn;
  int diy;
  double gst,cgst,sgst;
  double fday,dj,d__1;
  double rad = 57.295779513;
  double dtwopi = 360.;

  IGRF_SetDateTime(yr,mo,dy,hr,mt,sc, filename);

  dd   = AstAlg_dday(dy,hr,mt,sc);
  jd   = AstAlg_jde(yr,mo,dd);
  dec  = AstAlg_solar_declination(jd)*DTOR;
  sras = AstAlg_solar_right_ascension(jd)*DTOR;

  s1 = cos(sras) * cos(dec);
  s2 = sin(sras) * cos(dec);
  s3 = sin(dec);

  dyn = dayno(yr,mo,dy, &diy);

  /* need Greenwich Mean Sidereal Time */
  /* SGS: seems like this should be somewhere in astalg.c, but can't find it */
  fday = ((double)hr*3600. + mt*60.+sc)/86400.;
  dj   = ((double)yr - 1900.)*365 + ((double)yr - 1901)/4. + dyn - .5 + fday;
  d__1 = dj*0.9856473354 + 279.690983 + fday*360. + 180.;
  /* SGS: double modulus */
  q = d__1/dtwopi;
  q = (q >= 0) ? floor(q) : -floor(-q);
  gst  = (d__1 - dtwopi*q)/rad;

  sgst = sin(gst);
  cgst = cos(gst);

  d1 = geopack.stcl * cgst - geopack.stsl * sgst;
  d2 = geopack.stcl * sgst + geopack.stsl * cgst;
  d3 = geopack.ct0;

  sps  = d1*s1 + d2*s2 + d3*s3;

  return (asin(sps)/DTOR);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       IGRF_msg_notime
;
; PURPOSE:
;       Display error message because no date and time have been set.
;
; CALLING SEQUENCE:
;       IGRF_msg_notime();
;     
;+-----------------------------------------------------------------------------
*/

void IGRF_msg_notime(void) {
fprintf(stderr,
"\n"
"***************************************************************************\n"
"* IGRF ERROR: No Date/Time Set                                            *\n"
"*                                                                         *\n"
"* You must specifiy the date and time in order to use IGRF models. Before *\n"
"* calling IGRF functions you must set the date and time to the integer    *\n"
"* using the function:                                                     *\n"
"*                                                                         *\n"
"*   IGRF_SetDateTime(year,month,day,hour,minute,second,filename);         *\n"
"*                                                                         *\n"
"* or to the current computer time in UT using the function:               *\n"
"*                                                                         *\n"
"*   IGRF_SetNow(filename);                                                *\n"
"*                                                                         *\n"
"* subsequent calls to IGRF functions will use the last date and time      *\n"
"* that was set, so update to the actual date and time that is desired.    *\n"
"***************************************************************************"
"\n\n");
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       sph2car
;
; PURPOSE:
;       Converts spherical coordinates into Cartesian coordinates.
;
; CALLING SEQUENCE:
;       err = sph2car(r,theta,phi, x,y,z);
;     
;     Input Arguments:
;       r             - geocentric distance [RE, where RE=6371.2 km]
;       theta         - co-latitude [radians]
;       phi           - longitude [radians]
;
;     Output Arguments (pointers to type double):  
;       x             - Cartesian components
;       y
;       z
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/
int sph2car(const double rtp[], double xyz[]) {
  double sq;

  sq = rtp[0]*sin(rtp[1]);
  xyz[0] = sq*cos(rtp[2]);
  xyz[1] = sq*sin(rtp[2]);
  xyz[2] = rtp[0]*cos(rtp[1]);
/*
  sq = r*sin(theta);
  *x = sq*cos(phi);
  *y = sq*sin(phi);
  *z = r *cos(theta);
*/

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       car2sph
;
; PURPOSE:
;       Converts Cartesian coordinates into spherical coordinates.
;
; CALLING SEQUENCE:
;       err = car2sph(x,y,z, r,theta,phi);
;
;     Input Arguments
;       x             - Cartesian components [RE]
;       y
;       z
;
;     Output Arguments:
;       r             - geocentric distance [RE]
;       theta         - co-latitude [radians]
;       phi           - longitude [radians]
;
;     Return Value:
;       error code
;
;     Note: at the poles (x=0 and y=0) it is assumed that phi=0
;
;+-----------------------------------------------------------------------------
*/

int car2sph(const double xyz[], double rtp[]) {
  double sq;

  sq = xyz[0]*xyz[0] + xyz[1]*xyz[1];
  rtp[0] = sqrt(sq + xyz[2]*xyz[2]);
  
  if (sq == 0.) {
    rtp[2] = 0.;
    rtp[1] = (xyz[2] < 0) ? M_PI : 0.;
  } else {
    sq = sqrt(sq);
    rtp[2] = atan2(xyz[1],xyz[0]);
    rtp[1] = atan2(sq,xyz[2]);
    if (rtp[2] < 0) rtp[2] += 2*M_PI;
  }
/*
  sq = x*x + y*y;
  *r = sqrt(sq + z*z);
  
  if (sq == 0.) {
    *phi = 0.;
    *theta = (z < 0) ? M_PI : 0.;
  } else {
    sq = sqrt(sq);
    *phi   = atan2(y,x);
    *theta = atan2(sq,z);
    if (*phi < 0) *phi += 2*M_PI;
  }
*/

    return (0);
  }

/*-----------------------------------------------------------------------------
;
; NAME:
;       bspcar
;
; PURPOSE:
;       Converts spherical field components to Cartesian components.
;
; CALLING SEQUENCE:
;       err = bspcar(theta,phi, br,btheta,bphi, bx,by,bz);
;
;     Input Arguments
;       theta         - colatitude of point [radians]
;       phi           - longitude of point [radians]
;       br            - radial component [nT]; radially positive
;       btheta        - colatitude component [nT]; southward positive
;       bphi          - longitude component [nT]; eastward positive
; 
;     Output Arguments:
;       bx            - Cartesian components [RE]
;       by
;       bz
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int bspcar(double theta,double phi, const double brtp[], double bxyz[]) {
  double st,ct,sp,cp,be;

  st = sin(theta);
  ct = cos(theta);
  sp = sin(phi);
  cp = cos(phi);
  be = brtp[0]*st + brtp[1]*ct;

  bxyz[0] = be*cp - brtp[2]*sp;
  bxyz[1] = be*sp + brtp[2]*cp;
  bxyz[2] = brtp[0]*ct - brtp[1]*st;
/*
  st = sin(theta);
  ct = cos(theta);
  sp = sin(phi);
  cp = cos(phi);
  be = br*st + btheta*ct;

  *bx = be*cp - bphi*sp;
  *by = be*sp + bphi*cp;
  *bz = br*ct - btheta*st;
*/

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       bcarsp
;
; PURPOSE:
;       Converts Cartesian field components into spherical components.
;
; CALLING SEQUENCE:
;       err = bcarsp(theta,phi, bx,by,bz, br,btheta,bphi);
;
;     Input Arguments
;       x,y,z         - Cartesian components of point
;       bx,by,bz      - Cartesian field components [nT]
;
;     Output Arguments:
;       br            - spherical field components [nT]
;       btheta
;       bphi
;
;     Return Value:
;       error code
;
;     Note: at the poles (theta=0 or pi) it is assumed that phi=0 and therefore
;           btheta=bx and bphi=by
;
;+-----------------------------------------------------------------------------
*/

int bcarsp(const double xyz[], const double bxyz[], double brtp[]) {
  double r,rho,rho2,cp,sp,ct,st;

  rho2 = xyz[0]*xyz[0] + xyz[1]*xyz[1];
  r    = sqrt(rho2 + xyz[2]*xyz[2]);
  rho  = sqrt(rho2);

  if (rho == 0.) {
    cp = 1.;
    sp = 0.;
  } else {
    cp = xyz[0]/rho;
    sp = xyz[1]/rho;
  }

  ct = xyz[2]/r;
  st = rho/r;

  brtp[0] = (xyz[0]*bxyz[0] + xyz[1]*bxyz[1] + xyz[2]*bxyz[2])/r;
  brtp[1] = (bxyz[0]*cp + bxyz[1]*sp)*ct - bxyz[1]*st;
  brtp[2] = bxyz[1]*cp - bxyz[0]*sp;
/*
  rho2 = x*x+y*y;
  r    = sqrt(rho2 + z*z);
  rho  = sqrt(rho2);

  if (rho == 0.) {
    cp = 1.;
    sp = 0.;
  } else {
    cp = x/rho;
    sp = y/rho;
  }

  ct = z/r;
  st = rho/r;

  *br     = (x*bx + y*by + z*bz)/r;
  *btheta = (bx*cp + by*sp)*ct - bz*st;
  *bphi   = by*cp - bx*sp;
*/

  return (0);
}


int geo2mag(const double xyzg[], double xyzm[]) {

  xyzm[0] = xyzg[0]*geopack.ctcl + xyzg[1]*geopack.ctsl - xyzg[2]*geopack.st0;
  xyzm[1] = xyzg[1]*geopack.cl0  - xyzg[0]*geopack.sl0;
  xyzm[2] = xyzg[0]*geopack.stcl + xyzg[1]*geopack.stsl + xyzg[2]*geopack.ct0;
/*
  *xm = xg*geopack.ctcl + yg*geopack.ctsl - zg*geopack.st0;
  *ym = yg*geopack.cl0  - xg*geopack.sl0;
  *zm = xg*geopack.stcl + yg*geopack.stsl + zg*geopack.ct0;
*/

  return (0);
}

int mag2geo(const double xyzm[], double xyzg[]) {

  xyzg[0] = xyzm[0]*geopack.ctcl - xyzm[1]*geopack.sl0 + xyzm[2]*geopack.stcl;
  xyzg[1] = xyzm[0]*geopack.ctsl + xyzm[1]*geopack.cl0 + xyzm[2]*geopack.stsl;
  xyzg[2] = xyzm[2]*geopack.ct0  - xyzm[0]*geopack.st0;
/*
  *xg = xm*geopack.ctcl - ym*geopack.sl0 + zm*geopack.stcl;
  *yg = xm*geopack.ctsl + ym*geopack.cl0 + zm*geopack.stsl;
  *zg = zm*geopack.ct0  - xm*geopack.st0;
*/

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       geod2geoc
;
; PURPOSE:
;       Convert from geodetic coordinates (as specified by WGS84) to
;       geocentric coordinates using algorithm from IGRF Fortran code.
; 
; CALLING SEQUENCE:
;       err = geod2geoc(lat,lon,alt, rtp);
;     
;     Input Arguments:  
;       lat,lon       - geodetic latitude and longitude [degrees N and E]
;       alt           - distance above sea level [km]
;
;     Output Argument:  
;       rtp[3]        - geocentric coordinates: radial distance from center
;                       of Earth [RE], angle from north pole [radians],
;                       azimuthal angle [radians]
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int geod2geoc(double lat, double lon, double alt, double rtp[]) {

  double a,b,f,a2,b2,st,ct,one,two,three,rho,cd,sd;
  double r,theta;

  a = 6378.1370;              /* semi-major axis */
  f = 1./298.257223563;       /* flattening */
  b = a*(1. -f);              /* semi-minor axis */
  a2 = a*a;
  b2 = b*b;
  theta = (90. -lat)*DTOR;  /* colatitude in radians   */
  st = sin(theta);
  ct = cos(theta);
  one = a2*st*st;
  two = b2*ct*ct;
  three = one + two;
  rho = sqrt(three);          /* [km] */
  r = sqrt(alt*(alt+2*rho) + (a2*one + b2*two)/three);    /* [km] */
  cd = (alt+rho)/r;
  sd = (a2-b2)/rho *ct*st/r;

  rtp[0] = r/RE;              /* units of RE */
  rtp[1] = acos(ct*cd - st*sd);
  rtp[2] = lon*DTOR;

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       plh2xyz
;
; PURPOSE:
;       Convert from geodetic coordinates (as specified by WGS84) to geocentric
;       coordinates (RE = 6371.2 km) using an alternate method from wikipedia.
; 
; CALLING SEQUENCE:
;       [r,theta,phi] = geod2geoc(lat,lon,alt, rtp)
;     
;     Input Arguments:  
;       lat,lon       - geodetic latitude and longitude [degrees N and E]
;       alt           - distance above sea level [km]
;
;     Output Argument:
;       rtp[3]        - r:     radial distance from center of Earth [RE],
;                       theta: angle from north pole [radians],
;                       phi:   azimuthal angle [radians]
;     Return Value:  
;       err           - error code
;
;+-----------------------------------------------------------------------------
*/

int plh2xyz(double lat, double lon, double alt, double rtp[])
{
  double a,b,f,ee,st,ct,sp,cp,N,Nac,x,y,z,r,t;

  a = 6378.1370;              /* semi-major axis */
  f = 1./298.257223563;       /* flattening */
  b = a*(1. -f);              /* semi-minor axis */
  ee = (2. - f) * f;

  st = sin(lat*DTOR);
  ct = cos(lat*DTOR);
  sp = sin(lon*DTOR);
  cp = cos(lon*DTOR);

  N = a / sqrt(1. - ee*st*st);
  Nac = (N + alt) * ct;

  x = Nac * cp;
  y = Nac * sp;
  z = (N*(1. - ee)+alt) * st;

  r = sqrt(Nac*Nac + z*z);
  t = acos(z/r);

  rtp[0] = r/RE;              /* units of RE */
  rtp[1] = t;
  rtp[2] = lon*DTOR;

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       geoc2geod
;
; PURPOSE:
;       Convert from geocentric coordinates (RE = 6371.2 km) to geodetic
;       coordinates (as specified by WGS84) using algorithm from wikipedia.
; 
; CALLING SEQUENCE:
;       [lat,lon,h] = geoc2geod(lat,lon,r, llh)
;     
;     Input Arguments:  
;       lat,lon       - geocentric latitude and longitude [degrees N and E]
;       r             - radial distance from center of Earth [RE]
;
;     Output Argument:  
;       llh[3]        - geodetic latitude and longitude using WGS84 [radians],
;                       distance above sea level [km]
;     Return Value:  
;       err           - error code
;
;+-----------------------------------------------------------------------------
*/

int geoc2geod(double lat, double lon, double r, double llh[])
{
  double a,f,b,ee,e4,aa, theta,phi, st,ct,sp,cp, x,y,z;
  double k0i,pp,zeta,rho,s,rho3,t,u,v,w,kappa;

  a = 6378.1370;             /* semi-major axis */
  f = 1./298.257223563;     /* flattening */
  b = a*(1. -f);             /* semi-minor axis */
  ee = (2. - f) * f;
  e4 = ee*ee;
  aa = a*a;

  theta = (90. - lat)*DTOR;
  phi   = lon * DTOR;

  st = sin(theta);
  ct = cos(theta);
  sp = sin(phi);
  cp = cos(phi);

  x = r*RE * st * cp;
  y = r*RE * st * sp;
  z = r*RE * ct;

  k0i   = 1. - ee;
  pp    = x*x + y*y;
  zeta  = k0i*z*z/aa;
  rho   = (pp/aa + zeta - e4)/6.;
  s     = e4*zeta*pp/(4.*aa);
  rho3  = rho*rho*rho;
  t     = pow(rho3 + s + sqrt(s*(s+2*rho3)), 1./3.);
  u     = rho + t + rho*rho/t;
  v     = sqrt(u*u + e4*zeta);
  w     = ee*(u + v - zeta)/(2.*v);
  kappa = 1. + ee*(sqrt(u+v+w*w) + w)/(u + v);

  llh[0] = atan2(z*kappa,sqrt(pp))/DTOR;
  llh[1] = lon;
  llh[2] = sqrt(pp + z*z*kappa*kappa)/ee * (1./kappa - k0i);

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;      AACGM_v2_Newval 
;
; PURPOSE:
;       Advance position along magnetic field line by one step, i.e.,
;       numerical field-line tracing.
; 
; CALLING SEQUENCE:
;       k = AACGM_v2_Newval(xyz, dir, ds)
;     
;     Input Arguments:  
;       xyz           - Cartesian position
;       dir           - direction along field-line to trace
;       ds            - stepsize to take
;
;     Return value:
;       k[3]          - rate functions evaluated
;
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_Newval(double xyz[], int idir, double ds, double k[]) {
  int j;
  double rtp[3], brtp[3], bxyz[3];
  double bmag;

  car2sph(xyz, rtp);                  /* convert to spherical coords */
  IGRF_compute(rtp, brtp);            /* compute the IGRF field here */
  bspcar(rtp[1],rtp[2], brtp, bxyz);  /* convert field to Cartesian */

  bmag = sqrt(bxyz[0]*bxyz[0] + bxyz[1]*bxyz[1] + bxyz[2]*bxyz[2]);
  for (j=0; j<3; j++) k[j] = ds*idir*bxyz[j]/bmag;

  return (0);
}

/*-----------------------------------------------------------------------------
;
; NAME:
;       AACGM_v2_RK45
;
; PURPOSE:
;       Advance position along magnetic field line by one step, i.e.,
;       numerical field-line tracing using either a fixed stepsize RK4 method
;       or a Runge-Kutta-Fehlberg adaptive stepsize ODE solver.
; 
; CALLING SEQUENCE:
;       AACGM_v2_RK45, xyz, dir, ds, eps, fixed=fixed, max_ds=max_ds, RRds=RRds
;     
;     Input Arguments:  
;       xyz           - Cartesian position
;       dir           - direction along field-line to trace
;       ds            - stepsize to take
;
;     Keywords:
;       fixed         - set this keyword to do RK4 method with stepsize ds
;       max_ds        - maximum stepsize that is allowed, in units of RE
;       RRds          - set to use a maximum stepsize that is proportional
;                       to cube of the distance from the origin.
;
;     Return Value:
;       err           - error code
;
; NOTES:
;
; position variables (x,y,z) are modified directly
;
; HISTORY:
;
; Revision 1.0  150122 SGS initial version
;
;+-----------------------------------------------------------------------------
*/

int AACGM_v2_RK45(double xyz[], int idir, double *ds, double eps, int code) {
  int k;
  double bmag,rr,delt;
  double k1[3],k2[3],k3[3],k4[3],k5[3],k6[3], w1[3],w2[3];
  double rtp[3], brtp[3], bxyz[3];
  double xyztmp[3];

/*function test_aacgm_rk45, x,y,z, idir, ds, eps, noadapt=noadapt, $
 *          max_ds=max_ds, RRds=RRds*/

/*
  ; if noadapt is set then just do straight RK4 and ds is spatial step size
  ;  in kilometers
  ; default is to do adapative step size where eps is error in km
  ; set max_ds to the maximum step size (in RE) to prevent too large step
*/
  /* convert position to spherical coords */
  car2sph(xyz, rtp);

  /* compute IGRF field in spherical coords */
  IGRF_compute(rtp, brtp);

  /* convert field from spherical coords to Cartesian */
  bspcar(rtp[1],rtp[2], brtp, bxyz);

  /* magnitude of field to normalize vector */
  bmag = sqrt(bxyz[0]*bxyz[0] + bxyz[1]*bxyz[1] + bxyz[2]*bxyz[2]);

  if (code == 0) {  /* no adaptive stepping */
    /**************\
     * RK4 Method *
    \**************/
    for (k=0;k<3;k++) k1[k] = (*ds)*idir*bxyz[k]/bmag;
    for (k=0;k<3;k++) xyztmp[k] = xyz[k] + .5*k1[k];
    AACGM_v2_Newval(xyztmp,idir,*ds, k2);
    for (k=0;k<3;k++) xyztmp[k] = xyz[k] + .5*k2[k];
    AACGM_v2_Newval(xyztmp,idir,*ds, k3);
    for (k=0;k<3;k++) xyztmp[k] = xyz[k] + k3[k];
    AACGM_v2_Newval(xyztmp,idir,*ds, k4);

    for (k=0; k<3; k++)
      xyz[k] += (k1[k] + k2[k]+k2[k] + k3[k]+k3[k] + k4[k])/6.;
  } else {

    /************************\
     * Adaptive RK45 method * 
    \************************/
    rr = eps+1; /* just to get into the loop */
    while (rr > eps) {
      for (k=0;k<3;k++) k1[k] = (*ds)*idir*bxyz[k]/bmag;
      for (k=0;k<3;k++) xyztmp[k] = xyz[k] + k1[k]/4.;
      AACGM_v2_Newval(xyztmp,idir,*ds, k2);
      for (k=0;k<3;k++) xyztmp[k] = xyz[k] + (3.*k1[k] + 9.*k2[k])/32.;
      AACGM_v2_Newval(xyztmp,idir,*ds, k3);
      for (k=0;k<3;k++) xyztmp[k] = xyz[k] + (1932.*k1[k] - 7200.*k2[k] +
                                              7296.*k3[k])/2197.;
      AACGM_v2_Newval(xyztmp,idir,*ds, k4);
      for (k=0;k<3;k++)
        xyztmp[k] = xyz[k] + 439.*k1[k]/216. - 8.*k2[k] +
                            3680.*k3[k]/513. - 845.*k4[k]/4104.;
      AACGM_v2_Newval(xyztmp,idir,*ds, k5);
      for (k=0;k<3;k++)
        xyztmp[k] = xyz[k] - 8.*k1[k]/27. + 2.*k2[k] - 3544.*k3[k]/2565. +
                            1859.*k4[k]/4104. - 11.*k5[k]/40.;
      AACGM_v2_Newval(xyztmp,idir,*ds, k6);

      rr = 0.;
      for (k=0;k<3;k++) {
        w1[k] = xyz[k] + 25.*k1[k]/216. + 1408.*k3[k]/2565. +
                          2197.*k4[k]/4104. - k5[k]/5.;
        w2[k] = xyz[k] + 16.*k1[k]/135. + 6656.*k3[k]/12825. +
                          28561.*k4[k]/56430. - 9.*k5[k]/50. +
                          2.*k6[k]/55.;
        rr += (w1[k]-w2[k])*(w1[k]-w2[k]);
      }
      rr = sqrt(rr)/(*ds);

      if (fabs(rr) > 1e-16) {
        delt = 0.84 *pow(eps/rr,0.25);  /* this formula sucks because I have
                                              no it where it came from.
                                              Obviously it involves factors in
                                              the LTEs of the two methods, but
                                              I cannot find them written down
                                              anywhere. */
        /*newds = ds * delt;
        //ds = newds;*/
        *ds *= delt;

        /* maximum stepsize is fixed to max_ds in units of Re */
        /*if keyword_set(max_ds) then ds = min([max_ds,ds])*/
        /* maximum stepsize is r^2 * 1km, where r is in units of Re */
        /*if keyword_set(RRds) then   ds = min([50*r*r*r/RE, ds])*/
        *ds = MIN(50*rtp[0]*rtp[0]*rtp[0]/RE, *ds);
      } /* otherwise leave the stepsize alone */
    }

    /* we use the RK4 solution */
    for (k=0;k<3;k++) xyz[k] = w1[k];
    /*
    ; I would assume that using the higher order RK5 method is better, but
    ; there is the suggestion that using the RK4 solution guarantees accuracy
    ; while the RK5 does not. Apparently some texts are now suggesting using
    ; the RK5 solution...
    for (k=0;k<3;k++) xyz[k] = w2[k];
    */
  }

  return (0);
}

