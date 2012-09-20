! Main interface for IRI model
!
! Versions:
! 	May 2011: uses IRI07
!
! --------------------------------------------------------------------------
! --------------------------------------------------------------------------
! input:	iyyyy - year
! 				mmdd - month and day
! 				dhour - time in decimal hour
! 				iut - 1 for UT, 0 for LT
!         ivar     = 1      altitude
c                  = 2,3    latitude,longitude
c                  = 4,5,6  year,month,day
c                  = 7      day of year
c                  = 8      hour (UT or LT)
! 			vbeg - initial value of desired variable
! 			vend - final value of desired variable
! 			vstp - step value of desired variable (no more than 180 steps)
! 			lati - latitude (ignored if ivar = 2)
! 			longi - longitude (ignored if ivar = 3)
! 			alti - altitude (ignored if ivar = 1)
!
! output:	iriOUT.dat - binary file
! 					Number of elements is 1(I3) + 4 x 500(E25.11):
! 						* number of elements in each array (max 500)
! 						* variable (from ivar)
! 						* electron density
! 						* NmF2
! 						* HmF2
! --------------------------------------------------------------------------
! --------------------------------------------------------------------------
! Written by S. de Larquier (May 2011)
	PROGRAM iri_run

	implicit none
	integer(4)        :: i,ivar,nvar,nsteps
	integer(4)				:: jmag,jf(50),iut
	integer(4)        :: iyyyy,mmdd
	real(4)						:: vbeg,vend,vstp,dhour
	real(4)           :: lati,longi,alti,h_tec_max
	real(4)           :: a(20,1000),b(100,1000)

	read(5,*),lati,longi,alti,iyyyy,mmdd,iut,dhour,ivar,vbeg,vend,vstp

! Input choices for iri_sub
	do i=1,50
	   jf(i) = .true.
	enddo
	jf(2) = .true.               ! no temperatures
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

! Geographic or Geomagnetic coords
	jmag = 0

! h_tec_max = 0 no TEC otherwise upper boundary for integral
	h_tec_max = 800.

! Call iri
	call iri_web(jmag,jf,lati,longi,iyyyy,mmdd,iut,dhour,
     &          alti,h_tec_max,ivar,vbeg,vend,vstp,a,b)

	nsteps = nint((vend-vbeg)/vstp)

! Save to file
	OPEN(66,FILE='/tmp/iriOUT.dat',status='unknown')
	write(66,'(I4)')nsteps
100	FORMAT(500E19.11)
101	FORMAT(500F8.2)
	write(66,101)(vbeg + (nvar-1.)*vstp, nvar=1,500)
	write(66,100)(a(1,nvar), nvar=1,500)
	write(66,100)(b(1,nvar), nvar=1,500)
	write(66,100)(b(2,nvar), nvar=1,500)
	write(66,100)(b(37,nvar), nvar=1,500)
	write(66,100)(a(2,nvar), nvar=1,500)
	write(66,100)(a(3,nvar), nvar=1,500)
	write(66,100)(a(4,nvar), nvar=1,500)
	CLOSE(66)


	END