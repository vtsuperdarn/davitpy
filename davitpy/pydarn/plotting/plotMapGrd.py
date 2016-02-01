# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""plotMapGrd module

Plotting/Retreiving SuperDARN gridded velocities, fitted convection velocities
and contour plotting routines

Class
-------
MapConv
-------

"""
import logging

class MapConv(object):
    """Plot/retrieve data from mapex and grdex files

    Read a record (from a time) from grdex and mapex files and plot or retreive
    the gridded LoS velocity vectors, convection contours, fitted velocity
    vectors, model vectors and Heppnard-Maynard Boundary.

    Parameters
    ----------
    startTime : datetime.datetime
        start date and time of the data rec
    mObj : utils.plotUtils.mapObj
        the map object you want data to be overlayed on.
    axisHandle :
        the axis handle used
    hemi : Optional[str]
        hemisphere - 'north' or 'south'.  Default is north.
    maxVelScale : Optional[float]
        maximum velocity to be used for plotting, min is zero so scale is
        [0,1000]
    plotCoords : Optional[str]
        coordinates of the plot, only use either 'mag' or 'mlt'

    Attributes
    ----------
    radEarth : float
        Earth radius in kilometers
    lenFactor : float
        Used to change the length of the vector on the plot
    radEarthMtrs : float
        Earth radius in meters
    maxVelPlot : Optional[float]
        maximum velocity to be used for plotting, min is zero so scale is
        [0,1000]
    axisHandle :
        the axis handle used
    mObj : utils.plotUtils.mapObj
        the map object you want data to be overlayed on.
    

    Methods
    --------
    overlayGridVel(pltColBar=True, overlayRadNames=True, annotateTime=True,
                   colorBarLabelSize=15., colmap=cm.jet)
        Overlay gridded LoS velocity data from grdex files
    calcFitCnvVel()
        Calculate fitted convection velocity from mapex data
    calcCnvPots()
        Calculte equipotential contour values from mapex data
    overlayCnvCntrs()
        Overlay convection contours from mapex data
    overlayHMB(hmbCol='Gray')
        Overlay Heppnard-Maynard boundary from mapex data
    overlayMapModelVel(pltColBar=False, annotateTime=True,
                       colorBarLabelSize=15., colMap=cm.jet)
        Overlay model velocity vectors from mapex data
    overlayMapFitVel(pltColBar=True, overlayRadNames=True, annotateTime=True,
                     colorBarLabelSize=15., colMap=cm.jet)
        Overlay fitted velocity vectors from mapex data

    Example
    -------
        Plot contours, fitted velocities and Heppnard-Maynard
        boundary from convection map data on April-3-2011

        import datetime
        import matplotlib.pyplot as plt
        import pydarn.plotting.plotMapGrd
        from utils import *

        fig = plt.figure()
        ax = fig.add_subplot(111)

        sdate = datetime.datetime(2011,4,3,4,0)
        mObj = plotUtils.mapObj(boundinglat=50.,
                                gridLabels=True, coords='mag')

        mapDatObj = pydarn.plotting.plotMapGrd.MapConv(sdate, mObj, ax)
        mapDatObj.overlayMapFitVel()
        mapDatObj.overlayCnvCntrs()
        mapDatObj.overlayHMB()

    written by Bharat Kunduri and Sebastien de Larquier, 2013-08

    """
    import matplotlib.cm as cm


    def __init__(self, startTime, mObj, axisHandle, hemi='north',
                 maxVelScale=1000., plotCoords='mag'):

        import datetime
        from davitpy.pydarn.sdio import sdDataOpen
        import matplotlib.cm as cm
        import numpy
        import matplotlib

        # set up some initial paramteres
        self.radEarth = 6371.
        # This is used to change the length of the vector on the plot
        self.lenFactor = 500.
        self.radEarthMtrs = self.radEarth * 1000.
        self.maxVelPlot = maxVelScale
        self.axisHandle = axisHandle
        self.mObj = mObj

        # check if the mapObj is indicating the same hemisphere as data
        # requested
        if hemi == "north":
            assert(mObj.boundarylats[0] > 0.), \
                logging.error("Map object is using one hemisphere and data the"
                              " other")
        else:
            assert(mObj.boundarylats[0] < 0.), \
                logging.error("Map object is using one hemisphere and data the"
                              " other")

        # check if hemi and coords keywords are correct
        assert(hemi == "north" or hemi == "south"), \
            logging.error("hemi should either be 'north' or 'south'")
        assert(plotCoords == 'mag' or coords == 'mlt'), \
            logging.error("error, coords must be one of 'mag' or 'mlt'")

        self.hemi = hemi
        self.plotCoords = plotCoords

        # Read the corresponding data record from both map and grid files.
        # This is the way I'm setting stuff up to avoid confusion of reading
        # and plotting seperately.  Just give the date/hemi and the code reads
        # the corresponding rec
        endTime = startTime + datetime.timedelta(minutes=2)
        grdPtr = sdDataOpen(startTime, hemi, eTime=endTime, fileType='grdex')
        self.grdData = grdPtr.readRec()
        mapPtr = sdDataOpen(startTime, hemi, eTime=endTime, fileType='mapex')
        self.mapData = mapPtr.readRec()

    def overlayGridVel(self, pltColBar=True, overlayRadNames=True,
                       annotateTime=True, colorBarLabelSize=15.,
                       colMap=cm.jet):
        """Overlay Gridded LoS velocity data from grdex files

        Parameters
        ---------
        pltColBar : Optional[bool]

        overlayRadNames : Optional[bool]

        annotateTime : Optional[bool]

        colorBarLabelSize : Optional[float]

        colMap : Optional[ ]

        Note
        ----
        Belongs to class MapConv

        Returns
        -------
        Gridded LoS data is overlayed on the map object. HOW? OR IN WHAT
        VARIABLE?

        """
        import matplotlib
        import datetime
        import numpy
        from davitpy.pydarn.plotting import overlayRadar

        # the color maps work for [0, 1]
        norm = matplotlib.colors.Normalize(0, self.maxVelPlot)

        # dateString to overlay date on plot
        dateStr = '{:%Y/%b/%d %H%M} - {:%H%M} UT'.format(
            self.grdData.sTime, self.grdData.eTime)

        # get the standard location and LoS Vel parameters.
        mlatsPlot = self.grdData.vector.mlat
        mlonsPlot = self.grdData.vector.mlon
        velsPlot = self.grdData.vector.velmedian
        azmsPlot = self.grdData.vector.kvect
        stIds = self.grdData.vector.stid

        for nn in range(len(mlatsPlot)):

            # calculate stuff for plotting such as vector length, azimuth etc
            vecLen = velsPlot[nn] * self.lenFactor / self.radEarth / 1000.
            endLat = numpy.arcsin(numpy.sin(numpy.deg2rad(mlatsPlot[nn])) *
                                  numpy.cos(vecLen) +
                                  numpy.cos(numpy.deg2rad(mlatsPlot[nn])) *
                                  numpy.sin(vecLen) *
                                  numpy.cos(numpy.deg2rad(azmsPlot[nn])))
            endLat = numpy.degrees(endLat)
            delLon = (numpy.arctan2(numpy.sin(numpy.deg2rad(azmsPlot[nn])) *
                      numpy.sin(vecLen) *
                      numpy.cos(numpy.deg2rad(mlatsPlot[nn])),
                      numpy.cos(vecLen) -
                      numpy.sin(numpy.deg2rad(mlatsPlot[nn])) *
                      numpy.sin(numpy.deg2rad(endLat))))

            # depending on whether we have 'mag' or 'mlt' coords,
            # calculate endLon
            if self.plotCoords == 'mag':
                endLon = mlonsPlot[nn] + numpy.degrees(delLon)
            elif self.plotCoords == 'mlt':
                endLon = (mlonsPlot[nn] + numpy.degrees(delLon)) / 15.
            else:
                logging.warning('Check the coords')

            # get the start and end vecs
            xVecStrt, yVecStrt = self.mObj(mlonsPlot[nn], mlatsPlot[nn],
                                           coords=self.plotCoords)
            xVecEnd, yVecEnd = self.mObj(endLon, endLat,
                                         coords=self.plotCoords)

            # Plot the start point and then append the vector indicating magn.
            # and azimuth
            self.grdPltStrt = self.mObj.scatter(xVecStrt, yVecStrt,
                                                c=velsPlot[nn], s=10., vmin=0,
                                                vmax=self.maxVelPlot,
                                                alpha=0.7, cmap=colMap,
                                                zorder=5., edgecolor='none')
            self.grdPltVec = self.mObj.plot([ xVecStrt, xVecEnd ],
                                            [ yVecStrt, yVecEnd ],
                                            color=colMap(norm(velsPlot[nn])))

        # Check and overlay colorbar
        if pltColBar:
            cbar = matplotlib.pyplot.colorbar(self.grdPltStrt,
                                              orientation='vertical')
            cbar.set_label('Velocity [m/s]', size=colorBarLabelSize)
        # Check and overlay radnames
        if overlayRadNames:
            overlayRadar(self.mObj, fontSize=12, ids=self.grdData.stid)
        # Check and annotate time
        if annotateTime:
            self.axisHandle.annotate(dateStr, xy=(0.5, 1.), fontsize=12,
                                     ha="center", xycoords="axes fraction",
                                     bbox=dict(boxstyle='round,pad=0.2',
                                     fc="w", alpha=0.3))

    def calcFitCnvVel(self):
        """Calculate fitted convection velocity magnitude and azimuth from
           mapex data (basically coefficients of the fit)

        Returns
        ---------
        mlatsPlot : NEEDS TYPE

        mlonsPlot : NEEDS TYPE

        velMagn : NEEDS TYPE

        velAzm : NEEDS TYPE

            Arrays of Fitted velocity magnitude and azimuth

        Note
        ----
        Belongs to class MapConv

        Example
        -------
            ( mlat, mlon, magn, azimuth ) = MapConv.calcFitCnvVel()

        """

        import datetime
        import numpy
        import scipy

        if self.hemi == 'north' :
            hemisphere = 1
        else :
            hemisphere = -1

        # get the standard location/LoS(grid) Vel parameters.
        mlatsPlot = self.mapData.grid.vector.mlat
        mlonsPlot = self.mapData.grid.vector.mlon
        velsPlot = self.mapData.grid.vector.velmedian
        azmsPlot = self.mapData.grid.vector.kvect
        stIds = self.mapData.grid.vector.stid

        # Alright we have the parameters but we need to calculate the coeffs
        # for eField and then calc eField and Fitted Vels.

        # Some important parameters from fitting.
        coeffFit = numpy.array( [ self.mapData.Np2 ] )
        orderFit = self.mapData.fitorder
        latShftFit = self.mapData.latshft
        lonShftFit = self.mapData.lonshft
        latMinFit = self.mapData.latmin

        # Set up more parameters for getting the fitted vectors
        # the absolute part is for the southern hemisphere
        theta = numpy.deg2rad( 90. - numpy.absolute( mlatsPlot ) )
        thetaMax = numpy.deg2rad( 90. - numpy.absolute( latMinFit ) )

        # Now we need the adjusted/normalized values of the theta such that
        # full range of theta runs from 0 to pi.  At this point if you are
        # wondering why we are doing this, It would be good to refer Mike's
        # paper
        alpha = numpy.pi / thetaMax
        thetaPrime = alpha * theta
        x = numpy.cos( thetaPrime )

        # Here we evaluate the associated legendre polynomials..from order 0
        # to orderFit we use scipy.special.lpmn() function to get the assciated
        # legendre polynomials...but it doesnt accept an array...so do loop
        # calculate the leg.pol for each value of x and append these arrays to
        # a new array
        for j in range(len(x)):
            plmTemp = scipy.special.lpmn( orderFit, orderFit, x[j] )
            if j == 0:
                plmFit = numpy.append( [plmTemp[0]], [plmTemp[0]], axis=0 )
            else:
                plmFit = numpy.append( plmFit, [plmTemp[0]], axis=0 )

        # we need to remove the first part/subarray/element (whatever you want
        # to call it) of this array its there twice....look at j==0 part.
        plmFit = numpy.delete(plmFit, 0, 0)
        phi = numpy.deg2rad(mlonsPlot)

        # now do the index legender part,
        # We are doing Associated Legendre Polynomials but for each polynomial
        # we have two coefficients one for cos(phi) and the other for sin(phi),
        # so we do spherical harmonics for a real valued function using
        # sin(phi) and cos(phi) rather than exp(i*phi).

        # we use a lambda function for the index legender part, since we use
        # it in other places as well.  A good thing about python is this lambda
        # functions..u dont have to define another function for this.
        indexLgndr = lambda l, m : ( m == 0 and l**2 ) or \
            ( (l != 0 ) and (m != 0) and l**2 + 2 * m - 1 ) or 0
        kMax = indexLgndr( orderFit, orderFit )

        # set up arrays and small stuff for the eFld coeffs calculation
        thetaECoeffs = numpy.zeros((kMax + 2, len(theta)))
        phiECoeffs = numpy.zeros((kMax + 2, len(theta)))

        qPrime = numpy.array( numpy.where( thetaPrime != 0. ) )
        qPrime = qPrime[0]
        q = numpy.array( numpy.where( theta != 0. ) )
        q = q[0]

        # finally get to converting coefficients for the potential into
        # coefficients for elec. Field
        coeffFitFlat = coeffFit.flatten()
        for m in range( orderFit + 1 ):
            for L in range( m, orderFit + 1 ):

                k3 = indexLgndr( L, m )
                k4 = indexLgndr( L, m )

                if k3 >= 0:
                    thetaECoeffs[k4, qPrime] = thetaECoeffs[k4, qPrime] - \
                        coeffFitFlat[k3] * alpha * L * \
                        numpy.cos(thetaPrime[qPrime]) \
                        / numpy.sin(thetaPrime[qPrime]) / self.radEarthMtrs
                    phiECoeffs[k4, q] = phiECoeffs[k4, q] - \
                        coeffFitFlat[k3 + 1] * m / numpy.sin(theta[q]) / \
                        self.radEarthMtrs
                    phiECoeffs[k4 + 1, q] = phiECoeffs[k4 + 1, q] + \
                        coeffFitFlat[k3] * m / numpy.sin(theta[q]) / \
                        self.radEarthMtrs

                if L < orderFit:
                    k1 = indexLgndr( L+1, m )
                else:
                    k1 = -1

                k2 = indexLgndr(L, m )

                if k1 >= 0:
                    thetaECoeffs[k2, qPrime] = thetaECoeffs[k2, qPrime] + \
                        coeffFitFlat[k1] * alpha * (L + 1 + m) / \
                        numpy.sin(thetaPrime[qPrime]) / self.radEarthMtrs

                if m > 0:
                    if k3 >= 0:
                        k3 = k3 + 1
                    k4 = k4 + 1

                    if k1 >= 0:
                        k1 = k1 + 1
                    k2 = k2 + 1

                    if k3 >= 0:
                        thetaECoeffs[k4, qPrime] = thetaECoeffs[k4, qPrime] - \
                            coeffFitFlat[k3] * alpha * L * \
                            numpy.cos(thetaPrime[qPrime]) / \
                            numpy.sin(thetaPrime[qPrime]) / self.radEarthMtrs

                    if k1 >= 0:
                        thetaECoeffs[k2, qPrime] = thetaECoeffs[k2, qPrime] + \
                            coeffFitFlat[k1] * alpha * (L + 1 + m) / \
                            numpy.sin(thetaPrime[qPrime]) / self.radEarthMtrs

        # Calculate the Elec. fld positions where
        thetaEcomp = numpy.zeros( theta.shape )
        phiEcomp = numpy.zeros( theta.shape )

        for m in range( orderFit+1 ):
            for L in range( m, orderFit+1 ):

                k = indexLgndr( L, m )
                # Now in the IDL code we use plmFit[:,L,m] instead of
                # plmFit[:,m,L] like here, this is because we have a different
                # organization of plmFit due to the way scipy.special.lpmn
                # stores values in arrays...
                if m == 0:
                    thetaEcomp = thetaEcomp + thetaECoeffs[k, :] * \
                        plmFit[:, m, L]
                    phiEcomp = phiEcomp + phiECoeffs[k, :] * plmFit[:, m, L]
                else:
                    thetaEcomp = thetaEcomp + thetaECoeffs[k, :] * \
                        plmFit[:, m, L] * numpy.cos(m * phi) + \
                        thetaECoeffs[k + 1, :] * plmFit[:, m, L] * \
                        numpy.sin(m * phi)
                    phiEcomp = phiEcomp + phiECoeffs[k, :] * \
                        plmFit[:, m, L] * numpy.cos(m * phi) + \
                        phiECoeffs[k + 1, :] * plmFit[:, m, L] * \
                        numpy.sin(m * phi)

        # Store the two components of EFld into a single array
        eFieldFit = numpy.append( [thetaEcomp], [phiEcomp], axis=0 )

        # We'll calculate Bfld magnitude now, need to initialize some more
        # stuff
        alti = 300. * 1000.
        bFldPolar = -0.62e-4
        bFldMagn = bFldPolar * (1. - 3. * alti / self.radEarthMtrs) \
            * numpy.sqrt( 3.0*numpy.square( numpy.cos( theta ) ) + 1. )/2

        # get the velocity components from E-field
        velFitVecs = numpy.zeros( eFieldFit.shape )
        velFitVecs[0, :] = eFieldFit[1, :] / bFldMagn
        velFitVecs[1, :] = -eFieldFit[0, :] / bFldMagn

        velMagn = numpy.sqrt(numpy.square(velFitVecs[0, :]) +
                             numpy.square(velFitVecs[1, :]))
        velChkZeroInds = numpy.where( velMagn != 0. )
        velChkZeroInds = velChkZeroInds[0]

        velAzm = numpy.zeros( velMagn.shape )

        if len(velChkZeroInds) == 0:
            velMagn = numpy.array( [0.] )
            velAzm = numpy.array( [0.] )
        else:
            if hemisphere == -1:
                velAzm[velChkZeroInds] = numpy.rad2deg(numpy.arctan2(velFitVecs[1, velChkZeroInds], 
                    velFitVecs[0, velChkZeroInds]))
            else:
                velAzm[velChkZeroInds] = numpy.rad2deg(numpy.arctan2(velFitVecs[1, velChkZeroInds], 
                    -velFitVecs[0, velChkZeroInds]))            
                        
        return mlatsPlot, mlonsPlot, velMagn, velAzm

    def calcCnvPots(self):
        """Calculate equipotential contour values from mapex data (basically coefficients of the fit)

        Returns
        -------
        latCntr : NEEDS TYPE
            Array of latitudes
        lonCntr : NEEDS TYPE
            Array of longitudes
        potArr : NEEDS TYPE
            Array of potentials

        Note
        ----        
        Belongs to class MapConv

        Example
        -------
            (lats, lons, pots) = MapConv.calcCnvPots()

        """
        import datetime
        import numpy
        import scipy


        if self.hemi == 'north':
            hemisphere = 1
            intHemi = 0
        else:
            hemisphere = -1
            intHemi = 1


        # get the standard location parameters.
        mlatsPlot = self.mapData.grid.vector.mlat
        mlonsPlot = self.mapData.grid.vector.mlon
        stIds = self.mapData.grid.vector.stid

        # Alright we have the parameters but we need to 
        # calculate the coeffs for eField and then calc eField and Fitted Vels.
        
        # Some important parameters from fitting.
        coeffFit = numpy.array( [ self.mapData.Np2 ] )
        orderFit = self.mapData.fitorder
        latShftFit = self.mapData.latshft
        lonShftFit = self.mapData.lonshft
        latMinFit = self.mapData.latmin

        # Set up more parameters for getting the fitted vectors
        thetaMax = numpy.deg2rad( 90.-numpy.absolute( latMinFit ) )


        # Set the min plotting latitude...
        plotLatMin = 30

        # we set up a grid to evaluate potential on...
        latStep = 1
        lonStep = 2
        numLats     =  int( ( 90. - plotLatMin ) / latStep )
        numLongs    =  int( 360. / lonStep )+1
        zatArr = numpy.array( range(numLats) * latStep ) + plotLatMin
        zatArr = zatArr * hemisphere
        zonArr = numpy.array( range(numLongs) )* lonStep

        # Right now create a grid kinda stuff with lats and lons
        gridArr = numpy.zeros( (2, numLats * numLongs) )
        counter1 = 0
        for lo in zonArr :
            for la in zatArr :
                gridArr[0, counter1] = la 
                gridArr[1, counter1] = lo
                counter1 = counter1 + 1

        # Now we need to convert a few things to spherical coordinates
        theta = numpy.deg2rad( 90. - numpy.abs(gridArr[0,:]) )
        phi = numpy.deg2rad( gridArr[1,:] )

        # Now we need the adjusted/normalized values of the theta such that full range of theta runs from 0 to pi
        # At this point if you are wondering why we are doing this, It would be good to refer Mike's paper
        alpha = numpy.pi/thetaMax
        tPrime = alpha*theta
        x = numpy.cos(tPrime)


        # Here we evaluate the associated legendre polynomials..from order 0 to orderFit
        # we use scipy.special.lpmn() function to get the assciated legendre polynomials...but it doesnt
        # accept an array...so do loop calculate the leg.pol for each value of x and append these arrays to a new array
        for j in range(len(x)):
            plmTemp = scipy.special.lpmn( orderFit, orderFit, x[j] )
            
            if j == 0:
                plmFit = numpy.append( [plmTemp[0]], [plmTemp[0]], axis = 0 )
            else:
                plmFit = numpy.append( plmFit, [plmTemp[0]], axis= 0 )

        # we need to remove the first part/subarray/element (whatever you want to call it) of this array
        # its there twice, look at j==0 part.
        plmFit = numpy.delete(plmFit, 0, 0)

        # Get to evaluating the potential
        lMax = plmFit.shape
        lMax = lMax[1]
        v= numpy.zeros( phi.shape )


        # we use a lambda function for the index legender part, since we use it in other places as well..
        # a good thing about python is this lambda functions..u dont have to define another function for this....
        indexLgndr = lambda l,m :( m == 0 and l**2 ) or \
            ( (l != 0 ) and (m != 0) and l**2 + 2*m - 1 ) or 0

        coeffFitFlat = coeffFit.flatten()
        for m in range( lMax ):
            for L in range( m, lMax ):
                k = indexLgndr( L, m )
                if m == 0:
                    v = v + coeffFitFlat[k]*plmFit[:,0,L]
                else:
                    v = v + \
                        coeffFitFlat[k]*numpy.cos( m*phi )*plmFit[:,m,L] + \
                        coeffFitFlat[k+1]*numpy.sin( m*phi )*plmFit[:,m,L]

        potArr = numpy.zeros( ( numLongs, numLats ) ) 
        potArr = numpy.reshape(v, potArr.shape)/1000.

        # latShftFit and lonShftFit are almost always zero
        # but in case they are not... we print out a message...
        # you need an extra bit of code to account for the lat shift
        if latShftFit == 0.:

            q = numpy.array( numpy.where( numpy.abs(zatArr) <= numpy.abs(latMinFit) ) )
            q = q[0]
            
            if ( len(q) != 0 ):
                potArr[:,q] = 0
                
        else:
            logging.warning('LatShift is not zero, need to rewrite code for that, currently continuing assuming it is zero')

        # mlt conversion stuff
        if self.plotCoords == 'mlt':
            epoch = timeUtils.datetimeToEpoch(strtTime)
            mltDef = aacgm.mltFromEpoch(epoch,0.0) * 15.
            lonShftFit += mltDef
            gridArr[1,:] = numpy.mod( ( gridArr[1,:] + lonShftFit ) / 15., 24. )
        else:
            gridArr[1,:] = ( gridArr[1,:] + lonShftFit ) 

        latCntr = gridArr[0,:].reshape( ( 181, 60 ) )
        lonCntr = gridArr[1,:].reshape( ( 181, 60 ) )
        
        return latCntr, lonCntr, potArr

    def overlayCnvCntrs(self):
        """Overlay convection contours from mapex data

        Returns
        -------
        cntrPlt : NEEDS TYPE
            contours of convection are overlayed on the map object.

        Note
        ----
        Belongs to class MapConv

        Example
        -------
            MapConv.overlayCnvCntrs()

        """
        from matplotlib.ticker import LinearLocator
        import matplotlib.pyplot as plt


        # get the lats, lons and potentials from calcCnvPots() function
        ( latCntr, lonCntr, potCntr ) = self.calcCnvPots()

        #plot the contours
        xCnt, yCnt = self.mObj( lonCntr, latCntr, coords=self.plotCoords )
        cntrPlt = self.mObj.contour( xCnt, yCnt, potCntr, 
            zorder = 2.,
            vmax=potCntr.max(), vmin=potCntr.min(), 
            colors = 'DarkSlateGray', linewidths=1., 
            locator=LinearLocator(12) )
        plt.clabel(cntrPlt, inline=1, fontsize=10)
        return cntrPlt

    def overlayHMB(self, hmbCol='Gray'):
        """Overlay Heppnard-Maynard boundary from mapex data

        Parameters
        ----------
        hmbCol : Optional[str]

        Returns
        -------
            Heppnard-Maynard boundary is overlayed on the map object.

        Note
        ----
        Belongs to class MapConv

        Example
        -------
            MapConv.overlayHMB()

        """
        xVecHMB, yVecHMB = self.mObj( self.mapData.model.boundarymlon, 
            self.mapData.model.boundarymlat, coords = self.plotCoords )
        grdPltHMB = self.mObj.plot( xVecHMB, yVecHMB, 
            linewidth = 2., linestyle = ':', color = hmbCol, zorder = 4. )
        grdPltHMB2 = self.mObj.plot( xVecHMB, yVecHMB, 
            linewidth = 2., linestyle = '--', color = hmbCol, zorder = 4. )

    def overlayMapModelVel(self, pltColBar=False, 
        annotateTime=True, colorBarLabelSize=15., 
        colMap=cm.jet):
        """Overlay model velocity vectors from mapex data
        
        Parameters
        ----------
        pltColBar : Optional[bool]

        annotateTime : Optional[bool]

        colorBarLabelSize : Optional[float]

        colMap : Optional[ ]

        Returns
        -------
            velocity vectors from the model are overlayed on the map object.

        Note
        ----
        Belongs to class MapConv

        Example
        -------
            MapConv.overlayMapModelVel()

        """
        import matplotlib
        import datetime
        import numpy
        #from davitpy.pydarn.plotting import *

        norm = matplotlib.colors.Normalize(0, self.maxVelPlot) # the color maps work for [0, 1]

        # dateString to overlay date on plot
        dateStr = '{:%Y/%b/%d %H%M} - {:%H%M} UT'.format(
            self.mapData.sTime, self.mapData.eTime)

        # get the standard location and velocity parameters of the model.
        mlatsPlot = self.mapData.model.mlat
        mlonsPlot = self.mapData.model.mlon
        velMagn = self.mapData.model.velmedian
        velAzm = self.mapData.model.kvect

        for nn in range( len(mlatsPlot) ):

            vecLen = velMagn[nn]*self.lenFactor/self.radEarth/1000.
            endLat = numpy.arcsin( numpy.sin(numpy.deg2rad( mlatsPlot[nn] ) )*numpy.cos(vecLen) + \
                numpy.cos( numpy.deg2rad( mlatsPlot[nn] ) )*numpy.sin(vecLen) \
                *numpy.cos(numpy.deg2rad( velAzm[nn] ) ) )
            endLat = numpy.degrees( endLat )
            
            delLon = ( numpy.arctan2( numpy.sin(numpy.deg2rad( velAzm[nn] ) )*numpy.sin(vecLen)*numpy.cos(numpy.deg2rad( mlatsPlot[nn] ) ), numpy.cos(vecLen) - numpy.sin(numpy.deg2rad( mlatsPlot[nn] ) )*numpy.sin(numpy.deg2rad( endLat ) ) ) )
            
            if self.plotCoords == 'mag':
                endLon = mlonsPlot[nn] + numpy.degrees( delLon )
            elif self.plotCoords == 'mlt':
                endLon = ( mlonsPlot[nn] + numpy.degrees( delLon ) )/15.
            else:
                logging.warning('Check the coords.')
                
            
            xVecStrt, yVecStrt = self.mObj(mlonsPlot[nn], mlatsPlot[nn], coords=self.plotCoords)
            xVecEnd, yVecEnd = self.mObj(endLon, endLat, coords = self.plotCoords)

            self.mapModelPltStrt = self.mObj.scatter( xVecStrt, yVecStrt, c=velMagn[nn], s=10.,
                vmin=0, vmax=self.maxVelPlot, alpha=0.7, 
                cmap=colMap, zorder=5., edgecolor='none' )

            self.mapModelPltVec = self.mObj.plot( [ xVecStrt, xVecEnd ], [ yVecStrt, yVecEnd ], 
                color = colMap(norm(velMagn[nn])) )

        # Check and overlay colorbar
        if pltColBar:
            cbar = matplotlib.pyplot.colorbar(self.mapModelPltStrt, orientation='vertical')
            cbar.set_label('Velocity [m/s]', size = colorBarLabelSize)
        # Check and annotate time
        if annotateTime:
            self.axisHandle.annotate( dateStr, xy=(0.5, 1.), fontsize=12, 
                ha="center", xycoords="axes fraction",
                bbox=dict(boxstyle='round,pad=0.2', fc="w", alpha=0.3) )

    def overlayMapFitVel(self, pltColBar=True, 
        overlayRadNames=True, annotateTime=True, 
        colorBarLabelSize=15., colMap=cm.jet):
        """Overlay fitted velocity vectors from mapex data
        
        Parameters
        ----------
        plotColBar : Optional[bool]

        overlayRadNames : Optional[bool]

        annotateTime : Optional[bool]

        colorBarLabelSize : Optional[bool]

        colMap : Optional[ ]

        Returns
        -------
            vectors of fitted convection velocities are overlayed on the map object.

        Note
        ----
        Belongs to class MapConv

        Example
        -------
            MapConv.overlayMapFitVel()

        """
        import matplotlib
        import datetime
        import numpy
        from davitpy.pydarn.plotting import overlayRadar

        norm = matplotlib.colors.Normalize(0, self.maxVelPlot) # the color maps work for [0, 1]

        # dateString to overlay date on plot
        dateStr = '{:%Y/%b/%d %H%M} - {:%H%M} UT'.format(
            self.mapData.sTime, self.mapData.eTime)

        # get the standard location parameters.
        # mlatsPlot = self.mapData.grid.vector.mlat
        # mlonsPlot = self.mapData.grid.vector.mlon
        stIds = self.mapData.grid.vector.stid

        # get the fitted mlat, mlon, velocity magnitude and azimuth from calcFitCnvVel() function
        ( mlatsPlot, mlonsPlot, velMagn, velAzm ) = self.calcFitCnvVel()

        self.mapFitPltStrt = []
        self.mapFitPltVec = []

        for nn in range( len(mlatsPlot) ):

            vecLen = velMagn[nn]*self.lenFactor/self.radEarth/1000.
            endLat = numpy.arcsin( numpy.sin(numpy.deg2rad( mlatsPlot[nn] ) )*numpy.cos(vecLen) \
                + numpy.cos( numpy.deg2rad( mlatsPlot[nn] ) )*numpy.sin(vecLen) \
                *numpy.cos(numpy.deg2rad( velAzm[nn] ) ) )
            endLat = numpy.degrees( endLat )
            
            delLon = ( numpy.arctan2( numpy.sin(numpy.deg2rad( velAzm[nn] ) ) \
                *numpy.sin(vecLen)*numpy.cos(numpy.deg2rad( mlatsPlot[nn] ) ), 
                numpy.cos(vecLen) - numpy.sin(numpy.deg2rad( mlatsPlot[nn] ) ) \
                *numpy.sin(numpy.deg2rad( endLat ) ) ) )
            
            if self.plotCoords == 'mag':
                endLon = mlonsPlot[nn] + numpy.degrees( delLon )
            elif self.plotCoords == 'mlt':
                endLon = ( mlonsPlot[nn] + numpy.degrees( delLon ) )/15.
            else:
                logging.warning('Check the coords.')
                
            
            xVecStrt, yVecStrt = self.mObj(mlonsPlot[nn], mlatsPlot[nn], 
                coords=self.plotCoords)
            xVecEnd, yVecEnd = self.mObj(endLon, endLat, 
                coords = self.plotCoords)

            self.mapFitPltStrt.append(self.mObj.scatter( xVecStrt, yVecStrt, 
                c=velMagn[nn], s=10.,
                vmin=0, vmax=self.maxVelPlot, 
                alpha=0.7, cmap=colMap, zorder=5., 
                edgecolor='none' ))

            self.mapFitPltVec.append(self.mObj.plot( [ xVecStrt, xVecEnd ], [ yVecStrt, yVecEnd ], 
                color = colMap(norm(velMagn[nn])) ))

        # Check and overlay colorbar
        if pltColBar:
            cbar = matplotlib.pyplot.colorbar(self.mapFitPltStrt[0], orientation='vertical')
            cbar.set_label('Velocity [m/s]', size = colorBarLabelSize)
        # Check and overlay radnames
        if overlayRadNames:
            overlayRadar( self.mObj, fontSize=12, ids= self.mapData.grid.stid )
        # Check and annotate time
        if annotateTime:
            self.axisHandle.annotate( dateStr, xy=(0.5, 1.), 
                fontsize=12, ha="center", xycoords="axes fraction",
                bbox=dict(boxstyle='round,pad=0.2', fc="w", alpha=0.3) )
