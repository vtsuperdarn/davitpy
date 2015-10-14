! Copyright (C) 2012  VT SuperDARN Lab
! Full license can be found in LICENSE.txt
program     rayDARN

! ***********************************************************************************
! ***********************************************************************************
! MPI version of the ray tracing code
! ***********************************************************************************
!
! Inputs:
!   - txlat, txlon: latitude, longitude of transmitter (in geographic coordinates)
!   - azimbeg, azimend, azimstp: look direction (in degrees East)
!   - freq: operating frequency (in MHz)
!   - elevbeg, elevend, elevstp: elevation angle beginning, end and step (in degrees)
!   - year, mmdd: year, month+date
!   - nhop: number of hops to be considered (default is 1)
!   - hourbeg, hour end, hourstp: hour (+25 for UT)
!
! Outputs (files):
!   - edens.dat: electron densities from transmitter along given azimuth (from 60km to 560km altitude over 2500km distance)\
!   - rays.dat: rays information: Number of steps, hour, azimuth, elevation, altitude, theta, group range, true range, refractive index, latitude, longitude
!   - ranges.dat: information on rays reaching the ground: Reflection altitude, theta, grp range, hour, azimuth, elevation, true range, latitude, longitude
!   - ionos.dat: information on rays reaching good aspect conditions: Reflection altitude, theta, grp range, hour, azimuth, elevation, true range, ground range, weights, refractive index
!
! ***********************************************************************************
! Author: S. de Larquier
! Version: 17-Oct-2011
! ***********************************************************************************
! ***********************************************************************************

    use constants
    use MPIutils
    implicit none
    real*4::    elev, azim, hour, hrbase, elev_0, azim_0, hour_0
    integer::   iaz, iel, ihr, nelev, nazim, nhour, nextday
    integer::   dhour, dazim, delev
    character:: filename*250
    character(len=80):: arg
! IRI
    real*4::    edensARR(500,500), edens
    real*4::    edensPOS(500,2), dip(500,2), edensTHT(500)
! Inputs
    type(prm):: params
! MPI
    integer::       hfrays, hfranges, hfedens, hfionos      ! File handles
    integer::       type_vec, type_param                ! New data types
    integer::       slice, ipar                 ! Misc.

    integer i,j,nrows
    parameter (nrows=500)


    ! Initialize MPI environment
    CALL MPI_INIT(code)
    time_init = MPI_WTIME ()
    CALL MPI_COMM_SIZE(MPI_COMM_WORLD, nprocs, code)
    CALL MPI_COMM_RANK(MPI_COMM_WORLD ,rank, code)

!   print*, 'Hello from rank ', rank, 'of ', nprocs

    ! Create new data types for writting to files
    CALL MPI_RAYTYPES_INIT(type_vec, type_param)
    CALL MPI_TYPE_SIZE(MPI_REAL, mpi_size_real, code)
    CALL MPI_TYPE_SIZE(MPI_INTEGER, mpi_size_int, code)
    CALL MPI_TYPE_SIZE(type_vec, mpi_size_vec, code)

    ! Read parameters
    params%edens_file = "NONE"
    if (rank.eq.0) then 
        CALL READ_INP(params)
        print*, params
    endif
    ! Bcast parameters
    CALL MPI_BCAST(params, 1, type_param, 0, MPI_COMM_WORLD, code)

    ! Creates output files
    filename = trim(params%outdir)//"rays."//trim(params%filext)//".dat"
    CALL MPI_FILE_OPEN(MPI_COMM_WORLD, filename, &
        MPI_MODE_WRONLY + MPI_MODE_CREATE, MPI_INFO_NULL, hfrays, code)

    filename = trim(params%outdir)//"gscat."//trim(params%filext)//".dat"
    CALL MPI_FILE_OPEN(MPI_COMM_WORLD, filename, &
        MPI_MODE_WRONLY + MPI_MODE_CREATE, MPI_INFO_NULL, hfranges, code)

    filename = trim(params%outdir)//"iscat."//trim(params%filext)//".dat"
    CALL MPI_FILE_OPEN(MPI_COMM_WORLD, filename, &
        MPI_MODE_WRONLY + MPI_MODE_CREATE, MPI_INFO_NULL, hfionos, code)

    filename = trim(params%outdir)//"edens."//trim(params%filext)//".dat"
    CALL MPI_FILE_OPEN(MPI_COMM_WORLD, filename, &
        MPI_MODE_WRONLY + MPI_MODE_CREATE, MPI_INFO_NULL, hfedens, code)


    ! Write initial run settings
    nelev = nint((params%elevend - params%elevbeg)/params%elevstp)+1
    nazim = nint((params%azimend - params%azimbeg)/params%azimstp)+1
    nhour = nint((params%hourend - params%hourbeg)/params%hourstp)+1
    if (params%hourend.lt.params%hourbeg) then
        nhour = nint((24. - params%hourbeg + params%hourend)/params%hourstp)+1
    endif
    if (params%hourend.eq.params%hourbeg) nhour = nint(24./params%hourstp)+1
    if (rank.eq.0) then
        CALL MPI_FILE_WRITE_SHARED(hfrays, (/nhour, nazim, nelev/), 3, MPI_INTEGER, status, code)
        CALL MPI_FILE_WRITE_SHARED(hfrays, params, 1, type_param, status, code)
        CALL MPI_FILE_WRITE_SHARED(hfedens, (/nhour, nazim, nelev/), 3, MPI_INTEGER, status, code)
        CALL MPI_FILE_WRITE_SHARED(hfedens, params, 1, type_param, status, code)
        CALL MPI_FILE_WRITE_SHARED(hfranges, (/nhour, nazim, nelev/), 3, MPI_INTEGER, status, code)
        CALL MPI_FILE_WRITE_SHARED(hfranges, params, 1, type_param, status, code)
        CALL MPI_FILE_WRITE_SHARED(hfionos, (/nhour, nazim, nelev/), 3, MPI_INTEGER, status, code)
        CALL MPI_FILE_WRITE_SHARED(hfionos, params, 1, type_param, status, code)
    endif


    ! Select which of the loops should be parallelized
    dhour = 1
    dazim = 1
    delev = 1
    if (nhour.ge.nprocs) then
        slice = ceiling(real(nhour)/nprocs)
        nhour = slice
        dhour = nprocs
        hour_0 = rank*params%hourstp + params%hourbeg
        azim_0 = params%azimbeg
        elev_0 = params%elevbeg
    else if (nazim.ge.nprocs) then
        slice = ceiling(real(nazim)/nprocs)
        nazim = slice
        dazim = nprocs
        hour_0 = params%hourbeg
        azim_0 = rank*params%azimstp + params%azimbeg
        elev_0 = params%elevbeg
    else if (nelev.ge.nprocs) then
        slice = ceiling(real(nelev)/nprocs)
        nelev = slice
        delev = nprocs
        hour_0 = params%hourbeg
        azim_0 = params%azimbeg
        elev_0 = rank*params%elevstp + params%elevbeg
    else
        print*, 'Not enough calculations to parallelize...'
        hour_0 = params%hourbeg
        azim_0 = params%azimbeg
        elev_0 = params%elevbeg
    endif

    ! Determine if hours are in LT or UT
    if (params%hourbeg.ge.25.) then
        hrbase = 49.
    else
        hrbase = 24.
    endif


    WRITE(*,"('Rank ',i2,' of ',i2,':: ',i4,i4,i4,i4)") rank, nprocs, nhour, nazim, nelev, slice
    !**********************************************************
    ! Time loop
    nextday = 0
    hour = hour_0
    do ihr=1,nhour
        if (hour.gt.params%hourend) exit
!        print*, rank, 'hour',hour
        timeaz = MPI_WTIME()
        !**********************************************************
        ! Azimuth loop
        azim = azim_0
        do iaz=1,nazim
            if (azim.gt.params%azimend) exit
!            print*, rank, 'azim',hour,azim
            ! Generate electron density background

            if (trim(params%edens_file).eq."NONE") then
                CALL IRI_ARR(params, hour, azim, edensARR, edensPOS, edensTHT, dip)
!                open(unit=9,file='/home/w2naf/code/raytrace/edens_fort.txt')
!                do i=1,nrows
!                    write(9,*) edensARR(i,:)
!                end do
!                close(9)
            else
                CALL LOAD_BEAM_PROFILE(params, edensARR, edensPOS, edensTHT, dip)
!                open(unit=9,file='/home/w2naf/code/raytrace/edens_fort_py.txt')
!                do i=1,nrows
!                    write(9,*) edensARR(i,:)
!                end do
!                close(9)
            end if


            CALL MPI_FILE_WRITE_SHARED(hfedens, (/hour, azim, &
!                                            edensPOS(::2,:), &
                                            edensTHT(::2), &
                                            edensARR(::2,::2), &
                                            dip(::2,:)/), 2+253*250, MPI_REAL, status, code)

            timeel = MPI_WTIME()
            !**********************************************************
            ! Elevation loop
            elev = elev_0
            do iel=1,nelev
                if (elev.gt.params%elevend) exit
!                print*, rank, 'elev',hour,azim,elev
                    CALL TRACE_RKCK(params, hour, azim, elev, edensARR, edensTHT, dip, hfrays, hfranges, hfionos, &
                                mpi_size_int, mpi_size_real)

                ! Increment elevation value
                elev = elev + delev*params%elevstp
                if (elev.gt.params%elevend) elev = params%elevend
            enddo
            ! End elevation loop
            !**********************************************************
!            timeel = ( MPI_WTIME() - timeel)
!            CALL MPI_REDUCE (timeel,time,1, MPI_DOUBLE_PRECISION , MPI_MAX ,0, MPI_COMM_WORLD ,code)
!            print('("Time in elev loop ",I3," (rank ",I3,"): ",f6.3, " s")'), iaz, rank, timeel

            ! Increment azimuth value
            azim = azim + dazim*params%azimstp
            if (azim.gt.max(params%azimbeg,params%azimend)) azim = params%azimend
            if (azim.lt.min(params%azimbeg,params%azimend)) azim = params%azimend
        enddo
        ! End azimuth loop
        !**********************************************************
!        timeaz = ( MPI_WTIME() - timeaz)
!        CALL MPI_REDUCE (timeaz,time,1, MPI_DOUBLE_PRECISION , MPI_MAX ,0, MPI_COMM_WORLD ,code)
!        print('("Time in azim loop ",I3," (rank ",I3,"): ",f10.3, " s")'), ihr, rank, timeaz

        ! Increment time value (but if a process reaches the last value, don't let him go over it)
        hour = hour + dhour*params%hourstp
        ! If hour goes to the next day, then asjust accordingly
        if (hour.ge.hrbase) then
!            hour = hour - 24.
!            params%mmdd = params%mmdd + 1
            nextday = 1
        endif
        if (nextday.eq.1.and.hour.gt.params%hourend) hour = params%hourend
    enddo
    ! End time loop
    !**********************************************************

    ! Sync
    CALL MPI_BARRIER(MPI_COMM_WORLD, code)


    ! Close MPI files
    CALL MPI_FILE_CLOSE(hfrays, code)
    CALL MPI_FILE_CLOSE(hfranges, code)
    CALL MPI_FILE_CLOSE(hfionos, code)
    CALL MPI_FILE_CLOSE(hfedens, code)


    ! Free new data types
    CALL MPI_RAYTYPES_FREE(type_vec, type_param)


    ! Time of computation
    time_end = ( MPI_WTIME() - time_init)
    CALL MPI_REDUCE (time_end,time,1, MPI_DOUBLE_PRECISION , MPI_MAX ,0, MPI_COMM_WORLD ,code)
    if (rank.eq.0) print('("Time in fortran code: ",f10.3, " s")'), time


    ! Initialize MPI environment
    CALL MPI_FINALIZE(code)

end program


! *************************************************************************
! Creates MPI data types specific to ray tracing stuff
! *************************************************************************
SUBROUTINE MPI_RAYTYPES_INIT(type_vec, type_param)

    use MPIutils
    use constants
    implicit none
    integer,intent(out)::   type_vec, type_param        ! New data types

    integer::                                           i
    type(prm)::                                         tparams
    integer,dimension(4)::                              types, lblocks
    integer(kind=MPI_ADDRESS_KIND),dimension(4)::       disp, addr

    ! 500 element vector
    CALL MPI_TYPE_CONTIGUOUS(500, MPI_REAL, type_vec, code)
    CALL MPI_TYPE_COMMIT(type_vec, code)

    ! Parameters type
    types = (/MPI_REAL, MPI_INTEGER, MPI_REAL, MPI_CHAR/)
    lblocks = (/9, 3, 5, 510/)

    CALL MPI_GET_ADDRESS(tparams%txlat, addr(1), code)
    CALL MPI_GET_ADDRESS(tparams%nhop, addr(2), code)
    CALL MPI_GET_ADDRESS(tparams%hourbeg, addr(3), code)
    CALL MPI_GET_ADDRESS(tparams%filext, addr(4), code)

    do i=1,4
        disp(i) = addr(i) - addr(1)
    end do

    CALL MPI_TYPE_CREATE_STRUCT(4, lblocks, disp, types, type_param, code)
    CALL MPI_TYPE_COMMIT(type_param, code)

END SUBROUTINE MPI_RAYTYPES_INIT


! *************************************************************************
! Creates MPI data types specific to ray tracing stuff
! *************************************************************************
SUBROUTINE MPI_RAYTYPES_FREE(type_vec, type_param)

    use MPIutils
    implicit none
    integer,intent(out)::   type_vec, type_param        ! New data types

    CALL MPI_TYPE_FREE(type_vec, code)
    CALL MPI_TYPE_FREE(type_param, code)

END SUBROUTINE MPI_RAYTYPES_FREE


! *************************************************************************
! Reads input file for ray-tracing
! *************************************************************************
SUBROUTINE READ_INP(params)

    use constants
    implicit none
    type(prm),intent(out)::             params
    character(len=250)::                 filename
    character*250:: edens_file

    CALL getarg(1, filename)
    CALL getarg(2, params%outdir)
    CALL getarg(3, params%filext)

    print*, 'Input file: ', filename
    print*, 'Output directory: ', params%outdir
    print*, 'File extension: ', params%filext

    ! Skip first 2 lines
    open(10, file=filename, status='old')

    ! Read settings
    read(10, 100) params%txlat
    read(10, 100) params%txlon
    read(10, 100) params%azimbeg
    read(10, 100) params%azimend
    read(10, 100) params%azimstp
    read(10, 100) params%elevbeg
    read(10, 100) params%elevend
    read(10, 100) params%elevstp
    read(10, 100) params%freq
    read(10, 101) params%nhop
    read(10, 101) params%year
    read(10, 101) params%mmdd
    read(10, 100) params%hourbeg
    read(10, 100) params%hourend
    read(10, 100) params%hourstp
    read(10, 100) params%hmf2
    read(10, 100) params%nmf2
    read(10, 102) params%indir
    read(10, 102,end=200) params%edens_file

 100  format(F8.2)
 101  format(I8)
 102  format(A250)

 200  close(10)

END SUBROUTINE READ_INP


! *************************************************************************
! Ray-tracing subroutine: computes new ray position and elevation with an
! adaptative stepsize Runge-Kutta method
! The error is calculated on Q only for simplicity
! *************************************************************************
SUBROUTINE TRACE_RKCK(params, rayhour, rayazim, rayelev, edensARR, edensTHT, dip, hfrays, hfranges, hfionos, &
                        mpi_size_intin, mpi_size_realin)

  use constants
  use MPIutils
  implicit none
  type(prm),intent(in)::      params
  real*4,intent(in)::         rayelev, rayazim, rayhour
  real*4,intent(in)::         edensARR(500,500), edensTHT(500), dip(500,2)
  integer,intent(in)::        hfrays, hfranges, hfionos, mpi_size_intin, mpi_size_realin

  real*4::        latiin, longiin, latiout, longiout
  real*4::        edens, edensUP, vedens, nr2, dnr2dr, edensMax
  real*4::        r, Q, theta, rtmp, Qtmp, thetatmp
  real*4::        Qk(6), rk(6), thetak(6)
  real*4::        err, h, htmp, Qerr, Qscal
  real*4::        grpran, ranelev, rrefl
  real*4::        sina, sinb, d
  real*4::        asp_alt, asp_theta, asp_grpran, asp_ran, asp_w, aspect
  integer::       ihop, nrstep, istep, aspectind, n, naspstep

  ! Arrays for saving ray parameters
  real*4,dimension(5000)::    rsave, thsave, grpsave, nrsave ! ransave, 
  real*4,dimension(8)::       ranout
  real*4,dimension(9,5000)::  ionosout

  real*4,parameter::      alti = 0.           ! initial altitude [_km]
  real*4,parameter::      htry = 10000.       ! initial step size [_m]
  real*4,parameter::      eps = 1e-3          ! desired accuracy for the RKF integration
  real*4,parameter::      pgrow = -0.2        ! growth exponent when step size too small
  real*4,parameter::      pshrink = -0.25     ! shrink exponent when step size too large
  real*4,parameter::      Safety = 0.9        ! Safety parameter for step adjustments

  ! Find max electron density
  edensMax = maxval(edensARR)

  ! Pass mpi size values to local variable
  mpi_size_int = mpi_size_intin
  mpi_size_real = mpi_size_realin

  ! Initialize r, theta and Q (ref: Coleman, Radio Sci., 33(4), 1187-1197, 1998)
  r = (Rav + alti)*1e3
  theta = 0.
  Q = sin(rayelev*dtor)
  ! Initialize step size
  h = htry
  ! Initialize group range
  grpran = 0.
  ! Initialize current elevation
  ranelev = rayelev
  ! Initialize reflection altitude
  rrefl = 0.
  ! Initialize refractive index
  nr2 = 1.
  dnr2dr = 0.

  ! Save to arrays
  rsave(1) = r
  thsave(1) = theta
  grpsave(1) = grpran
!  ransave(1) = grpran
  nrsave(1) = sqrt(nr2)

  ! Initialize position
  latiout = params%txlat
  longiout = params%txlon


  ! Loops until ray describes the desired number of hops
  ihop = 0        ! hop counter
  nrstep = 2      ! number of steps per ray counter
  naspstep = 1    ! number of ionospheric scatter occurence counter
  do while (ihop.lt.params%nhop.and.r.lt.(Rav + 500.)*1e3.and.theta.lt.edensTHT(500).and.r.ge.Rav*1e3.and.nrstep.lt.5000)
    ! Current position
    latiin = latiout
    longiin = longiout
    ! Resets error
    err = 10.

    do while (err.gt.1.)
    ! Adaptative step Runge-Kutta method (Cash-Karp)
      ! Initialize derivatives
      call DERIV(r, theta, Q, nr2, dnr2dr, rk(1), thetak(1), Qk(1))


      ! ********** 1st step
      Qtmp = Q + h*b2(1)*Qk(1)
      rtmp = r + h*b2(1)*rk(1)
      thetatmp = theta + h*b2(1)*thetak(1)
      ! Updates current elevation
      if ((thetatmp-theta).eq.0.) thetatmp = theta + h / r
      ranelev = asin( (rtmp*cos(thetatmp-theta) - r) / h)*radeg
      ! Calculate new position, index of refraction, and index gradient
      CALL CALC_INDEX(thetatmp, edensTHT, edensARR, rayazim, params%freq, rtmp, ranelev, h, &
                                      nr2, dnr2dr)
      ! Calculate derivatives
      call DERIV(rtmp, thetatmp, Qtmp, nr2, dnr2dr, rk(2), thetak(2), Qk(2))


      ! ********** 2nd step
      Qtmp = Q + h*(b3(1)*Qk(1) + b3(2)*Qk(2))
      rtmp = r + h*(b3(1)*rk(1) + b3(2)*rk(2))
      thetatmp = theta + h*(b3(1)*thetak(1) + b3(2)*thetak(2))
      ! Updates current elevation
      if ((thetatmp-theta).eq.0.) thetatmp = theta + h / r
      ranelev = asin( (rtmp*cos(thetatmp-theta) - r) / h)*radeg
      ! Calculate new position, index of refraction, and index gradient
      CALL CALC_INDEX(thetatmp, edensTHT, edensARR, rayazim, params%freq, rtmp, ranelev, h, &
                                      nr2, dnr2dr)
      ! Calculate derivatives
      call DERIV(rtmp, thetatmp, Qtmp, nr2, dnr2dr, rk(3), thetak(3), Qk(3))


      ! ********** 3rd step
      Qtmp = Q + h*(b4(1)*Qk(1) + b4(2)*Qk(2) + b4(3)*Qk(3))
      rtmp = r + h*(b4(1)*rk(1) + b4(2)*rk(2) + b4(3)*rk(3))
      thetatmp = theta + h*(b4(1)*thetak(1) + b4(2)*thetak(2) + b4(3)*thetak(3))
      ! Updates current elevation
      if ((thetatmp-theta).eq.0.) thetatmp = theta + h / r
      ranelev = asin( (rtmp*cos(thetatmp-theta) - r) / h)*radeg
      ! Calculate new position, index of refraction, and index gradient
      CALL CALC_INDEX(thetatmp, edensTHT, edensARR, rayazim, params%freq, rtmp, ranelev, h, &
                                      nr2, dnr2dr)
      ! Calculate derivatives
      call DERIV(rtmp, thetatmp, Qtmp, nr2, dnr2dr, rk(4), thetak(4), Qk(4))


      ! ********** 4th step
      Qtmp = Q + h*(b5(1)*Qk(1) + b5(2)*Qk(2) + b5(3)*Qk(3) + b5(4)*Qk(4))
      rtmp = r + h*(b5(1)*rk(1) + b5(2)*rk(2) + b5(3)*rk(3) + b5(4)*rk(4))
      thetatmp = theta + h*(b5(1)*thetak(1) + b5(2)*thetak(2) + b5(3)*thetak(3) + b5(4)*thetak(4))
      ! Updates current elevation
      if ((thetatmp-theta).eq.0.) thetatmp = theta + h / r
      ranelev = asin( (rtmp*cos(thetatmp-theta) - r) / h)*radeg
      ! Calculate new position, index of refraction, and index gradient
      CALL CALC_INDEX(thetatmp, edensTHT, edensARR, rayazim, params%freq, rtmp, ranelev, h, &
                                      nr2, dnr2dr)
      ! Calculate derivatives
      call DERIV(rtmp, thetatmp, Qtmp, nr2, dnr2dr, rk(5), thetak(5), Qk(5))


      ! ********** 5th step
      Qtmp = Q + h*(b6(1)*Qk(1) + b6(2)*Qk(2) + b6(3)*Qk(3) + b6(4)*Qk(4) + b6(5)*Qk(5))
      rtmp = r + h*(b6(1)*rk(1) + b6(2)*rk(2) + b6(3)*rk(3) + b6(4)*rk(4) + b6(5)*rk(5))
      thetatmp = theta + h*(b6(1)*thetak(1) + b6(2)*thetak(2) + b6(3)*thetak(3) + b6(4)*thetak(4) + b6(5)*thetak(5))
      ! Updates current elevation
      if ((thetatmp-theta).eq.0.) thetatmp = theta + h / r
      ranelev = asin( (rtmp*cos(thetatmp-theta) - r) / h)*radeg
      ! Calculate new position, index of refraction, and index gradient
      CALL CALC_INDEX(thetatmp, edensTHT, edensARR, rayazim, params%freq, rtmp, ranelev, h, &
                                      nr2, dnr2dr)
      ! Calculate derivatives
      call DERIV(rtmp, thetatmp, Qtmp, nr2, dnr2dr, rk(6), thetak(6), Qk(6))


      ! ********** 6th steps
      Qtmp = Q + h*(ci(1)*Qk(1) + ci(2)*Qk(2) + ci(3)*Qk(3) + ci(4)*Qk(4) + ci(5)*Qk(5) + ci(6)*Qk(6))
      rtmp = r + h*(ci(1)*rk(1) + ci(2)*rk(2) + ci(3)*rk(3) + ci(4)*rk(4) + ci(5)*rk(5) + ci(6)*rk(6))
      thetatmp = theta + h*(ci(1)*thetak(1) + ci(2)*thetak(2) + ci(3)*thetak(3) + &
          ci(4)*thetak(4) + ci(5)*thetak(5) + ci(6)*thetak(6))


      ! ********** Error calculation
      Qerr = h*(dci(1)*Qk(1) + dci(2)*Qk(2) + dci(3)*Qk(3) + dci(4)*Qk(4) + dci(5)*Qk(5) + dci(6)*Qk(6))
      ! Calculates reference vector for error adjustment
      Qscal = sqrt(nr2)*(rtmp - r)/h
      ! error
      if (Qscal.eq.0.) then
          err = 0.
      else
          err = abs(Qerr/Qscal)/eps
      endif
      ! If error too large, reduce step size and restart
      if (err.gt.1.) then
          htmp = Safety*h*err**pshrink
          ! no less than a 1m step (which is already an overkill)
          h = max(htmp, 1.)
      endif
    enddo

    ! If ray reaches reflection point
    if (rtmp-r.le.0..and.rtmp-rrefl.ge.0.) rrefl = rtmp

    ! If ray reaches the ground (or passses through it)
    if (rtmp*1e-3.le.Rav) then
      ! calculates theta intercepting ground
      sina = rtmp*sin(thetatmp-theta)/h
      sinb = r*sina/(Rav*1e3)
      thetatmp = theta + (pi - asin(sina) - (pi - asin(sinb)))

      ! local elevation angle
      ranelev = asin( (rtmp*cos(thetatmp-theta) - r) / h)*radeg

      ! Re-evaluate h, rtmp and Qtmp for new thetatmp
      h = Rav*1e3*sin(thetatmp-theta)/sina
      rtmp = Rav*1e3
      Qtmp = sin(pi/2.-asin(sina))

      ! Calculate new position
      call CALC_POS(latiin, longiin, r*1e-3-Rav, rayazim, h*1e-3, ranelev, latiout, longiout)

      ! Write to file
      ! Reflection altitude, theta, grp range, hour, azimuth, elevation, true range, latitude, longitude
      ranout = (/rayhour, rayazim, rayelev, rrefl, thetatmp, grpran+h, latiout, longiout/) ! , (ransave(nrstep-1) + sqrt(nr2)*h)
      CALL MPI_FILE_WRITE_SHARED(hfranges, ranout, 8, MPI_REAL, status, code)
      ! Counts number of hops
      ihop = ihop + 1

      ! resets reflection altitude
      rrefl = 0.
    endif

    ! Updates group range
    grpran = grpran + h

    ! Updates current elevation
    ranelev = asin( (rtmp*cos(thetatmp-theta) - r) / h)*radeg

    ! Calculate new position, index of refraction, and index gradient
    CALL CALC_INDEX(thetatmp, edensTHT, edensARR, rayazim, params%freq, rtmp, ranelev, h, &
                                    nr2, dnr2dr)

    ! Search current ray step for good aspect conditions
    if (grpran.gt.180e3.and.rtmp*1e-3.gt.(Rav+90.)) then
      CALL CALC_ASPECT(edensTHT, dip, rayazim, theta, thetatmp, r, rtmp, aspectind, aspect)
      if (aspectind.gt.0) then
        ! Calculate mean range
        d = r/rtmp*h*sin(edensTHT(aspectind) - theta)/sin(thetatmp-theta)
        asp_grpran = grpran + h/2.
        ! Calculate mean slant range
!        asp_ran = ransave(nrstep-1) + h/2.*sqrt(nr2)
        ! Calculate mean ground range
        asp_theta = (thetatmp-theta)/2. + theta
        ! Calculate mean altitude
        asp_alt = sqrt( h**2./4. + r**2. + h/2.*r*sin(ranelev) )
        ! Calculate weighing (to account for backsground electron density and deviation from perfect aspect conditions)
        asp_w = ( edensARR(nint(((rtmp-r)/2.+r)*1e-3 - 60. - Rav), aspectind) )**2. / asp_grpran**3.

        ! Write to file
        ! Reflection altitude, theta, grp range, true range, weights, refractive index, latitude, longitude, aspect
        ionosout(1:9,naspstep) = (/asp_alt, asp_theta, asp_grpran, ranelev, asp_w, sqrt(nr2), latiin, longiin, h/)
        naspstep = naspstep + 1
      endif
      ! Resets aspect indices
      aspectind = 0
    endif

    ! Passes new values
    Q = Qtmp
    r = rtmp
    theta = thetatmp

    ! Calculate new position
    call CALC_POS(latiin, longiin, r*1e-3-Rav, rayazim, h*1e-3*sqrt(nr2), ranelev, latiout, longiout)

    ! Save to arrays
    rsave(nrstep) = r
    thsave(nrstep) = theta
    grpsave(nrstep) = grpran
!    ransave(nrstep) = ransave(nrstep-1) + sqrt(nr2)*h
    nrsave(nrstep) = sqrt(nr2)

    ! Calculates new step size (bigger)
    if (err.gt.(5./Safety)**(1./pgrow)) then
        h = Safety*h*err**pgrow
    else
        h = 5.*h
    endif
    h = min(h, 10e3)
    nrstep = nrstep + 1
  enddo

  ! Write ray parameters to file
  ! Number of steps, hour, azimuth, elevation, altitude, theta, group range, true range, refractive index, latitude, longitude
  CALL MPI_FILE_WRITE_SHARED(hfrays, (/real(nrstep-1), &
                                      rayhour, rayazim, rayelev, &
                                      (rsave(n),n=1,nrstep-1), &
                                      (thsave(n),n=1,nrstep-1), &
                                      (grpsave(n),n=1,nrstep-1), &
!                                      (ransave(n),n=1,nrstep-1), &
                                      (nrsave(n),n=1,nrstep-1)/), 1 + 3 + 4*(nrstep-1), MPI_REAL, status, code)

  ! Write ionospheric scatter to file
  ! Number of scatter, hour, azimuth, elevation, altitude, theta, grp range, true range, weights, refractive index, latitude, longitude, aspect
  CALL MPI_FILE_WRITE_SHARED(hfionos, (/real(naspstep-1), &
                                      rayhour, rayazim, rayelev, &
                                      (ionosout(1,n),n=1,naspstep-1), &
                                      (ionosout(2,n),n=1,naspstep-1), &
                                      (ionosout(3,n),n=1,naspstep-1), &
                                      (ionosout(4,n),n=1,naspstep-1), &
                                      (ionosout(5,n),n=1,naspstep-1), &
                                      (ionosout(6,n),n=1,naspstep-1), &
                                      (ionosout(7,n),n=1,naspstep-1), &
                                      (ionosout(8,n),n=1,naspstep-1), &
                                      (ionosout(9,n),n=1,naspstep-1)/), 1 + 3 + 9*(naspstep-1), MPI_REAL, status, code)

END SUBROUTINE TRACE_RKCK


! *************************************************************************
! Calculates derivatives of r, theta and Q
! (ref: Coleman, Radio Sci., 33(4), 1187-1197, 1998)
! *************************************************************************
SUBROUTINE DERIV(r, theta, Q, nr2, dnr2dr, drdp, dthetadp, dQdp)

    implicit none
    real*4,intent(in):: r, theta, Q, nr2, dnr2dr
    real*4,intent(out):: drdp, dthetadp, dQdp

    drdp = Q
    dthetadp = SQRT(nr2 - Q**2.)/r
    dQdp = 1./2.*dnr2dr + (nr2 - Q**2.)/r

END SUBROUTINE DERIV


! *************************************************************************
! Calculates refractive index and its vertical gradient at a given ray point
! *************************************************************************
SUBROUTINE CALC_INDEX(tht, edensTHT, edensARR, azim, freq, r, elev, h, &
                        nr2, dnr2dr)

    use constants
    implicit none
    real*4,intent(in)::     tht, r, azim, freq, h
    real*4,intent(in)::     edensARR(500,500), edensTHT(500)
    real*4,intent(out)::    nr2, dnr2dr

    real*4::                edens, edensUP, vedens, elev, Bvec(2), dip(500,2)

    ! Finds electron density at current position
    call IRI_INTERP(tht, r*1e-3-Rav, edensTHT, edensARR, edens)
    call IRI_INTERP(tht, r*1e-3-Rav+1., edensTHT, edensARR, edensUP)

    ! Calculates gradient
    vedens = (edensUP-edens)/1e3

    ! Calculates refractive index (sqaured) with Appleton-Hartree formula (no field, no colisions)
    nr2 = (1. - 80.5e-12*edens/(freq**2.))

    ! Calculates vertical gradient of the square of the refractive index
    dnr2dr = -80.5e-12/(freq**2.)*vedens

!   print*,'CALC_INDEX', tht*radeg, (r*1e-3 - Rav), edens, edensUP, nr2, dnr2dr



END SUBROUTINE CALC_INDEX


! *************************************************************************
! Calculates new position for a given path distance, elevation angle and azimuth.
! Input and output positions are in degrees
! *************************************************************************
SUBROUTINE CALC_POS(lati, longi, alti, azim, dist, elev, latiout, longiout)

    use constants
    implicit none
    real*4,intent(in)::         lati, longi, alti, dist, azim, elev
    real*4,intent(out)::        latiout, longiout

    real*4::    Re, glat, glon, rho, gaz, gel
    real*4::    rx, ry, rz, sx, sy, sz, tx, ty, tz
    real*4::    coslat, sinlat, coslon, sinlon, tlat, tlon

! use temp variable to store latitude and longitude
    tlat = lati
    tlon = longi

! Converts from geodetic to geocentric and find Earth radius
    CALL CALC_GD2GC(1, tlat, tlon, Re, glat, glon)

! Adjusts azimuth and elevation for the oblateness of the Earth
    CALL CALC_AZEL(tlat, tlon, azim, elev, gaz, gel)

! Pre-calculate sin and cos of lat and lon
    coslat = cos(glat*dtor)
    sinlat = sin(glat*dtor)
    coslon = cos(glon*dtor)
    sinlon = sin(glon*dtor)

! Convert from glabal spherical to global cartesian
    rx = (Re + alti) * coslat * coslon
    ry = (Re + alti) * coslat * sinlon
    rz = (Re + alti) * sinlat

! Convert from local spherical to local cartesian
    sx = -dist * cos(gel*dtor) * cos(gaz*dtor)
    sy = dist * cos(gel*dtor) * sin(gaz*dtor)
    sz = dist * sin(gel*dtor)

! Convert from local cartesian to global cartesian
    tx = sinlat * sx + coslat * sz
    ty = sy
    tz = -coslat * sx + sinlat * sz
    sx = coslon * tx - sinlon * ty
    sy = sinlon * tx + coslon * ty
    sz = tz

! Add vectors in global cartesian system
    tx = rx + sx
    ty = ry + sy
    tz = rz + sz

! Convert from global cartesian to global spherical
    rho = sqrt( tx**2. + ty**2. + tz**2. )
    glat = 90. - acos(tz/rho)*radeg
    glon = atan2(ty, tx)*radeg

! Compute geodetic coordinates and Earth radius at new point
    CALL CALC_GD2GC(-1, latiout, longiout, Re, glat, glon)

END SUBROUTINE CALC_POS


! *************************************************************************
! Converts between geocentric coordinates and geodetic (World Geodetic System 1984 (WGS84))
! iopt: -1, geocentric to geodetic
!           +1, geodetic to geocentric
! *************************************************************************
SUBROUTINE CALC_GD2GC(iopt, gdlat, gdlon, rho, glat, glon)

    use constants
    implicit none
    integer,intent(in)::        iopt
    real*4,intent(inout)::      gdlat, gdlon, glat, glon
    real*4,intent(out)::        rho

    real*4::                    b, e2

! semi-minor axis (polar radius)
    b = a*(1. - f)

! first eccentricity squared
    e2 = a**2./b**2. - 1.

! geodetic to geocentric
    if (iopt.eq.1) then
        glat = atan( b**2./a**2. * tan(gdlat*dtor) ) * radeg
        glon = gdlon
        if (glon.gt.180.)  glon = glon - 360.
! geocentric to geodetic
    else if (iopt.eq.-1) then
        gdlat = atan( a**2./b**2. * tan(glat*dtor) ) * radeg
        gdlon = glon
    else
        print*, 'CALC_GD2GC: wrong argument iopt = ', iopt
    endif

! calculate Earth radius at point (uses geocentric latitude)
    rho = a / sqrt( 1. + e2*sin(glat*dtor)**2. )

END SUBROUTINE CALC_GD2GC


! *************************************************************************
! Calculates azimuth and elevation for oblate Earth.
! Input and output positions are in degrees
! *************************************************************************
SUBROUTINE CALC_AZEL(lati, longi, azim, elev, gaz, gel)

    use constants
    implicit none
    real*4,intent(in)::         lati, longi, azim, elev
    real*4,intent(out)::        gaz, gel

    real*4::    Re, glat, glon, del, tlat, tlon
    real*4::    kxg, kyg, kzg, kxr, kyr, kzr

! use temp variable to store latitude and longitude
    tlat = lati
    tlon = longi

! Converts from geodetic to geocentric and find Earth radius
    CALL CALC_GD2GC(1, tlat, tlon, Re, glat, glon)
    del = tlat - glat

! Ray k-vector
    kxg = cos(elev*dtor) * sin(azim*dtor)
    kyg = cos(elev*dtor) * cos(azim*dtor)
    kzg = sin(elev*dtor)

! Correction to the k-vector due to oblateness
    kxr = kxg
    kyr = kyg * cos(del*dtor) + kzg * sin(del*dtor)
    kzr = -kyg * sin(del*dtor) + kzg * cos(del*dtor)

! Finally compute corrected elevation and azimuth
    gaz = atan2(kxr,kyr) * radeg
    gel = atan(kzr / sqrt(kxr**2. + kyr**2.) ) * radeg

END SUBROUTINE CALC_AZEL


! *************************************************************************
! Calculates aspect angle and determines if it satisfies reflection conditions
! Calculations are performed in the propagation plane with:
! - Z axis directed upward.
! - X axis in the direction of propagation,
!   tangential to the Earth at current position.
! *************************************************************************
SUBROUTINE CALC_ASPECT(edensTHT, dip, azim, stht, ftht, salt, falt, aspind, aspect)

    use constants
    implicit none
    real*4,intent(in)::     edensTHT(500), dip(500,2)
    real*4,intent(in)::     azim, stht, ftht, salt, falt
    integer,intent(out)::   aspind
    real*4,intent(out)::    aspect

    real*4::    kx, kz, kvec, Bx, Bz
    real*4::    midtht, diff, middip, middec
    integer::   temp(1)

    ! Calculate k vector for current ray step
    kx = falt*sin(ftht - stht)
    kz = falt*cos(ftht - stht) - salt
    kvec = sqrt(kx**2. + kz**2.)

    ! Middle of the step: position and index in B grid
    midtht = (ftht-stht)/2. + stht
    temp = minloc(abs(edensTHT - midtht))
    aspind = temp(1)

    ! Dip and declination at this position
    temp = dip(aspind,1)
    middip = temp(1)
    temp = dip(aspind,2)
    middec = temp(1)

    ! calculate vector magnetic field
    Bx = cos(-middip*dtor) * cos(azim*dtor - middec*dtor)
    Bz = sin(-middip*dtor)

    ! calculate cosine of aspect angle
    aspect = (Bx*kx + Bz*kz)/kvec

    if (abs(aspect).le.cos(pi/2. - 1.*dtor)) then
        aspect = acos(aspect)*radeg
    else
        aspind = -1
    endif

END SUBROUTINE CALC_ASPECT


! *************************************************************************
! Generates fixed arrays of electron densities along the azimuth path:
!   - from 60 to 560 km in 1km steps
!   - over 2500km surface distance in 5km steps
! *************************************************************************
SUBROUTINE LOAD_BEAM_PROFILE(params,edensARR, edensPOS, edensTHT, dip)
    use constants
    use MPI
    implicit none
    type(prm),intent(in)::                      params

    integer i,j,stat
    integer nrows
    parameter (nrows=500)
    character(100):: msg

    real*4,dimension(500,500),intent(out)::     edensARR
    real*4,dimension(500,2),intent(out)::       edensPOS, dip
    real*4,dimension(500),intent(out)::         edensTHT

    open(unit=73,file=trim(params%edens_file),form='unformatted',recl=4*nrows,access='direct')
    do i=1,500
    read(unit=73,iostat=stat,iomsg=msg,rec=i) (edensARR(i,j), j=1,nrows)
    end do

    read(unit=73,rec=501) (edensPOS(j,1), j=1,nrows)
    read(unit=73,rec=502) (edensPOS(j,2), j=1,nrows)

    read(unit=73,rec=503) (dip(j,1), j=1,nrows)
    read(unit=73,rec=504) (dip(j,2), j=1,nrows)

    read(unit=73,rec=505) (edensTHT(j), j=1,nrows)
    close(73)

END SUBROUTINE LOAD_BEAM_PROFILE

SUBROUTINE IRI_ARR(params, hour, azim, edensARR, edensPOS, edensTHT, dip)

    use constants
    use MPI
    implicit none
    real*4,intent(in)::                         azim, hour
    type(prm),intent(in)::                      params
    real*4,dimension(500,500),intent(out)::     edensARR
    real*4,dimension(500,2),intent(out)::       edensPOS, dip
    real*4,dimension(500),intent(out)::         edensTHT

    real*4::                    old_hour, vbeg, vend, vstp
    real*4::                    lonDeg, latDeg, thtmp
    integer::                   n, j
    logical::                   jf(50)
    real*4,dimension(100)::     oar
    real*4,dimension(20,1000):: outf
    real*4,dimension(500)::     dayNe

    integer i,stat
    integer nrows
    parameter (nrows=500)
    character(100):: msg
    character(250):: datapath

    datapath = params%indir
! Initialize position
    vbeg = 60.
    vend = 560.
    vstp = (vend-vbeg)/500.

    ! adjust to have latitude between -90 and 90
    edensPOS(1,1) = params%txlat
    IF(edensPOS(1,1).gt.90.OR.edensPOS(1,1).lt.-90)THEN
        edensPOS(1,1) = sign(modulo(-abs(edensPOS(1,1)), 90.), edensPOS(1,1))
    ENDIF
    ! adjust to have tongitude between 0 and 360E
    edensPOS(1,2) = params%txlon
    IF(edensPOS(1,2).lt.0)THEN
        edensPOS(1,2) = modulo(edensPOS(1,2), 360.)
    ENDIF
    edensTHT(1) = 0.

! Initialize call for IRI
    do n=1,50
       jf(n) = .true.
    enddo
    if (params%hmf2.gt.0.) then
        jf(9) = .false.
        oar(2) = params%hmf2
    endif
    if (params%nmf2.gt.0.) then
        jf(8) = .false.
        oar(1) = 10.**(params%nmf2)
    endif
    jf(2) = .false.               ! no temperatures
    jf(3) = .false.               ! no ion composition
    jf(5) = .false.               ! URSI foF2 model
    jf(6) = .false.               ! Newest ion composition model
    jf(21) = .false.              ! ion drift not computed
    jf(23) = .false.              ! Te topside (TBT 2011)
    jf(26) = .false.              ! no fof2 storm updating
    jf(29) = .false.              ! New Topside options
    jf(30) = .false.              ! NeQuick topside
    jf(33) = .false.               ! Do not calcultae auroral boundary
    jf(34) = .false.              ! Messages off
    jf(35) = .false.              ! no foE storm updating

! Calling IRI subroutine
    call IRI_SUB(jf,0,edensPOS(1,1),edensPOS(1,2),params%year,params%mmdd,hour, &
               vbeg,vend,vstp,outf,oar,datapath)

    do j=1,500
        edensARR(j,1) = outf(1,j)
    enddo
    dip(1,1) = oar(25)
    dip(1,2) = oar(27)

! Lat/lon loop
    do n=2,500
        ! Calculates new position after one step
!        call CALC_POS(edensPOS(n-1,1), edensPOS(n-1,2), 0., azim, 5., 0., &
!                edensPOS(n,1), edensPOS(n,2))

        call CALC_POS(edensPOS(1,1), edensPOS(1,2), 0., azim, (5.*(n-1)), 0., &
                edensPOS(n,1), edensPOS(n,2))

        edensTHT(n) = acos( cos(edensPOS(1,1)*PI/180.)*cos(edensPOS(n,1)*PI/180.)* &
                            cos((edensPOS(n,2) - edensPOS(1,2))*PI/180.) &
                    + sin(edensPOS(1,1)*PI/180.)*sin(edensPOS(n,1)*PI/180.))
        ! Calculates electron density and magnetic dip and dec at current position and time
        call IRI_SUB(jf,0,edensPOS(n,1),edensPOS(n,2),params%year,params%mmdd,hour, &
                   vbeg,vend,vstp,outf,oar,datapath)
        ! Altitude loop (pass output of IRI_SUB to the proper matrix)
        do j=1,500
            edensARR(j,n) = outf(1,j) 
        enddo
        dip(n,1) = oar(25)
        dip(n,2) = oar(27)
    ENDDO
END SUBROUTINE IRI_ARR


! *************************************************************************
! Interpolates electron densities at a given position
! *************************************************************************
SUBROUTINE IRI_INTERP(tht, alti, edensTHT, edensARR, edens)

    use constants
    implicit none
    real*4,intent(in)::                         tht, alti
    real*4,dimension(500),intent(in)::          edensTHT
    real*4,dimension(500,500),intent(in)::      edensARR
    real*4,intent(out)::                        edens

    integer::   vind, thtind, i
    real*4::    neazu, neazd
    real*4::    dtht, tdiff

    if(alti.lt.60.or.alti.gt.560.or.isnan(alti).or.isnan(tht))then
        edens = 0.
      return
    endif

! Look-up in table (vertical, latitudinal, longitudinal limits)
    vind = INT(alti-60.)+1
    thtind = 1
    do i=1,499
        dtht = edensTHT(i+1) - edensTHT(i)
        tdiff = tht - edensTHT(i)
        if (ABS(tdiff).lt.ABS(dtht)) then
            thtind = i
            EXIT
        endif
    enddo
    if (tht.gt.edensTHT(500)) then
        thtind = 499
    endif

!    print*, tht,alti,thtind, vind

    ! Bilinear interpolation
    neazu = (edensTHT(thtind+1) - tht)/(edensTHT(thtind+1) - edensTHT(thtind))*edensARR(vind+1,thtind) + &
         (tht - edensTHT(thtind))/(edensTHT(thtind+1) - edensTHT(thtind))*edensARR(vind+1,thtind+1)
    neazd = (edensTHT(thtind+1) - tht)/(edensTHT(thtind+1) - edensTHT(thtind))*edensARR(vind,thtind) + &
         (tht - edensTHT(thtind))/(edensTHT(thtind+1) - edensTHT(thtind))*edensARR(vind,thtind+1)
!   neazu = edensARR(vind+1,1)
!   neazd = edensARR(vind,1)
    edens = (alti - ((vind-1)*1.+60.))/1.*neazu + (vind*1.+60. - alti)/1.*neazd


END SUBROUTINE IRI_INTERP
