#ifndef _IGRFLIB_
#define _IGRFLIB_

#define IGRF_FIRST_EPOCH 1900
#define IGRF_LAST_EPOCH 2015
/* SGS using IGRF_COEFFS environment variable */
/*#define IGRF_FILE "igrf12coeffs.txt"*/  /* current IGRF model */

#ifndef RE
#define RE     6371.2                 /* Earth Radius */
#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846 /* define M_PI if not already */
#endif

#define MAXSTR 200                    /* maximum string length */
#define MAXNYR 100                    /* maximum number of epochs */
#define IGRF_ORDER  13                     /* maximum order of SH expansion */
#define IGRF_MAXK   ((IGRF_ORDER+1)*(IGRF_ORDER+1)) /* # of SH coefficients */

#define DTOR (M_PI/180.)
#define MIN(a,b) ((a) < (b) ? (a) : (b))

/* function prototypes */

/* private functions */
int IGRF_loadcoeffs(char *filename);
int IGRF_interpolate_coefs(void);
void pause(void);
void IGRF_msg_notime(void);

/* public functions */
int IGRF_compute(const double rtp[], double brtp[]);
int IGRF_SetNow(char *filename);
int IGRF_GetDateTime(int *year, int *month, int *day,
                      int *hour, int *minute, int *second, int *dayno);
int IGRF_SetDateTime(int year, int month, int day,
		     int hour, int minute, int second, char *filename);
double IGRF_Tilt(int yr, int mo, int dy, int hr, int mt, int sc,
		 char *filename);

/* some geopack functionality */
int geo2mag(const double xyzg[], double xyzm[]);
int mag2geo(const double xyzm[], double xyzg[]);
int bcarsp(const double xyz[], const double bxyz[], double brtp[]);
int bspcar(double theta,double phi, const double brtp[], double bxyz[]);
int car2sph(const double xyz[], double rtp[]);
int sph2car(const double rtp[], double xyz[]);

int geod2geoc(double lat, double lon, double alt, double rtp[]);
int plh2xyz(double lat, double lon, double alt, double rtp[]);
int geoc2geod(double lat, double lon, double r, double llh[]);

int AACGM_v2_Newval(double xyz[], int idir, double ds, double k[]);
int AACGM_v2_RK45(double xyz[], int idir, double *ds, double eps, int code);

#endif

