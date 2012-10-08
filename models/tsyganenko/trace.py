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
	def __init__(lat, lon, rho, coords='geo', datetime=None,
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
|		**.lat[N/S]H**: latitude of the trace footpoint in Northern/Southern hemispher
|		**.lon[N/S]H**: longitude of the trace footpoint in Northern/Southern hemispher
|		**.rho[N/S]H**: distance of the trace footpoint in Northern/Southern hemispher
|
|   **EXAMPLES**:
|
|
|   Written by Sebastien 20121005
		"""
		self.__test_valid__(lat, lon, rho, coords, vswgse)

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
		self.trace()


	def __test_valid__(self, coords, vswgse):
		"""
| Test the validity of input arguments to the tsygTrace class and trace method
		"""
		assert (len(vswgse) == 3), 'vswgse must have 3 elements'
		assert (coords.lower() == 'geo'), '{}: this coordinae system is not supported'.format(coords.lower())
		# A provision for those who want to batch trace
		try:
			[l for l in lat]
		except:
			lat = [lat]
		try:
			[l for l in lon]
		except:
			lon = [lon]
		try:
			[r for r in rho]
		except:
			rho = [rho]
		# Make sure they're all the sam elength
		assert (len(lat) == len(lon) == len(rho)), 'lat, lon and rho must me the same length'


	def trace(self, lat=None, lon=None, rho=None, coords=None, datetime=None,
		vswgse=None, pdyn=None, dst=None, byimf=None, bzimf=None,
        lmax=5000, rmax=60., rmin=1., dsmax=0.01, err=0.000001):
		"""
|   See tsygTrace for a description of each parameter
|	Any unspecified parameter default to the one stored in the object
|	Unspecified lmax, rmax, rmin, dsmax, err has a set default value
		"""
		from models.tsyganenko import tsygFort
		from numpy import radians, degrees
		from datetime import datetime as pydt

		# Test that everything is in order
		self.__test_valid__(lat, lon, rho, coords, vswgse)

		# Pass position
		if lat: self.lat = lat else lat = self.lat
		if lon: self.lon = lon else lon = self.lon
		if rho: self.rho = rho else rho = self.rho

		# Set necessary parameters
		if coords: self.coords = coords else coords = self.coords
		if datetime: self.datetime = datetime else datetime = self.datetime
		if vswgse: self.vswgse = vswgse else vswgse = self.vswgse
		if pdyn: self.pdyn = pdyn else pdyn = self.pdyn
		if dst: self.dst = dst else dst = self.dst
		if byimf: self.byimf = byimf else byimf = self.byimf
		if bzimf: self.bzimf = bzimf else bzimf = self.bzimf

		# Declare the same Re as used in Tsyganenko models [km]
		Re = 6371.2

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
					self.latSH = 90. - degrees(geoColat)
					self.lonSH = degrees(geoLon)
					self.rhoSH = geoR*Re
				elif mapto == -1:
					self.latNH = 90. - degrees(geoColat)
					self.lonNH = degrees(geoLon)
					self.rhoNH = geoR*Re



