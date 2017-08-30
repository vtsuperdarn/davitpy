AACGM-v2 Software
v2.4 20170601

C Instructions:

1. Download the coefficients and put them in a convenient directory

2. Set the environment variable AACGM_v2_DAT_PREFIX to the directory that
   you are storing the coefficients in AND include the prefix of the
   coefficient files, i.e., aacgm_coeffs-12-

   e.g.:

   AACGM_v2_DAT_PREFIX=/mnt/thayerfs/shepherd/AACGM/idl/coeffs/aacgm_coeffs-12-

   Note that if you used the old AACGM software from JHU/APL you should have
   a similar variable already set.

   AGB: I altered the routines to allow the file root to be entered as input

3. Untar the contents of the .tar file into a directory

4. Setup IGRF by putting the IGRF coefficients (igrf12coeffs.txt) somewhere
   or leaving them in the current directory and setting the environment
   variable IGRF_COEFFS to the fully qualified path, i.e.,

   IGRF_COEFFS=/directory_you_put_IGRF_coefs_in/igrf12coeffs.txt

   AGB: I altered the routines to allow the filename to be entered as input

5. Build the test program by running:

   gcc -o test_aacgm test_aacgm.c aacgmlib_v2.c igrflib.c genmag.c astalglib.c
                         mlt_v2.c time.c -lm

6. Run the test program by running:

   test_aacgm

   AGB: or by running:
   
   test_aacgm aagcm_coeff_fileroot igrf_filename

   Both commands will yeild the same result
   

   The output should look something like:

================================================================================

AACGM-v2 Test Program

================================================================================

TEST: no date/time (this will return an error.)

**************************************************************************
* AACGM-v2 ERROR: No Date/Time Set                                       *
*                                                                        *
* You must specifiy the date and time in order to use AACGM coordinates, *
* which depend on the internal (IGRF) magnetic field. Before calling     *
* AACGM_v2_Convert() you must set the date and time to the integer values*
* using the function:                                                    *
*                                                                        *
*   AACGM_v2_SetDateTime(year,month,day,hour,minute,second);             *
*                                                                        *
* or to the current computer time in UT using the function:              *
*                                                                        *
*   AACGM_v2_SetNow();                                                   *
*                                                                        *
* subsequent calls to AACGM_v2_Convert() will use the last date and time *
* that was set, so update to the actual date and time that is desired.   *
**************************************************************************

TEST: Setting time to : 20140322 0311:00

TEST: geographic to AACGM-v2
     GLAT       GLON        HEIGHT       MLAT       MLON       R
     45.500000  -23.500000  1135.000000  48.189618  57.763454  1.177533

TEST: AACGM-v2 to geographic
     MLAT       MLON        HEIGHT       GLAT       GLON       HEIGHT
     48.189618  57.763454  1131.097495  45.440775  -23.472757  1134.977896

Do the same thing but use field-line tracing

TEST: geographic to AACGM-v2 (TRACE)
     GLAT       GLON        HEIGHT       MLAT       MLON       R
     45.500000  -23.500000  1135.000000  48.194757  57.758831  1.177533

TEST: AACGM-v2 to geographic (TRACE)
     MLAT       MLON        HEIGHT       GLAT       GLON       HEIGHT
     48.194757  57.758831  1131.097495  45.500000  -23.500000  1135.000000

--------------------------------------------------------------------------------

Testing MLT
--------------------------------------------------------------------------------

      GLAT       GLON        HEIGHT       MLAT       MLON       MLT
TRACE 37.000000  -88.000000  300.000000  48.840368  -17.006090  1.977745
COEFF 37.000000  -88.000000  300.000000  48.844355  -16.999464  1.978187


Array:
      45.0000   0.0000    150.0000     40.2841     76.6676      8.2227
      45.0000   1.0000    150.0000     40.2447     77.4899      8.2775
      45.0000   2.0000    150.0000     40.2108     78.3157      8.3325
      45.0000   3.0000    150.0000     40.1822     79.1452      8.3878
      45.0000   4.0000    150.0000     40.1587     79.9785      8.4434
      45.0000   5.0000    150.0000     40.1400     80.8157      8.4992
      45.0000   6.0000    150.0000     40.1261     81.6569      8.5553
      45.0000   7.0000    150.0000     40.1165     82.5020      8.6116
      45.0000   8.0000    150.0000     40.1111     83.3513      8.6682
      45.0000   9.0000    150.0000     40.1097     84.2048      8.7251
      45.0000  10.0000    150.0000     40.1121     85.0624      8.7823
      45.0000  11.0000    150.0000     40.1179     85.9243      8.8398
      45.0000  12.0000    150.0000     40.1271     86.7904      8.8975
      45.0000  13.0000    150.0000     40.1394     87.6608      8.9555
      45.0000  14.0000    150.0000     40.1546     88.5354      9.0138
      45.0000  15.0000    150.0000     40.1725     89.4143      9.0724
      45.0000  16.0000    150.0000     40.1930     90.2976      9.1313
      45.0000  17.0000    150.0000     40.2157     91.1850      9.1905
      45.0000  18.0000    150.0000     40.2405     92.0768      9.2499
      45.0000  19.0000    150.0000     40.2673     92.9728      9.3097


IMPORTANT NOTES:

1. Magnetic local time (MLT) functions have been restored:

      double MLTConvertYMDHMS_v2(int yr,int mo,int dy,int hr,int mt,int sc,
                      double mlon);
      double MLTConvertYrsec_v2(int yr,int yrsec, double mlon);
      double MLTConvertEpoch_v2(double epoch, double mlon);


   Note that AACGM-v2 longitude is much less sensitive to altitude; maximum
   difference of <1 degree (5 min in MLT) over the range 0-2000 km. For this
   reason there is no height passed directly into the MLT routines. The value
   of AACGM-v2 longitude does change with altitude and variations of MLT with
   altitude above a given geographic location do exist.

2. The function AACGM_v2_Convert is a direct replacement for the function
   AACGMConvert that is used in much of the SD software. This is your
   starting point, but you can modify the test program as you like.

3. New user-space functions have been added that allow users to set the
   date and time. The functions are:

       AACGM_v2_SetDateTime(int year, int month, int day, int hour,
                        int minute, int second);

       AACGM_v2_SetNow();

   The latter will use the current computer date and time in UT.

   Note that setting the time frequently triggers an interpolation in time and
   in altitude, which will slow the calculations. Testing should be done to
   determine what the correspondence between changes in time and AACGM lat/lon
   are.

4. You must set the date and time at least once or the code will not run.

5. A new user-space function has been added that allow users to see what
   date and time are being used. The function is:

       AACGM_v2_GetDateTime(int *year, int *month, int *day, int *hour,
                        int *minute, int *second, int *doy);


This package include the following files:

AACGM C software:

README.txt            ; this file
release_notes.txt     ; details of changes to v2.4
aacgmlib_v2.c         ; AACGM-v2 functions
aacgmlib_v2.h         ; AACGM-v2 header file
genmag.c              ; general purpose functions
genmag.h              ; general purpose header file
igrflib.c             ; internal IGRF functions
igrflib.h             ; internal IGRF header file
time.c                ; internal date/time functions
time.h                ; internal date/time header file
astalg.c              ; Astronomical algorithms functions
astalg.h              ; Astronomical algorithms header file
mlt_v2.c              ; MLT-v2 functions
mlt_v2.h              ; MLT-v2 header file
igrf12coeffs.txt      ; IGRF12 coefficients
test_aacgm.c          ; testing and example program
LICENSE-AstAlg.txt    ; license file for Astro algrorithms

