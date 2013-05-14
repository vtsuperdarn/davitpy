# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: utils.plotUtils
*********************
Basic plotting tools

**Functions**:
    * :func:`utils.plotUtils.mapObj`: Create empty map 
    * :func:`utils.plotUtils.genCmap`: 
    * :func:`utils.plotUtils.curvedEarthAxes`: Plot axes in (R, Theta) coordinates with lower limit at R = Earth radius
    * :func:`utils.plotUtils.addColorbar`: Colorbar for :func:`curvedEarthAxes`

"""
from mpl_toolkits import basemap


################################################################################
################################################################################
class mapObj(basemap.Basemap):
    """This class wraps arround :class:`mpl_toolkits.basemap.Basemap` (<http://tinyurl.com/d4rzmfo>)
    
    **Members**: 
        * **coords** (str): map coordinate system ('geo', 'mag', 'mlt').
        * all members of :class:`mpl_toolkits.basemap.Basemap` (<http://tinyurl.com/d4rzmfo>) 
    **Methods**:
        * all methods of :class:`mpl_toolkits.basemap.Basemap` (<http://tinyurl.com/d4rzmfo>)
    **Example**:
        ::

            # Create the map
            myMap = utils.mapObj(boundinglat=30, coords='mag')
            # Plot the geographic and geomagnetic North Poles
            # First convert from lat/lon to map projection coordinates...
            x, y = myMap(0., 90., coords='geo')
            # ...then plot
            myMap.scatter(x, y, zorder=2, color='r')
            # Convert to map projection...
            x, y = myMap(0., 90., coords='mag')
            # ...and plot
            myMap.scatter(x, y, zorder=2, color='g')

    .. note:: Once the map is created, all plotting calls will be assumed to already be in the map's declared coordinate system given by **coords**.

    """

    def __init__(self, datetime=None, coords='geo', 
        projection='stere', resolution='l', dateTime=None, 
        lat_0=None, lon_0=None, boundinglat=None, width=None, height=None, 
        fillContinents='.8', fillOceans='None', fillLakes=None, coastLineWidth=0., 
        grid=True, gridLabels=True, **kwargs):
        """Create empty map 
        
        **Args**: 
            * **[limits]**: [llLat, llLon, urLat, urLon] lower-left and upper-right corners coordinates    
            * **[width, height]**: width and height in m from the (lat_0, lon_0) center
            * **[lon_0]**: center meridian (default is -70E)    
            * **[lat_0]**: center latitude (default is -90E)
            * **[boundingLat]**: bounding latitude (default it +/-20)    
            * **[grid]**: show/hide parallels and meridians grid    
            * **[fill_continents]**: continent color. Default is 'grey'    
            * **[fill_water]**: water color. Default is 'None'    
            * **[coords]**: 'geo'
            * **[dateTime]** (datetime.datetime): necessary for MLT plots if you want the continents to be plotted
            * **[kwargs]**: See <http://tinyurl.com/d4rzmfo> for more keywords
        **Returns**:
            * **map**: a Basemap object (<http://tinyurl.com/d4rzmfo>)
        **Example**:
            ::

                myMap = mapObj(lat_0=50, lon_0=-95, width=111e3*60, height=111e3*60)
                
        written by Sebastien, 2013-02
        """
        from models import aacgm
        import numpy as np
        from pylab import text
        import math
        from copy import deepcopy

        self._coordsDict = {'mag': 'AACGM',
                            'geo': 'Geographic',
                            'mlt': 'MLT'}

        if coords is 'mlt':             
            print 'MLT coordinates not implemented yet.'
            return

        # Add an extra member to the Basemap class
        if coords is not None and coords not in self._coordsDict:
            print 'Invalid coordinate system given in coords ({}): setting "geo"'.format(coords)
            coords = 'geo'
        self.coords = coords

        # Set map projection limits and center point depending on hemisphere selection
        if lat_0 is None: 
            lat_0 = 90.
            if boundinglat: lat_0 = math.copysign(lat_0, boundinglat)
        if lon_0 is None: 
            lon_0 = -100.
            if self.coords == 'mag': 
                _, lon_0, _ = aacgm.aacgmConv(0., lon_0, 0., 0)
        if boundinglat:
            width = height = 2*111e3*( abs(lat_0 - boundinglat) )

        # Initialize map
        super(mapObj, self).__init__(self, projection=projection, resolution=resolution, 
                lat_0=lat_0, lon_0=lon_0, width=width, height=height, **kwargs)

        # Add continents
        if coords is not 'mlt' or dateTime is not None:
            _ = self.drawcoastlines(linewidth=coastLineWidth)
            # self.drawmapboundary(fill_color=fillOceans)
            _ = self.fillcontinents(color=fillContinents, lake_color=fillLakes)

        # Add coordinate spec
        _ = text(self.urcrnrx, self.urcrnry, self._coordsDict[coords]+' coordinates', 
                rotation=-90., va='top', fontsize=8)

        # draw parallels and meridians.
        if grid:
            parallels = np.arange(-80.,81.,20.)
            out = self.drawparallels(parallels, color='.6')
            # label parallels on map
            if gridLabels: 
                lablon = int(self.llcrnrlon/10)*10
                rotate_label = lablon - lon_0 if lat_0 >= 0 else lon_0 - lablon + 180.
                x,y = basemap.Basemap.__call__(self, lablon*np.ones(parallels.shape), parallels)
                for ix,iy,ip in zip(x,y,parallels):
                    if not self.xmin <= ix <= self.xmax: continue
                    if not self.ymin <= iy <= self.ymax: continue
                    _ = text(ix, iy, r"{:3.0f}$^\circ$".format(ip), 
                            rotation=rotate_label, va='center', ha='center')
            # label meridians on bottom and left
            meridians = np.arange(-180.,181.,20.)
            if gridLabels: 
                merLabels = [True,False,False,True]
            else: 
                merLabels = [False,False,False,False]
            # draw meridians
            out = self.drawmeridians(meridians, labels=merLabels, color='.6')

    
    def __call__(self, x, y, inverse=False, coords=None):
        from models import aacgm
        from copy import deepcopy
        import numpy as np
        import inspect

        if coords is not None and coords not in self._coordsDict:
            print 'Invalid coordinate system given in coords ({}): setting "{}"'.format(coords, self.coords)
            coords = None

        if coords and coords != self.coords:
            trans = coords+'-'+self.coords
            if trans in ['geo-mag','mag-geo']:
                flag = 0 if trans == 'geo-mag' else 1
                try:
                    nx, ny = len(x), len(y)
                    xt = np.array(x)
                    yt = np.array(y)
                    shape = xt.shape    
                    y, x, _ = aacgm.aacgmConvArr(list(yt.flatten()), list(xt.flatten()), [0.]*nx, flag)
                    x = np.array(x).reshape(shape)
                    y = np.array(y).reshape(shape)
                except TypeError as e:
                    y, x, _ = aacgm.aacgmConv(y, x, 0., flag)


        if self.coords is 'geo':
            return basemap.Basemap.__call__(self, x, y, inverse=inverse)

        elif self.coords is 'mag':
            try:
                callerFile, _, callerName = inspect.getouterframes(inspect.currentframe())[1][1:4]
            except: 
                return basemap.Basemap.__call__(self, x, y, inverse=inverse)
            if isinstance(y, float) and abs(y) == 90.:
                return basemap.Basemap.__call__(self, x, y, inverse=inverse)
            if 'mpl_toolkits' in callerFile and callerName is '_readboundarydata':
                if not inverse:
                    try:
                        nx, ny = len(x), len(y)
                        x = np.array(x)
                        y = np.array(y)
                        shape = x.shape
                        yout, xout, _ = aacgm.aacgmConvArr(list(y.flatten()), list(x.flatten()), [0.]*nx, 0)
                        xout = np.array(xout).reshape(shape)
                        yout = np.array(yout).reshape(shape)
                    except TypeError:
                        yout, xout, _ = aacgm.aacgmConv(y, x, 0., 0)
                    return basemap.Basemap.__call__(self, xout, yout, inverse=inverse)
                else:
                    return basemap.Basemap.__call__(self, x, y, inverse=inverse)
            else:
                return basemap.Basemap.__call__(self, x, y, inverse=inverse)

        elif self.coords is 'mlt':
            callerFile, _, callerName = inspect.getouterframes(inspect.currentframe())[1][1:4]


    def _readboundarydata(self, name, as_polygons=False):
        from models import aacgm
        from copy import deepcopy
        import _geoslib
        import numpy as np

        if self.coords is 'mag':
            nPts = len(self._boundarypolyll.boundary[:, 0])
            lats, lons, _ = aacgm.aacgmConvArr(list(self._boundarypolyll.boundary[:, 1]), 
                            list(self._boundarypolyll.boundary[:, 0]), 
                            [0.]*nPts, 1)
            b = np.asarray([lons,lats]).T
            oldgeom = deepcopy(self._boundarypolyll)
            newgeom = _geoslib.Polygon(b).fix()
            self._boundarypolyll = newgeom
            out = basemap.Basemap._readboundarydata(self, name, as_polygons=as_polygons)
            self._boundarypolyll = oldgeom
            return out
        else: 
            return basemap.Basemap._readboundarydata(self, name, as_polygons=as_polygons)


def genCmap(param, scale, colors='lasse', lowGray=False):
    """Generates a colormap and plots a colorbar

    **Args**:
        * **fig**: the parent figure
        * **coll**: the collection of items (e.g. polygons) being mapped to this colormap
        * **param**: the parameter being plotted, valid for 'velocity', 'power', 'width', 'elevation', 'phi0'
        * **scale**: the max and min values of the color scale in list form
        * **pos**: the position of the parent plot, NOT of the COLORBAR
        * **[colors]**: a string indicating which colorbar to use, valid inputs are 'lasse', 'aj'
    **Returns**:

    **Example**:
        ::

            myFig = figure()
            genCmap(myFig, polyCollection, 'velocity', [-200,200], pos)
        
    Written by AJ 20120820
    """
    import matplotlib,numpy
    import matplotlib.pyplot as plot
    
    #the MPL colormaps we will be using
    cmj = matplotlib.cm.jet
    cmpr = matplotlib.cm.prism
    
    #check for a velocity plot
    if(param == 'velocity'):
        
        #check for what color scale we want to use
        if(colors == 'aj'):
            if(not lowGray):
                #define our discrete colorbar
                cmap = matplotlib.colors.ListedColormap([cmpr(.142),cmpr(.125),cmpr(.11),cmpr(.1),\
                cmpr(.175),cmpr(.158),cmj(.32),cmj(.37)])
            else:
                cmap = matplotlib.colors.ListedColormap([cmpr(.142),cmpr(.125),cmpr(.11),cmpr(.1),'.6',\
                cmpr(.175),cmpr(.158),cmj(.32),cmj(.37)])
        else:
            if(not lowGray):
                #define our discrete colorbar
                cmap = matplotlib.colors.ListedColormap([cmj(.9),cmj(.8),cmj(.7),cmj(.65),\
                cmpr(.142),cmj(.45),cmj(.3),cmj(.1)])
            else:
                cmap = matplotlib.colors.ListedColormap([cmj(.9),cmj(.8),cmj(.7),cmj(.65),'.6',\
                cmpr(.142),cmj(.45),cmj(.3),cmj(.1)])
                
        #define the boundaries for color assignments
        bounds = numpy.round(numpy.linspace(scale[0],scale[1],7))
        if(lowGray):
            bounds[3] = -15.
            bounds = numpy.insert(bounds,4,15.)
        bounds = numpy.insert(bounds,0,-50000.)
        bounds = numpy.append(bounds,50000.)
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
        
    elif(param == 'phi0'):
        #check for what color scale we want to use
        if(colors == 'aj'):
            #define our discrete colorbar
            cmap = matplotlib.colors.ListedColormap([cmpr(.142),cmpr(.125),cmpr(.11),cmpr(.1),\
            cmpr(.18),cmpr(.16),cmj(.32),cmj(.37)])
        else:
            #define our discrete colorbar
            cmap = matplotlib.colors.ListedColormap([cmj(.9),cmj(.8),cmj(.7),cmj(.65),\
            cmpr(.142),cmj(.45),cmj(.3),cmj(.1)])
            
        #define the boundaries for color assignments
        bounds = numpy.linspace(scale[0],scale[1],9)
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
        
    elif(param == 'grid'):
        #check what color scale we want to use
        if(colors == 'aj'):
            #define our discrete colorbar
            cmap = matplotlib.colors.ListedColormap([cmpr(.175),cmpr(.17),cmj(.32),cmj(.37),\
            cmpr(.142),cmpr(.13),cmpr(.11),cmpr(.10)])
        else:
            #define our discrete colorbar
            cmap = matplotlib.colors.ListedColormap([cmj(.1),cmj(.3),cmj(.45),cmpr(.142),\
            cmj(.65),cmj(.7),cmj(.8),cmj(.9)])
            
        #define the boundaries for color assignments
        bounds = numpy.round(numpy.linspace(scale[0],scale[1],8))
        bounds = numpy.append(bounds,50000.)
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
        
    #if its a non-velocity plot
    else:
        
        #check what color scale we want to use
        if(colors == 'aj'):
            #define our discrete colorbar
            cmap = matplotlib.colors.ListedColormap([cmpr(.175),cmpr(.158),cmj(.32),cmj(.37),\
            cmpr(.142),cmpr(.13),cmpr(.11),cmpr(.10)])
        else:
            #define our discrete colorbar
            cmap = matplotlib.colors.ListedColormap([cmj(.1),cmj(.3),cmj(.45),cmpr(.142),\
            cmj(.65),cmj(.7),cmj(.8),cmj(.9)])
            
        #define the boundaries for color assignments
        bounds = numpy.round(numpy.linspace(scale[0],scale[1],8))
        bounds = numpy.append(bounds,50000.)
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
        

    cmap.set_bad('w',1.0)
    cmap.set_over('w',1.0)
    cmap.set_under('.6',1.0)

    return cmap,norm,bounds
    
    #cb = drawCB(fig,coll,cmap,norm,map=map,pos=pos)
    #l = []
    ##define the colorbar labels
    #for i in range(0,len(bounds)):
        #if(param == 'phi0'):
            #ln = 4
            #if(bounds[i] == 0): ln = 3
            #elif(bounds[i] < 0): ln = 5
            #l.append(str(bounds[i])[:ln])
            #continue
        #if((i == 0 and param == 'velocity') or i == len(bounds)-1):
            #l.append(' ')
            #continue
        #l.append(str(int(bounds[i])))
    #cb.ax.set_yticklabels(l)
        
    ##set colorbar ticklabel size
    #for t in cb.ax.get_yticklabels():
        #t.set_fontsize(9)
    
    ##set colorbar label
    #if(param == 'velocity'): cb.set_label('Velocity [m/s]',size=10)
    #if(param == 'grid'): cb.set_label('Velocity [m/s]',size=10)
    #if(param == 'power'): cb.set_label('Power [dB]',size=10)
    #if(param == 'width'): cb.set_label('Spec Wid [m/s]',size=10)
    #if(param == 'elevation'): cb.set_label('Elev [deg]',size=10)
    #if(param == 'phi0'): cb.set_label('Phi0 [rad]',size=10)
    
    #return


def drawCB(fig,coll,cmap,norm,map=0,pos=[0,0,1,1]):
    """Draw a colorbar I guess... AJ?
    """
    import matplotlib,numpy
    import matplotlib.pyplot as plot

    if(map == 0):
        #create a new axes for the colorbar
        cax = fig.add_axes([pos[0]+pos[2]+.02, pos[1], 0.02, pos[3]])
        #set the colormap and boundaries for the collection
        #of plotted items
        if(isinstance(coll,list)):
            for c in coll:
                c.set_cmap(cmap)
                c.set_norm(norm)
                cb = plot.colorbar(c,cax=cax)
        else:
            coll.set_cmap(cmap)
            coll.set_norm(norm)
            cb = plot.colorbar(coll,cax=cax)
    else:
        if(isinstance(coll,list)):
            for c in coll:
                c.set_cmap(cmap)
                c.set_norm(norm)
                cb = fig.colorbar(c,location='right')
        else:
            coll.set_cmap(cmap)
            coll.set_norm(norm)
            cb = fig.colorbar(coll,location='right',pad="5%")
    
    cb.ax.tick_params(axis='y',direction='out')
    return cb
    

def curvedEarthAxes(rect=111, fig=None, 
    minground=0., maxground=2000, 
    minalt=0, maxalt=500, Re=6371., 
    nyticks=5, nxticks=4):
    """ Create curved axes in ground-range and altitude
        
    **Args**: 
        * [**rect**]: subplot spcification
        * [**fig**]: A pylab.figure object (default to gcf)
        * [**maxground**]: maximum ground range [km]
        * [**minalt**]: lowest altitude limit [km]
        * [**maxalt**]: highest altitude limit [km]
        * [**Re**]: Earth radius
    **Returns**:
        * **ax**: matplotlib.axes object containing formatting
        * **aax**: matplotlib.axes object containing data
    **Example**:
        ::

            import numpy as np
            from utils import plotUtils
            ax, aax = plotUtils.curvedEarthAxes()
            th = np.linspace(0, ax.maxground/ax.Re, 50)
            r = np.linspace(ax.Re+ax.minalt, ax.Re+ax.maxalt, 20)
            Z = exp( -(r - 300 - ax.Re)**2 / 100**2 ) * np.cos(th[:, np.newaxis]/th.max()*4*np.pi)
            x, y = np.meshgrid(th, r)
            im = aax.pcolormesh(x, y, Z.T)
            ax.grid()

            
    written by Sebastien, 2013-04
    """
    from matplotlib.transforms import Affine2D, Transform
    import mpl_toolkits.axisartist.floating_axes as floating_axes
    from matplotlib.projections import polar
    from mpl_toolkits.axisartist.grid_finder import FixedLocator, DictFormatter
    import numpy as np
    from pylab import gcf

    ang = maxground / Re
    minang = minground / Re
    angran = ang - minang
    angle_ticks = [(0, "{:.0f}".format(minground))]
    while angle_ticks[-1][0] < angran:
        tang = angle_ticks[-1][0] + 1./nxticks*angran
        angle_ticks.append( ( tang, 
                            "{:.0f}".format((tang-minang)*Re) ) )
    grid_locator1 = FixedLocator([v for v, s in angle_ticks])
    tick_formatter1 = DictFormatter(dict(angle_ticks))

    
    altran = maxalt - minalt
    alt_ticks = [(minalt+Re, "{:.0f}".format(minalt))]
    while alt_ticks[-1][0] < Re+maxalt:
        alt_ticks.append( ( 1./nyticks*altran+alt_ticks[-1][0], 
                            "{:.0f}".format(altran*1./nyticks+alt_ticks[-1][0]-Re) ) )
    _ = alt_ticks.pop()
    grid_locator2 = FixedLocator([v for v, s in alt_ticks])
    tick_formatter2 = DictFormatter(dict(alt_ticks))
        
    tr_rotate = Affine2D().rotate(np.pi/2-ang/2)
    tr_shift = Affine2D().translate(0, Re)
    tr = polar.PolarTransform() + tr_rotate

    grid_helper = floating_axes.GridHelperCurveLinear(tr,
                                        extremes=(0, angran, Re+minalt, Re+maxalt),
                                        grid_locator1=grid_locator1,
                                        grid_locator2=grid_locator2,
                                        tick_formatter1=tick_formatter1,
                                        tick_formatter2=tick_formatter2,
                                        )

    if not fig: fig = gcf()
    ax1 = floating_axes.FloatingSubplot(fig, rect, grid_helper=grid_helper)

    # adjust axis
    ax1.axis["left"].label.set_text(r"ALt. [km]")
    ax1.axis["bottom"].label.set_text(r"Ground range [km]")
    ax1.invert_xaxis()

    ax1.minground = minground
    ax1.maxground = maxground
    ax1.minalt = minalt
    ax1.maxalt = maxalt
    ax1.Re = Re
    
    fig.add_subplot(ax1, transform=tr)


    # create a parasite axes whose transData in RA, cz
    aux_ax = ax1.get_aux_axes(tr)

    aux_ax.patch = ax1.patch # for aux_ax to have a clip path as in ax
    ax1.patch.zorder=0.9 # but this has a side effect that the patch is
                        # drawn twice, and possibly over some other
                        # artists. So, we decrease the zorder a bit to
                        # prevent this.

    return ax1, aux_ax


def addColorbar(mappable, ax):
    """ Append colorbar to axes

    **Args**:
        * **mappable**: a mappable object
        * **ax**: an axes object
    **Returns**:
        * **cbax**: colorbar axes object

    .. note:: This is mostly useful for axes created with :func:`curvedEarthAxes`.

    written by Sebastien, 2013-04
    """
    from mpl_toolkits.axes_grid1 import SubplotDivider, LocatableAxes, Size
    import matplotlib.pyplot as plt 

    fig1 = ax.get_figure()
    divider = SubplotDivider(fig1, *ax.get_geometry(), aspect=True)

    # axes for colorbar
    cbax = LocatableAxes(fig1, divider.get_position())

    h = [Size.AxesX(ax), # main axes
         Size.Fixed(0.1), # padding
         Size.Fixed(0.2)] # colorbar
    v = [Size.AxesY(ax)]

    _ = divider.set_horizontal(h)
    _ = divider.set_vertical(v)

    _ = ax.set_axes_locator(divider.new_locator(nx=0, ny=0))
    _ = cbax.set_axes_locator(divider.new_locator(nx=2, ny=0))

    _ = fig1.add_axes(cbax)

    _ = cbax.axis["left"].toggle(all=False)
    _ = cbax.axis["top"].toggle(all=False)
    _ = cbax.axis["bottom"].toggle(all=False)
    _ = cbax.axis["right"].toggle(ticklabels=True, label=True)

    _ = plt.colorbar(mappable, cax=cbax)

    return cbax