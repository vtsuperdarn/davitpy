! Copyright (C) 2012  VT SuperDARN Lab
! Full license can be found in LICENSE.txt
! A list of useful constants for the ray tracing program
MODULE constants

	implicit none
	real*4,parameter::			pi = 4.*atan(1.)
	real*4,parameter::			dtor = pi/180.
	real*4,parameter::			radeg = 180./pi
	real*4,parameter::			Rav = 6370.						! Earth radius [_km]
	real*4,parameter::			a = 6378.137					! Equatorial radius [_km]
	real*4,parameter::			f = 1./298.257223563	! Flattening of the Earth

	! Run parameter structure (which is sort of a constant...)
	type prm
		real*4::	txlat
		real*4::	txlon
		real*4::	azimbeg
		real*4::	azimend
		real*4::	azimstp
		real*4::	elevbeg
		real*4::	elevend
		real*4::	elevstp
		real*4::	freq
		integer::	nhop
		integer::	year
		integer::	mmdd
		real*4::	hourbeg
		real*4::	hourend
		real*4::	hourstp
		real*4::	hmf2
		real*4::	nmf2
		character*10::	filext
		character*250::	indir
		character*250::	outdir
                character*250::edens_file
	end type prm

	! Cash-Karp Parameters for embeded Runge-Kutta method (ref: Numerical recipes in C, Press et al., 2nd ed., pp.717)
	real*4,dimension(6),parameter::	ai = (/ 0., 1./5., 3./10., 3./5., 1., 7./8. /)
	real*4,dimension(6),parameter::	ci = (/ 37./378., 0., 250./621., 125./594., 0., 512./1771. /)
	real*4,dimension(6),parameter::	dci = (/ ci(1)-2825./27648., ci(2)-0., ci(3)-18575./48384., ci(4)-13525./55296., &
																					ci(5)-277./14336., ci(6)-1./4. /)
	real*4,dimension(5),parameter::	b2 = (/ 1./5., 0., 0., 0., 0. /)
	real*4,dimension(5),parameter::	b3 = (/ 3./40., 9./40., 0., 0., 0. /)
	real*4,dimension(5),parameter::	b4 = (/ 3./10., -9./10., 6./5., 0., 0. /)
	real*4,dimension(5),parameter::	b5 = (/ -11./54., 5./2., -70./27., 35./27., 0. /)
	real*4,dimension(5),parameter::	b6 = (/ 1631./55296., 175./512., 575./13824., 44275./110592., 253./4096. /)
	

END MODULE constants
