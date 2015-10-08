import numpy as np
import scipy as sp
import gsetup as gs
import igrf as ig
import ginteg as gint

  

class Aux(object):
    
    """
    Auxiliary routines for field line trace integration
    
    Initiation:
    Aux is initiated by inst = Aux(year, day, model)
        year: dtype = int, a year between 1900 and latest year of model
        day: dtype = int, Julian day
        model: dtype = string, name of model (currently 'igrf' and 'igrfb' are only valid names)
    
    Notes:
    When an instance of Aux is created the magnetic field model(s) for the particular year and 
    day are extractewd from the data produced by the module gsetup. The auxiliary subroutines for
    the Runge Kutta integration and the regula falsi process for convergence on the end point are
    methods of the instance and use the model coefficients appropriate for the year and day.  
    
    """
    
    def __init__(self,year,day,model,cond,h0):
        """
        Select and initiate model
        
        INPUT:
        year: dtype = int, a year between 1900 and latest year of model
        day: dtype = int, Julian day
        model: dtype = string, name of model (currently) 'igrf' and 'igrfb' are only valid names
        cond: dtype = string, name of condition determining end point. Currently 'default' and
                      'height' are only valid names
        h0: dtype = float, parameter needed for exit condition according to following table:
                    'default'  h0 irrelevant. Use arbitrary value
                    'height'   h0 is height in km above Earth's surface at which integration is 
                               terminated
        
        
        """
        
        # Dictionary relating model name to correct Runge Kutta auxiliary function
        self.keys_rk4 = {'igrf':self.auxigrfbdb,
                     'igrfb':self.auxigrfb,
                     'harris':None,
                     'tsy95':None}
        
        # Dictionary relating condition name to correct regula falsi auxiliary function
        self.keys_rf = {'default':self.return_false,
                      'height':self.regfalsi_aux_h,
                      'equator':self.regfalsi_aux_mageq}
        
        # Dictionary relating condition name to correct function for determining that 
        # integration exit condition has been reached.  
        self.conds = {'default':self.return_false,
                      'height':self.h_lt_h0,
                      'equator':self.mag_eq}
        
        # Input parameters
        self.md = model
        self.cn = cond
        self.yr = year
        self.dy = day
        self.h0 = h0
        
        #Parameter for method mag_eq
        self.rlast = 0.
        
        # Set up class instances for model
        self.igb = ig.Bmath(self.yr,self.dy)
        self.gi=gint.Ginteg()
        
    def modelsub(self,y,s):
        """
        Return result of calling appropriate subroutine for the model object md
        
        Input:
        y: dtype = float. Current value of vector from rk4_driver
        s: dtype = float. Current value of path length
        """
        return self.keys_rk4[self.md](y,s)
    
    def condsub(self,step,y,s):
        """
        Return result of calling appropriate subroutine for the model object md
        
        """
        return self.keys_rf[self.cn](step,y,s)
    
    def condition(self,y,s,*args,**kwargs):
        """
        Returns the result of calling the appropriate subroutine for the condition object cn
        """
        return self.conds[self.cn](y,s,*args,**kwargs)
        
        
    # Standard functions for terminating field line trace
    
    def return_false(self,y,s):
        """
        Return False
        
        Note:
        The result of returning false to the integration routine after each step allows it to 
        continue to the maximum number of steps defined by the RK4 driver routine.
        """
        return False


    # Return if h less than h0 
    def h_lt_h0(self,y,s):

        """
        Return True if h<h0

        Input:
        y: Current value of the vector y[0:3] 0r y[0:9] where y[0:3] contains gc coordinates in Earth radii
        s: Current field line length (not used) 
        """
        r = np.sqrt(np.dot(y[0:3],y[0:3]))*6371.2
        return (r < 6371.2+self.h0)
    
    # Return when magnetic equator passed
    def mag_eq(self,y,s):
        '''
        Return True if r greater than previous value
        
        
        Input:
        y: Current value of the vector y[0:3] 0r y[0:9] where y[0:3] contains gc coordinates in Earth radii
        s: Current field line length (not used)
        
        Note:
        This is a crude criterion for determining whether magnetic equator has been passed.
        It avoids the expense of calculating dr/ds at every step. The equator may lie between
        r[-1] and r[-2] or between r[-2] and r[-3]. The calling routine must determine which by
        investigating dr/ds in order that the final convergence procedure may start.
        '''
        r = np.sqrt(y[0]**2 + y[1]**2 + y[2]**2)
        crit = r < self.rlast
        self.rlast = r
        return crit
   
    # Routines required for convergence on the magnetic equator. 
    def drbyds(self,y):
        """
        Given position x,y,z, = y[0:3] on field line, return dr/ds
        """
        r = np.sqrt(y[0]**2 + y[1]**2 + y[2]**2)
        bvec = self.igb.bgc(y[0],y[1],y[2])
        mu = bvec/(np.sqrt(bvec[0]**2 + bvec[1]**2 + bvec[2]**2))
        return (mu[0]*y[0] +mu[1]*y[1] + mu[2]*y[2])/r
    
    def check_drbyds(self,inarray,ins):
        x1 = self.drbyds(inarray[-1,0:3])
        x2 = self.drbyds(inarray[-2,0:3])
        x3 = self.drbyds(inarray[-3,0:3])
        if x1*x2 >= 0.:
            return inarray[0:-1,],ins[0:-1]
        return inarray, ins

    
    # Routine to check accuracy of integration
    def flag(self,y,*args,**kwargs):
        """
        Return True if mu.w/|w| lt 1.e-5 else False
        """
        # Currently, when only a field line trace is being done there is no check on accuracy
        if self.md=='igrfb':
            return False
        r=np.sqrt(y[0]**2+y[1]**2+y[2]**2)
        rho=np.sqrt(y[0]**2+y[1]**2)
        theta=np.arctan2(rho,y[2])
        phi=np.arctan2(y[1],y[0])
        rarr=np.array([r*np.sin(theta)*np.cos(phi),r*np.sin(theta)*np.sin(phi),
                       r*np.cos(theta)])
        # Compute unit vectors
        bvec = self.igb.bgeog(r,theta,phi,*args,**kwargs)
        muxyz=bvec/np.sqrt(np.sum(bvec*bvec))        # Unit B in geographic coords
        wdotmu1=abs(np.dot(muxyz,y[3:6]))/np.sqrt(sum(y[3:6]*y[3:6]))
        wdotmu2=abs(np.dot(muxyz,y[6:9]))/np.sqrt(sum(y[6:9]*y[6:9]))
        if (wdotmu1<1.e-5) and (wdotmu2<1.e-5):return True,wdotmu1,wdotmu2,bvec
        return False,wdotmu1,wdotmu2,bvec
        
    
    # Auxiliary functions for Runge Kutta Integration
    def auxigrfb(self,y,s):
        """
        Return rhs of diff eqns dy_i/ds =  f(y_i) for one step of a simple field line trace
        
        input: numpy array y = [x, y, z] where x, y, z are global geographic coordinates
        """
        x,y,z = y[0:3]
        bvec=self.igb.bfield(x,y,z)
        b=np.sqrt(bvec[0]**2+bvec[1]**2+bvec[2]**2)
        muxyz=bvec/b # Unit vector along B in spherical
        #                                        polar system
    
        # Set up transformation matrices and tensors for transformation
        #
        lij=self.igb._lij(x,y,z)
        # Transform to geographic coordinates
        return np.einsum('ij,j',lij,muxyz)
    

    def auxigrfbdb(self,y,s):
        """
        Return rhs of differential equations for B field line and field line separation
        """
        xv,yv,zv = y[0:3]
        bvec,dbmatrix=self.igb.bdb(xv,yv,zv) # B and dB/dx in gc coords
        b=np.sqrt(bvec[0]**2+bvec[1]**2+bvec[2]**2)
        mu=bvec/b # Unit vector along B in gc coords   

        #
        # Compute tensor $T_{ij}$
        kron=np.array([[1,0,0],[0,1,0],[0,0,1]]) # kronecker delta
        muouter=np.einsum('i,j->ij',mu,mu) # Form $\mu_i \mu_j$
        tmatrix = np.einsum('ik,kj',(kron-muouter),dbmatrix)/b
        #
        # Return rhs of differential equations
        wx1,wy1,wz1=y[3],y[4],y[5]
        wgeog=np.array([wx1,wy1,wz1])
        tdotw=np.einsum('ij,j',tmatrix,wgeog)
        tdotmu=np.einsum('ij,j',tmatrix,mu)
        dw1=tdotw - mu*(np.einsum('i,i',wgeog,tdotmu))
        wx2,wy2,wz2=y[6],y[7],y[8]
        wgeog=np.array([wx2,wy2,wz2])
        tdotw=np.einsum('ij,j',tmatrix,wgeog)
        tdotmu=np.einsum('ij,j',tmatrix,mu)
        dw2=tdotw - mu*(np.einsum('i,i',wgeog,tdotmu))
        return np.reshape([mu,dw1,dw2],-1)
    

    # Auxiliary functions for Regula Falsi convergence 
    def regfalsi_aux_h(self,step,y0,s):
        """
        Return value of step that takes field line to h=h0.
    
        Input:
        step: RK4 step size on entry
        auxiliary_rk:  Runge Kutta auxiliary subroutine
        y0:   Value of vector y corresponding to step
        """
        auxiliary = self.modelsub
        ynew=self.gi.rk4_int(auxiliary,y0,s,step)
        re = 6371.2
        return re*(np.sqrt(np.dot(ynew[0:3],ynew[0:3]))-1)-self.h0

    def regfalsi_aux_mageq(self,step,y0,s):
        """
        Return value of step that takes field line to magnetic equator
        
        """
        auxiliary = self.modelsub
        ynew=self.gi.rk4_int(auxiliary,y0,s,step)
        return self.drbyds(ynew[0:3])
        

