# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""Plotting/Retreiving SuperDARN gridded velocities, fitted convection
velocities and contour plotting routines

Class
-------
MapConv
-------

"""
import logging
import datetime as dt
import numpy as np

class MapConv(object):
    """Plot/retrieve data from map(ex) and grd(ex) files

    Parameters
    ----------
    start_time : (datetime.datetime)
        start date and time of the data rec
    mobj : (utils.plotUtils.mapObj)
        the map object you want data to be overlayed on.
    ax : (matplotlib.axes._subplots.AxesSubplot)
        the axis handle used
    hemi : (str)
        hemisphere - 'north' or 'south'.  Default is north.
    maxVelScale : (float)
        maximum velocity to be used for plotting (default=1000.0)
    min_vel : (float)
        Minimum velocity to be used for plotting (default=0.0)
    grid_type : (str or NoneType)
        File type for grid file, or None to only load map (default='grd')
    map_type : (str or NoneType)
        File type for map file, or None to only load grid (default='map')

    Attributes
    ----------
    radEarth : (float)
        Earth radius in kilometers
    lenFactor : (float)
        Used to change the length of the vector on the plot
    radEarthMtrs : (float)
        Earth radius in meters
    maxVelPlot : (float)
        maximum velocity to be used for plotting
    min_vel : (float)
        Minimum velocity to be used for plotting
    axisHandle : (matplotlib.axes._subplots.AxesSubplot)
        the axis handle used
    mObj : (utils.plotUtils.mapObj)
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
                       colorBarLabelSize=15.0, colMap=cm.jet)
        Overlay model velocity vectors from mapex data
    overlayMapFitVel(pltColBar=True, overlayRadNames=True, annotateTime=True,
                     colorBarLabelSize=15.0, colMap=cm.jet)
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

    Notes
    ------
    Read a record (from a time) from grd(ex) and/or map(ex) files and plot or
    retreive the gridded LoS velocity vectors, convection contours, fitted
    velocity vectors, model vectors and Heppnard-Maynard Boundary.

    written by Bharat Kunduri and Sebastien de Larquier, 2013-08
    """
    import matplotlib.cm as cm

    def __init__(self, start_time, mobj=None, ax=None, end_time=None,
                 hemi='north', maxVelScale=1000.0, min_vel=0.0, grid_type='grd',
                 map_type='map'):
        from davitpy.pydarn.sdio import sdDataOpen
        import matplotlib as mpl

        # set up some initial parameters
        self.radEarth = 6371.0
        # This is used to change the length of the vector on the plot
        self.lenFactor = 500.0
        self.radEarthMtrs = self.radEarth * 1000.0
        self.maxVelPlot = maxVelScale
        self.min_vel = min_vel
        self.axisHandle = ax
        self.mObj = mobj

        # check if hemi and coords keywords are correct
        assert(hemi == "north" or hemi == "south"), \
            logging.error("hemi should either be 'north' or 'south'")

        # check if the mapObj is indicating the same hemisphere as data
        # requested, if it was provided.
        if mobj is not None:
            if hemi == "north":
                assert(mobj.boundarylats[0] > 0.0), \
                    logging.error("Map and data objects must be from the same"
                                  " hemisphere")
            else:
                assert(mobj.boundarylats[0] <= 0.0), \
                    logging.error("Map and data objects must be from the same"
                                  " hemisphere")

        self.hemi = hemi

        # Read the corresponding data record from both map and grid files.
        # This is the way I'm setting stuff up to avoid confusion of reading
        # and plotting seperately.  Just give the date/hemi and the code reads
        # the corresponding rec
        if end_time is None:
            end_time = start_time + dt.timedelta(minutes=2)

        if grid_type is not None:
            grdPtr = sdDataOpen(start_time, hemi, eTime=end_time,
                                fileType=grid_type)
            try:
                self.grdData = grdPtr.readRec()
            except:
                self.grdData = None
        else:
            self.grdData = None

        if map_type is not None:
            mapPtr = sdDataOpen(start_time, hemi, eTime=end_time,
                                fileType=map_type)
            try:
                self.mapData = mapPtr.readRec()
            except:
                self.mapData = None
        else:
            self.mapData = None

        if self.grdData is None and self.mapData is None:
            estr = "unable to load data for grid type [{:s}] ".format(grid_type)
            estr = "{:s}and map type [{:s}] for ".format(estr, map_type)
            estr = "{:s}[{:} to {:}]".format(estr, start_time, end_time)
            logging.error(estr)

    def __repr__(self):
        """Provides a readable representation of the MapConv object
        """

        out = "SuperDARN Map Convection for the "
        out = "{:s}{:s}ern Hemisphere\n".format(out, self.hemi.capitalize())
        out = "{:s}{:-<77s}".format(out, "")

        # Output the grid and map file information
        if self.grdData is None:
            out = "{:s}\nGrid File: None".format(out)
        else:
            out = "{:s}\nGrid File: {:s}\nGrid Time: {:} to {:}".format(out, \
                self.grdData.fPtr._sdDataPtr__filename, self.grdData.sTime, \
                self.grdData.eTime)

        if self.mapData is None:
            out = "{:s}\nMap File: None".format(out)
        else:
            out = "{:s}\nMap File: {:s}\nMap Time: {:} to {:}".format(out, \
                self.mapData.fPtr._sdDataPtr__filename, self.mapData.sTime, \
                self.mapData.eTime)

        # Indicate whether or not the map and axis handles are initialized
        out = "{:s}\n{:-<77s}\n".format(out, "")
        out = "{:s}Map is {:s}set\n".format(out, "not " if self.mObj is None
                                            else "")
        out = "{:s}Subplot axis is {:s}set".format(out, "not "
                                                   if self.axisHandle is None
                                                   else "")

        return(out)

    def __str__(self):
        """Provide a readable representation of the MapConv object
        """

        out = self.__repr__()
        return out

    def date_string(self, sd_type, label_style="web"):
        """Format a data string using data from an sdDataPtr class object

        Parameters
        ------------
        sd_type : (str)
            Plot 'map' or 'grd' times? 
        label_style : (str)
            Set colorbar label style.  'web'=[m/s]; 'agu'=[$m s^{-1}$]
            (default='web')

        Returns
        --------
        date_str : (str)
            String containing formated date range
        """
        assert sd_type == "grd" or sd_type == "map", \
            logging.error("unknown sdDataPtr type, must be 'map' or 'grd'")

        # Set the date and time formats
        dfmt = '%Y/%b/%d' if label_style == "web" else '%d %b %Y,'
        tfmt = '%H%M' if label_style == "web" else '%H:%M'

        # Set the times
        stime = self.grdData.sTime if sd_type == "grd" else self.mapData.sTime
        etime = self.grdData.eTime if sd_type == "grd" else self.mapData.eTime

        # Set the start time
        date_str = '{:{dd} {tt}} - '.format(stime, dd=dfmt, tt=tfmt)

        # Set the end time, only including the date if it differs from the
        # start time
        if etime.date() == stime.date():
            date_str = '{:s}{:{tt}} UT'.format(date_str, etime, tt=tfmt)
        else:
            date_str = '{:s}{:{dd} {tt}} UT'.format(date_str, etime, dd=dfmt,
                                                    tt=tfmt)

        return date_str

    def overlayGridVel(self, pltColBar=True, overlayRadNames=True,
                       annotateTime=True, colorBarLabelSize=15.0,
                       colMap=cm.jet, label_style="web"):
        """Overlay Gridded LoS velocity data from grd files

        Parameters
        ---------
        pltColBar : (bool)
            Add color bar for velocity (default=True)
        overlayRadNames : (bool)
            Add radar names (default=True)
        annotateTime : (bool)
            Add time to plot (default=True)
        colorBarLabelSize : (float)
            Set colorbar label size (default=15.0)
        colMap : (matplotlib.colors.LinearSegmentedColormap)
            Set color map (default=cm.jet)
        label_style : (str)
            Set colorbar label style.  'web'=[m/s]; 'agu'=[$m s^{-1}$]
            (default='web')

        Note
        ----
        Belongs to class MapConv

        Returns
        -------
        Gridded LoS data is overlayed on the subplot axis contained in the
        MapConv class object
        """
        import matplotlib as mpl
        from davitpy.pydarn.plotting import overlayRadar

        # Test to make sure the necessary attributes have been set
        assert self.grdData is not None, logging.error("no grid data available")
        assert self.mObj is not None, logging.error("no map available")
        assert self.axisHandle is not None, \
            logging.error("no axis handle available")

        # the color maps work for [0, 1]
        norm = mpl.colors.Normalize(self.min_vel, self.maxVelPlot)

        # dateString to overlay date on plot
        date_str = self.date_string("grd", label_style=label_style)

        # get the standard location and LoS Vel parameters.
        mlats_plot = self.grdData.vector.mlat
        mlons_plot = self.grdData.vector.mlon
        vels_plot = self.grdData.vector.velmedian
        azms_plot = self.grdData.vector.kvect

        for nn, nn_mlats in enumerate(mlats_plot):
            # calculate stuff for plotting such as vector length, azimuth etc
            vec_len = (vels_plot[nn] * self.lenFactor / self.radEarth) / 1000.0
            end_lat = np.arcsin(np.sin(np.deg2rad(nn_mlats)) * np.cos(vec_len) +
                                np.cos(np.deg2rad(nn_mlats)) * np.sin(vec_len) *
                                np.cos(np.deg2rad(azms_plot[nn])))
            end_lat = np.degrees(end_lat)
            del_lon = np.arctan2(np.sin(np.deg2rad(azms_plot[nn])) *
                                 np.sin(vec_len) * np.cos(np.deg2rad(nn_mlats)),
                                 np.cos(vec_len) - np.sin(np.deg2rad(nn_mlats))
                                 * np.sin(np.deg2rad(end_lat)))

            # depending on whether we have 'mag' or 'mlt' coords,
            # calculate the end longitude
            end_lon = mlons_plot[nn] + np.degrees(del_lon)

            # get the start and end vecs
            x_vec_strt, y_vec_strt = self.mObj(mlons_plot[nn], nn_mlats,
                                               coords='mag')
            x_vec_end, y_vec_end = self.mObj(end_lon, end_lat, coords='mag')

            # Plot the start point and then append the vector indicating magn.
            # and azimuth
            self.grdPltStrt = self.mObj.scatter(x_vec_strt, y_vec_strt,
                                                c=vels_plot[nn], s=10.0,
                                                vmin=self.min_vel,
                                                vmax=self.maxVelPlot,
                                                alpha=0.7, cmap=colMap,
                                                zorder=5.0, edgecolor='none')
            self.grdPltVec = self.mObj.plot([x_vec_strt, x_vec_end],
                                            [y_vec_strt, y_vec_end],
                                            color=colMap(norm(vels_plot[nn])))

        # Check and overlay colorbar
        if pltColBar:
            cbar = mpl.pyplot.colorbar(self.grdPltStrt, orientation='vertical')
            vlabel = "Velocity [m/s]" if label_style == "web" else \
                     "v [$m s^{-1}$]"
            cbar.set_label(vlabel, size=colorBarLabelSize)
        # Check and overlay radnames
        if overlayRadNames:
            overlayRadar(self.mObj, fontSize=12, ids=self.grdData.stid)
        # Check and annotate time
        if annotateTime:
            self.axisHandle.set_title(date_str, fontsize="medium")

    def calcFitCnvVel(self):
        """Calculate fitted convection velocity magnitude and azimuth from
        map data (basically coefficients of the fit)

        Returns
        ---------
        mlats_plot : (list)
            List of map latitudes
        mlons_plot : (list)
            List of map longitudes
        vel_mag : (numpy.ndarray)
            Array of fitted velocity magnitudes
        vel_azm : (numpy.ndarray)
            Array of velocity azimuths

        Example
        -------
            (mlat, mlon, magn, azimuth) = MapConv.calcFitCnvVel()
        """
        import scipy

        # Test to make sure the necessary attributes have been set
        assert self.mapData is not None, logging.error("no map data available")

        if self.hemi == 'north' :
            hemisphere = 1
        else :
            hemisphere = -1

        # get the standard location/LoS(grid) Vel parameters.
        mlats_plot = self.mapData.grid.vector.mlat
        mlons_plot = self.mapData.grid.vector.mlon
        vels_plot = self.mapData.grid.vector.velmedian
        azms_plot = self.mapData.grid.vector.kvect

        # Alright we have the parameters but we need to calculate the coeffs
        # for eField and then calc eField and Fitted Vels.

        # Some important parameters from fitting.
        coeff_fit = np.array([self.mapData.Np2])
        order_fit = self.mapData.fitorder
        lat_shft_fit = self.mapData.latshft
        lon_shft_fit = self.mapData.lonshft
        lat_min_fit = self.mapData.latmin

        # Set up more parameters for getting the fitted vectors
        # the absolute part is for the southern hemisphere
        theta = np.deg2rad(90.0 - np.absolute(mlats_plot))
        theta_max = np.deg2rad(90.0 - np.absolute(lat_min_fit))

        # Now we need the adjusted/normalized values of the theta such that
        # full range of theta runs from 0 to pi.  At this point if you are
        # wondering why we are doing this, It would be good to refer Mike's
        # paper
        alpha = np.pi / theta_max
        theta_prime = alpha * theta
        x = np.cos(theta_prime)

        # Here we evaluate the associated legendre polynomials..from order 0
        # to order_fit we use scipy.special.lpmn() function to get the assciated
        # legendre polynomials...but it doesnt accept an array...so do loop
        # calculate the leg.pol for each value of x and append these arrays to
        # a new array
        for j,xj in enumerate(x):
            plm_temp = scipy.special.lpmn(order_fit, order_fit, xj)
            if j == 0:
                plm_fit = np.append([plm_temp[0]], [plm_temp[0]], axis=0)
            else:
                plm_fit = np.append(plm_fit, [plm_temp[0]], axis=0)

        # we need to remove the first part/subarray/element (whatever you want
        # to call it) of this array its there twice....look at j==0 part.
        plm_fit = np.delete(plm_fit, 0, 0)
        phi = np.deg2rad(mlons_plot)

        # now do the index legender part,
        # We are doing Associated Legendre Polynomials but for each polynomial
        # we have two coefficients one for cos(phi) and the other for sin(phi),
        # so we do spherical harmonics for a real valued function using
        # sin(phi) and cos(phi) rather than exp(i*phi).

        # we use a lambda function for the index legender part, since we use
        # it in other places as well.  A good thing about python is this lambda
        # functions..u dont have to define another function for this.
        indexLgndr = lambda l, m : (m == 0 and l**2) or \
            ((l != 0) and (m != 0) and l**2 + 2 * m - 1) or 0
        kmax = indexLgndr(order_fit, order_fit)

        # set up arrays and small stuff for the eFld coeffs calculation
        theta_ecoeffs = np.zeros((kmax + 2, len(theta)))
        phi_ecoeffs = np.zeros((kmax + 2, len(theta)))

        qprime = np.array(np.where(theta_prime != 0.0))
        qprime = qprime[0]
        q = np.array(np.where(theta != 0.0))
        q = q[0]

        # finally get to converting coefficients for the potential into
        # coefficients for elec. Field
        coeff_fit_flat = coeff_fit.flatten()
        for m in range(order_fit + 1):
            for l in range(m, order_fit + 1):
                k3 = indexLgndr(l, m)
                k4 = indexLgndr(l, m)

                if k3 >= 0:
                    theta_ecoeffs[k4, qprime] = theta_ecoeffs[k4, qprime] - \
                        coeff_fit_flat[k3] * alpha * l * \
                        np.cos(theta_prime[qprime]) \
                        / np.sin(theta_prime[qprime]) / self.radEarthMtrs
                    phi_ecoeffs[k4, q] = phi_ecoeffs[k4, q] - \
                        coeff_fit_flat[k3 + 1] * m / np.sin(theta[q]) / \
                        self.radEarthMtrs
                    phi_ecoeffs[k4 + 1, q] = phi_ecoeffs[k4 + 1, q] + \
                        coeff_fit_flat[k3] * m / np.sin(theta[q]) / \
                        self.radEarthMtrs

                if l < order_fit:
                    k1 = indexLgndr(l+1, m)
                else:
                    k1 = -1

                k2 = indexLgndr(l, m)

                if k1 >= 0:
                    theta_ecoeffs[k2, qprime] = theta_ecoeffs[k2, qprime] + \
                        coeff_fit_flat[k1] * alpha * (l + 1 + m) / \
                        np.sin(theta_prime[qprime]) / self.radEarthMtrs

                if m > 0:
                    if k3 >= 0:
                        k3 = k3 + 1
                    k4 = k4 + 1

                    if k1 >= 0:
                        k1 = k1 + 1
                    k2 = k2 + 1

                    if k3 >= 0:
                        theta_ecoeffs[k4, qprime] = theta_ecoeffs[k4, qprime] \
                            - coeff_fit_flat[k3] * alpha * l * \
                            np.cos(theta_prime[qprime]) / \
                            np.sin(theta_prime[qprime]) / self.radEarthMtrs

                    if k1 >= 0:
                        theta_ecoeffs[k2, qprime] = theta_ecoeffs[k2, qprime] \
                            + coeff_fit_flat[k1] * alpha * (l + 1 + m) / \
                            np.sin(theta_prime[qprime]) / self.radEarthMtrs

        # Calculate the Elec. fld positions where
        theta_ecomp = np.zeros(theta.shape)
        phi_ecomp = np.zeros(theta.shape)

        for m in range(order_fit + 1):
            for l in range(m, order_fit + 1):
                k = indexLgndr(l, m)
                # Now in the IDL code we use plm_fit[:,l,m] instead of
                # plm_fit[:,m,l] like here, this is because we have a different
                # organization of plm_fit due to the way scipy.special.lpmn
                # stores values in arrays...
                if m == 0:
                    theta_ecomp = theta_ecomp + theta_ecoeffs[k,:] * \
                                 plm_fit[:,m,l]
                    phi_ecomp = phi_ecomp + phi_ecoeffs[k,:] * plm_fit[:,m,l]
                else:
                    theta_ecomp = theta_ecomp + theta_ecoeffs[k,:] * \
                        plm_fit[:,m,l] * np.cos(m * phi) + \
                        theta_ecoeffs[k+1,:] * plm_fit[:,m,l] * np.sin(m * phi)
                    phi_ecomp = phi_ecomp + phi_ecoeffs[k,:] * \
                        plm_fit[:,m,l] * np.cos(m * phi) + \
                        phi_ecoeffs[k+1,:] * plm_fit[:,m,l] * np.sin(m * phi)

        # Store the two components of EFld into a single array
        efield_fit = np.append([theta_ecomp], [phi_ecomp], axis=0)

        # We'll calculate Bfld magnitude now, need to initialize some more
        # stuff
        alti = 300.0 * 1000.0
        b_fld_polar = -0.62e-4
        b_fld_mag = b_fld_polar * (1.0 - 3.0 * alti / self.radEarthMtrs) \
            * np.sqrt(3.0 * np.square(np.cos(theta)) + 1.0) / 2

        # get the velocity components from E-field
        vel_fit_vecs = np.zeros(efield_fit.shape)
        vel_fit_vecs[0,:] = efield_fit[1,:] / b_fld_mag
        vel_fit_vecs[1,:] = -efield_fit[0,:] / b_fld_mag

        vel_mag = np.sqrt(np.square(vel_fit_vecs[0,:]) +
                          np.square(vel_fit_vecs[1,:]))
        vel_chk_zero_inds = np.where(vel_mag != 0.0)
        vel_chk_zero_inds = vel_chk_zero_inds[0]

        vel_azm = np.zeros(vel_mag.shape)

        if len(vel_chk_zero_inds) == 0:
            vel_mag = np.array([0.0])
            vel_azm = np.array([0.0])
        else:
            if hemisphere == -1:
                vel_azm[vel_chk_zero_inds] = np.rad2deg(np.arctan2(vel_fit_vecs[1,vel_chk_zero_inds], vel_fit_vecs[0,vel_chk_zero_inds]))
            else:
                vel_azm[vel_chk_zero_inds] = np.rad2deg(np.arctan2(vel_fit_vecs[1,vel_chk_zero_inds], -vel_fit_vecs[0,vel_chk_zero_inds]))            
                        
        return mlats_plot, mlons_plot, vel_mag, vel_azm

    def calcCnvPots(self, plot_lat_min=30):
        """Calculate equipotential contour values from map data (basically
        coefficients of the fit)

        Parameters
        -----------
        plot_lat_min : (int)
            Minimum plot latitude (default=30)

        Returns
        -------
        latCntr : (numpy.ndarray)
            Array of latitudes
        lonCntr : (numpy.ndarray)
            Array of longitudes
        potArr : (numpy.ndarray)
            Array of potentials

        Note
        ----        
        Belongs to class MapConv

        Example
        -------
            (lats, lons, pots) = MapConv.calcCnvPots()
        """
        import scipy

        # Test to make sure the necessary attributes have been set
        assert self.mapData is not None, logging.error("no map data available")
        hemisphere = 1 if self.hemi == 'north' else -1

        # get the standard location parameters.
        mlats_plot = self.mapData.grid.vector.mlat
        mlons_plot = self.mapData.grid.vector.mlon

        # Alright we have the parameters but we need to 
        # calculate the coeffs for efield and then calc efield and Fitted Vels.
        
        # Some important parameters from fitting.
        coeff_fit = np.array([self.mapData.Np2])
        order_fit = self.mapData.fitorder
        lat_shft_fit = self.mapData.latshft
        lon_shft_fit = self.mapData.lonshft
        lat_min_fit = self.mapData.latmin

        # Set up more parameters for getting the fitted vectors
        theta_max = np.deg2rad(90.0 - np.absolute(lat_min_fit))

        # we set up a grid to evaluate potential on...
        lat_step = 1
        lon_step = 2
        num_lats = int((90.0 - plot_lat_min) / lat_step)
        num_longs = int(360.0 / lon_step) + 1
        zat_arr = np.array(range(num_lats) * lat_step) + plot_lat_min
        zat_arr = zat_arr * hemisphere
        zon_arr = np.array(range(num_longs))* lon_step

        # Right now create a grid kinda stuff with lats and lons
        grid_arr = np.zeros((2, num_lats * num_longs))
        counter1 = 0
        for lo in zon_arr :
            for la in zat_arr :
                grid_arr[0, counter1] = la 
                grid_arr[1, counter1] = lo
                counter1 = counter1 + 1

        # Now we need to convert a few things to spherical coordinates
        theta = np.deg2rad(90.0 - np.abs(grid_arr[0,:]))
        phi = np.deg2rad(grid_arr[1,:])

        # Now we need the adjusted/normalized values of the theta such that
        # full range of theta runs from 0 to pi.  At this point if you are
        # wondering why we are doing this, refer Mike's paper (REF NEEDED)
        alpha = np.pi / theta_max
        x = np.cos(alpha * theta)

        # Here we evaluate the associated legendre polynomials..from order 0 to
        # order_fit.  We use scipy.special.lpmn() function to get the assciated
        # legendre polynomials...but it doesn't accept an array...so do loop
        # calculate the leg.pol for each value of x and append these arrays to
        # a new array
        for j,xj in enumerate(x):
            plm_temp = scipy.special.lpmn(order_fit, order_fit, xj)
            
            if j == 0:
                plm_fit = np.append([plm_temp[0]], [plm_temp[0]], axis=0)
            else:
                plm_fit = np.append(plm_fit, [plm_temp[0]], axis=0)

        # we need to remove the first part/subarray/element (whatever you want
        # to call it) of this array. It's there twice, look at j==0 part.
        plm_fit = np.delete(plm_fit, 0, 0)

        # Get to evaluating the potential
        lmax = plm_fit.shape
        lmax = lmax[1]
        v = np.zeros(phi.shape)

        # we use a lambda function for the index legender part, since we use it
        # in other places as well.
        indexLgndr = lambda l,m : (m == 0 and l**2) or \
            ((l != 0) and (m != 0) and l**2 + 2*m - 1) or 0

        coeff_fit_flat = coeff_fit.flatten()
        for m in range(lmax):
            for l in range(m, lmax):
                k = indexLgndr(l, m)
                if m == 0:
                    v = v + coeff_fit_flat[k] * plm_fit[:,0,l]
                else:
                    v = v + \
                        coeff_fit_flat[k]*np.cos(m * phi) * plm_fit[:,m,l] + \
                        coeff_fit_flat[k+1]*np.sin(m * phi) * plm_fit[:,m,l]

        pot_arr = np.zeros((num_longs, num_lats))
        pot_arr = np.reshape(v, pot_arr.shape) / 1000.0

        # lat_shft_fit and lon_shft_fit are almost always zero
        # but in case they are not... we print out a message...
        # you need an extra bit of code to account for the lat shift
        if lat_shft_fit == 0.0:
            q = np.array(np.where(np.abs(zat_arr) <= np.abs(lat_min_fit)))
            q = q[0]

            if len(q) != 0:
                pot_arr[:,q] = 0
        else:
            estr = 'LatShift is not zero, need to rewrite code for that, '
            estr = '{:s}currently continuing assuming it is zero'.format(estr)
            logging.warning(estr)

        grid_arr[1,:] = (grid_arr[1,:] + lon_shft_fit)

        lat_cntr = grid_arr[0,:].reshape((181, 60))
        lon_cntr = grid_arr[1,:].reshape((181, 60))

        return lat_cntr, lon_cntr, pot_arr

    def overlayCnvCntrs(self, zorder=2, line_color="DarkSlateGray",
                        line_width=1.0, font_size=10.0, plot_label=True):
        """Overlay convection contours from map data

        Parameters
        -----------
        zorder : (int)
            Specify the top-to-bottom ordering of layers for the contours
            (default=2)
        line_color : (str/float)
            Specify the line color for the contours (default='DarkSlateGray')
        line_width : (float)
            Specify the contour line width (default=1.0)
        font_size : (float)
            Specify the font size for the contour labels (default=10.0)
        plot_label : (bool)
            Specify whether or not to plot the contour labels (default=True)

        Returns
        -------
        cntr_plt : (matplotlib.contour.QuadContourSet)
            contours of convection are overlayed on the map object.

        Example
        -------
            MapConv.overlayCnvCntrs()
        """
        from matplotlib.ticker import LinearLocator
        import matplotlib.pyplot as plt

        # Test to make sure the necessary attributes have been set
        assert self.mapData is not None, logging.error("no map data available")
        assert self.mObj is not None, logging.error("no map available")

        # get the lats, lons and potentials from calcCnvPots() function
        (lat_cntr, lon_cntr, pot_cntr) = self.calcCnvPots()

        # plot the contours
        x_cntr, y_cntr = self.mObj(lon_cntr, lat_cntr, coords='mag')
        cntr_plt = self.mObj.contour(x_cntr, y_cntr, pot_cntr, zorder=zorder,
                                     vmax=pot_cntr.max(), vmin=pot_cntr.min(),
                                     colors=line_color, linewidths=line_width,
                                     locator=LinearLocator(12))

        if plot_label:
            plt.clabel(cntr_plt, inline=1, fontsize=font_size)

        return cntr_plt

    def overlayHMB(self, hmbCol='Gray'):
        """Overlay Heppnard-Maynard boundary from map data

        Parameters
        ----------
        hmbCol : (str)
            Specify color of the HMB

        Returns
        -------
            Heppnard-Maynard boundary is overlayed on the map object.

        Example
        -------
            MapConv.overlayHMB()

        """
        # Test to make sure the necessary attributes have been set
        assert self.mapData is not None, logging.error("no map data available")
        assert self.mObj is not None, logging.error("no map available")

        x_vec_hmb, y_vec_hmb = self.mObj(self.mapData.model.boundarymlon, 
                                         self.mapData.model.boundarymlat,
                                         coords='mag')
        grd_plt_hmb = self.mObj.plot(x_vec_hmb, y_vec_hmb, linewidth=2.0,
                                     linestyle=':', color=hmbCol, zorder=4.0)
        grd_plt_hmb2 = self.mObj.plot(x_vec_hmb, y_vec_hmb, linewidth=2.0,
                                      linestyle='--', color=hmbCol, zorder=4.0)

    def overlayMapModelVel(self, pltColBar=False, annotateTime=True,
                           colorBarLabelSize=15.0, colMap=cm.jet,
                           label_style="web"):
        """Overlay model velocity vectors from the map data

        Parameters
        ----------
        pltColBar : (bool)
            Plot color bar (default=True)
        annotateTime : (bool)
            Add timestamp to axis (default=True)
        colorBarLabelSize : (float)
            Specify label size for colorbar (default=15.0)
        colMap : (matplotlib.colors.LinearSegmentedColormap)
            Set color map (default=cm.jet)
        label_style : (str)
            Set colorbar label style.  'web'=[m/s]; 'agu'=[$m s^{-1}$]
            (default='web')

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
        import matplotlib as mpl

        # Test to make sure the necessary attributes have been set
        assert self.mapData is not None, logging.error("no map data available")
        assert self.mObj is not None, logging.error("no map available")
        assert self.axisHandle is not None, \
            logging.error("no axis handle available")

        # the color maps work for [0, 1]
        norm = mpl.colors.Normalize(self.min_vel, self.maxVelPlot)

        # date_string to overlay date on plot
        date_str = self.date_string("map", label_style=label_style)

        # get the standard location and velocity parameters of the model.
        mlats_plot = self.mapData.model.mlat
        mlons_plot = self.mapData.model.mlon
        vel_mag = self.mapData.model.velmedian
        vel_azm = self.mapData.model.kvect

        for nn, nn_mlats in enumerate(mlats_plot):
            vec_len = vel_mag[nn] * self.lenFactor / self.radEarth / 1000.0
            end_lat = np.arcsin(np.sin(np.deg2rad(nn_mlats)) * np.cos(vec_len) +
                               np.cos(np.deg2rad(nn_mlats)) * np.sin(vec_len) *
                               np.cos(np.deg2rad(vel_azm[nn])))
            end_lat = np.degrees(end_lat)

            del_lon = (np.arctan2(np.sin(np.deg2rad(vel_azm[nn])) *
                                  np.sin(vec_len) *
                                  np.cos(np.deg2rad(nn_mlats)), np.cos(vec_len)
                                  - np.sin(np.deg2rad(nn_mlats)) *
                                  np.sin(np.deg2rad(end_lat))))

            end_lon = mlons_plot[nn] + np.degrees(del_lon)

            x_vec_strt, y_vec_strt = self.mObj(mlons_plot[nn], nn_mlats,
                                               coords='mag')
            x_vec_end, y_vec_end = self.mObj(end_lon, end_lat, coords='mag')

            self.mapModelPltStrt = self.mObj.scatter(x_vec_strt, y_vec_strt,
                                                     c=vel_mag[nn], s=10.0,
                                                     vmin=self.min_vel,
                                                     vmax=self.maxVelPlot,
                                                     alpha=0.7, cmap=colMap,
                                                     zorder=5.0,
                                                     edgecolor='none')

            map_color = colMap(norm(vel_mag[nn]))
            self.mapModelPltVec = self.mObj.plot([x_vec_strt, x_vec_end],
                                                 [y_vec_strt, y_vec_end],
                                                 color=map_color)

        # Check and overlay colorbar
        if pltColBar:
            cbar = mpl.pyplot.colorbar(self.mapModelPltStrt,
                                       orientation='vertical')
            vlabel = "Velocity [m/s]" if label_style == "web" else \
                     "v [$m s^{-1}$]"
            cbar.set_label(vlabel, size = colorBarLabelSize)
        # Check and annotate time
        if annotateTime:
            self.axisHandle.set_title(date_str, fontsize="medium")

    def overlayMapFitVel(self, pltColBar=True, overlayRadNames=True,
                         annotateTime=True, colorBarLabelSize=15.0,
                         colMap=cm.jet, label_style="web"):
        """Overlay fitted velocity vectors from the map data
        
        Parameters
        ----------
        plotColBar : (bool)
            Add colorbar to plot (default=True)
        overlayRadNames : (bool)
            Overlay radar names (default=True)
        annotateTime : (bool)
            Add timestamp to axis (default=True)
        colorBarLabelSize : (float)
            Specify colorbar label size (default=15.0)
        colMap : (matplotlib.colors.LinearSegmentedColormap)
            Set color map (default=cm.jet)
        label_style : (str)
            Set colorbar label style.  'web'=[m/s]; 'agu'=[$m s^{-1}$]
            (default='web')

        Returns
        -------
            vectors of fitted convection velocities are overlayed on the map
            object.

        Note
        ----
        Belongs to class MapConv

        Example
        -------
            MapConv.overlayMapFitVel()
        """
        import matplotlib as mpl
        from davitpy.pydarn.plotting import overlayRadar

        # Test to make sure the necessary attributes have been set
        assert self.mapData is not None, logging.error("no map data available")
        assert self.mObj is not None, logging.error("no map available")
        assert self.axisHandle is not None, \
            logging.error("no axis handle available")

        # the color maps work for [0, 1]
        norm = mpl.colors.Normalize(self.min_vel, self.maxVelPlot)

        # dateString to overlay date on plot
        date_str = self.date_string("map", label_style=label_style)

        # get the fitted mlat, mlon, velocity magnitude and azimuth from
        # calcFitCnvVel() function
        (mlats_plot, mlons_plot, vel_mag, vel_azm) = self.calcFitCnvVel()

        self.mapFitPltStrt = []
        self.mapFitPltVec = []

        for nn, nn_mlats in enumerate(mlats_plot):
            vec_len = vel_mag[nn] * self.lenFactor / self.radEarth / 1000.0
            end_lat = np.arcsin(np.sin(np.deg2rad(nn_mlats)) * np.cos(vec_len) +
                               np.cos(np.deg2rad(nn_mlats)) * np.sin(vec_len) *
                               np.cos(np.deg2rad(vel_azm[nn])))
            end_lat = np.degrees(end_lat)
            
            del_lon = np.arctan2(np.sin(np.deg2rad(vel_azm[nn])) *
                                 np.sin(vec_len) * np.cos(np.deg2rad(nn_mlats)),
                                 np.cos(vec_len) - np.sin(np.deg2rad(nn_mlats))
                                 * np.sin(np.deg2rad(end_lat)))

            end_lon = mlons_plot[nn] + np.degrees(del_lon)

            x_vec_strt, y_vec_strt = self.mObj(mlons_plot[nn], nn_mlats,
                                           coords='mag')
            x_vec_end, y_vec_end = self.mObj(end_lon, end_lat, coords='mag')

            self.mapFitPltStrt.append(self.mObj.scatter(x_vec_strt, y_vec_strt, 
                                                        c=vel_mag[nn], s=10.0,
                                                        vmin=self.min_vel,
                                                        vmax=self.maxVelPlot, 
                                                        alpha=0.7, cmap=colMap,
                                                        zorder=5.0,
                                                        edgecolor='none'))

            map_color = colMap(norm(vel_mag[nn]))
            self.mapFitPltVec.append(self.mObj.plot([x_vec_strt, x_vec_end],
                                                    [y_vec_strt, y_vec_end], 
                                                    color=map_color))

        # Check and overlay colorbar
        if pltColBar:
            cbar = mpl.pyplot.colorbar(self.mapFitPltStrt[0],
                                       orientation='vertical')
            vlabel = "Velocity [m/s]" if label_style == "web" else \
                     "v [$m s^{-1}$]"
            cbar.set_label(vlabel, size=colorBarLabelSize)
        # Check and overlay radnames
        if overlayRadNames:
            overlayRadar(self.mObj, fontSize=12, ids=self.mapData.grid.stid)
        # Check and annotate time
        if annotateTime:
            self.axisHandle.set_title(date_str, fontsize="medium")
