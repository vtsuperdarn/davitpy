# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: pydarn.plotting.mapOverlay
*********************
Overlay information on maps

**Functions**:
	* :func:`overlayRadar`: Overlay radar position and name on a map
	* :func:`overlayFov`: Overlay field(s)-of-view on a map

"""

# *************************************************************
def overlayRadar(mapObj, codes=None, ids=None, names=None, dateTime=None, 
                 annotate=True, plot_all=False, hemi=None, zorder=2,
                 markerColor='k', markerSize=10, fontSize=10, font_color='k',
                 xOffset=None):
    """
    Overlay radar position(s) and name(s) on map 
    
    **Args**: 
        * **mapObj**: a mapObj class object or Basemap map object
        * **[codes]**: a list of radar 3-letter codes to plot
        * **[ids]**: a list of radar IDs to plot
        * **[names]**: a list of radar names to plot
        * **[dateTime]**: a datetime.datetime object to use for the radar.
                          Default: uses mapObj.dateTime
        * **[annotate]**: wether or not to show the radar(s) name(s)
        * **[plot_all]**: set to true to plot all the radars (active ones)
        * **[hemi]**: 'north', 'south', or None.  If a hemisphere is specified,
                      limits radar calls to that hemisphere.  Default: None
        * **[zorder]**: the overlay order number. Default: 2
        * **[markerColor]**: Default: 'k' (black)
        * **[markerSize]**: [point] Default: 10
        * **[fontSize]**: [point] Default: 10
        * **[xOffset]**: x-Offset of the annotation in points.  Default: None 
    **Returns**:
        * None
    **Example**:
        ::

        import pydarn
        import utils
        m1 = utils.plotUtils.mapObj(boundinglat=30., gridLabels=True, coords='mag')
        pydarn.plot.overlayRadar(m1, fontSize=8, plot_all=True, markerSize=5)
			
    written by Sebastien, 2012-08
    """
    from davitpy.pydarn.radar import network
    from datetime import datetime as dt
    from datetime import timedelta
    from davitpy.utils.plotUtils import textHighlighted

    rn = "overlayRadar"

    # List paired radars.  Each member of a pair is placed in a different
    # sublist, with the more westward member in the first sublist
    nearby_rad = [['adw','kod','cve','fhe','wal','gbr','pyk','aze','sys'],
                  ['ade','ksr','cvw','fhw','bks','sch','sto','azw','sye']]

    # Set dateTime.
    if dateTime is not None:
        if hasattr(mapObj, 'dateTime') and dateTime != mapObj.dateTime:
            estr = '{:s} WARNING: dateTime is {:}'.format(rn,dateTime)
            estr = '{:s}, not mapObj.dateTime {:}'.format(estr,mapObj.dateTime)
            print estr
    else:
        dateTime = mapObj.dateTime
	
    # Load radar structure
    NetworkObj = network()
	
    # If all radars are to be plotted, create the list
    if plot_all:
        codes = NetworkObj.getAllCodes(datetime=dateTime, hemi=hemi)
	
    # Define how the radars to be plotted are identified (code, id or name)
    if codes:
        rad_input = {'meth': 'code', 'vals': codes}
    elif ids:
        rad_input = {'meth': 'id', 'vals': ids}
    elif names:
        rad_input = {'meth': 'name', 'vals': names}
    else:
        print 'overlayRadar: no radars to plot'
        return
	
    # Check if radars is given as a list
    if not isinstance(rad_input['vals'], list):
        rad_input['vals'] = [rad_input['vals']]

    # Check if the radar text colors were given as a list
    if isinstance(font_color, list):
        rad_input['fcolor'] = font_color
    else:
        rad_input['fcolor'] = [font_color for i in rad_input['vals']]

    # Check if the radar marker colors were given as a list
    if isinstance(markerColor, list):
        rad_input['mcolor'] = markerColor
    else:
        rad_input['mcolor'] = [markerColor for i in rad_input['vals']]

    # Map width and height
    width = mapObj.urcrnrx - mapObj.llcrnrx
    height = mapObj.urcrnry - mapObj.llcrnry

    if hemi is None:
        hemiInt = 0
    else:
        hemiInt = 1 if hemi.lower()[0]=='n' else -1

    # iterates through radars to be plotted
    for ir,radN in enumerate(rad_input['vals']):
        rad = NetworkObj.getRadarBy(radN, rad_input['meth'])
        if not rad: continue
        site = rad.getSiteByDate(dateTime)
        if not site: continue
        # Check for hemisphere specification
        if site.geolat*hemiInt < 0: continue
        # Get radar coordinates in map projection
        if not hasattr(mapObj, 'coords'): 
            x,y = mapObj(site.geolon, site.geolat)
        else:
            x,y = mapObj(site.geolon, site.geolat, coords='geo')
        if not mapObj.xmin <= x <= mapObj.xmax: continue
        if not mapObj.ymin <= y <= mapObj.ymax: continue

        # Plot radar position
        mapObj.scatter(x, y, s=markerSize, marker='o',
                       color=rad_input['mcolor'][ir], zorder=zorder)

        # Now add radar name
        if annotate:
            # If any of the other radar is too close...
            if rad.code[0] in nearby_rad[0]:
                xOff = 5 if not xOffset else xOffset
                ha = 0
            elif rad.code[0] in nearby_rad[1]:
                xOff = -5 if not xOffset else xOffset
                ha = 1
            else: 
                xOff = 0.0
                ha = .5
            # Plot radar name
            textHighlighted((x, y), rad.code[0].upper(), xytext=(xOff, -5), 
                            text_alignment=(ha,1), variant='small-caps',
                            fontsize=fontSize, zorder=zorder,
                            color=rad_input['fcolor'][ir])

    return

# *************************************************************
def overlayFov(mapObj, codes=None, ids=None, names=None, dateTime=None,
               plot_all=False, maxGate=None, rangeLimits=None, model='IS',
               fov_dir='front', fovColor=None, fovAlpha=0.2, beams=None,
               beamsColors=None, hemi=None, fovObj=None, zorder=2,
               lineColor='k', lineWidth=1):
    """ Overlay FoV position(s) on map

    **Args**: 
        * **mapObj**: a mapObj or Basemap object on which to overplot
                      the radar position(s)
        * **[codes]**: a list of radar 3-letter codes to plot
        * **[ids]**: a list of radar IDs to plot
        * **[names]**: a list of radar names to plot
        * **[dateTime]**: a datetime.datetime object to use for the FOV.
        Default: uses mapObj.dateTime
        * **[plot_all]**: set to true to plot all the radars (active ones)
        * **[maxGate]**: Maximum number of gates to be plotted. Defaults to
                         hdw.dat information.
        * **[rangeLimits]**: (2-element list) Plot only between the range gates
                             specified.
        * **model**:
            * **'IS'**: for ionopsheric scatter projection model (default)
            * **'GS'**: for ground scatter projection model
            * **None**: if you are really confident in your elevation or
                        altitude values
        * **[fov_dir]**: Field of view direction ('front' or 'back').
                         Default='front'
        * **[zorder]**: the overlay order number
        * **[lineColor]**: FoV contour line color
        * **[lineWidth]**: FoV contour line width
        * **[fovColor]**: field of view fill color
        * **[fovAlpha]**: field of view fill color transparency
        * **[fovObj]**: a fov object. See pydarn.radar.radFov.fov
        * **[hemi]**: 'north' or 'south', ignore radars from the other
                      hemisphere
        * **[beams]**: hightlight specified beams
        * **[beamsColors]**: colors of the hightlighted beams
    **Returns**:
        * None
    **Example**:
        ::

        import pydarn, utils
        # Width and height give the window size in meters
        width = 111e3*40
        m=utils.plotUtils.mapObj(width=width,height=width,lat_0=50.,lon_0=-95.)
        # Plot radar position and code
        pydarn.plot.overlayRadar(m, fontSize=12, codes='bks')
        # Plot radar fov
        pydarn.plot.overlayFov(m, codes='bks', maxGate=75, beams=[0,4,7,8,23])

    written by Sebastien, 2012-09
    """
    from davitpy.pydarn.radar import network
    from davitpy.pydarn.radar.radFov import fov
    from datetime import datetime as dt
    from datetime import timedelta
    import matplotlib.cm as cm
    from numpy import transpose, ones, concatenate, vstack, shape
    from matplotlib.patches import Polygon
    from pylab import gca

    # Set dateTime.
    if dateTime is not None:
        if hasattr(mapObj, 'dateTime') and dateTime != mapObj.dateTime:
            print "Warning, dateTime is " + str(dateTime) + \
                    ", not mapObj.dateTime " + str(mapObj.dateTime)
    else:
        dateTime = mapObj.dateTime

    # Load radar structure
    network_obj = network()

    # If all radars are to be plotted, create the list
    if plot_all: codes = network_obj.getAllCodes(datetime=dateTime, hemi=hemi)

    # Define how the radars to be plotted are identified (code, id or name)
    if codes:
        rad_input = {'meth': 'code', 'vals': codes}
    elif ids:
        rad_input = {'meth': 'id', 'vals': ids}
    elif names:
        rad_input = {'meth': 'name', 'vals': names}
    else:
        print 'overlayFov: no radars to plot'
        return

    # Check if radars is given as a list
    if not isinstance(rad_input['vals'], list):
        rad_input['vals'] = [rad_input['vals']]

    nradars = len(rad_input['vals'])

    # Initialize the line color for the field of view
    lcolor=lineColor

    # iterates through radars to be plotted
    for ir in xrange(nradars):
        # Get field of view coordinates
        if(fovObj == None):
            rad = network_obj.getRadarBy(rad_input['vals'][ir],
                                         rad_input['meth'])
            if not rad:
                continue
            site = rad.getSiteByDate(dateTime)
            if not site:
                continue
            # Set number of gates to be plotted
            egate = site.maxgate-1 if not maxGate else maxGate

            if not hasattr(mapObj, 'coords'): 
                rad_fov = fov(site=site, ngates=egate+1, model=model,
                              fov_dir=fov_dir)
            else:
                rad_fov = fov(site=site, ngates=egate+1, coords=mapObj.coords, 
                              model=model, date_time=dateTime, fov_dir=fov_dir)
        else:
            rad_fov = fovObj
            egate = len(fovObj.gates)

        if rangeLimits is not None:
            sgate = rangeLimits[0]
            egate = rangeLimits[1]
        else:
            sgate = 0

        if model == 'GS':
        # Ground scatter model is not defined for close in rangegates.
        # np.nan will be returned for these gates.
        # Set sGate >= to the first rangegate that has real values.
                    
            not_finite  = np.logical_not(np.isfinite(radFov.lonFull))
            grid        = np.tile(np.arange(radFov.lonFull.shape[1]),(radFov.lonFull.shape[0],1)) 
            grid[not_finite] = 999999
            tmp_sGate   = (np.min(grid,axis=1)).max()
            if tmp_sGate > sgate: sgate = tmp_sGate

        # Get radar coordinates in map projection
        if hasattr(mapObj, 'coords'): 
            x, y = mapObj(rad_fov.lonFull, rad_fov.latFull,
                          coords=rad_fov.coords)
        else:
            x, y = mapObj(rad_fov.lonFull, rad_fov.latFull)
        # Plot field of view
        # Create contour
        contour_x = concatenate((x[0,sgate:egate], x[:,egate],
                                 x[-1,egate:sgate:-1], x[-1::-1,sgate]))
        contour_y = concatenate((y[0,sgate:egate], y[:,egate],
                                 y[-1,egate:sgate:-1], y[-1::-1,sgate]))
        # Set the color if a different color has been specified for each radar
        if isinstance(lineColor, list) and len(lineColor) > ir:
            lcolor=lineColor[ir]

        # Plot contour
        mapObj.plot(contour_x, contour_y, color=lcolor, zorder=zorder,
                    linewidth=lineWidth)
        # Field of view fill
        if fovColor:
            contour = transpose(vstack((contour_x,contour_y)))
            patch = Polygon(contour, color=fovColor, alpha=fovAlpha,
                            zorder=zorder)
            gca().add_patch(patch)
        # Beams fill
        if beams:
            try:
                [b for b in beams]
            except:
                beams = [beams]
            for ib in beams:
                if not (0 <= ib <= x.shape[0]): continue
                if not beamsColors:
                    bcol_rgb = ib/float(x.shape[0])
                    bcol = (bcol_rgb/2., bcol_rgb, 1)
                else:
                    bcol = beamsColors[beams.index(ib)]
                contour_x = concatenate((x[ib,0:egate+1], x[ib:ib+2,egate],
                                         x[ib+1,egate::-1], x[ib+1:ib-1:-1,0]))
                contour_y = concatenate((y[ib,0:egate+1], y[ib:ib+2,egate],
                                         y[ib+1,egate::-1], y[ib+1:ib-1:-1,0]))
                contour = transpose(vstack((contour_x, contour_y)))
                patch = Polygon(contour, color=bcol, alpha=.4,
                                zorder=zorder)
                gca().add_patch(patch)

    return

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from datetime import datetime

    from davitpy import utils

    print "Creating figure and axes"
    fig = plt.figure()
    ax = fig.add_axes()
    # Changed coords from "mlt" to "geo" because mlt kept crashing
    print "Creating map object for datetime(2012,1,1,0,2) in Geographic"
    mo = utils.mapObj(lat_0=90., lon_0=0., boundinglat=40.,
                      dateTime=datetime(2012,1,1,0,2), coords="geo",
                      projection="stere")
    print "overlayRadar"
    overlayRadar(mo, codes="sas")
    print "overlayRadar for datetime(2012,1,1,1,2);"
    print "should produce warning about different time"
    overlayRadar(mo, codes="sas", dateTime=datetime(2012,1,1,1,2))
    print "overlayFov"
    overlayFov(mo, codes="sas", maxGate=45)
    print "overlay the near-range rear-FoV and fill shade it magenta"
    overlayFov(mo, codes="sas", maxGate=10, fov_dir='back', fovColor="m")
    print "overlayFov for datetime(2012,1,1,1,2);"
    print "should produce warning about different time"
    overlayFov(mo, codes="sas", maxGate=45, dateTime=datetime(2012,1,1,1,2))
    print "Showing plot"
    plt.show()
