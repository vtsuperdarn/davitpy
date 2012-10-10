#!bin/env python

from pylab import *
import numpy as np
from mpl_toolkits.mplot3d import proj3d
from models import tsyganenko

# Inputs
# Date and time
year = 2000
doy = 1
hr = 12
mn = 0
sc = 0
# Solar wind speed
vxgse = -400.
vygse = 0.
vzgse = 0.
# Execution parameters
lmax = 5000
rlim = 60. 
r0 = 1. 
dsmax = .01
err = .000001
# Direction of the tracing
mapto = 1
# Magnetic activity [SW pressure (nPa), Dst, ByIMF, BzIMF]
parmod = np.zeros(10)
parmod[0:4] = [2, -8, -2, -5]
# Start point (rh in Re)
lat = 50.
lon = 0.
rh = 0.

# This has to be called first
tsyganenko.recalc_08(year,doy,hr,mn,sc,vxgse,vygse,vzgse)

# Convert lat,lon to geographic cartesian and then gsw
r,theta,phi, xgeo, ygeo, zgeo = tsyganenko.sphcar_08(1., np.radians(90.-lat), np.radians(lon), 0., 0., 0., 1)
xgeo,ygeo,zgeo,xgsw,ygsw,zgsw  = tsyganenko.geogsw_08(xgeo, ygeo, zgeo,0,0,0,1)

# Trace field line
xfgsw,yfgsw,zfgsw,xarr,yarr,zarr,l = tsyganenko.trace_08(xgsw,ygsw,zgsw,mapto,dsmax,err, 
    rlim,r0,0,parmod,'T96_01','IGRF_GSW_08',lmax) 

# Convert back to spherical geographic coords
xfgeo,yfgeo,zfgeo,xfgsw,yfgsw,zfgsw  = tsyganenko.geogsw_08(0,0,0,xfgsw,yfgsw,zfgsw,-1)
gcR, gdcolat, gdlon, xgeo, ygeo, zgeo = tsyganenko.sphcar_08(0., 0., 0., xfgeo, yfgeo, zfgeo, -1)


print '** START: {:6.3f}, {:6.3f}, {:6.3f}'.format(lat, lon, 1.)
print '** STOP:  {:6.3f}, {:6.3f}, {:6.3f}'.format(90.-np.degrees(gdcolat), np.degrees(gdlon), gcR)

# A quick checking plot
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111, projection='3d')
# Plot coordinate system
ax.plot3D([0,1],[0,0],[0,0],'b')
ax.plot3D([0,0],[0,1],[0,0],'g')
ax.plot3D([0,0],[0,0],[0,1],'r')

# First plot a nice sphere for the Earth
u = np.linspace(0, 2 * np.pi, 179)
v = np.linspace(0, np.pi, 179)
tx = np.outer(np.cos(u), np.sin(v))
ty = np.outer(np.sin(u), np.sin(v))
tz = np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_surface(tx,ty,tz,rstride=10, cstride=10, color='grey', alpha=.5, zorder=2, linewidth=0.5)

# Then plot the traced field line
latarr = [10.,20.,30.,40.,50.,60.,70.,80.]
lonarr = [0., 180.]
rh = 0.
for lat in latarr:
    for lon in lonarr:
        r,theta,phi, xgeo, ygeo, zgeo = tsyganenko.sphcar_08(1., np.radians(90.-lat), np.radians(lon), 0., 0., 0., 1)
        xgeo,ygeo,zgeo,xgsw,ygsw,zgsw  = tsyganenko.geogsw_08(xgeo, ygeo, zgeo,0,0,0,1)
        xfgsw,yfgsw,zfgsw,xarr,yarr,zarr,l = tsyganenko.trace_08(xgsw,ygsw,zgsw,mapto,dsmax,err, 
            rlim,r0,0,parmod,'T96_01','IGRF_GSW_08',lmax) 
        for i in xrange(l):
            xgeo,ygeo,zgeo,dum,dum,dum  = tsyganenko.geogsw_08(0,0,0,xarr[i],yarr[i],zarr[i],-1)
            xarr[i],yarr[i],zarr[i] = xgeo,ygeo,zgeo
        ax.plot3D(xarr[0:l],yarr[0:l],zarr[0:l], zorder=3, linewidth=2, color='y')

# Set plot limits
lim=5
ax.set_xlim3d([-lim,lim])
ax.set_ylim3d([-lim,lim])
ax.set_zlim3d([-lim,lim])

show()