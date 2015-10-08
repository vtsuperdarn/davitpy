
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch
#import mpl_toolkits.mplot3d.art3d as art3d
import matplotlib.lines as mlines
#from mpl_toolkits.mplot3d import Axes3D
from mayavi import mlab

class BGraph3d(object):
    """
    emap graphics routines
    
    CLASSES:
    BGraph2d: Graphics routines using matplotlib
    BGraph3d: Visualizations in three dimensions using Mayavi2
    
    NOTES:
    The coordinate systems used are appropriate to electrostatic fields.
    
    Global cartesian (gc) coordinates are geocentric right handed coordinates
    x is in the Greenwich meridian plane perpendicular to the rotation axis.
    y is eastwards
    z is parallel to the rotation axis and towards the north pole.
    
    
    """
    
    
    def __init__(self):
        pass
        
    
    @mlab.show
    def visual_e(self,xarr,yarr,zarr,exarr,eyarr,ezarr):
        """
        Mayavi visualization of field line and mapped E field
        
        INPUT:
        xarr, yarr, zarr: x, y, z, coordinates of points on field line in gc oordinates
        exarr, eyarr, ezarr: Vector components of electric field (arbitrary units)
        
        """
        u = np.linspace(0, 2 * np.pi, 36.)
        v = np.linspace(0, np.pi, 180.)
    
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        mlab.figure(bgcolor=(1.,1.,1.),size = (1680,1050))
        # Display continents outline, using the VTK Builtin surface 'Earth'
        from mayavi.sources.builtin_surface import BuiltinSurface
        continents_src = BuiltinSurface(source='earth', name='Continents')
        # continents outline.
        continents_src.data_source.on_ratio = 2
        continents = mlab.pipeline.surface(continents_src, color=(0, 0, 0))
        mlab.plot3d(xarr,yarr,zarr,
                    color = (0.,0.,1.), line_width = 2., tube_radius = None)
        mlab.quiver3d(xarr,yarr,zarr,exarr,eyarr,ezarr,
                      color=(1.,0.25,0.25), line_width=2.)
        mlab.mesh(x,y,z,representation = 'surface', color=(0.9,0.9,1.))
        for theta in np.arange(np.pi/12., np.pi, np.pi/12.):
            phi = np.arange(0., 2.*np.pi, np.pi/100.)
            mlab.plot3d(np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi),
                        np.cos(theta)*np.ones(np.size(phi)),
                        color = (0.,0.,0.), tube_radius = None, line_width = 1.)
        for phi in np.arange(0.,2.*np.pi,np.pi/12.):
            theta = np.arange(0.,np.pi,np.pi/100.)
            mlab.plot3d(1.00*np.sin(theta)*np.cos(phi),1.00*np.sin(theta)*np.sin(phi),
                        1.00*np.cos(theta)*np.ones(np.size(phi)),
                        color=(0.,0.,0.),tube_radius=None,line_width=1.)
        phi=np.arange(0,2.*np.pi,np.pi/100.)
        mlab.plot3d(np.cos(phi), np.sin(phi), np.zeros(np.size(phi)),
                    color = (1.0,0.,0.),tube_radius = None, line_width=2.)
        theta=np.arange(0., np.pi, np.pi/100)
        mlab.plot3d(np.sin(theta), np.zeros(np.size(theta)), np.cos(theta),
                    color = (1.0,0.,0.), tube_radius = None, line_width = 2.)
        mlab.plot3d(-np.sin(theta),np.zeros(np.size(theta)),np.cos(theta),
                    color=(0.,1.0,0.),tube_radius=None,line_width=2.)
        return
        
        
    @mlab.show
    def visual_b(self,xarr,yarr,zarr):
        """
        Mayavi visualization of field line and mapped E field
        
        INPUT:
        xarr, yarr, zarr: x, y, z, coordinates of points on field line in gc oordinates
        exarr, eyarr, ezarr: Vector components of electric field (arbitrary units)
        
        """
        u = np.linspace(0, 2 * np.pi, 36.)
        v = np.linspace(0, np.pi, 180.)
    
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        mlab.figure(bgcolor=(1.,1.,1.),size = (1680,1050))
        # Display continents outline, using the VTK Builtin surface 'Earth'
        from mayavi.sources.builtin_surface import BuiltinSurface
        continents_src = BuiltinSurface(source='earth', name='Continents')
        # continents outline.
        continents_src.data_source.on_ratio = 2
        continents = mlab.pipeline.surface(continents_src, color=(0, 0, 0))
        mlab.plot3d(xarr,yarr,zarr,
                    color = (0.,0.,1.), line_width = 2., tube_radius = None)
        mlab.mesh(x,y,z,representation = 'surface', color=(0.9,0.9,1.))
        for theta in np.arange(np.pi/12., np.pi, np.pi/12.):
            phi = np.arange(0., 2.*np.pi, np.pi/100.)
            mlab.plot3d(np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi),
                        np.cos(theta)*np.ones(np.size(phi)),
                        color = (0.,0.,0.), tube_radius = None, line_width = 1.)
        for phi in np.arange(0.,2.*np.pi,np.pi/12.):
            theta = np.arange(0.,np.pi,np.pi/100.)
            mlab.plot3d(1.00*np.sin(theta)*np.cos(phi),1.00*np.sin(theta)*np.sin(phi),
                        1.00*np.cos(theta)*np.ones(np.size(phi)),
                        color=(0.,0.,0.),tube_radius=None,line_width=1.)
        phi=np.arange(0,2.*np.pi,np.pi/100.)
        mlab.plot3d(np.cos(phi), np.sin(phi), np.zeros(np.size(phi)),
                    color = (1.0,0.,0.),tube_radius = None, line_width=2.)
        theta=np.arange(0., np.pi, np.pi/100)
        mlab.plot3d(np.sin(theta), np.zeros(np.size(theta)), np.cos(theta),
                    color = (1.0,0.,0.), tube_radius = None, line_width = 2.)
        mlab.plot3d(-np.sin(theta),np.zeros(np.size(theta)),np.cos(theta),
                    color=(0.,1.0,0.),tube_radius=None,line_width=2.)
        return
        

class BGraph2d(object):


    """"
    emap matplotlib 2d graphics routines
    
    """

    def __init__(self):
        matplotlib.rcParams.update({'font.size': 18, 'font.family': 'STIXGeneral',
                                    'mathtext.fontset': 'stix'})

    
        

    def plot_azmerid(self,elong,emerid,ea,em):
        """
        
        """
        arr = np.array([abs(elong),abs(emerid),abs(ea),abs(em)])
        ymax = int(np.amax(np.array([emerid, em, 0.])))+10
        ymin = int(np.amin(np.array([emerid, em, 0.])))-15
        xmax = int(np.amax(np.array([elong, ea, 0.])))+10
        xmin = int(np.amin(np.array([elong, ea, 0.])))-15       
        fig = plt.figure(figsize=(8,8))
        axe=fig.add_subplot(1,1,1)
        axe.quiver(0.,0.,elong,emerid,angles='xy',scale_units='xy',scale=1,color='r')
        axe.quiver(0.,0.,ea,em,angles='xy',scale_units='xy',scale=1,color='g')
        axe.set_xlim([xmin,xmax])
        axe.set_ylim([ymin,ymax])
        axe.set_xlabel('Meridional component of $E$ (mV/m)',fontsize=20)
        axe.set_ylabel('Azimuthal component of $E$ (mV/m)',fontsize=20)
        axe.grid(True, which='both')
        axe.axhline(y=0, color='k')
        axe.axvline(x=0, color='k')
        axe.plot([xmin+5.,xmin+15.],[ymin+10.,ymin+10.],'r',label='$E_0$',lw=2)
        axe.annotate('$E_0$',xy=(xmin+15.,ymin+10.),xytext=(xmin+16.,ymin+9.))
        axe.plot([xmin+5.,xmin+15.],[ymin+5.,ymin+5.],'g',label='$E_{\rm end}$',lw=2)
        axe.annotate(r'$E_{\rm end} $',xy=(xmin+15.,ymin+5.),xytext=(xmin+16.,ymin+4.))
        plt.show
        
        

                
    def plot_efield(self,exarr,eyarr,ezarr,strunc,legpos=2):
        """
        Plot electric field and components as function of distance along field line
        """
        fig = plt.figure(figsize=(8,8))
        axe = fig.add_subplot(1,1,1)
        axe.plot(strunc,np.sqrt(exarr**2+eyarr**2+ezarr**2),'k',label='$E$')
        axe.plot(strunc,exarr,'b',label='$E_x$')
        axe.plot(strunc,eyarr,'r',label='$E_y$')
        axe.plot(strunc,ezarr,'g',label='$E_z$')
        axe.legend(loc=legpos, fontsize=18)
        axe.set_xlabel('Distance along field line ($R_E$)',fontsize=20)
        axe.set_ylabel('Electric Field (mV/m)',fontsize=20)
        fig.savefig('/home/david/Documents/current_papers/emap/efieldtemp.eps',
                    bbox_inches="tight")
        plt.show
        return
    
    
        
    def plot_b_field_projection(self,xarr,yarr,zarr,exarr,eyarr,ezarr):
        """
        Plot projection of field line and electric field vectors on global cartesiona planes.
        """
        fig=plt.figure(figsize=(6,15),tight_layout=True)
        ax1= fig.add_subplot(3,1,1)
        ax1.plot(xarr,zarr)
        ax1.quiver(xarr,zarr,exarr,ezarr,color='r')
        ax1.axis('equal')
        ax1.set_xlabel(r'$x\; (R_E)$')
        ax1.set_ylabel(r'$z\; (R_E)$')
        ax2 = fig.add_subplot(3,1,2)
        ax2.axis('equal')
        ax2.plot(yarr,zarr)
        ax2.quiver(yarr,zarr,eyarr,ezarr,color='r')
        ax2.set_xlabel(r'$y\; (R_E)$')
        ax2.set_ylabel(r'$z\; (R_E)$')
        ax3 = fig.add_subplot(3,1,3)
        ax3.plot(xarr,yarr)
        ax3.quiver(xarr,yarr,exarr,eyarr,color='r')
        ax3.axis('equal')
        ax3.set_xlabel(r'$x\; (R_E)$')
        ax3.set_ylabel(r'$y\; (R_E)$')
        fig.savefig('/home/david/Documents/current_papers/emap/bfieldprojtemp.eps',
                bbox_inches="tight")
        plt.show()
        return
    
    
    def plot_width(self,
                   wxarraz,wyarraz,wzarraz,
                   wxarrmerid,wyarrmerid,wzarrmerid,strunc,
                   legpos=2):
        """
        plot gc components of normalized field line separation 
        """
        fig = plt.figure(figsize=(8,16),tight_layout=True)
        axw1 = fig.add_subplot(2,1,1)
        axw1.plot(strunc,np.sqrt(wxarraz**2+wyarraz**2+wzarraz**2),'k',label='$w/w_0$')
        axw1.plot(strunc,wxarraz,'b',label='$w_x/w_0$')
        axw1.plot(strunc,wyarraz,'r',label='$w_y/w_0$')
        axw1.plot(strunc,wzarraz,'g',label='$w_z/w_0$')
        axw1.legend(loc=2)
        axw1.set_xlabel('Distance along field line $(R_E)$')
        axw1.set_ylabel('Normalized azimuthal field line separation$')
        axw2 = fig.add_subplot(2,1,2)
        axw2.plot(strunc,np.sqrt(wxarrmerid**2+wyarrmerid**2+wzarrmerid**2),'k',label='$w/w_0$')
        axw2.plot(strunc,wxarrmerid,'b',label='$w_x/w_0$')
        axw2.plot(strunc,wyarrmerid,'r',label='$w_y/w_0$')
        axw2.plot(strunc,wzarrmerid,'g',label='$w_z/w_0$')
        axw2.legend(loc=legpos)
        axw2.set_xlabel('Distance along field line $(R_E)$')
        axw2.set_ylabel('Normalized meridional field line separation$')
        plt.savefig('/home/david/Documents/current_papers/emap/widthtemp.eps',
                    bbox_inches="tight")
        plt.show()
        plt.rcParams['font.size'] = 12
        return
