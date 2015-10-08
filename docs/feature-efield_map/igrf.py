import numpy as np
import scipy as sp
import scipy.misc

import warnings
import gsetup as gs


class IGRF(object):
    """ Set up model coefficients"""
    
    def __init__(self):
        pass
        

    def _schmidt_coeff(self):
        """
        Return Schmidt coefficients
    
        Provides Schmidt quasi-normalization coefficients for associated
        Legendre polynomials of degree n=13 and order m=13.
        Uses module globals nn and mm
        Output: Numpy array of size(104) containing the coefficients in form
        S[1,0],S[1,1],S[2,0],S[2,1] S[2,2],S[3,0],S[3,1],S[3,2],S[3,3, ..., S[13,13]
        """
        return ((-1)**gs.mm)*np.sqrt(2.*scipy.misc.factorial(gs.nn-gs.mm)
                                     /(scipy.misc.factorial(gs.nn+gs.mm)))*(gs.mm!=0) + (gs.mm==0)
         
    
    def _igrfcoeff(self,year,day):
        """
        Return interpolated igrf12 coefficients
        
        year must lie between 1900 and gs.yrlast+5
        """
        i0 = int(year)
        iday = int(day)
        if (i0 < 1900): 
            i0 = 1900
            print('WARNING! Year ',year,' earlier than 1900, values for 1900 used.')
        if (i0 > gs.yrlast+5):
            i0 = gs.yrlast+5
            print('WARNING! Year ',year, ' later than  yrlast+5, yrlast+5 used.')
        year0 = 1900 + ((i0-1900)/5)*5  
        if (year0  != gs.yrlast):
            f2 = (i0 + (iday-1)/365.25-year)/5.
            f1 = 1.-f2
            g = np.array(gs.gdata[str(year0)].values)*f1 + np.array(gs.gdata[str(year0+5)].values)*f2
            h = np.array(gs.hdata[str(year0)].values)*f1 + np.array(gs.hdata[str(year0+5)].values)*f2
        # Extrapolate beyond self.yrlast
        else: 
            dt = i0+((iday-1)/365.25-i0)
            g = np.array(gs.gdata[str(year0)].values)
            h = np.array(gs.hdata[str(year0)].values)
            g = g+np.array(gs.gdata[gs.dyr])*dt
            h = h+np.array(gs.hdata[gs.dyr])*dt
        hout = np.insert(h,gs.hmask,gs.hval)
        return np.array(g),np.array(hout)
    
    def model(self,year,day):
        """
        Return Schmidt-normalized assoc. Legendre coefficients for epoch 'year, day'
        
        INPUT:
        year: dtype=int
        day: dtype=int
        
        OUTPUT:
        Numpy arrays (size(104) for year>=2000, size(78) for year<2000) in form
          [x[1,0], x[1,1],x[2,0],x[2,1],x[2,2],x[3,0],x[3,1],x[3,2],x[3,3],
            ... , x[n,m], ... , x[n,n]]
                
        g*sch: Schmidt normalized coefficients of cos(m*phi).  
        h*sch: Schmidt normalized coefficients of sin(m*phi).  
        mm: array of m values
        nn: array of n values
         
        """
        g,h = self._igrfcoeff(year,day)
        sch = self._schmidt_coeff()
        if (year < 2000):
            g,h,sch = g[0:77],h[0:77],sch[0:77]
        return g*sch, h*sch, gs.mm, gs.nn



class Bmath(object):
    
    
    """
    Compute IGRF magnetic field and magnetic field gradient tensor at a point.
    
    Create initiation by bf = Bmath(year,day)
    year: dtype int
    day: dtype int
    
    Attributes:
    yr: year - set when class is initiated
    dy: day - set when class is initiated
    gcoeff: Array of coefficients of cos(m*phi) in spherical harmonic representation 
            of IGRF in format
            [g[1,0],g[1,1],g[2,0],g[2,1],g[2,2], ... g[n,n]]. 
            If 1900<year<2000 then n=10. If 2000<=year<=2020 then n=13.
    hcoeff: Array of coefficients of sin(m*phi) in same format
    """
    
    def __init__(self,year,day):
        """
        From the instance 'ig', of the class 'IGRF', compute the appropriate igrf 
        coefficients corresponding to the epoch: year, day. Set them as attributes 
        gcoeff, hcoeff of this class.
        """
        self.yr = year
        self.dy = day
        if self.yr < 2000:
            self.nref = 10
        else:
            self.nref = 13
        ig=IGRF()
        self.gcoeff,self.hcoeff, self.mm, self.nn = ig.model(year,day)

    def _assleg(self,n,x):
        """ 
        Return associated Legendre polynomials, 1st derivs, array size.
        
        INPUT:
        n: dtype=int.Highest degree and order of required polynomials
        x: dtype=float. Argument of polynomials.
        
        
        Uses SciPy function lpmn to compute all the unnormalized associated
        Legendre polynomials of degree nn <= n and order mm<=nn and their first 
        derivatives with respect to x where x=cos(theta). All orders
        from 
        Parameters:
        n: dtype int
        x: dtype float
        Returns (Pnm[n,m],dPnm[n,m],length)
        """
        p,dp = sp.special.lpmn(n,n,x) #Ass. Leg. polynomials and 1st deriv.
        p=np.reshape(p.T[1:n+1,0:n+1],-1)
        dp=np.reshape(dp.T[1:n+1,0:n+1],-1)
        dp=(dp[p!=0.])
        p=(p[p!=0.])
        return p,dp,np.size(p)
    
    def _d2alp(self,x,p,dp):
        """
        Return second derivatives of array of associated Legendre polynomials
        
        INPUT:
        x: dtype=float. Argument of polynomials
        p: dtype=float. Numpy array of associated Legendre polynomials of
           order and degree nn
           
        NOTE:
        Uses differential equation for associated Legendre polynomials to 
        compute second derivatives from the polynomials and their first 
        derivatives
        """
        return (2.*x*dp-((self.nn[0:np.size(p)]*(self.nn[0:np.size(p)]+1)
                          -self.mm[0:np.size(p)]**2/(1-x**2))*p))/(1-x**2)
        
    
    def _funcr(self,r,length):
        """
        Return R(r)=1/r^n and dR(r)/dr 
    
        Input
        r:  dtype=float. radius in earth radii.
        length: dtype=int. Must have been set by previous call to assleg
        """
        
        fr = 1./r**(self.nn[0:length]+1) 
        dfr = -(self.nn[0:length]+1)*fr/r 
        return fr,dfr
    
    def _d2funcr(self,df,r):
        """
        Return second deriv of R(r)=1/r^n
        
        INPUT:
        """
        return -(self.nn[0:np.size(df)]+2)*df/r
        
    def _funcphi(self,phi,length):
        """ 
        Return spherical harmonic terms depending on \phi for IGRF
    
        INPUT:
        phi: dtype=float. Longitude in radians
        length: dtype=int. Must have been set by previous call to assleg

        Returns array of phi dependent factors of spherical harmonics
        and their first derivatives.
        
        """
        smphi=np.sin(self.mm[0:length]*phi)
        cmphi=np.cos(self.mm[0:length]*phi)
        phifunc= (self.gcoeff[0:length]*cmphi+
                  self.hcoeff[0:length]*smphi)
        dphifunc= self.mm[0:length]*(-self.gcoeff[0:length]*smphi+
                      self.hcoeff[0:length]*cmphi)
        return phifunc,dphifunc
    
    def _d2funcphi(self,phifunc):
        """
        Returns second derivatives of function defined by method _funcphi.
        
        INPUT:
        phifunc: dtype=float. Numpy array of the phi dependent factors 
        of spherical harmonics
        """
        return -(self.mm[0:np.size(phifunc)]**2)*phifunc
     
    def _sphhar(self,r,theta,phi,n):
        """
        Return R, Theta Phi factors in spherical harmonic expansion
             
        INPUT:
        r: dtype=float. radius in earth radii
        theta: dtype=float. co-latitude in radians
        phi: dtype=float. longitude (eastwards) in radians
        n: dtype=int. order and degree of spherical harmonic expansion
        OUTPUT:
        Numpy arrays of the theta, phi and r factors in the s.h. expansion 
        and their first derivatives.
                  
        """
        x=np.cos(theta)
        pnm,dpnm,length = self._assleg(n,x)
        fphi,dfphi = self._funcphi(phi,length)
        fr,dfr = self._funcr(r,length)
        return (pnm,dpnm,fphi,dfphi,fr,dfr)
    
    def _b(self,r,theta,pnm,dpnm,fphi,dfphi,fr,dfr):
        """
        Return spherical harmonic representation of B
             
                        
        """
        #Problem to be solved later: B is singular at the geographic poles. 
        dftheta=-np.sin(theta)*dpnm
        return np.array([sum(fr*fphi*dftheta)/(r), 
                         -sum(fr*pnm*dfphi)/(r*np.sin(theta)), 
                         sum(pnm*fphi*dfr)
                         ])
    
    def bfield(self,x,y,z):
        """
        Return local magnetic components of IGRF
        
        INPUTS:
        x, y, z: gc coordinates in Earth radii
        
        RETURNS: 
        X: Northward horizontal component of B in nT
        Y: Eastward horizontal component of B in nT
        Z: Inward (towards centre of Earth) component of B in nT
        
        """
        r, theta, phi = self._cart2pol(x,y,z)
        # Select suitable value of n to ignore negligible terms in spherical harmonic representation
        n = 3*(self.yr >= 2000) + 30/int(r+2)*(r >= 1.) + 10*(r < 1.)
        args = self._sphhar(r,theta,phi,n)
        return self._b(r,theta,*args)
    
    def bgeog(self,r,theta,phi):
        """
        Return local magnetic components of IGRF
        
        INPUTS:
        r, theta,phi: spherical polar coordinates in Earth radii
        
        RETURNS: 
        np.array([Bx,By,Bz]) the vector B in gc coordinates        
        """
        # Select suitable value of n to ignore negligible terms in spherical harmonic representation
        n = 3*(self.yr >= 2000) + 30/int(r+2)*(r >= 1.) + 10*(r < 1.)
        args = self._sphhar(r,theta,phi,n)
        bxyz = self._b(r,theta,*args)
        # Set up transformation matrices and tensors for transformation
        #
        x,y,z = self._pol2cart(r,theta,phi)
        lij=self._lij(x,y,z)
        # Transform to geographic coordinates
        return np.einsum('ij,j',lij,bxyz)
    
    def bgc(self,x,y,z):
        """
        Return components of IGRF in gc coordinates
        
        INPUTS:
        x, y, z: gc coordinates in Earth radii

        OUTPUT:
        
        
        RETURNS: 
        X: Northward horizontal component of B in nT
        Y: Eastward horizontal component of B in nT
        Z: Inward (towards centre of Earth) component of B in nT
        
        """
        r, theta, phi = self._cart2pol(x,y,z)
        # Select suitable value of n to ignore negligible terms in spherical harmonic representation
        n = 3*(self.yr >= 2000) + 30/int(r+2)*(r >= 1.) + 10*(r < 1.)
        args = self._sphhar(r,theta,phi,n)
        bsph = self._b(r,theta,*args)
        lij=self._lij(x,y,z)
        # Transform to geographic coordinates
        return np.einsum('ij,j',lij,bsph)
     
    def _bderivs(self,r,theta,phi,n):
        """
        Return igrf B and $dB_i/dx_j$ in local magnetic X,Y,Z coordinate system
        """
        #Problem to be solved later: B and its derivatives are singular at the geographic poles. 
        #This is a coordinate singularity and should be resolvable by noting there is no
        #singularity in the cartesian system in which the field tracing and mapping is done.
        #We should thus exclude any step that ends on a point within (say) 0.1 degrees of the pole.
        
        # Compute spherical harmonic factors Theta(theta), Phi(phi), R(r) and X,Y,Z, B components
        if (theta < .02 or theta > np.pi-0.02):
            warnings.warn("In function bderivs data point very near pole. Treat results with caution."
                          ,RuntimeWarning)
            print 'theta =', np.rad2deg(theta)
        
        pnm,dpnm,fphi,dfphi,fr,dfr = self._sphhar(r,theta,phi,n)
        bvec = self._b(r,theta,pnm,dpnm,fphi,dfphi,fr,dfr)
        
        # Compute 2nd derivs of Theta, Phi, R w.r.t. theta, phi, r respectively
        dftheta=-np.sin(theta)*dpnm
        x=np.cos(theta)
        d2ftheta =  -np.cos(theta)*dpnm + self._d2alp(x,pnm,dpnm)*(np.sin(theta))**2
        d2fphi = self._d2funcphi(fphi)
        d2fr = self._d2funcr(dfr,r)
        
        # Compute components of gradient tensor in X, Y, Z components
        dbxx = -sum(fr*fphi*d2ftheta)/r**2
        dbxy = sum(fr*dfphi*dftheta)/(r**2*np.sin(theta))
        dbxz = -sum((dfr-fr/r)*fphi*dftheta)/r
        dbyx = sum(fr*(-pnm*np.cos(theta)/(np.sin(theta))+dftheta)*dfphi)/((r**2)*np.sin(theta))
        dbyy = -sum(fr*pnm*d2fphi)/(r**2*(np.sin(theta))**2)
        dbyz = sum((dfr-fr/r)*pnm*dfphi)/(r*np.sin(theta))
        dbzx = - sum(dftheta*fphi*dfr)/r
        dbzy = sum(pnm*dfphi*dfr)/(r*np.sin(theta))
        dbzz = -sum(pnm*fphi*d2fr)
        dbmatrix=np.array([[dbxx,dbxy,dbxz],
                           [dbyx,dbyy,dbyz],
                           [dbzx,dbzy,dbzz]])
        
        return bvec,dbmatrix
    
    def _lij(self,x,y,z):
        """
        Return transformation matrix $l_{ij}$
        """
        r = np.sqrt(x**2+y**2+z**2)
        rho = np.sqrt(x**2+y**2)
        return np.array([[-x*z/(rho*r), -y/rho, -x/r],
                         [-y*z/(rho*r),  x/rho, -y/r],
                         [rho/r,         0,     -z/r]])
    
    def _sijk(self,x,y,z):
        """
        Return derivative of transformation matrix $l_{ij}$
    
        Inputs:
        x,y,z: Coordinates in geographical system
    
        Outputs:
        3x3x3 matrix $\partial l_{ik}/\partial x_j$
        """
        r=np.sqrt(x**2+y**2+z**2)
        rho=np.sqrt(x**2+y**2)
        return np.array([[[z*((rho*x)**2-(r*y)**2)/(rho*r)**3,   x*y/rho**3,   -(y**2+z**2)/r**3],
                          [x*y*z*(rho**2+r**2)/(rho*r)**3,      -x**2/rho**3,   x*y/r**3],
                          [-rho*x/r**3,                          0.,            x*z/r**3]],
                         [[x*y*z*(r**2+rho**2)/(rho*r)**3,       y**2/rho**3,   x*y/r**3],
                          [z*((rho*y)**2-(r*x)**2)/(rho*r)**3,  -x*y/rho**3,   -(x**2+z**2)/r**3],
                          [-rho*y/r**3,                          0.,            y*z/r**3]],
                         [[x*z**2/(rho*r**3),                    0.,            x*z/r**3], 
                          [y*z**2/(rho*r**3),                    0.,            y*z/r**3],
                          [-rho*z/r**3,                          0.,           -rho**2/r**3]]])
    
    def _cart2pol(self,x,y,z):
        """
        Return global spherical polar (gsp) coordinates in radians
        
        Input:
        x, y, z: Global Cartesian (gc) coordinates. (Normally in R_E but any consistent units will do)
        
        Note: Utility gspToGcar in davitpy package utils uses degrees for angles
        """
        r=np.sqrt(x**2+y**2+z**2)
        rho=np.sqrt(x**2+y**2)
        theta=np.arctan2(rho,z)
        phi=np.arctan2(y,x)
        return r, theta, phi
    
    def _pol2cart(self,r,theta,phi):
        """
        Return gc coordinates in Earth radii
        
        Input:
        r: Radius in Earth radii
        theta, phi: colatitude and longitude in radians
        
        """
        return r*np.sin(theta)*np.cos(phi), r*np.sin(theta)*np.sin(phi), r*np.cos(theta)
    
    def bdb(self,x,y,z):
        """
        Return magnetic field and field gradient tensor in Global Cartesian (gc) coordinates
        
        INPUT:
        x, y, z: gc coordinates in Earth radii
        
        RETURN
        bgc: 3 element Numpy array of Bx, By, Bz  (nT)
        dbgc: 3x3 Numpy array dBi/dxj (nt/Earth radius)
        """
        
        # Get magnetic field and gradient tensor in magnetic X, Y, Z coordinates
        r, theta, phi = self._cart2pol(x,y,z)
        # Select suitable value of n to ignore negligible terms in spherical harmonic representation
        n = 3*(self.yr >= 2000) + 30/int(r+2)*(r >= 1.) + 10*(r < 1.)
        bvec,dbmatrix =self._bderivs(r,theta,phi,n)
        b=np.sqrt(bvec[0]**2+bvec[1]**2+bvec[2]**2)
        
        # Set up transformation matrices and tensors for transformation from mag XYZ to gc coordinates
        lij = self._lij(x,y,z)
        dlij = self._sijk(x,y,z)
        
        # Transform field and gradient tensor to gc coordinates
        bgc=np.einsum('ij,j',lij,bvec)
        dbgc=np.einsum('ik,jl,kl',lij,lij,dbmatrix)+np.einsum('ijk,k', dlij,bvec)
        return bgc, dbgc

