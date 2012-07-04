! Compute ionospheric conductivities from IRI+NRLMSIS models
! Conductivity formulas from Intro. to Space Physics, MG Kivelson and CT Russel p.201,
! and from Rishbeth and Garriott, Intro to Ionospheric Physics, p.136
! Collision frequency formulas from Rishbeth and Garriott, Intro to Ionospheric Physics, p.130
! 
! Written by S. de Larquier - Feb. 2011
program conductivities

    implicit none
    INTEGER               :: i
!     Constants
    REAL,PARAMETER        :: amu=1.66e-27,qe=1.60e-19,me=9.11e-31
    REAL,PARAMETER        :: Ahe=4.,Ao=16.,An2=28.,Ao2=32.,Aar=40.,An=14., Ah=1.
!     Inputs
    INTEGER               :: year,doy,hrut
    REAL                  :: glat,glon
!     Models inputs
    LOGICAL               :: jf(50)
    INTEGER               :: yyyy,iyd,dhour,yyddd
    REAL                  :: sec,stl,yeardec
    REAL                  :: f107,f107a,ap(7),xl,dipl,BNORTH,BEAST,BDOWN,BABS
    REAL                  :: hbeg,hend,hstep,alt
!     Models outputs
    REAL                  :: iriout(20,1000),iriarr(100)
    REAL                  :: msisDout(9),msisTout(2)
!     Parameters for conductivity calculations (electron, ions, neutrals)
    REAL(8),DIMENSION(500)   :: nel,Te,wce,nu_en
    REAL(8),DIMENSION(500)   :: mio,mio2,mino,mi
    REAL(8),DIMENSION(500)   :: nio,nio2,nino,ni,wci,nu_in
    REAL(8),DIMENSION(500)   :: no,nn2,no2,nar,nhe,nn,A,B0
!     Conductivity
    REAL(8)               :: sig0height(500),sig0int
    REAL(8)               :: sig1height(500),sig1int
    REAL(8)               :: sig2height(500),sig2int
    
! **************************************************************************************
! ************************** Input
! **************************************************************************************
! Read in year, day-of-year, hour UT, geographic latitude and longitude
!     print *,'Provide year(yyyy), day-of-year, hour(UT), latitude and longitude'
    read(*,*)yyyy,doy,hrut,glat,glon
    

! Correct longitude to have it in degrees East (IRI requirement)
    if (glon.lt.0.) then
			glon = glon + 360.
    endif


! **************************************************************************************
! ************************** IRI
! **************************************************************************************
! Prepare parameters for call to IRI
!   true/false switches
    jf = .true.	! All true
    jf(5) = .false.	! foF2 model
    jf(6) = .true.  ! Old models for ion composition, because the new ones do not work under 300 km altitude
    jf(12) = .false.	! no messages
    jf(21) = .false.
    jf(22) = .false.	! ion densities in m-3
    jf(23) = .false.
    jf(28) = .false.
    jf(29) = .false.
    jf(30) = .false.
    jf(33) = .false.              ! Do not calcultae auroral boundary
		jf(34) = .false.              ! Messages off
		jf(35) = .false.              ! no foE storm updating
!   Altitude range
    hbeg = 120.
    hend = 620.
    hstep = 1.
!   Call IRI
    call IRI_SUB(jf,0,glat,glon,yyyy,-doy,hrut+25.,hbeg,hend,hstep,iriout,iriarr)
!     print *,'------------IRI profile complete!'
    nel = iriout(1,1:500)
    Te = iriout(2,1:500)
    nio = iriout(5,1:500)
    nio2 = iriout(8,1:500)
    nino = iriout(9,1:500)
    
    
! **************************************************************************************
! ************************** NRL-MSIS
! **************************************************************************************
! Prepare parameters for call to NRLMSIS
    yyddd = yyyy*1000 + doy
    sec = hrut*3600.
    stl = sec/3600. + glon/15.
    f107 = iriarr(41)
    f107a = iriout(20,1)
    ap(1) = SUM(iriout(20,2:9))/8.
    ap(2:5) = iriout(20,2:5)
    ap(6) = SUM(iriout(20,6:12))/7.
    ap(7) = SUM(iriout(20,13:14))/2.
! Call NRL-MSIS
    call METERS(.TRUE.)
    alt = hbeg
    do i=1,500
			alt = alt + hstep
			call GTD7(yyddd,sec,alt,glat,glon,stl,f107a,f107,ap,48,msisDout,msisTout)
			nhe(i) = msisDout(1)
			no(i) = msisDout(2)
			nn2(i) = msisDout(3)
			no2(i) = msisDout(4)
			nar(i) = msisDout(5)
    enddo
!     print *,'------------NRL-MSIS profile complete!'
    
! **************************************************************************************
! ************************** IGRF
! **************************************************************************************
    yeardec = year + doy/365.25
    alt = hbeg
    do i=1,500
			alt = alt + hstep
			call FELDG(glat,glon,alt,BNORTH,BEAST,BDOWN,BABS)
			B0(i) = babs*1e-4
    enddo
    
! **************************************************************************************
! ************************** Pedersen conductivities
! **************************************************************************************
! Ion density
    ni = nio + nio2 + nino
! Neutral density
    nn = nhe + no + nn2 + no2 + nar
! ion mass (harmonic mean over NO+, O+, O2+)
		mi = ni/(nio/Ao/amu + nio2/Ao2/amu + nino/(An + Ao)/amu)
!     mi = (nio*Ao*amu + nio2*Ao2*amu + nino*(An + Ao)*amu)/ni
! neutral mean molecular mass in amu
    A = (Ahe*nhe + Ao*no + An2*nn2 + Ao2*no2 + Aar*nar)/nn
! gyroradii
    wce = qe*B0/me
    wci = qe*B0/mi
! collision frequencies
    nu_en = 5.4e-16 * nn * Te**(1./2.) &
		+ ( 59. + 4.18*log10(Te**3 / nel) )*1e-6 * nel * Te**(-3./2.)
    nu_in = 2.6e-15 * (nn + ni) * A**(-1./2.)
    print*, nel(10), ni(10), nn(10), A(10), hbeg+10*hstep
    print*, nu_en(10), nu_in(10)

! Direct conductivity (altitude dependant)
    sig0height = nel*qe**2 * ( 1./(me * nu_en) + 1./(mi * nu_in) )
!  Direct conductivity (height integrated)
    sig0int = SUM(sig0height*hstep*1e3)
    
! Pedersen conductivity (altitude dependant)
    sig1height = nel*qe**2 * ( nu_en/me * (1./(nu_en**2 + wce**2) ) &
		+ nu_in/mi * ( 1./(nu_in**2 + wci**2) ) )
!  Pedersen conductivity (height integrated)
    sig1int = SUM(sig1height*hstep*1e3)
    
! Hall conductivity (altitude dependant)
    sig2height = nel*qe**2 * ( wce/me * (1./(nu_en**2 + wce**2) ) &
		- wci/mi * ( 1./(nu_in**2 + wci**2) ) )
!  Hall conductivity (height integrated)
    sig2int = SUM(sig2height*hstep*1e3)
    
    OPEN(66,FILE='sigpout.dat',status='unknown')
    WRITE(66,400)(hbeg+i*hstep, i=1,500)
400 FORMAT(500F7.2)
    WRITE(66,500)sig0int
500 FORMAT(E19.11)
    WRITE(66,600)(sig0height(i), i=1,500)
600 FORMAT(500E19.11)
    WRITE(66,500)sig1int
    WRITE(66,600)(sig1height(i), i=1,500)
    WRITE(66,500)sig2int
    write(66,600)(sig2height(i), i=1,500)
    write(66,600)(nu_en(i), i=1,500)
    write(66,600)(nu_in(i), i=1,500)
    CLOSE(66)
!     print *,'------------Conductivity profile complete!'
    
    
    
!  debug
!     write(6,700)yyyy,doy,hrut,glat,glon
! 700 format('year: ',I4,', doy: ',I3,', hour: ',I2,', lat.: ',f5.1,', lon.: ',f5.1)
!     write(6,701)sig0int,sig1int,sig2int
! 701 format('s0 = ',e9.3,', s1 = ',e9.3,', s2 = ',e9.3)



end program conductivities
