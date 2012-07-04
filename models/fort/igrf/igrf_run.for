! Main interface for IGRF model
! 
! Versions:
! 	March 2011: uses IGRF-11 coefficients
! 
! --------------------------------------------------------------------------
! --------------------------------------------------------------------------
! input:	ryear - decimal year (year+month/12.0-0.5 or 
!                  	year+day-of-year/365 or ../366 if leap year)
! 			vbeg - initial altitude
! 			vend - final altitude
! 			vstep - altitude step value
! 			lati - latitude
! 			longi - longitude
! 
! output:	igrfOUT.dat - binary file
! 					Number of elements is 1(I5) + 3 x nelem(F8.3):
! 						* number of elements in each array (nelem)
! 						* magnetic field amplitude (in Gauss)
! 						* magnetic field dip angle
! 						* magnetic field declination angle (+East)
! --------------------------------------------------------------------------
! --------------------------------------------------------------------------
! Written by S. de Larquier (March 2011)
	PROGRAM igrf_run
		
		implicit none
		integer(4)        								:: nvar,nsteps,xlcode
		real(4)          								  :: ryear,vbeg,vend,vstep
		real(4)           								:: lati,longi,alti
		real(4)           								:: babs,dip,dipdec,xl,dipl
		real(4),ALLOCATABLE,dimension(:) 	:: diparr,decarr,fabs
		character*13											:: fmt

		read(5,*),ryear,vbeg,vend,vstep,lati,longi
! 		print*,ryear,vbeg,vend,vstep,lati,longi
		
		if (vstep .ne. 0.) then
			nsteps = int((vend-vbeg)/vstep) + 1
		else
			nsteps = 1
		endif
		if (nsteps .gt. 99999) then
			print*, 'Too many steps: ',nsteps
			return
		endif
		allocate(diparr(nsteps), decarr(nsteps), fabs(nsteps))
		alti = vbeg
		do nvar = 1,nsteps
			call igrf_sub(lati,longi,ryear,alti,xl,xlcode,
     &                dipl,babs,dip,dipdec)
			diparr(nvar) = dip
			decarr(nvar) = dipdec
			fabs(nvar) = babs
! 			print*, lati, longi, alti, dip, dipdec, babs
		!	Update variable
			alti = vbeg + nvar*vstep
		end do

		OPEN(66,FILE='/tmp/igrfOUT.dat',status='unknown')
		write(66,'(I5)')nsteps
		write(fmt,100)nsteps
100		FORMAT('(',I5,'F8.3)')
		write(66,fmt)(fabs(nvar), nvar=1,nsteps)
		write(66,fmt)(diparr(nvar), nvar=1,nsteps)
		write(66,fmt)(decarr(nvar), nvar=1,nsteps)
		CLOSE(66)
		
		
	END