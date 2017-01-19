C     -*- fortran -*-
C     This file is autogenerated with f2py (version:2)
C     It contains Fortran 77 wrappers to fortran functions.

      subroutine f2pywrapbes (besf2pywrap, x, k)
      external bes
      real*8 x
      integer k
      double precision besf2pywrap, bes
      besf2pywrap = bes(x, k)
      end


      subroutine f2pywrapbes0 (bes0f2pywrap, x)
      external bes0
      real*8 x
      double precision bes0f2pywrap, bes0
      bes0f2pywrap = bes0(x)
      end


      subroutine f2pywrapbes1 (bes1f2pywrap, x)
      external bes1
      real*8 x
      double precision bes1f2pywrap, bes1
      bes1f2pywrap = bes1(x)
      end


      subroutine f2pywrapxksi (xksif2pywrap, x, y, z)
      external xksi
      real*8 x
      real*8 y
      real*8 z
      double precision xksif2pywrap, xksi
      xksif2pywrap = xksi(x, y, z)
      end


      subroutine f2pywrapfexp (fexpf2pywrap, s, a)
      external fexp
      real*8 s
      real*8 a
      real*8 fexpf2pywrap, fexp
      fexpf2pywrap = fexp(s, a)
      end


      subroutine f2pywrapfexp1 (fexp1f2pywrap, s, a)
      external fexp1
      real*8 s
      real*8 a
      real*8 fexp1f2pywrap, fexp1
      fexp1f2pywrap = fexp1(s, a)
      end


      subroutine f2pywraptksi (tksif2pywrap, xksi, xks0, dxksi)
      external tksi
      real*8 xksi
      real*8 xks0
      real*8 dxksi
      double precision tksif2pywrap, tksi
      tksif2pywrap = tksi(xksi, xks0, dxksi)
      end


      subroutine f2pywrapr_s (r_sf2pywrap, a, r, theta)
      external r_s
      real*8 r
      real*8 theta
      real*8 a(31)
      double precision r_sf2pywrap, r_s
      r_sf2pywrap = r_s(a, r, theta)
      end


      subroutine f2pywraptheta_s (theta_sf2pywrap, a, r, theta)
      external theta_s
      real*8 r
      real*8 theta
      real*8 a(31)
      double precision theta_sf2pywrap, theta_s
      theta_sf2pywrap = theta_s(a, r, theta)
      end


      subroutine f2pywrapap (apf2pywrap, r, sint, cost)
      external ap
      real r
      real sint
      real cost
      double precision apf2pywrap, ap
      apf2pywrap = ap(r, sint, cost)
      end


      subroutine f2pywrapapprc (apprcf2pywrap, r, sint, cost)
      external apprc
      real r
      real sint
      real cost
      double precision apprcf2pywrap, apprc
      apprcf2pywrap = apprc(r, sint, cost)
      end


      subroutine f2pywrapbr_prc_q (br_prc_qf2pywrap, r, sint, cost
     &)
      external br_prc_q
      real r
      real sint
      real cost
      double precision br_prc_qf2pywrap, br_prc_q
      br_prc_qf2pywrap = br_prc_q(r, sint, cost)
      end


      subroutine f2pywrapbt_prc_q (bt_prc_qf2pywrap, r, sint, cost
     &)
      external bt_prc_q
      real r
      real sint
      real cost
      double precision bt_prc_qf2pywrap, bt_prc_q
      bt_prc_qf2pywrap = bt_prc_q(r, sint, cost)
      end


      subroutine f2pyinitgeopack2(setupfunc)
      external setupfunc
      real g(105)
      real h(105)
      real rec(105)
      common /geopack2/ g,h,rec
      call setupfunc(g,h,rec)
      end

      subroutine f2pyinitgeopack1(setupfunc)
      external setupfunc
      real aa(10)
      real sps
      real cps
      real bb(22)
      common /geopack1/ aa,sps,cps,bb
      call setupfunc(aa,sps,cps,bb)
      end

      subroutine f2pyinitwarp(setupfunc)
      external setupfunc
      real*8 cpss
      real*8 spss
      real*8 dpsrr
      real*8 rps
      real*8 warp
      real*8 d
      real*8 xs
      real*8 zs
      real*8 dxsx
      real*8 dxsy
      real*8 dxsz
      real*8 dzsx
      real*8 dzsy
      real*8 dzsz
      real*8 dzetas
      real*8 ddzetadx
      real*8 ddzetady
      real*8 ddzetadz
      real*8 zsww
      common /warp/ cpss,spss,dpsrr,rps,warp,d,xs,zs,dxsx,dxsy,dxs
     &z,dzsx,dzsy,dzsz,dzetas,ddzetadx,ddzetady,ddzetadz,zsww
      call setupfunc(cpss,spss,dpsrr,rps,warp,d,xs,zs,dxsx,dxsy,dx
     &sz,dzsx,dzsy,dzsz,dzetas,ddzetadx,ddzetady,ddzetadz,zsww)
      end

      subroutine f2pyinitcoord21(setupfunc)
      external setupfunc
      real*8 xx2(14)
      real*8 yy2(14)
      real*8 zz2(14)
      common /coord21/ xx2,yy2,zz2
      call setupfunc(xx2,yy2,zz2)
      end

      subroutine f2pyinitrhdr(setupfunc)
      external setupfunc
      real*8 rh
      real*8 dr
      common /rhdr/ rh,dr
      call setupfunc(rh,dr)
      end

      subroutine f2pyinitloopdip1(setupfunc)
      external setupfunc
      real*8 tilt
      real*8 xcentre(2)
      real*8 radius(2)
      real*8 dipx
      real*8 dipy
      common /loopdip1/ tilt,xcentre,radius,dipx,dipy
      call setupfunc(tilt,xcentre,radius,dipx,dipy)
      end

      subroutine f2pyinitdx1(setupfunc)
      external setupfunc
      real*8 dx
      real*8 scalein
      real*8 scaleout
      common /dx1/ dx,scalein,scaleout
      call setupfunc(dx,scalein,scaleout)
      end

      subroutine f2pyinitcoord11(setupfunc)
      external setupfunc
      real*8 xx1(12)
      real*8 yy1(12)
      common /coord11/ xx1,yy1
      call setupfunc(xx1,yy1)
      end

      subroutine f2pyinitbirkpar(setupfunc)
      external setupfunc
      real xkappa1
      real xkappa2
      common /birkpar/ xkappa1,xkappa2
      call setupfunc(xkappa1,xkappa2)
      end

      subroutine f2pyinitrh0(setupfunc)
      external setupfunc
      real rh0
      common /rh0/ rh0
      call setupfunc(rh0)
      end

      subroutine f2pyinittail(setupfunc)
      external setupfunc
      real dxshift1
      real dxshift2
      real d
      real deltady
      common /tail/ dxshift1,dxshift2,d,deltady
      call setupfunc(dxshift1,dxshift2,d,deltady)
      end

      subroutine f2pyinitrcpar(setupfunc)
      external setupfunc
      real sc_sy
      real sc_as
      real phi
      common /rcpar/ sc_sy,sc_as,phi
      call setupfunc(sc_sy,sc_as,phi)
      end

      subroutine f2pyinitg(setupfunc)
      external setupfunc
      real g
      common /g/ g
      call setupfunc(g)
      end

      subroutine f2pyinitdphi_b_rho0(setupfunc)
      external setupfunc
      real*8 dphi
      real*8 b
      real*8 rho_0
      real*8 xkappa
      common /dphi_b_rho0/ dphi,b,rho_0,xkappa
      call setupfunc(dphi,b,rho_0,xkappa)
      end

      subroutine f2pyinitmodenum(setupfunc)
      external setupfunc
      integer m
      common /modenum/ m
      call setupfunc(m)
      end

      subroutine f2pyinitdtheta(setupfunc)
      external setupfunc
      real*8 dtheta
      common /dtheta/ dtheta
      call setupfunc(dtheta)
      end


