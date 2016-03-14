# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""Van Allen probe module

This module handles Van Allen probe (formerly RBSP) foorpoint
calculations and plotting

Class
-------------------------------------------------
rbspFp  FPs reading (or calculating) and plotting
-------------------------------------------------

"""
import logging

############################################################################
# Foot Points (FPs) calculation and plotting
############################################################################
class rbspFp(object):
    """This class reads FPs from the SuperDARN FPs database, or generate them if necessary

    Parameters
    ----------
    sTime :
        start date/time to get FPs
    eTime : Optional[ ]
        end date/time to get FPs (defaulst to 24 hours after `sTime`)
    spacecraft : Optional[ ]
        limit FPs loading to a specific spacecraft
    L_shell_min :
        limit FPs loading to L-shell values greater than this
    L_shell_max : Optional[ ]
        limit FPs loading to L-shell values lesser than this
    apogees_only : Optional[ ]
        record foot-points (usefull if all you want are apogees)

    Attributes
    ----------
    sTime :
        start date/time to get FPs
    eTime : Optional[ ]
        end date/time to get FPs (defaulst to 24 hours after `sTime`)
    L_shell_min :
        limit FPs loading to L-shell values greater than this
    L_shell_max : Optional[ ]
        limit FPs loading to L-shell values lesser than this
    spacecraft : Optional[ ]
        limit FPs loading to a specific spacecraft

    Methods
    -------
    map(hemisphere='north', boundinglat=35, spacecraft=None, legend=True, date=True, 
        apogees=False)
        Plot footpoints on a map
    showISR(myMap, isr)
        Overlay incoherent-scatter radar field-of-views on map
    
    Example
    -------
        # Get all the FPs for 1/Sept/2012 from 0 to 6 UT
        from datetime import datetime
        import rbsp
        sTime = datetime(2012,9,1,0)
        eTime = datetime(2012,9,1,6)
        fps = rbsp.rbspFp(sTime, eTime)
        # Pretty print the apogees in that period
        print fps
        # Plot them on a map
        fps.map()

    Notes
    -----
    Try not to request more than 24 hours at once, unless all you want are apogees.

    written by Sebastien de Larquier, 2013-03

    """

    def __init__(self, sTime, eTime=None, spacecraft=None, 
        L_shell_min=None, L_shell_max=None,  
        apogees_only=False):
        from datetime import datetime, timedelta
        from davitpy import rcParams

        # MongoDB server
        self._db_user = rcParams['SDBREADUSER']
        self._db_pswd = rcParams['SDBREADPASS']
        self._db_host = rcParams['SDDB']
        self._db_name = 'rbsp'

        # Input
        self.sTime = sTime
        self.eTime = eTime if eTime else sTime + timedelta(hours=24)
        self._spacecraft = spacecraft.lower() if spacecraft else ['a','b']
        self.L_shell_min = L_shell_min
        self.L_shell_max = L_shell_max
        self._apogees_only = apogees_only

        # Connect to DB
        isDb = self.__getFpsFromDb()
        if not isDb:
            orbit = self.__getOrbit()
            trace = self.__getTrace(orbit)
            self.scraft = orbit['scraft']


    def map(self, hemisphere='north', boundinglat=35, 
        spacecraft=None, legend=True, date=True, 
        apogees=False):
        """Plot FPs on a map

        Parameters
        ----------
        hemisphere : Optional[str]
            plot FPs in this hemisphere ('north' or 'south')
        boundinglat : Optional[int]
            bounding latitude of map (absolute value)
        spacecraft : Optional[char]
            limit the plotting to one spacecraft ('a' or 'b')
        legend : Optional[bool]
            to show or not to show the legend
        date : Optional[bool]
            to show or not to show the date
        apogees : Optional[bool]
            to show or not to show the apogees

        Returns
        -------
        myMap : mpl_toolkits.basemap.Basemap

        Notes
        -----
        Belongs to class rbspFp

        Example
        -------
            # To plot 2 panels (1 per hemisphere)
            fig = figure(figsize=(11,8))
            subplot(121)
            fps.map()
            subplot(122)
            fps.map(hemisphere='South')
            fig.tight_layout()

        """
        from mpl_toolkits.basemap import Basemap
        from pylab import gca

        ax = gca()

        if hemisphere.lower() == 'north':
            projection = 'npstere'
            sgn = 1
            lat = self.latNH
            lon = self.lonNH
        elif hemisphere.lower() == 'south':
            projection = 'spstere'
            sgn = -1
            lat = self.latSH
            lon = self.lonSH

        # Generate map and background
        myMap = Basemap(projection=projection, lon_0=270, boundinglat=sgn*boundinglat, ax=ax)
        myMap.fillcontinents(color='.8')
        myMap.drawmeridians(range(0,360,20), alpha=0.5)
        myMap.drawparallels(range(-80,81,20), alpha=0.5)
        # Calculate FP coordinates
        x, y = myMap(lon, lat)
        # Scatter FPs
        if spacecraft is None or spacecraft == 'a':
            myMap.scatter(x[self.scraft == 'a'], y[self.scraft == 'a'], 
                zorder=5, edgecolors='none', s=10, facecolors='r', 
                alpha=.8)
            if legend:
                ax.text(0, -0.01, 'RBSP-A', transform=ax.transAxes, 
                    color='r', ha='left', va='top')
        if spacecraft is None or spacecraft == 'b':
            myMap.scatter(x[self.scraft == 'b'], y[self.scraft == 'b'], 
                zorder=5, edgecolors='none', s=10, facecolors='b', 
                alpha=.8)
            if legend:
                ax.text(1, -0.01, 'RBSP-B', transform=ax.transAxes, 
                    color='b', ha='right', va='top')
        # Show date/time interval
        if date:
            if self.sTime.date() == self.eTime.date():
                dateTitle = '{:%d/%b/%Y %H:%M UT} - {:%H:%M UT}'
            elif self.sTime.time() == self.eTime.time():
                dateTitle = '{:%d/%b/%Y} - {:%d/%b/%Y (%H:%M UT)}'
            else: dateTitle = '{:%d/%b/%Y %H:%M UT} - {:%d/%b/%Y %H:%M UT}'
            ax.text(0, 1.01, dateTitle.format(self.sTime, self.eTime), transform=ax.transAxes)

        if apogees:
            myMap.scatter(x[self.apogees], y[self.apogees], 
                zorder=5, edgecolors='w', s=10, facecolors='k')
            for ap in self.apogees:
                self.__textHighlighted((x[ap],y[ap]), '{:%H:%M}'.format(self.times[ap]))

        return myMap


    def showISR(self, myMap, isr):
        """overlay ISR fovs on map

        Parameters
        ----------
        myMap : Basemap

        isr : list or str
            a list of ISRs to be plotted (codes include mho, sdt, eiscat, pfisr, risr)

        Notes
        -----
        Belongs to class rbspFp

        """
        if isinstance(isr, str): isr = [isr]

        for rad in isr:
            dbConn = self.__dbConnect('isr')
            if not dbConn: 
                logging.error('Could not access DB')
                return

            qIn = {'code': rad}
            qRes = dbConn.info.find(qIn)
            if qRes.count() == 0: 
                logging.warning('Radar {} not found in db'.format(rad))
                logging.warning('Use one or more in {}'.format(dbConn.codes.find_one()['codes']))
                continue

            for el in qRes:
                x, y = myMap(el['pos']['lon'], el['pos']['lat'])
                myMap.scatter(x, y, zorder=6, s=20, facecolors='k')
                if isinstance(x, list): x, y = x[0], y[0]
                myMap.ax.text(x*1.04, y*0.96, el['code'].upper())
                x, y = myMap(el['fov']['lon'], el['fov']['lat'])
                myMap.plot(x, y, 'g')


    def __getFpsFromDb(self):
        """Get FPs from DB

        Parameters
        ----------
        None

        Returns
        -------
        isSuccess : bool
            True it worked, False otherwise

        Notes
        -----
        Belongs to class:`rbspFp`

        """
        import numpy as np

        dbConn = self.__dbConnect(self._db_name)
        if not dbConn: return False

        isAp = True if self._apogees_only else None

        # Build querry
        qIn = {'time': {'$gte': self.sTime, '$lte': self.eTime}}
        if not self._spacecraft == ['a', 'b']:
            qIn['spacecraft'] = self._spacecraft.upper()
        if self.L_shell_min:
            if 'L' not in qIn: qIn['L'] = {}
            qIn['L']['$gte'] = self.L_shell_min
        if self.L_shell_max:
            if 'L' not in qIn: qIn['L'] = {}
            qIn['L']['$lte'] = self.L_shell_max
        if self._apogees_only:
            qIn['isApogee'] = True
        # Launch query
        qRes = dbConn.ephemeris.find(qIn).sort('time')
        if qRes.count() == 0: return False

        # Store query results
        self.lonNH = []
        self.latNH = []
        self.lonSH = []
        self.latSH = []
        self.times = []
        self.scraft = []
        self.apogees = []
        self.L = []
        for i, el in enumerate(qRes):
            self.lonNH.append( el['lonNH'] )
            self.latNH.append( el['latNH'] )
            self.lonSH.append( el['lonSH'] )
            self.latSH.append( el['latSH'] )
            self.times.append( el['time'] )
            self.scraft.append( el['scraft'] )
            self.L.append( el['L'] )
            if el['isApogee']: self.apogees.append( i )
        self.lonNH = np.array(self.lonNH)
        self.latNH = np.array(self.latNH)
        self.lonSH = np.array(self.lonSH)
        self.latSH = np.array(self.latSH)
        self.times = np.array(self.times)
        self.scraft = np.array(self.scraft)
        self.apogees = np.array(self.apogees)
        self.L = np.array(self.L)

        return True


    def __dbConnect(self, dbName):
        """Try to establish a connection to remote db database

        Parameters
        ----------
        dbName

        Returns
        -------
        dbConn : pymongo database

        Notes
        -----
        Belongs to class rbspFp

        """
        from pymongo import MongoClient
        import sys

        try:
            conn = MongoClient( 'mongodb://{}:{}@{}/{}'.format(self._db_user,
                                                            self._db_pswd, 
                                                            self._db_host,
                                                            dbName) )

            dba = conn[dbName]
        except:
            logging.error('Could not connect to remote DB: ' + sys.exc_info()[0])
            return False

        return dba


    def __getOrbit(self):
        """Get orbit data from APL

        Parameters
        ----------
        None

        Returns
        -------
        orbit : 

        Notes
        -----
        Belongs to class rbspFp

        """
        import urllib2, urllib
        from datetime import datetime

        logging.info('Get orbit from JHU/APL')

        header = 'on'
        cmode = 'geo'
        Cadence = 5

        try:
            [i in self._spacecraft]
            scraft = set(self._spacecraft)
        except:
            scraft = (self._spacecraft)

        orbit = {'time': [], 
                'alt': [],
                'lat': [],
                'lon': [],
                'scraft': []}
        for sc in scraft:
            params = urllib.urlencode({'sDay': str( self.sTime.day ),
                                        'sMonth': str( self.sTime.month ),
                                        'sYear': str( self.sTime.year ),
                                        'sHour': str( self.sTime.hour ),
                                        'sMinute': str( self.sTime.minute ),
                                        'eDay': str( self.eTime.day ),
                                        'eMonth': str( self.eTime.month ),
                                        'eYear': str( self.eTime.year ),
                                        'eHour': str( self.eTime.hour ),
                                        'eMinute': str( self.eTime.minute ),
                                        'Cadence': str( Cadence ),
                                        'mode': str( cmode ),
                                        'scraft': sc,
                                        'header': header,
                                        'getASCII': 'Get ASCII Output'})
            f = urllib2.urlopen("http://athena.jhuapl.edu/LT_Position_Calc", params)
            # f = urllib2.urlopen("http://athena.jhuapl.edu/orbit_pos", params)
            out = f.read().splitlines()
            f.close()

            st = out.index('<pre>')+1
            ed = out.index('</pre>')
            header = out[st].split()
            lines = out[st+1:ed]
            for i,l in enumerate(lines):
                row = l.split()
                cTime = datetime(	int(row[0]), int(row[1]), int(row[2]), 
                                    int(row[3]), int(row[4]), int(row[5])	)
                orbit['time'].append( cTime )
                orbit['alt'].append( float(row[6]) )
                orbit['lat'].append( float(row[7]) )
                orbit['lon'].append( float(row[8]) )
                orbit['scraft'].append( sc )

        return orbit


    def __getTrace(self, data):
        """Trace orbit to the ionosphere

        Parameters
        ----------
        data : dict
            a dictionnary containing ephemeris (with keys 'lat', 'lon', 'alt', 'time')

        Returns
        -------
        Nothing

        Notes
        -----
        Belongs to class rbspFp

        """
        import tsyganenko as ts
        import numpy as np

        fname = 'trace.{:%Y%m%d}.{:%Y%m%d}.dat'.format(self.sTime, self.eTime)
        try:
            trace = ts.tsygTrace(filename=fname)
            logging.info('Read tracing results...')
        except:
            logging.info('Tracing...')
            trace = ts.tsygTrace(data['lat'], data['lon'], data['alt'], datetime=data['time'], rmin=1.047)
            trace.save( fname )

        self.lonNH = trace.lonNH
        self.latNH = trace.latNH
        self.lonSH = trace.lonSH
        self.latSH = trace.latSH
        self.times = trace.datetime

        # Mark apogees
        mins = np.r_[True, trace.rho[1:] >= trace.rho[:-1]] & np.r_[trace.rho[:-1] > trace.rho[1:], True]
        mins[0] = mins[-1] = False
        self.apogees = np.where(mins)[0]


    def __repr__(self):
        """Output formatting?

        Parameters
        ----------
        None

        Returns
        -------
        sOut : str

        """
        sOut = 'Van Allen Probes (a.k.a. RBSP) ionospheric footpoints\n'
        sOut += '{:%Y-%b-%d at %H:%M UT} to {:%Y-%b-%d at %H:%M UT}\n'.format(self.sTime, self.eTime)
        sOut += '\t{} points\n'.format(len(self.times))
        sOut += '\t{} apogee(s):\n'.format(len(self.apogees))

        if len(self.apogees) > 0:
            for i in self.apogees:
                sOut += '\t\t{:%H:%M} UT, {}: ({:6.2f} N, {:6.2f} E)\t({:6.2f} N, {:6.2f} E)\n'.format(self.times[i], self.scraft[i].upper(), 
                                                                                                self.latNH[i], self.lonNH[i], 
                                                                                                self.latSH[i], self.lonSH[i])

        return sOut


    def __textHighlighted(self, xy, text, zorder=None, color='k', fontsize=None):
        """Plot highlighted annotation (with a white lining)

        Parameters
        ----------
        xy :
            position of point to annotate
        text : str
            text to show
        zorder : Optional[ ]
            text zorder
        color : Optional[char]
            text color
         fontsize : Optional[ ]
            text font size

        Notes
        -----
        Belongs to class rbspFp

        """
        import matplotlib as mp
        from pylab import gca

        ax = gca()

        text_path = mp.text.TextPath( (0,0), text, size=fontsize)

        p1 = mp.patches.PathPatch(text_path, ec="w", lw=2, fc="w", alpha=0.7, zorder=zorder, 
                            transform=mp.transforms.IdentityTransform())
        p2 = mp.patches.PathPatch(text_path, ec="none", fc=color, zorder=zorder, 
                            transform=mp.transforms.IdentityTransform())

        offsetbox2 = mp.offsetbox.AuxTransformBox(mp.transforms.IdentityTransform())
        offsetbox2.add_artist(p1)
        offsetbox2.add_artist(p2)

        ax2disp = ax.transAxes.transform
        disp2ax = ax.transAxes.inverted().transform
        data2disp = ax.transData.transform
        disp2data = ax.transData.inverted().transform
        xyA = disp2ax( data2disp( xy ) )
        frac = 0.5
        scatC = (-frac*(xyA[0]-0.5)+xyA[0], -frac*(xyA[1]-0.5)+xyA[1])
        scatC = disp2data( ax2disp( scatC ) )
        ab = mp.offsetbox.AnnotationBbox( offsetbox2, xy,
                xybox=(scatC[0], scatC[1]), 
                boxcoords="data",
                box_alignment=(.5,.5),
                arrowprops=dict(arrowstyle="-|>", 
                facecolor='none'),
                frameon=False )

        ax.add_artist(ab)
############################################################################
