!
!  Test driver for HWM14 subroutines
!  The output of the program is given at the end of the file
!
!  AUTHORS
!    John Emmert
!    Douglas Drob
!
!  DATE
!    6 January 2015 (Updated)
!
!******************************************************************************

!program checkhwm14
subroutine checkhwm14(path)
  use hwm
  use dwm

  implicit none

  integer            :: iyd
  real(4)            :: sec,alt,glat,glon,stl,f107a,f107,ap(2)
  real(4)            :: w(2), qw(2), dw(2)
  real(4)            :: mlt, mlat, kp, mmpwind, mzpwind
  real(4)            :: ut, apqt(2)
  real(4),external   :: pershift
  integer            :: day
  integer            :: ialt,istl,ilat,ilon,iaptemp
  integer            :: imlat,imlt,ikp
  character(250),intent(in)   :: path
  character(250)             :: datapath

  COMMON /DATPTH/datapath
  datapath = path

! height profile
  day = 150
  iyd = 95000 + day
  ut = 12.0
  sec = ut * 3600.0
  glat = -45.0
  glon = -85.0
  stl = pershift(ut + glon/15.0, (/0.0, 24.0/) )
  ap(2) = 80.0
  apqt(2) = -1.0
  print *, 'height profile'
  print '(a5,i3, a5,f4.1, a7,f5.1, a7,f6.1, a6,f4.1, a5,f5.1)', &
            'day=',day, ', ut=',ut, ', glat=',glat,  &
            ', glon=',glon, ', stl=',stl, ', ap=',ap(2)
  print '(6x,3a22)', 'quiet', 'disturbed', 'total'
  print '(a6,3(a12,a10))', 'alt', 'mer','zon', 'mer','zon', 'mer','zon'
  do ialt = 0, 400, 25
    alt = float(ialt)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,apqt,datapath,qw)
    call dwm07(iyd,sec,alt,glat,glon,ap,dw)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,datapath,w)
    print '(f6.0,3(f12.3,f10.3))', alt, qw, dw, w
  end do
  print *
  print *

! latitude profile
  day = 305
  iyd = 95000 + day
  ut = 18.0
  sec = ut * 3600.0
  alt = 250.0
  glon = 30.0
  stl = pershift(ut + glon/15.0, (/0.0, 24.0/) )
  ap(2) = 48.0
  apqt(2) = -1.0
  print *, 'latitude profile'
  print '(a5,i3, a5,f4.1, a6,f5.1, a7,f6.1, a6,f4.1, a5,f5.1)', &
            'day=',day, ', ut=',ut, ', alt=',alt,  &
            ', glon=',glon, ', stl=',stl, ', ap=',ap(2)
  print '(6x,3a22)', 'quiet', 'disturbed', 'total'
  print '(a6,3(a12,a10))', 'glat', 'mer','zon', 'mer','zon', 'mer','zon'
  do ilat = -90, 90, 10
    glat = float(ilat)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,apqt,datapath,qw)
    call dwm07(iyd,sec,alt,glat,glon,ap,dw)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,datapath,w)
    print '(f6.1,3(f12.3,f10.3))', glat, qw, dw, w
  end do
  print *
  print *

! local time profile
  day = 75
  iyd = 95000 + day
  alt = 125.0
  glat = 45.0
  glon = -70.0
  ap(2) = 30.0
  apqt(2) = -1.0
  print *, 'local time profile'
  print '(a5,i3, a6,f5.1, a7,f5.1, a7,f6.1, a5,f5.1)', &
            'day=',day, ', alt=',alt, ', glat=',glat,  &
            ', glon=',glon, ', ap=',ap(2)
  print '(5x,3a22)', 'quiet', 'disturbed', 'total'
  print '(a5,3(a12,a10))', 'stl', 'mer','zon', 'mer','zon', 'mer','zon'
  do istl = 0,16
    stl = 1.5 * float(istl)
    sec = (stl - glon/15.0) * 3600.0
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,apqt,datapath,qw)
    call dwm07(iyd,sec,alt,glat,glon,ap,dw)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,datapath,w)
    print '(f5.1,3(f12.3,f10.3))', stl, qw, dw, w
  end do
  print *
  print *

! longitude profile
  day = 330
  iyd = 95000 + day
  ut = 6.0
  sec = ut * 3600.0
  alt = 40.0
  glat = -5.0
  ap(2) = 4.0
  apqt(2) = -1.0
  print *, 'longitude profile'
  print '(a5,i3, a5,f4.1, a6,f5.1, a7,f5.1, a7,f6.1, a5,f5.1)', &
            'day=',day, ', ut=',ut, ', alt=',alt, ', glat=',glat,  &
            ', glon=',glon, ', ap=',ap(2)
  print '(6x,3a22)', 'quiet', 'disturbed', 'total'
  print '(a6,3(a12,a10))', 'glon', 'mer','zon', 'mer','zon', 'mer','zon'
  do ilon = -180, 180, 20
    glon = float(ilon)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,apqt,datapath,qw)
    call dwm07(iyd,sec,alt,glat,glon,ap,dw)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,datapath,w)
    print '(f6.0,3(f12.3,f10.3))', glon, qw, dw, w
  end do
  print *
  print *

! day of year profile
  ut = 21.0
  sec = ut * 3600.0
  alt = 200.0
  glat = -65.0
  glon = -135.0
  stl = pershift(ut + glon/15.0, (/0.0, 24.0/) )
  ap(2) = 15.0
  apqt(2) = -1.0
  print *, 'day of year profile'
  print '(a4,f4.1, a6,f5.1, a7,f5.1, a7,f6.1, a6,f4.1, a5,f5.1)', &
            'ut=',ut, ', alt=',alt, ', glat=',glat,  &
            ', glon=',glon, ', stl=',stl, ', ap=',ap(2)
  print '(6x,3a22)', 'quiet', 'disturbed', 'total'
  print '(a6,3(a12,a10))', 'day', 'mer','zon', 'mer','zon', 'mer','zon'
  do day = 0, 360, 20
    iyd = 95000 + day
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,apqt,datapath,qw)
    call dwm07(iyd,sec,alt,glat,glon,ap,dw)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,datapath,w)
    print '(i6,3(f12.3,f10.3))', day, qw, dw, w
  end do
  print *
  print *

! ap profile
  day = 280
  iyd = 95000 + day
  ut = 21.0
  sec = ut * 3600.0
  alt = 350.0
  glat = 38.0
  glon = 125.0
  stl = pershift(ut + glon/15.0, (/0.0, 24.0/) )
  ap(2) = 48.0
  apqt(2) = -1.0
  print *, 'magnetic activity profile'
  print '(a5,i3, a5,f4.1, a6,f5.1, a7,f5.1, a7,f6.1, a6,f4.1)', &
            'day=',day, ', ut=',ut, ', alt=',alt,  &
            ', glat=',glat, ', glon=',glon, ', stl=',stl
  print '(6x,3a22)', 'quiet', 'disturbed', 'total'
  print '(a6,3(a12,a10))', 'ap', 'mer','zon', 'mer','zon', 'mer','zon'
  do iaptemp = 0, 260, 20
    ap(2) = float(iaptemp)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,apqt,datapath,qw)
    call dwm07(iyd,sec,alt,glat,glon,ap,dw)
    call hwm14(iyd,sec,alt,glat,glon,stl,f107a,f107,ap,datapath,w)
    print '(f6.1,3(f12.3,f10.3))', ap(2), qw, dw, w
  end do
  print *
  print *

! dwm: mlat profile
  kp = 6.0
  mlt = 3.0
  print *, 'dwm: magnetic latitude profile'
  print '(a5,f4.1, a5,f3.1)', 'mlt=',mlt, ', kp=',kp
  print '(a6,a12,a10)', 'mlat', 'mag mer', 'mag zon'
  do imlat = -90, 90, 10
    mlat = float(imlat)
    call dwm07b(mlt, mlat, kp, mmpwind, mzpwind)
    print '(f6.1,f12.3,f10.3)', mlat, mmpwind, mzpwind
  end do
  print *
  print *

! dwm: mlt profile
  kp = 6.0
  mlat = 45.0
  print *, 'dwm: magnetic local time profile'
  print '(a6,f5.1, a5,f3.1)', 'mlat=',mlat, ', kp=',kp
  print '(a6,a12,a10)', 'mlt', 'mag mer', 'mag zon'
  do imlt = 0, 16
    mlt = float(imlt)*1.5
    call dwm07b(mlt, mlat, kp, mmpwind, mzpwind)
    print '(f6.1,f12.3,f10.3)', mlt, mmpwind, mzpwind
  end do
  print *
  print *

! dwm: kp profile
  mlat = -50.0
  mlt = 3.0
  print *, 'dwm: kp profile'
  print '(a6,f5.1, a6,f4.1)', 'mlat=',mlat, ', mlt=',mlt
  print '(a6,a12,a10)', 'kp', 'mag mer', 'mag zon'
  do ikp = 0, 18
    kp = float(ikp)*0.5
    call dwm07b(mlt, mlat, kp, mmpwind, mzpwind)
    print '(f6.1,f12.3,f10.3)', kp, mmpwind, mzpwind
  end do
  print *
  print *

!end program checkhwm14
end subroutine checkhwm14

!******************************************************************************
!
!PERSHIFT
!JOHN EMMERT   9/12/03
!TRANSLATED TO FORTRAN-90 10/4/06. FORTRAN VERSION ONLY ALLOWS SCALAR INPUTS
!SHIFTS INPUT VALUES INTO A SPECIFIED PERIODIC INTERVAL
!
!CALLING SEQUENCE:   Result = PERSHIFT(x, range)
!
!ARGUMENTS
!      x:        The value to be shifted
!      perint:   2-element vector containing the start and end values
!                of the desired periodic interval.  The periodicity is
!                determined by the span of the range.
!
!ROUTINES USED THAT ARE NOT IN THE STANDARD FORTRAN-90 LIBRARY
!      None

function pershift(x, perint)

  real(4), parameter :: tol=1e-4
  real(4)            :: x, perint(0:1)
  real(4)            :: a, span, offset, offset1, pershift

  pershift = x
  a = perint(0)
  span = perint(1) - perint(0)
  if (span .ne. 0) then
    offset = x-a
    offset1 = mod(offset,span)
    if (abs(offset1) .lt. tol) offset1 = 0
  endif
  pershift = a + offset1
  if ((offset .lt. 0) .and. (offset1 .ne. 0)) pershift = pershift + span

  return

end function pershift


!******************************************************************************
!  TEST OUTPUT (ifort -O2) Default
!******************************************************************************
 ! height profile
 ! day=150, ut=12.0, glat=-45.0, glon= -85.0, stl= 6.3, ap= 80.0
 !                       quiet             disturbed                 total
 !   alt         mer       zon         mer       zon         mer       zon
 !    0.       0.031     6.271       0.000    -0.000       0.031     6.271
 !   25.       2.965    25.115       0.000    -0.000       2.965    25.115
 !   50.      -6.627    96.343       0.000    -0.000      -6.627    96.343
 !   75.       2.238    44.845       0.000    -0.000       2.238    44.845
 !  100.     -14.339    31.627       0.086    -0.037     -14.253    31.590
 !  125.      15.125    21.110      22.279    -9.483      37.404    11.628
 !  150.      -1.683   -14.391      44.472   -18.929      42.789   -33.319
 !  175.     -24.280   -31.019      44.558   -18.965      20.278   -49.984
 !  200.     -19.531   -49.623      44.558   -18.965      25.027   -68.588
 !  225.     -10.261   -61.057      44.558   -18.965      34.297   -80.022
 !  250.      -4.150   -68.595      44.558   -18.965      40.408   -87.560
 !  275.      -0.122   -73.564      44.558   -18.965      44.436   -92.530
 !  300.       2.534   -76.840      44.558   -18.965      47.092   -95.806
 !  325.       4.285   -79.000      44.558   -18.965      48.843   -97.965
 !  350.       5.439   -80.424      44.558   -18.965      49.997   -99.389
 !  375.       6.200   -81.362      44.558   -18.965      50.758  -100.327
 !  400.       6.702   -81.981      44.558   -18.965      51.259  -100.946


 ! latitude profile
 ! day=305, ut=18.0, alt=250.0, glon=  30.0, stl=20.0, ap= 48.0
 !                       quiet             disturbed                 total
 !  glat         mer       zon         mer       zon         mer       zon
 ! -90.0     -37.423   130.673     -86.773    46.502    -124.197   177.174
 ! -80.0     -16.364    76.079    -133.904   -12.215    -150.268    63.864
 ! -70.0      12.734    40.446    -137.274  -112.417    -124.540   -71.971
 ! -60.0      35.676    53.028     -58.808  -158.941     -23.132  -105.913
 ! -50.0      47.513    83.641     -16.136  -111.817      31.377   -28.176
 ! -40.0      50.456    87.682     -10.932   -51.150      39.524    36.532
 ! -30.0      48.334    69.088       7.971   -36.298      56.305    32.790
 ! -20.0      45.757    68.768      15.092   -34.427      60.849    34.341
 ! -10.0      46.997    99.279      11.120   -26.603      58.117    72.676
 !   0.0      50.930   126.837       5.821   -16.657      56.751   110.180
 !  10.0      50.389   124.748       0.659   -13.275      51.048   111.472
 !  20.0      40.982   110.968      -5.329   -20.421      35.653    90.547
 !  30.0      27.572   112.203     -12.740   -34.467      14.832    77.736
 !  40.0      16.513   116.979     -15.446   -41.985       1.068    74.993
 !  50.0       3.940    96.754      -6.688   -54.782      -2.749    41.972
 !  60.0     -20.111    61.456      -7.001  -202.013     -27.112  -140.557
 !  70.0     -54.689    56.348     -36.510   -52.515     -91.199     3.833
 !  80.0     -83.216    97.972    -103.542    81.980    -186.757   179.951
 !  90.0     -90.879   144.768     -75.838    90.679    -166.717   235.447


 ! local time profile
 ! day= 75, alt=125.0, glat= 45.0, glon= -70.0, ap= 30.0
 !                      quiet             disturbed                 total
 !  stl         mer       zon         mer       zon         mer       zon
 !  0.0      15.039   -20.115      -8.475   -20.072       6.564   -40.187
 !  1.5      35.812   -57.326      -7.022     2.427      28.790   -54.899
 !  3.0      27.917   -77.389      -5.600    20.202      22.316   -57.187
 !  4.5       3.087   -69.451      -8.034    21.516      -4.946   -47.936
 !  6.0      -9.467   -50.533     -13.708     9.066     -23.175   -41.468
 !  7.5       5.518   -42.214     -16.795    -1.433     -11.278   -43.648
 !  9.0      33.677   -44.876     -16.107    -4.815      17.570   -49.691
 ! 10.5      48.133   -40.807     -13.941    -4.061      34.192   -44.868
 ! 12.0      38.355   -20.578     -11.480    -1.964      26.875   -22.542
 ! 13.5      17.633     1.913      -8.243     0.139       9.390     2.052
 ! 15.0       3.349     5.533      -4.710    -0.930      -1.362     4.603
 ! 16.5      -3.237   -10.940      -3.931   -13.190      -7.168   -24.130
 ! 18.0     -12.932   -25.485      -8.103   -40.895     -21.035   -66.380
 ! 19.5     -27.966   -19.085     -13.157   -64.857     -41.123   -83.942
 ! 21.0     -33.947     0.020     -12.756   -60.282     -46.702   -60.262
 ! 22.5     -16.987     4.486     -10.061   -41.102     -27.048   -36.616
 ! 24.0      15.039   -20.115      -8.473   -20.030       6.566   -40.145


 ! longitude profile
 ! day=330, ut= 6.0, alt= 40.0, glat= -5.0, glon= -70.0, ap=  4.0
 !                       quiet             disturbed                 total
 !  glon         mer       zon         mer       zon         mer       zon
 ! -180.      -0.757   -16.835       0.000    -0.000      -0.757   -16.835
 ! -160.      -0.592   -18.073       0.000    -0.000      -0.592   -18.073
 ! -140.       0.033   -20.107       0.000    -0.000       0.033   -20.107
 ! -120.       0.885   -22.166       0.000    -0.000       0.885   -22.166
 ! -100.       1.507   -22.900      -0.000    -0.000       1.507   -22.900
 !  -80.       1.545   -21.649      -0.000     0.000       1.545   -21.649
 !  -60.       1.041   -19.089       0.000     0.000       1.041   -19.089
 !  -40.       0.421   -16.596       0.000     0.000       0.421   -16.596
 !  -20.       0.172   -14.992       0.000     0.000       0.172   -14.992
 !    0.       0.463   -13.909       0.000     0.000       0.463   -13.909
 !   20.       1.049   -12.395      -0.000    -0.000       1.049   -12.395
 !   40.       1.502   -10.129      -0.000     0.000       1.502   -10.129
 !   60.       1.552    -7.991      -0.000     0.000       1.552    -7.991
 !   80.       1.232    -7.369       0.000     0.000       1.232    -7.369
 !  100.       0.757    -8.869       0.000    -0.000       0.757    -8.869
 !  120.       0.288   -11.701       0.000    -0.000       0.288   -11.701
 !  140.      -0.146   -14.359       0.000    -0.000      -0.146   -14.359
 !  160.      -0.538   -15.945       0.000    -0.000      -0.538   -15.945
 !  180.      -0.757   -16.835       0.000    -0.000      -0.757   -16.835


 ! day of year profile
 ! ut=21.0, alt=200.0, glat=-65.0, glon=-135.0, stl=12.0, ap= 15.0
 !                       quiet             disturbed                 total
 !   day         mer       zon         mer       zon         mer       zon
 !     0      -3.256   -51.416       4.826     9.273       1.570   -42.143
 !    20     -10.257   -46.217       4.827     9.270      -5.430   -36.947
 !    40     -18.736   -39.190       4.828     9.264     -13.908   -29.927
 !    60     -27.317   -32.339       4.828     9.262     -22.489   -23.077
 !    80     -35.666   -26.986       4.823     9.288     -30.843   -17.698
 !   100     -44.220   -23.381       4.805     9.366     -39.415   -14.016
 !   120     -53.496   -20.845       4.778     9.495     -48.717   -11.350
 !   140     -63.335   -18.348       4.753     9.628     -58.582    -8.720
 !   160     -72.501   -15.238       4.740     9.708     -67.762    -5.530
 !   180     -78.864   -11.743       4.740     9.704     -74.124    -2.039
 !   200     -80.126    -9.010       4.755     9.618     -75.371     0.608
 !   220     -74.801    -8.633       4.781     9.482     -70.021     0.850
 !   240     -62.997   -11.886       4.807     9.356     -58.190    -2.529
 !   260     -46.636   -19.017       4.824     9.284     -41.813    -9.733
 !   280     -28.987   -28.928       4.829     9.262     -24.159   -19.666
 !   300     -13.666   -39.428       4.828     9.264      -8.838   -30.164
 !   320      -3.508   -47.955       4.827     9.270       1.319   -38.685
 !   340       0.238   -52.481       4.826     9.273       5.064   -43.208
 !   360      -1.918   -52.224       4.826     9.273       2.908   -42.951


 ! magnetic activity profile
 ! day=280, ut=21.0, alt=350.0, glat= 38.0, glon= 125.0, stl= 5.3
 !                       quiet             disturbed                 total
 !    ap         mer       zon         mer       zon         mer       zon
 !   0.0      20.082   -66.483      -1.453    -5.318      18.630   -71.801
 !  20.0      20.082   -66.483      -9.057    -2.548      11.026   -69.031
 !  40.0      20.082   -66.483     -20.477   -17.007      -0.395   -83.490
 !  60.0      20.082   -66.483     -29.204   -30.416      -9.121   -96.899
 !  80.0      20.082   -66.483     -34.047   -38.327     -13.965  -104.811
 ! 100.0      20.082   -66.483     -36.950   -43.408     -16.868  -109.891
 ! 120.0      20.082   -66.483     -38.558   -46.501     -18.476  -112.984
 ! 140.0      20.082   -66.483     -39.463   -48.508     -19.380  -114.991
 ! 160.0      20.082   -66.483     -39.902   -49.810     -19.820  -116.293
 ! 180.0      20.082   -66.483     -39.969   -50.507     -19.887  -116.990
 ! 200.0      20.082   -66.483     -39.767   -50.737     -19.685  -117.220
 ! 220.0      20.082   -66.483     -39.640   -50.729     -19.558  -117.212
 ! 240.0      20.082   -66.483     -39.640   -50.729     -19.558  -117.212
 ! 260.0      20.082   -66.483     -39.640   -50.729     -19.558  -117.212


 ! dwm: magnetic latitude profile
 ! mlt= 3.0, kp=6.0
 !  mlat     mag mer   mag zon
 ! -90.0     157.613  -158.954
 ! -80.0     158.138  -141.865
 ! -70.0      56.293   -41.271
 ! -60.0      60.878    69.305
 ! -50.0     121.506    -5.004
 ! -40.0      40.882   -15.775
 ! -30.0      21.850   -25.517
 ! -20.0      11.640   -34.856
 ! -10.0       5.533   -40.228
 !   0.0       5.327   -45.354
 !  10.0       8.204   -50.906
 !  20.0       9.422   -55.711
 !  30.0       3.494   -56.017
 !  40.0      -7.319   -49.619
 !  50.0      -7.873    18.973
 !  60.0     -33.112    80.795
 !  70.0     -20.227    -8.189
 !  80.0     -55.275   -64.783
 !  90.0    -137.149  -170.526


 ! dwm: magnetic local time profile
 ! mlat= 45.0, kp=6.0
 !   mlt     mag mer   mag zon
 !   0.0     -22.332  -129.270
 !   1.5     -28.861   -78.026
 !   3.0      -6.246   -33.077
 !   4.5      -5.592   -33.656
 !   6.0     -32.813   -39.796
 !   7.5     -49.672   -34.709
 !   9.0     -48.676   -26.754
 !  10.5     -41.507   -20.200
 !  12.0     -35.088   -15.157
 !  13.5     -28.140   -12.072
 !  15.0     -18.344   -13.870
 !  16.5      -9.103   -27.605
 !  18.0     -12.015   -57.829
 !  19.5     -27.512   -86.677
 !  21.0     -24.814  -103.293
 !  22.5     -11.058  -127.315
 !  24.0     -22.332  -129.270


 ! dwm: kp profile
 ! mlat=-50.0, mlt= 3.0
 !    kp     mag mer   mag zon
 !   0.0      -8.066     5.787
 !   0.5      -6.955     5.282
 !   1.0      -3.365     3.849
 !   1.5       3.202     1.647
 !   2.0      13.413    -1.112
 !   2.5      26.175    -3.461
 !   3.0      39.805    -4.712
 !   3.5      54.121    -5.081
 !   4.0      68.787    -4.864
 !   4.5      83.302    -4.428
 !   5.0      97.009    -4.194
 !   5.5     109.699    -4.429
 !   6.0     121.506    -5.004
 !   6.5     132.195    -5.750
 !   7.0     141.548    -6.483
 !   7.5     149.386    -7.019
 !   8.0     155.576    -7.193
 !   8.5     155.576    -7.193
 !   9.0     155.576    -7.193
