import numpy as np
import scipy as sp

import ginteg as gint
import emapaux as aux
import igrf as ig

 
  
  

class Driv(object):

    """
    Control routines for field line trace and electric field map
    
    
    """
    
    def __init__(self,iyr,iday,model,cond,h0):
        self.year=iyr
        self.day=iday
        self.md = model
        self.cd = cond
        self.h0 = h0
        self.au=aux.Aux(self.year,self.day,self.md,self.cd,self.h0)
        self.gi=gint.Ginteg()
        if self.md == 'igrfb':
            self.neq = 3
        else:
            self.neq = 9

    def rk4_driver(self,auxiliary,y,step,nsteps,*args,**kwargs):
        """
        Return result of advancing Runge Kutta integration by nsteps steps
      
        Parameters:
        auxiliary: Of the form auxinst.name where aux is an instance of the class Aux in 
           module emapaux that defines the model and name is the Aux method that returns dy/ds
           for the model.
        neq (int): Number of 1st order differential equations to be integrated
        step (float): step length
        nsteps (int): Maximum number of steps
        condition: User defined function that specifies condition 
            for exit. Default function allows for integration to be advanced the full
            number of steps, nsteps
        parameter list (y, s, default=None).
        aux (optional): List of any additional parameters required by the 
            user defined auxiliary function.
    
        Returns:
        yarr (float array): Array of shape (nsteps+1,neq) containing value of
              y after each step
        sarr (float): Array of size nsteps+1 containg values of independent 
              variable after each step.
    
    
        Developer: A D M Walker
    
        """
        yarr=np.array([])
        sarr=np.arange(0.,(nsteps+1.)*step,step)
        barr=np.array([])
        bvec=self.au.igb.bgc(y[0],y[1],y[2])
        i=1
        for s in sarr:
            yarr=np.append(yarr,y)
            barr=np.append(barr,bvec)
            i=i+1
            # Advance integration by one step
            y=self.gi.rk4_int(auxiliary,y,s,step,*args,**kwargs)
            if self.md != 'igrfb':
                # Test orthogonality of w and magnetic field
                # test omitted if only simple field trace. 
                check,wdotmu1,wdotmu2,bvec=self.au.flag(y,*args,**kwargs)
                if (check==False): print 'Violation of precision criterion s=',s
            # Test exit condition
            test=self.au.condition(y,s,*args,**kwargs)
            if (test == True):
                return np.reshape(np.append(yarr,y),(-1,self.neq)),sarr[0:i],barr
        # Return on maximum number of iterations
        return np.reshape(yarr,(-1,self.neq)),sarr[0:i],barr

    def regfalsi_driver(self,yarr,sarr,auxiliary_rf,auxiliary_rk):
        """
        yarr,sarr: result of calculation by method rk4_driver.
        auxiliary_rf: auxiliary routine of the form auxinst.name where aux is an instance 
           of the class Aux in module emapaux that defines the model and name is the Aux method
           for regfalsi.
        auxiliary_rk: auxiliary for RK4 method, of the form auxinst.name where auxinst is 
           an instance of the class Aux in module emapaux that defines the model and name 
           is the Aux method that returns dy/ds for the model.
        
        """
        y0 = yarr[-2,]
        s = sarr[-2]
        step1 = 0.
        step2 = sarr[-1]-sarr[-2]
        args = (y0,s)
        step,counter = self.gi.reg_falsi(auxiliary_rf,step1,step2,1.e-5,10,*args)
        yout = np.append(yarr[0:-1,],self.gi.rk4_int(auxiliary_rk,y0,s,step))
        sout = np.append(sarr[0:-1],sarr[-2]+step)
        return np.reshape(yout,(-1,self.neq)),sout


    def efield(self,emerid,eazim,wxarraz,wyarraz,wzarraz,wxarrmerid,wyarrmerid,wzarrmerid):
        """
        Return electric field in GEO coordinate system
        """
        waz=np.sqrt(wxarraz**2+wyarraz**2+wzarraz**2)
        wmerid=np.sqrt(wxarrmerid**2+wyarrmerid**2+wzarrmerid**2)
        costheta=(wxarraz*wxarrmerid+wyarraz*wyarrmerid+wzarraz*wzarrmerid)/(waz*wmerid)
        sin2theta=1.-costheta**2
        eazarrcov = eazim/waz
        emeridarrcov = emerid/wmerid
        eazarrcont = (eazarrcov-emeridarrcov*costheta)/sin2theta
        emeridarrcont = (emeridarrcov-eazarrcov*costheta)/sin2theta
        exarr = eazarrcont*wxarraz/waz+emeridarrcont*wxarrmerid/wmerid
        eyarr = eazarrcont*wyarraz/waz+emeridarrcont*wyarrmerid/wmerid
        ezarr = eazarrcont*wzarraz/waz+emeridarrcont*wzarrmerid/wmerid
        return exarr,eyarr,ezarr
    
    def etransf(self,x,y,z,ex,ey,ez,bx,by,bz):
        """
        Return azimuthal and meridional components of E
        """
        mu = np.array([bx,by,bz])/np.sqrt(bx**2+by**2+bz**2)
        runit = np.array([x,y,z])/np.sqrt(x**2+y**2+z**2)
        azvec = np.cross(mu,runit)
        azunit = azvec/np.sqrt(sum(azvec*azvec))
        meridunit = np.cross(azunit,mu)
        e = np.array([ex,ey,ez])
        return sum(e*azunit), sum(e*meridunit)



    
    def e_trace(self,lat,lon,hinit,step,nsteps):  
        """
        Return coordinates of field line trace and field line separations in GEO system
    
        """
        theta=np.pi/2. - np.deg2rad(lat)
        phi=np.deg2rad(lon)
        r=(6371.2+hinit)/6371.2
        # Set up IGRF model
        rarr=np.array([r*np.sin(theta)*np.cos(phi),r*np.sin(theta)*np.sin(phi),r*np.cos(theta)])
        bvec = ig.Bmath(self.year,self.day).bgeog(r,theta,phi)
        mu=bvec/np.sqrt(sum(bvec*bvec))        # Unit B in geographic coords
        if self.md == 'igrfb':
            y_array=np.reshape(rarr,-1)
        else:
            runit=rarr/r                        # Unit r in geographic coordinates
            wazvec=np.cross(mu,runit)
            warraz=wazvec/np.sqrt(sum(wazvec*wazvec)) # Unit vector in eastward magnetic 
            #                                     azimuthal direction - geog coords
            warrmerid=np.cross(warraz,mu)       # Unit outward transverse vector in 
            #                                     mag meridian - geographic 
            #                                     coordinates
            y_array=np.reshape([rarr,warraz,warrmerid],-1)
        auxiliary_rk = self.au.modelsub
        # Perform integration and exit when exit condition has been passed.
        outarray,strunc,barr = self.rk4_driver(auxiliary_rk,y_array,step,nsteps)
        if (np.size(strunc) > nsteps):
            print 'Maximum number of steps exceeded'
            return np.reshape(outarray,(-1,self.neq)),strunc,barr
        if self.cd == 'equator':
            outarray,strunc = self.au.check_drbyds(outarray,strunc)
        auxiliary_rf=self.au.condsub
        yarr,sarr = self.regfalsi_driver(outarray,strunc,auxiliary_rf,auxiliary_rk)
        npts = np.size(sarr)
        ylast = yarr[npts-1,0:3]
        blast =  ig.Bmath(self.year,self.day).bgc(ylast[0],ylast[1],ylast[2])
        return yarr, sarr, np.append(barr,blast)




