import numpy as np
import scipy as sp




class Ginteg(object):

    
    """
    
    """
    
    def __init__(self):
        pass
     
    
    def rk4_int(self,aux,y,s,step,*args,**kwargs):    
        """
        Return result of 4th order Runge Kutta integration of 1st order diff. eqns
    
        Parameters:
        aux: User provided function with parameter list 
            (y,s,optional additional parameters). Returns dy/ds.
        y (float): numpy array of initial values of independent variables
        satisfying differential equation.
        s (float): Independent variable.
        auxparams (optional): List of any additional parameters required by 
        the user defined auxiliary function.
        step (float): Steplength.
        *args, **kwargs: Any additional parameters required by auxiliary.
    
        Returns:
        y (float): Updated numpy array giving y at s=s+step.
    
        Notes:
            This is a straightforward fourth order single step Runge-Kutta 
            integration for fixed step length with no adaptive step length control.
            It is suitable for non-stiff equations. It would normally be 
            called by an rk4_driver which would advance the differential equations  
            a defined number of steps. It is similar to the Numerical Recipes 
            version but does not require an initial value of dy/ds to be 
            supplied by the calling routine.
    
        Developer: A D M Walker
        """
        hh = 0.5*step
        h6 = step/6.
        sh = s+hh
        dydx = aux(y,s,*args,**kwargs)
        yt = y+hh*dydx
        dyt = aux(yt,sh,*args,**kwargs)
        yt = y+hh*dyt
        dym = aux(yt,sh,*args,**kwargs)
        yt = y+step*dym
        dym = dyt+dym
        dyt = aux(yt,s+step,*args,**kwargs)
        return y+h6*(dydx+dyt+2.*dym)
    
    def reg_falsi(self,auxiliary_rf,x1,x2,xacc,maxit,*args,**kwargs):
        """
        Return root of auxiliary function=0 using regula falsi
    
        INPUT:
        auxiliary_rf: User defined function with argument 'x' plus optional arguments
            which returns the value of the function whose root is to be found
        x1, x2 (float): Initial guesses bracketing the root.
        xacc (float): Absolute accuracy desired.
        maxit (int): Maximum number of iterations.
        args, kwargs (optional): Any arguments required as parameters by auxiliary_rf  
        
        OUTPUT:
        root (float): Value of root
        counter (int): Number of iterations
    
        NOTES:
        Straightforward Regula Falsi determination of the root of the function
        defined by the auxiliary subroutine. 
        The code is a Python implementation of the algorithm described by Press et al. 
        (Press, WH, Flannery, BP, Teukolski, SA, Vetterling,  WT: "Numerical
        Recipes", Cambridge University Press, 1989)
        
        Originator: A D M Walker
        """
    
        fl=auxiliary_rf(x1,*args,**kwargs)
        fh=auxiliary_rf(x2,*args,**kwargs)
        f=fl
        delta=x1-x2
        if (fl*fh > 0.): # Check that root is bracketed by x1 x2
            raise Exception, "x1, x2 must bracket root" 
        if (fl<0.):
            xl=x1
            xh=x2
        else:
            xl=x2
            xh=x1
            swap=fl
            fl=fh
            fh=swap
        dx=xh-xl
        counter=0 # Count iterations
        while ((abs(delta) > xacc) and (f != 0)): # Iterate to find root
            counter=counter+1
            if (counter > maxit): raise Exception,"No convergence after maxit iterations"
            root=xl+dx*fl/(fl-fh)
            f=auxiliary_rf(root,*args,**kwargs)
            if (f<0.):
                delta=xl-root
                xl=root
                fl=f
            else:
                delta=xh-root
                xh=root
                fh=f
            dx=xh-xl
        return root,counter

    

