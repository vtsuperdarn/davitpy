#ifndef _AACGMLIB_

#define _AACGMLIB_

/*****************************************************************************
 * defines and structures
 *****************************************************************************/

#define RE      6371.2  /* Earth Radius */
#define MAXALT  2000    /* maximum altitude in km */
#define NCOORD  3       /* xyz */
#define POLYORD 5       /* quartic polynomial fit in altitude */
#define NFLAG   2       /* 0: geo to AACGM, 1: AACGM to geo */
#define SHORDER 10      /* order of Spherical Harmonic expansion */
#define AACGM_KMAX ((SHORDER+1)*(SHORDER+1))   /* number of SH coefficients */

/* options for AACGM-v2 coordinate determination                           */
#define G2A        0  /* convert geographic (geodetic) to AACGM-v2 coords  */
#define A2G        1  /* convert AACGM-v2 to geographic (geodetic) coords  */
#define TRACE      2  /* use field-line tracing to compute coordinates     */
#define ALLOWTRACE 4  /* if height is >2000 km use tracing, else use coefs */
#define BADIDEA    8  /* use coefficients above 2000 km; Terrible idea!!   */
#define GEOCENTRIC 16 /* assume inputs are geocentric with sphere RE       */
#ifndef M_PI
  #define M_PI 3.14159265358979323846 /* define M_PI if not already */
#endif

/* added for MSC compatibility */
#ifdef _MSC_VER
  #ifndef NAN
    #include <float.h>
    #define INFINITY (DBL_MAX+DBL_MAX)
    #define NAN (INFINITY-INFINITY)
  #endif
#endif

/*****************************************************************************
 * function prototypes
 *****************************************************************************/

/* private functions */
int AACGM_v2_Rylm(double colat, double lon, int order, double *ylmval);
void AACGM_v2_Alt2CGM(double r_height_in, double r_lat_alt, double *r_lat_adj);
int AACGM_v2_CGM2Alt(double r_height_in, double r_lat_in, double *r_lat_adj);
double AACGM_v2_Sgn(double a, double b);
int convert_geo_coord_v2(double lat_in, double lon_in, double height_in,
                         double *lat_out, double *lon_out, int flag, int order,
			 char *igrf_filename);
int AACGM_v2_LoadCoefFP(FILE *fp, int code);
int AACGM_v2_LoadCoef(char *fname, int code);
int AACGM_v2_LoadCoefs(int year, char *root);
int AACGM_v2_TimeInterp(char *root);
void AACGM_v2_errmsg(int ecode);
int AACGM_v2_Trace(double lat_in, double lon_in, double alt,
                   double *lat_out, double *lon_out, char *igrf_filename);
int AACGM_v2_Trace_inv(double lat_in, double lon_in, double alt,
                       double *lat_out, double *lon_out, char *igrf_filename);


/* public functions */
int AACGM_v2_Convert(double in_lat, double in_lon, double height,
                     double *out_lat, double *out_lon, double *r, int code,
		     char *igrf_filename);
int AACGM_v2_SetDateTime(int year, int month, int day,
                         int hour, int minute, int second, char *root);
int AACGM_v2_GetDateTime(int *year, int *month, int *day,
                         int *hour, int *minute, int *second, int *dayno);
int AACGM_v2_SetNow(char *root);

#endif

