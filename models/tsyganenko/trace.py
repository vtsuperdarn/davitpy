"""
*******************************
MODULE: models.tsyganenko.trace
*******************************

This module contains the following functions:

  trace

This module contains the following classes:

  tsygTrace

*******************************
"""

class tsygTrace(object):
    def __init__(self, lat, lon, rho, coords='geo', datetime=None,
        vswgse=[-400.,0.,0.], pdyn=2., dst=-5., byimf=0., bzimf=-5.,
        lmax=5000, rmax=60., rmin=1., dsmax=0.01, err=0.000001):
        """
|   **PACKAGE**: models.tsyganenko.trace
|   **FUNCTION**: trace(lat, lon, rho, coords='geo', datetime=None,
|        vswgse=[-400.,0.,0.], Pdyn=2., Dst=-5., ByIMF=0., BzIMF=-5.
|        lmax=5000, rmax=60., rmin=1., dsmax=0.01, err=0.000001)
|   **PURPOSE**: trace magnetic field line(s) from point(s)
|
|   **INPUTS**:
|       **lat**: latitude [degrees]
|       **lon**: longitude [degrees]
|       **rho**: distance from center of the Earth [km]
|       **[coords]**: coordinates used for start point ['geo']
|       **[datetime]**: a python datetime object
|       **[vswgse]**: solar wind velocity in GSE coordinates [m/s, m/s, m/s]
|       **[pdyn]**: solar wind dynamic pressure [nPa]
|       **[dst]**: Dst index [nT]
|       **[byimf]**: IMF By [nT]
|       **[bzimf]**: IMF Bz [nT]
|       **[lmax]**: maximum number of points to trace
|       **[rmax]**: upper trace boundary in Re
|       **[rmin]**: lower trace boundary in Re
|       **[dsmax]**: maximum tracing step size
|       **[err]**: tracing step tolerance
|
|   **OUTPUTS**:
|       Elements of this object:
|       **.lat[N/S]H**: latitude of the trace footpoint in Northern/Southern hemispher
|       **.lon[N/S]H**: longitude of the trace footpoint in Northern/Southern hemispher
|       **.rho[N/S]H**: distance of the trace footpoint in Northern/Southern hemispher
|
|   **EXAMPLES**:
|
|
|   Written by Sebastien 20121005
        """
        self.lat = lat
        self.lon = lon
        self.rho = rho
        self.coords = coords
        self.datetime = datetime
        self.vswgse = vswgse
        self.pdyn = pdyn
        self.dst = dst
        self.byimf = byimf
        self.bzimf = bzimf
        iTest = self.__test_valid__()
        if not iTest: self.__del__()
        self.trace()


    def __test_valid__(self):
        """
|   Test the validity of input arguments to the tsygTrace class and trace method
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
        # Make sure they're all the sam elength
        assert (len(self.lat) == len(self.lon) == len(self.rho)), 'lat, lon and rho must me the same length'
        
        return True


    def trace(self, lat=None, lon=None, rho=None, coords=None, datetime=None,
        vswgse=None, pdyn=None, dst=None, byimf=None, bzimf=None,
        lmax=5000, rmax=60., rmin=1., dsmax=0.01, err=0.000001):
        """
|   See tsygTrace for a description of each parameter
|   Any unspecified parameter default to the one stored in the object
|   Unspecified lmax, rmax, rmin, dsmax, err has a set default value
        """
        from models.tsyganenko import tsygFort
        from numpy import radians, degrees, zeros
        from datetime import datetime as pydt

        # Store existing values of class attributes in case something is wrong
        # and we need to revert back to them
        if lat: _lat = self.lat
        if lon: _lon = self.lon
        if rho: _rho = self.rho
        if coords: _coords = self.coords
        if vswgse: _vswgse = self.vswgse

        # Pass position if new
        if lat: self.lat = lat
        lat = self.lat
        if lon: self.lon = lon
        lon = self.lon
        if rho: self.rho = rho
        rho = self.rho

        # Set necessary parameters if new
        if coords: self.coords = coords
        coords = self.coords
        if datetime: self.datetime = datetime
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

        # Declare the same Re as used in Tsyganenko models [km]
        Re = 6371.2
        
        # Initialize trace array
        self.l = zeros(len(lat))
        self.xTrace = zeros((len(lat),2*lmax))
        self.yTrace = self.xTrace.copy()
        self.zTrace = self.xTrace.copy()
        self.xGsw = []
        self.yGsw = []
        self.zGsw = []
        self.latNH = []
        self.lonNH = []
        self.rhoNH = []
        self.latSH = []
        self.lonSH = []
        self.rhoSH = []

        # If no datetime is provided, defaults to today
        if not datetime: datetime = pydt.utcnow()

        # This has to be called first
        tsygFort.recalc_08(datetime.year,datetime.timetuple().tm_yday,
                                datetime.hour,datetime.minute,datetime.second,
                                vswgse[0],vswgse[1],vswgse[2])

        # And now iterate through the desired points
        for ip in xrange(len(lat)):
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
            self.xGsw = xgsw
            self.yGsw = ygsw
            self.zGsw = zgsw

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
                    self.latSH.append( 90. - degrees(geoColat) )
                    self.lonSH.append( degrees(geoLon) )
                    self.rhoSH.append( geoR*Re )
                elif mapto == -1:
                    self.latNH.append( 90. - degrees(geoColat) )
                    self.lonNH.append( degrees(geoLon) )
                    self.rhoNH.append( geoR*Re )
                    
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


    def plot3d(self, xyzlim=None):
        """
|   Generate a 3D plot of the trace
        """
        from mpl_toolkits.mplot3d import proj3d
        from numpy import pi, linspace, outer, ones, size, cos, sin, radians
        from pylab import figure, show

        fig = figure(figsize=(10,10))
        ax = fig.add_subplot(111, projection='3d')

        # First plot a nice sphere for the Earth
        u = linspace(0, 2 * pi, 179)
        v = linspace(0, pi, 179)
        tx = outer(cos(u), sin(v))
        ty = outer(sin(u), sin(v))
        tz = outer(ones(size(u)), cos(v))
        ax.plot_surface(tx,ty,tz,rstride=10, cstride=10, color='grey', alpha=.5, zorder=2, linewidth=0.5)

        # Then plot the traced field line
        for ip in xrange(len(self.lat)):
            ax.plot3D(  self.xTrace[ip,0:self.l[ip]],
                        self.yTrace[ip,0:self.l[ip]],
                        self.zTrace[ip,0:self.l[ip]], 
                        zorder=3, linewidth=2, color='y')

        # Set plot limits
        if not xyzlim:
            xyzlim = max( [ ax.get_xlim3d().max(),
                         ax.get_ylim3d().max(),
                         ax.get_zlim3d().max(), ] )
        ax.set_xlim3d([-xyzlim,xyzlim])
        ax.set_ylim3d([-xyzlim,xyzlim])
        ax.set_zlim3d([-xyzlim,xyzlim])

        show()

        return ax