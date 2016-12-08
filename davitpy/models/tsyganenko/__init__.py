# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""tsyganenko module

This modules containes the following object(s):

Classes
-------------------------------------------------------------
tsygTrace   Wraps fortran subroutines in one convenient class
-------------------------------------------------------------

Module
-------------------------------
tsygFort    Fortran subroutines
-------------------------------

"""

import tsygFort
import logging

class tsygTrace(object):
    """models.tsyganenko.trace

    Trace magnetic field line(s) from point(s)

    Parameters
    ----------
    lat : Optional[ ]
        latitude [degrees]
    lon : Optional[ ]
        longitude [degrees]
    rho : Optional[ ]
        distance from center of the Earth [km]
    filename : Optional[ ]
        load a trace object directly from a file
    coords : Optional[str]
        coordinates used for start point ['geo']
    datetime : Optional[datetime]
        a python datetime object
    vswgse : Optional[list, float]
        solar wind velocity in GSE coordinates [m/s, m/s, m/s]
    pdyn : Optional[float]
        solar wind dynamic pressure [nPa]
    dst : Optional[flaot]
        Dst index [nT]
    byimf : Optional[float]
        IMF By [nT]
    bzimf : Optional[float]
        IMF Bz [nT]
    lmax : Optional[int]
        maximum number of points to trace
    rmax : Optional[float]
        upper trace boundary in Re
    rmin : Optional[float]
        lower trace boundary in Re
    dsmax : Optional[float]
        maximum tracing step size
    err : Optional[float]
        tracing step tolerance

    Attributes
    ----------
    lat :
        latitude [degrees]
    lon :
        longitude [degrees]
    rho :
        distance from center of the Earth [km]
    coords : str
        coordinates used for start point ['geo']
    vswgse : list
        solar wind velocity in GSE coordinates [m/s, m/s, m/s]
    pdyn : float
        solar wind dynamic pressure [nPa]
    dst : flaot
        Dst index [nT]
    byimf : float
        IMF By [nT]
    bzimf : float
        IMF Bz [nT]
    datetime : Optional[datetime]
        a python datetime object

    Returns
    -------
    Elements of this object:
    lat[N/S]H :
        latitude of the trace footpoint in Northern/Southern hemispher
    lon[N/S]H :
        longitude of the trace footpoint in Northern/Southern hemispher
    rho[N/S]H :
        distance of the trace footpoint in Northern/Southern hemispher

    Examples
    --------
        from numpy import arange, zeros, ones
        import tsyganenko
        # trace a series of points
        lats = arange(10, 90, 10)
        lons = zeros(len(lats))
        rhos = 6372.*ones(len(lats))
        trace = tsyganenko.tsygTrace(lats, lons, rhos)
        # Print the results nicely
        print trace
        # Plot the traced field lines
        ax = trace.plot()
        # Or generate a 3d view of the traced field lines
        ax = trace.plot3d()
        # Save your trace to a file for later use
        trace.save('trace.dat')
        # And when you want to re-use the saved trace
        trace = tsyganenko.tsygTrace(filename='trace.dat')

    Notes
    -----
    **FUNCTION**: trace(lat, lon, rho, coords='geo', datetime=None,
         vswgse=[-400.,0.,0.], Pdyn=2., Dst=-5., ByIMF=0., BzIMF=-5.
         lmax=5000, rmax=60., rmin=1., dsmax=0.01, err=0.000001)

    Written by Sebastien 2012-10

    """
    def __init__(self, lat=None, lon=None, rho=None, filename=None, 
        coords='geo', datetime=None,
        vswgse=[-400.,0.,0.], pdyn=2., dst=-5., byimf=0., bzimf=-5.,
        lmax=5000, rmax=60., rmin=1., dsmax=0.01, err=0.000001):
        from datetime import datetime as pydt

        assert (None not in [lat, lon, rho]) or filename, 'You must provide either (lat, lon, rho) or a filename to read from'

        if None not in [lat, lon, rho]: 
            self.lat = lat
            self.lon = lon
            self.rho = rho
            self.coords = coords
            self.vswgse = vswgse
            self.pdyn = pdyn
            self.dst = dst
            self.byimf = byimf
            self.bzimf = bzimf
            # If no datetime is provided, defaults to today
            if datetime is None: datetime = pydt.utcnow()
            self.datetime = datetime

            iTest = self.__test_valid__()
            if not iTest: self.__del__()

            self.trace()

        elif filename:
            self.load(filename)


    def __test_valid__(self):
        """Test the validity of input arguments to the tsygTrace class and trace method

        Written by Sebastien 2012-10
        """
        assert (len(self.vswgse) == 3), 'vswgse must have 3 elements'
        assert (self.coords.lower() == 'geo'), '{}: this coordinae system is not supported'.format(self.coords.lower())
        # A provision for those who want to batch trace
        try:
            [l for l in self.lat]
        except:
            self.lat = [self.lat]
        try:
            [l for l in self.lon]
        except:
            self.lon = [self.lon]
        try:
            [r for r in self.rho]
        except:
            self.rho = [self.rho]
        try:
            [d for d in self.datetime]
        except:
            self.datetime = [self.datetime for l in self.lat]
        # Make sure they're all the sam elength
        assert (len(self.lat) == len(self.lon) == len(self.rho) == len(self.datetime)), \
            'lat, lon, rho and datetime must me the same length'
        
        return True


    def trace(self, lat=None, lon=None, rho=None, coords=None, datetime=None,
        vswgse=None, pdyn=None, dst=None, byimf=None, bzimf=None,
        lmax=5000, rmax=60., rmin=1., dsmax=0.01, err=0.000001):
        """See tsygTrace for a description of each parameter
        Any unspecified parameter default to the one stored in the object
        Unspecified lmax, rmax, rmin, dsmax, err has a set default value

        Parameters
        ----------
        lat : Optional[ ]
            latitude [degrees]
        lon : Optional[ ]
            longitude [degrees]
        rho : Optional[ ]
            distance from center of the Earth [km]
        coords : Optional[str]
            coordinates used for start point ['geo']
        datetime : Optional[datetime]
            a python datetime object
        vswgse : Optional[list, float]
            solar wind velocity in GSE coordinates [m/s, m/s, m/s]
        pdyn : Optional[float]
            solar wind dynamic pressure [nPa]
        dst : Optional[flaot]
            Dst index [nT]
        byimf : Optional[float]
            IMF By [nT]
        bzimf : Optional[float]
            IMF Bz [nT]
        lmax : Optional[int]
            maximum number of points to trace
        rmax : Optional[float]
            upper trace boundary in Re
        rmin : Optional[float]
            lower trace boundary in Re
        dsmax : Optional[float]
            maximum tracing step size
        err : Optional[float]
            tracing step tolerance

        Written by Sebastien 2012-10

        """

        from numpy import radians, degrees, zeros

        # Store existing values of class attributes in case something is wrong
        # and we need to revert back to them
        if lat: _lat = self.lat
        if lon: _lon = self.lon
        if rho: _rho = self.rho
        if coords: _coords = self.coords
        if vswgse: _vswgse = self.vswgse
        if not datetime is None: _datetime = self.datetime

        # Pass position if new
        if lat: self.lat = lat
        lat = self.lat
        if lon: self.lon = lon
        lon = self.lon
        if rho: self.rho = rho
        rho = self.rho
        if not datetime is None: self.datetime = datetime
        datetime = self.datetime

        # Set necessary parameters if new
        if coords: self.coords = coords
        coords = self.coords
        if not datetime is None: self.datetime = datetime
        datetime = self.datetime
        if vswgse: self.vswgse = vswgse
        vswgse = self.vswgse
        if pdyn: self.pdyn = pdyn
        pdyn = self.pdyn
        if dst: self.dst = dst
        dst = self.dst
        if byimf: self.byimf = byimf
        byimf = self.byimf
        if bzimf: self.bzimf = bzimf
        bzimf = self.bzimf

        # Test that everything is in order, if not revert to existing values
        iTest = self.__test_valid__()
        if not iTest: 
            if lat: self.lat = _lat
            if lon: _self.lon = lon
            if rho: self.rho = _rho
            if coords: self.coords = _coords 
            if vswgse: self.vswgse = _vswgse
            if not datetime is None: self.datetime = _datetime

        # Declare the same Re as used in Tsyganenko models [km]
        Re = 6371.2
        
        # Initialize trace array
        self.l = zeros(len(lat))
        self.xTrace = zeros((len(lat),2*lmax))
        self.yTrace = self.xTrace.copy()
        self.zTrace = self.xTrace.copy()
        self.xGsw = self.l.copy()
        self.yGsw = self.l.copy()
        self.zGsw = self.l.copy()
        self.latNH = self.l.copy()
        self.lonNH = self.l.copy()
        self.rhoNH = self.l.copy()
        self.latSH = self.l.copy()
        self.lonSH = self.l.copy()
        self.rhoSH = self.l.copy()

        # And now iterate through the desired points
        for ip in xrange(len(lat)):
            # This has to be called first
            tsygFort.recalc_08(datetime[ip].year,datetime[ip].timetuple().tm_yday,
                                datetime[ip].hour,datetime[ip].minute,datetime[ip].second,
                                vswgse[0],vswgse[1],vswgse[2])

            # Convert lat,lon to geographic cartesian and then gsw
            r, theta, phi, xgeo, ygeo, zgeo = tsygFort.sphcar_08(
                                                    rho[ip]/Re, radians(90.-lat[ip]), radians(lon[ip]),
                                                    0., 0., 0.,
                                                    1)
            if coords.lower() == 'geo':
                xgeo, ygeo, zgeo, xgsw, ygsw, zgsw = tsygFort.geogsw_08(
                                                            xgeo, ygeo, zgeo,
                                                            0. ,0. ,0. ,
                                                            1)
            self.xGsw[ip] = xgsw
            self.yGsw[ip] = ygsw
            self.zGsw[ip] = zgsw

            # Trace field line
            inmod = 'IGRF_GSW_08'
            exmod = 'T96_01'
            parmod = [pdyn, dst, byimf, bzimf, 0, 0, 0, 0, 0, 0]
            # First towards southern hemisphere
            maptoL = [-1, 1]
            for mapto in maptoL:
                xfgsw, yfgsw, zfgsw, xarr, yarr, zarr, l = tsygFort.trace_08( xgsw, ygsw, zgsw,
                                                                mapto, dsmax, err, rmax, rmin, 0,
                                                                parmod, exmod, inmod,
                                                                lmax )

                # Convert back to spherical geographic coords
                xfgeo, yfgeo, zfgeo, xfgsw, yfgsw, zfgsw  = tsygFort.geogsw_08(
                                                                    0. ,0. ,0. ,
                                                                    xfgsw, yfgsw, zfgsw,
                                                                    -1)
                geoR, geoColat, geoLon, xgeo, ygeo, zgeo = tsygFort.sphcar_08(
                                                                    0., 0., 0.,
                                                                    xfgeo, yfgeo, zfgeo,
                                                                    -1)

                # Get coordinates of traced point
                if mapto == 1:
                    self.latSH[ip] = 90. - degrees(geoColat)
                    self.lonSH[ip] = degrees(geoLon)
                    self.rhoSH[ip] = geoR*Re
                elif mapto == -1:
                    self.latNH[ip] = 90. - degrees(geoColat)
                    self.lonNH[ip] = degrees(geoLon)
                    self.rhoNH[ip] = geoR*Re
                    
                # Store trace
                if mapto == -1:
                    self.xTrace[ip,0:l] = xarr[l-1::-1]
                    self.yTrace[ip,0:l] = yarr[l-1::-1]
                    self.zTrace[ip,0:l] = zarr[l-1::-1]
                elif mapto == 1:
                    self.xTrace[ip,self.l[ip]:self.l[ip]+l] = xarr[0:l]
                    self.yTrace[ip,self.l[ip]:self.l[ip]+l] = yarr[0:l]
                    self.zTrace[ip,self.l[ip]:self.l[ip]+l] = zarr[0:l]
                self.l[ip] += l

        # Resize trace output to more minimum possible length
        self.xTrace = self.xTrace[:,0:self.l.max()]
        self.yTrace = self.yTrace[:,0:self.l.max()]
        self.zTrace = self.zTrace[:,0:self.l.max()]


    def __str__(self):
        """Print object information in a nice way

        Written by Sebastien 2012-10
        """
        # Declare print format
        outstr =    '''
vswgse=[{:6.0f},{:6.0f},{:6.0f}]    [m/s]
pdyn={:3.0f}                        [nPa]
dst={:3.0f}                         [nT]
byimf={:3.0f}                       [nT]
bzimf={:3.0f}                       [nT]
                    '''.format(self.vswgse[0],
                               self.vswgse[1],
                               self.vswgse[2],
                               self.pdyn,
                               self.dst,
                               self.byimf,
                               self.bzimf)
        outstr += '\nCoords: {}\n'.format(self.coords)
        outstr += '(latitude [degrees], longitude [degrees], distance from center of the Earth [km])\n'

        # Print stuff
        for ip in xrange(len(self.lat)):
            outstr +=   '''
({:6.3f}, {:6.3f}, {:6.3f}) @ {}
    --> NH({:6.3f}, {:6.3f}, {:6.3f})
    --> SH({:6.3f}, {:6.3f}, {:6.3f}) 
                        '''.format(self.lat[ip], self.lon[ip], self.rho[ip], 
                                   self.datetime[ip].strftime('%H:%M UT (%d-%b-%y)'), 
                                   self.latNH[ip], self.lonNH[ip], self.rhoNH[ip], 
                                   self.latSH[ip], self.lonSH[ip], self.rhoSH[ip])

        return outstr


    def save(self, filename):
        """Save trace information to a file

        Parameters
        ----------
        filename : str

        Written by Sebastien 2012-10

        """
        import cPickle as pickle

        with open( filename, "wb" ) as fileObj:
            pickle.dump(self, fileObj)


    def load(self, filename):
        """load trace information from a file

        Parameters
        ----------
        filename : str

        Written by Sebastien 2012-10
        """
        import cPickle as pickle

        with open( filename, "rb" ) as fileObj:
            obj = pickle.load(fileObj)
            for k, v in obj.__dict__.items():
                self.__dict__[k] = v


    def plot(self, proj='xz', color='b', onlyPts=None, showPts=False, 
        showEarth=True, disp=True, **kwargs):
        """Generate a 2D plot of the trace projected onto a given plane
        Graphic keywords apply to the plot method for the field lines

        Parameters
        ----------
        proj : Optional[str]
            the projection plane in GSW coordinates
        color : Optional[char]
            field line color
        onlyPts : Optional[ ]
            if the trace countains multiple point, only show the specified indices (list)
        showEarth : Optional[bool]
            Toggle Earth disk visibility on/off
        showPts : Optional[bool]
            Toggle start points visibility on/off
        disp : Optional[bool]
            invoke pylab.show()
        **kwargs :
            see matplotlib.axes.Axes.plot

        Returns
        -------
        ax : matplotlib axes object

        Written by Sebastien 2012-10

        """
        from pylab import gcf, gca, show
        from matplotlib.patches import Circle
        from numpy import pi, linspace, outer, ones, size, cos, sin, radians, cross
        from numpy.ma import masked_array

        assert (len(proj) == 2) or \
            (proj[0] in ['x','y','z'] and proj[1] in ['x','y','z']) or \
            (proj[0] != proj[1]), 'Invalid projection plane'

        fig = gcf()
        ax = fig.gca()
        ax.set_aspect('equal')

        # First plot a nice disk for the Earth
        if showEarth:
            circ = Circle(xy=(0,0), radius=1, facecolor='0.8', edgecolor='k', alpha=.5, zorder=0)
            ax.add_patch(circ)

        # Select indices to show
        if onlyPts is None:
            inds = xrange(len(self.lat))
        else:
            try:
                inds = [ip for ip in onlyPts]
            except:
                inds = [onlyPts]

        # Then plot the traced field line
        for ip in inds:
            # Select projection plane
            if proj[0] == 'x':
                xx = self.xTrace[ip,0:self.l[ip]]
                xpt = self.xGsw[ip]
                ax.set_xlabel(r'$X_{GSW}$')
                xdir = [1,0,0]
            elif proj[0] == 'y':
                xx = self.yTrace[ip,0:self.l[ip]]
                xpt = self.yGsw[ip]
                ax.set_xlabel(r'$Y_{GSW}$')
                xdir = [0,1,0]
            elif proj[0] == 'z':
                xx = self.zTrace[ip,0:self.l[ip]]
                xpt = self.zGsw[ip]
                ax.set_xlabel(r'$Z_{GSW}$')
                xdir = [0,0,1]
            if proj[1] == 'x':
                yy = self.xTrace[ip,0:self.l[ip]]
                ypt = self.xGsw[ip]
                ax.set_ylabel(r'$X_{GSW}$')
                ydir = [1,0,0]
            elif proj[1] == 'y':
                yy = self.yTrace[ip,0:self.l[ip]]
                ypt = self.yGsw[ip]
                ax.set_ylabel(r'$Y_{GSW}$')
                ydir = [0,1,0]
            elif proj[1] == 'z':
                yy = self.zTrace[ip,0:self.l[ip]]
                ypt = self.zGsw[ip]
                ax.set_ylabel(r'$Z_{GSW}$')
                ydir = [0,0,1]
            sign = 1 if -1 not in cross(xdir,ydir) else -1
            if 'x' not in proj: 
                zz = sign*self.xGsw[ip]
                indMask = sign*self.xTrace[ip,0:self.l[ip]] < 0
            if 'y' not in proj: 
                zz = sign*self.yGsw[ip]
                indMask = sign*self.yTrace[ip,0:self.l[ip]] < 0
            if 'z' not in proj: 
                zz = sign*self.zGsw[ip]
                indMask = sign*self.zTrace[ip,0:self.l[ip]] < 0
            # Plot
            ax.plot(masked_array(xx, mask=~indMask), 
                    masked_array(yy, mask=~indMask), 
                    zorder=-1, color=color, **kwargs)
            ax.plot(masked_array(xx, mask=indMask), 
                    masked_array(yy, mask=indMask), 
                    zorder=1, color=color, **kwargs)
            if showPts:
                ax.scatter(xpt, ypt, c='k', s=40, zorder=zz)

        if disp: show()

        return ax


    def plot3d(self, onlyPts=None, showEarth=True, showPts=False, disp=True, 
        xyzlim=None, zorder=1, linewidth=2, color='b', **kwargs):
        """Generate a 3D plot of the trace
        Graphic keywords apply to the plot3d method for the field lines

        Parameters
        ----------
        onlyPts : Optional[ ]
            if the trace countains multiple point, only show the specified indices (list)
        showEarth : Optional[bool]
            Toggle Earth sphere visibility on/off
        showPts : Optional[bool]
            Toggle start points visibility on/off
        disp : Optional[bool]
            invoke pylab.show()
        xyzlim : Optional[ ]
            3D axis limits
        zorder : Optional[int]
            3D layers ordering
        linewidth : Optional[int]
            field line width
        color : Optional[char]
            field line color
        **kwargs :
            see mpl_toolkits.mplot3d.axes3d.Axes3D.plot3D

        Returns
        -------
        ax :  matplotlib axes
            axes object

        Written by Sebastien 2012-10

        """
        from mpl_toolkits.mplot3d import proj3d
        from numpy import pi, linspace, outer, ones, size, cos, sin, radians
        from pylab import gca, gcf, show

        fig = gcf()
        ax = fig.gca(projection='3d')

        # First plot a nice sphere for the Earth
        if showEarth:
            u = linspace(0, 2 * pi, 179)
            v = linspace(0, pi, 179)
            tx = outer(cos(u), sin(v))
            ty = outer(sin(u), sin(v))
            tz = outer(ones(size(u)), cos(v))
            ax.plot_surface(tx,ty,tz,rstride=10, cstride=10, color='grey', alpha=.5, zorder=0, linewidth=0.5)


        # Select indices to show
        if onlyPts is None:
            inds = xrange(len(self.lat))
        else:
            try:
                inds = [ip for ip in onlyPts]
            except:
                inds = [onlyPts]

        # Then plot the traced field line
        for ip in inds:
            ax.plot3D(  self.xTrace[ip,0:self.l[ip]],
                        self.yTrace[ip,0:self.l[ip]],
                        self.zTrace[ip,0:self.l[ip]], 
                        zorder=zorder, linewidth=linewidth, color=color, **kwargs)
            if showPts:
                ax.scatter3D(self.xGsw[ip], self.yGsw[ip], self.zGsw[ip], c='k')

        # Set plot limits
        if not xyzlim:
            xyzlim = max( [ ax.get_xlim3d().max(),
                         ax.get_ylim3d().max(),
                         ax.get_zlim3d().max(), ] )
        ax.set_xlim3d([-xyzlim,xyzlim])
        ax.set_ylim3d([-xyzlim,xyzlim])
        ax.set_zlim3d([-xyzlim,xyzlim])

        if disp: show()

        return ax
