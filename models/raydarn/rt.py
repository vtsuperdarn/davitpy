# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.raydarn.rt
*********************
This module runs the raytracing code

**Class**:
    * :class:`models.rt.RtRun`: run the code
    * :class:`models.rt.Scatter`: store and process modeled backscatter
    * :class:`models.rt.Edens`: store and process electron density profiles
    * :class:`models.rt.Rays`: store and process individual rays

.. note:: The ray tracing requires mpi to run. You can adjust the number of processors, but be wise about it and do not assign more than you have

"""

#########################################################################
# Main object
#########################################################################
class RtRun(object):
    """This class runs the raytracing code and processes the output

    **Args**: 
        * [**sTime**] (datetime.datetime): start time UT
        * [**eTime**] (datetime.datetime): end time UT (if not provided run for a single time sTime)
        * [**rCode**] (str): radar 3-letter code
        * [**radarObj**] (:class:`pydarn.radar.radar`): radar object (overrides rCode)
        * [**dTime**] (float): time step in Hours
        * [**freq**] (float): operating frequency [MHz]
        * [**beam**] (int): beam number (if None run all beams)
        * [**nhops**] (int): number of hops
        * [**elev**] (tuple): (start elevation, end elevation, step elevation) [degrees]
        * [**azim**] (tuple): (start azimuth, end azimuth, step azimuth) [degrees East] (overrides beam specification)
        * [**hmf2**] (float): F2 peak alitude [km] (default: use IRI)
        * [**nmf2**] (float): F2 peak electron density [log10(m^-3)] (default: use IRI)
        * [**debug**] (bool): print some diagnostics of the fortran run and output processing
        * [**fext**] (str): output file id, max 10 character long (mostly used for multiple users environments, like a website)
        * [**loadFrom**] (str): file name where a pickled instance of RtRun was saved (supersedes all other args)
        * [**nprocs**] (int): number of processes to use with MPI
    **Returns**:
        * **RtRun** (:class:`RtRun`)
    **Example**:
        ::

            # Run a 2-hour ray trace from Blackstone on a random day
            sTime = dt.datetime(2012, 11, 18, 5)
            eTime = sTime + dt.timedelta(hours=2)
            radar = 'bks'
            # Save the results to your /tmp directory
            rto = raydarn.RtRun(sTime, eTime, rCode=radar, outDir='/tmp')

    """
    def __init__(self, sTime=None, eTime=None, 
        rCode=None, radarObj=None, 
        dTime=.5, 
        freq=11, beam=None, nhops=1, 
        elev=(5, 60, .1), azim=None, 
        hmf2=None, nmf2=None, 
        outDir=None, 
        debug=False, 
        fext=None, 
        loadFrom=None, 
        nprocs=4):
        import datetime as dt
        from os import path
        from pydarn import radar

        # Load pickled instance...
        if loadFrom:
            self.load(loadFrom)
        # ...or get to work!
        else:
            # Load radar info
            if radarObj:
                self.radar = radarObj
            elif rCode:
                self.radar = radar.radar(code=rCode)

            # Set azimuth
            self.site = self.radar.getSiteByDate(sTime)
            if beam and not azim: 
                az = self.site.beamToAzim(beam)
                azim = (az, az, 1)
            else:
                az1 = self.site.beamToAzim(0)
                az2 = self.site.beamToAzim(self.site.maxbeam-1)
                azim = (az1, az2, self.site.bmsep)
            self.azim = azim
            self.beam = beam

            # Set elevation
            self.elev = elev

            # Set time interval
            if not sTime: 
                print 'No start time. Using now.'
                sTime = dt.datetime.utcnow()
            if not eTime:
                eTime = sTime + dt.timedelta(minutes=1)
            if eTime > sTime + dt.timedelta(days=1):
                print 'The time interval requested if too large. Reducing to 1 day.'
                eTime = sTime + dt.timedelta(days=1)
            self.time = [sTime, eTime]
            self.dTime = dTime

            # Set frequency
            self.freq = freq

            # Set number of hops
            self.nhops = nhops

            # Set ionosphere
            self.hmf2 = hmf2 if hmf2 else 0
            self.nmf2 = nmf2 if nmf2 else 0

            # Set output directory and file extension
            if not outDir:
                outDir = path.abspath( path.curdir )
            self.outDir = path.join( outDir, '' )
            self.fExt = '0' if not fext else fext

            # Write input file
            inputFile = self._genInput()
            
            # Run the ray tracing
            success = self._execute(nprocs, inputFile, debug=debug)


    def _genInput(self):
        """Generate input file
        """
        from os import path

        fname = path.join(self.outDir, 'rtrun.{}.inp'.format(self.fExt))
        with open(fname, 'w') as f:
            f.write( "{:8.2f}  Transmitter latitude (degrees N)\n".format( self.site.geolat ) )
            f.write( "{:8.2f}  Transmitter Longitude (degrees E\n".format( self.site.geolon ) )
            f.write( "{:8.2f}  Azimuth (degrees E) (begin)\n".format( self.azim[0] ) )
            f.write( "{:8.2f}  Azimuth (degrees E) (end)\n".format( self.azim[1] ) )
            f.write( "{:8.2f}  Azimuth (degrees E) (step)\n".format( self.azim[2] ) )
            f.write( "{:8.2f}  Elevation angle (begin)\n".format( self.elev[0] ) )
            f.write( "{:8.2f}  Elevation angle (end)\n".format( self.elev[1] ) )
            f.write( "{:8.2f}  Elevation angle (step)\n".format( self.elev[2] ) )
            f.write( "{:8.2f}  Frequency (Mhz)\n".format( self.freq ) )
            f.write( "{:8d}  nubmer of hops (minimum 1)\n".format( self.nhops) )
            f.write( "{:8d}  Year (yyyy)\n".format( self.time[0].year ) )
            f.write( "{:8d}  Month and day (mmdd)\n".format( self.time[0].month*100 + self.time[0].day ) )
            tt = self.time[0].hour + self.time[0].minute/60.
            tt += 25.
            f.write( "{:8.2f}  hour (add 25 for UT) (begin)\n".format( tt ) )
            tt = self.time[1].hour + self.time[1].minute/60.
            tt += (self.time[1].day - self.time[0].day) * 24.
            tt += 25.
            f.write( "{:8.2f}  hour (add 25 for UT) (end)\n".format( tt ) )
            f.write( "{:8.2f}  hour (step)\n".format( self.dTime ) )
            f.write( "{:8.2f}  hmf2 (km, if 0 then ignored)\n".format( self.hmf2 ) )
            f.write( "{:8.2f}  nmf2 (log10, if 0 then ignored)\n".format( self.nmf2 ) )

        return fname
        

    def _execute(self, nprocs, inputFileName, debug=False):
        """Execute raytracing command
        """
        import subprocess as subp
        from os import path

        command = ['mpiexec', '-n', '{}'.format(nprocs), 
            path.join(path.abspath( __file__.split('rt.py')[0] ), 'rtFort'), 
            inputFileName, 
            self.outDir, 
            self.fExt]
        
        process = subp.Popen(command, shell=False, stdout=subp.PIPE, stderr=subp.STDOUT)
        output = process.communicate()[0]
        exitCode = process.returncode

        if debug or (exitCode != 0):
            print 'In:: {}'.format( command )
            print 'Exit code:: {}'.format( exitCode )
            print 'Returned:: \n', output
        
        if (exitCode != 0):
            raise Exception('Fortran execution error.')
        else:
            subp.call(['rm',inputFileName])
            return True


    def readRays(self, saveToAscii=None, debug=False):
        """Read rays.dat fortran output into dictionnary

        **Args**:
            * [**saveToAscii**] (str): output content to text file
            * [**debug**] (bool): print some i/o diagnostics
        **Returns**:
            * Add a new member to :class:`rt.RtRun`: **rays**, of type :class:`rt.rays`
        """
        import subprocess as subp
        from os import path

        # File name and path
        fName = path.join(self.outDir, 'rays.{}.dat'.format(self.fExt))
        if hasattr(self, 'rays') and not path.exists(fName):
            print 'The file is gone, and it seems you may already have read it into memory...?'
            return

        # Initialize rays output
        self.rays = Rays(fName, 
            site=self.site, radar=self.radar,
            saveToAscii=saveToAscii, debug=debug)
        # Remove Input file
        subp.call(['rm',fName])


    def readEdens(self, debug=False):
        """Read edens.dat fortran output

        **Args**:
            * [**site**] (pydarn.radar.radStrict.site): site object of current radar
            * [**debug**] (bool): print some i/o diagnostics
        **Returns**:
            * Add a new member to :class:`rt.RtRun`: **rays**, of type :class:`rt.rays`
        """
        import subprocess as subp
        from os import path

        # File name and path
        fName = path.join(self.outDir, 'edens.{}.dat'.format(self.fExt))
        if hasattr(self, 'ionos') and not path.exists(fName):
            print 'The file is gone, and it seems you may already have read it into memory...?'
            return

        # Initialize rays output
        self.ionos = Edens(fName, 
            site=self.site, radar=self.radar,
            debug=debug)
        # Remove Input file
        subp.call(['rm',fName])


    def readScatter(self, debug=False):
        """Read edens.dat fortran output

        **Args**:
            * [**site**] (pydarn.radar.radStrict.site): site object of current radar
            * [**debug**] (bool): print some i/o diagnostics
        **Returns**:
            * Add a new member to :class:`rt.RtRun`: **rays**, of type :class:`rt.rays`
        """
        import subprocess as subp
        from os import path

        # File name and path
        isName = path.join(self.outDir, 'iscat.{}.dat'.format(self.fExt))
        gsName = path.join(self.outDir, 'gscat.{}.dat'.format(self.fExt))
        if hasattr(self, 'scatter') \
            and (not path.exists(isName) \
            or not path.exists(gsName)):
            print 'The files are gone, and it seems you may already have read them into memory...?'
            return

        # Initialize rays output
        self.scatter = Scatter(gsName, isName, 
            site=self.site, radar=self.radar,
            debug=debug)
        # Remove Input file
        # subp.call(['rm',isName])
        # subp.call(['rm',gsName])


    def save(self, filename):
        """Save :class:`rt.RtRun` to a file
        """
        import cPickle as pickle

        with open( filename, "wb" ) as f:
            pickle.dump(self, f)


    def load(self, filename):
        """Load :class:`rt.RtRun` from a file
        """
        import cPickle as pickle

        with open( filename, "rb" ) as f:
            obj = pickle.load(f)
            for k, v in obj.__dict__.items():
                self.__dict__[k] = v


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        self.clean()


    def clean(self):
        '''Clean-up files
        '''
        import subprocess as subp
        from os import path

        files = ['rays', 'edens', 'ranges', 'ionos']
        for f in files:
            fName = path.join(self.outDir, '{}.{}.dat'.format(f, self.fExt))
            subp.call(['rm', fName])


#########################################################################
# Electron densities
#########################################################################
class Edens(object):
    """Store and process electron density profiles after ray tracing

    **Args**:
        * **readFrom** (str): edens.dat file to read the rays from
        * [**site**] (:class:`pydarn.radar.site): radar site object
        * [**radar**] (:class:`pydarn.radar.radar): radar object
        * [**debug**] (bool): verbose mode
    """
    def __init__(self, readFrom, 
        site=None, radar=None, 
        debug=False):
        self.readFrom = readFrom
        self.edens = {}

        self.name = ''
        if radar:
            self.name = radar.code[0].upper()

        # Read rays
        self.readEdens(site=site, debug=debug)


    def readEdens(self, site=None, debug=False):
        """Read edens.dat fortran output

        **Args**:
            * [**site**] (pydarn.radar.radStrict.site): site object of current radar
            * [**debug**] (bool): print some i/o diagnostics
        **Returns**:
            * Populate member edens :class:`rt.Edens`
        """
        from struct import unpack
        import datetime as dt
        from numpy import array

        # Read binary file
        with open(self.readFrom, 'rb') as f:
            if debug:
                print self.readFrom+' header: '
            self.header = _readHeader(f, debug=debug)
            self.edens = {}
            while True:
                bytes = f.read(2*4)
                # Check for eof
                if not bytes: break
                # read hour and azimuth
                hour, azim = unpack('2f', bytes)
                # format time index
                hour = hour - 25.
                mm = self.header['mmdd']/100
                dd = self.header['mmdd'] - mm*100
                rtime = dt.datetime(self.header['year'], mm, dd) + dt.timedelta(hours=hour)
                # format azimuth index (beam)
                raz = site.azimToBeam(azim) if site else round(raz, 2)
                # Initialize dicts
                if rtime not in self.edens.keys(): self.edens[rtime] = {}
                self.edens[rtime][raz] = {}
                # Read edens dict
                # self.edens[rtime][raz]['pos'] = array( unpack('{}f'.format(250*2), 
                #     f.read(250*2*4)) )
                self.edens[rtime][raz]['th'] = array( unpack('{}f'.format(250), 
                    f.read(250*4)) )
                self.edens[rtime][raz]['nel'] = array( unpack('{}f'.format(250*250), 
                    f.read(250*250*4)) ).reshape((250,250), order='F')
                self.edens[rtime][raz]['dip'] = array( unpack('{}f'.format(250*2), 
                    f.read(250*2*4)) ).reshape((250,2), order='F')


    def plot(self, time, beam=None, maxground=2000, maxalt=500,
        nel_cmap='jet', nel_lim=[10, 12], title=False, 
        fig=None, rect=111, ax=None, aax=None):
        """Plot electron density profile
        
        **Args**: 
            * **time** (datetime.datetime): time of profile
            * [**beam**]: beam number
            * [**maxground**]: maximum ground range [km]
            * [**maxalt**]: highest altitude limit [km]
            * [**nel_cmap**]: color map name for electron density index coloring
            * [**nel_lim**]: electron density index plotting limits
            * [**rect**]: subplot spcification
            * [**fig**]: A pylab.figure object (default to gcf)
            * [**ax**]: Existing main axes
            * [**aax**]: Existing auxialary axes
            * [**title**]: Show default title
        **Returns**:
            * **ax**: matplotlib.axes object containing formatting
            * **aax**: matplotlib.axes object containing data
            * **cbax**: matplotlib.axes object containing colorbar
        **Example**:
            ::

                # Show electron density profile
                import datetime as dt
                from models import raydarn
                sTime = dt.datetime(2012, 11, 18, 5)
                rto = raydarn.RtRun(sTime, rCode='bks', beam=12)
                rto.readEdens() # read electron density into memory
                ax, aax, cbax = rto.ionos.plot(sTime, title=True)
                ax.grid()
                
        written by Sebastien, 2013-04
        """
        from utils import plotUtils
        from matplotlib.collections import LineCollection
        import matplotlib.pyplot as plt
        import numpy as np

        # Set up axes
        if not ax and not aax:
            ax, aax = plotUtils.curvedEarthAxes(fig=fig, rect=rect, 
                maxground=maxground, maxalt=maxalt)
        else:
            ax = ax
            aax = aax
            if hasattr(ax, 'time'):
                time = ax.time
            if hasattr(ax, 'beam'):
                beam = ax.beam

        # make sure that the required time and beam are present
        assert (time in self.edens.keys()), 'Unkown time %s' % time
        if beam:
            assert (beam in self.edens[time].keys()), 'Unkown beam %s' % beam
        else:
            beam = self.edens[time].keys()[0]

        X, Y = np.meshgrid(self.edens[time][beam]['th'], ax.Re + np.linspace(60,560,250))
        im = aax.pcolormesh(X, Y, np.log10( self.edens[time][beam]['nel'] ), 
            vmin=nel_lim[0], vmax=nel_lim[1], cmap=nel_cmap)

        # Plot title with date ut time and local time
        if title:
            stitle = _getTitle(time, beam, self.header, None)
            ax.set_title( stitle )

        # Add a colorbar
        cbax = plotUtils.addColorbar(im, ax)
        _ = cbax.set_ylabel(r"N$_{el}$ [$\log_{10}(m^{-3})$]")

        ax.beam = beam
        return ax, aax, cbax


#########################################################################
# Scatter
#########################################################################
class Scatter(object):
    """Stores and process ground and ionospheric scatter

    **Args**:
        * **readISFrom** (str): iscat.dat file to read the ionospheric scatter from
        * **readGSFrom** (str): gscat.dat file to read the ground scatter from
        * [**site**] (:class:`pydarn.radar.site): radar site object
        * [**debug**] (bool): verbose mode
    """
    def __init__(self, readGSFrom=None, readISFrom=None, 
        site=None, radar=None, 
        debug=False):
        self.readISFrom = readISFrom
        self.readGSFrom = readGSFrom

        # Read ground scatter
        if self.readGSFrom:
            self.gsc = {}
            self.readGS(site=site, debug=debug)

        # Read ionospheric scatter
        if self.readISFrom:
            self.isc = {}
            self.readIS(site=site, debug=debug)


    def readGS(self, site=None, debug=False):
        """Read gscat.dat fortran output

        **Args**:
            * [**site**] (pydarn.radar.radStrict.site): site object of current radar
            * [**debug**] (bool): print some i/o diagnostics
        **Returns**:
            * Populate member isc :class:`rt.Scatter`
        """
        from struct import unpack
        import datetime as dt
        import numpy as np

        with open(self.readGSFrom, 'rb') as f:
            # read header
            if debug:
                print self.readGSFrom+' header: '
            self.header = _readHeader(f, debug=debug)
            # Then read ray data, one ray at a time
            while True:
                bytes = f.read(3*4)
                # Check for eof
                if not bytes: break
                # read number of ray steps, time, azimuth and elevation
                rhr, raz, rel = unpack('3f', bytes)
                # Read reminder of the record
                rr, tht, gran, lat, lon  = unpack('5f', f.read(5*4))
                # Convert azimuth to beam number
                raz = site.azimToBeam(raz) if site else np.round(raz, 2)
                # convert time to python datetime
                rhr = rhr - 25.
                mm = self.header['mmdd']/100
                dd = self.header['mmdd'] - mm*100
                rtime = dt.datetime(self.header['year'], mm, dd) + dt.timedelta(hours=rhr)
                # Create new entries in rays dict
                if rtime not in self.gsc.keys(): self.gsc[rtime] = {}
                if raz not in self.gsc[rtime].keys(): self.gsc[rtime][raz] = {}
                if rel not in self.gsc[rtime][raz].keys(): 
                    self.gsc[rtime][raz][rel] = {
                        'r': np.empty(0),
                        'th': np.empty(0),
                        'gran': np.empty(0),
                        'lat': np.empty(0),
                        'lon': np.empty(0) }
                self.gsc[rtime][raz][rel]['r'] = np.append( self.gsc[rtime][raz][rel]['r'], rr )
                self.gsc[rtime][raz][rel]['th'] = np.append( self.gsc[rtime][raz][rel]['th'], tht )
                self.gsc[rtime][raz][rel]['gran'] = np.append( self.gsc[rtime][raz][rel]['gran'], gran )
                self.gsc[rtime][raz][rel]['lat'] = np.append( self.gsc[rtime][raz][rel]['lat'], lat )
                self.gsc[rtime][raz][rel]['lon'] = np.append( self.gsc[rtime][raz][rel]['lon'], lon )


    def readIS(self, site=None, debug=False):
        """Read iscat.dat fortran output

        **Args**:
            * [**site**] (pydarn.radar.radStrict.site): site object of current radar
            * [**debug**] (bool): print some i/o diagnostics
        **Returns**:
            * Populate member isc :class:`rt.Scatter`
        """
        from struct import unpack
        import datetime as dt
        from numpy import round, array

        with open(self.readISFrom, 'rb') as f:
            # read header
            if debug:
                print self.readISFrom+' header: '
            self.header = _readHeader(f, debug=debug)
            # Then read ray data, one ray at a time
            while True:
                bytes = f.read(4*4)
                # Check for eof
                if not bytes: break
                # read number of ray steps, time, azimuth and elevation
                nstp, rhr, raz, rel = unpack('4f', bytes)
                nstp = int(nstp)
                # Convert azimuth to beam number
                raz = site.azimToBeam(raz) if site else round(raz, 2)
                # convert time to python datetime
                rhr = rhr - 25.
                mm = self.header['mmdd']/100
                dd = self.header['mmdd'] - mm*100
                rtime = dt.datetime(self.header['year'], mm, dd) + dt.timedelta(hours=rhr)
                # Create new entries in rays dict
                if rtime not in self.isc.keys(): self.isc[rtime] = {}
                if raz not in self.isc[rtime].keys(): self.isc[rtime][raz] = {}
                self.isc[rtime][raz][rel] = {}
                # Read to paths dict
                self.isc[rtime][raz][rel]['nstp'] = nstp
                self.isc[rtime][raz][rel]['r'] = array( unpack('{}f'.format(nstp), 
                    f.read(nstp*4)) )
                self.isc[rtime][raz][rel]['th'] = array( unpack('{}f'.format(nstp), 
                    f.read(nstp*4)) )
                self.isc[rtime][raz][rel]['gran'] = array( unpack('{}f'.format(nstp), 
                    f.read(nstp*4)) )
                self.isc[rtime][raz][rel]['rel'] = array( unpack('{}f'.format(nstp), 
                    f.read(nstp*4)) )
                self.isc[rtime][raz][rel]['w'] = array( unpack('{}f'.format(nstp), 
                    f.read(nstp*4)) )
                self.isc[rtime][raz][rel]['nr'] = array( unpack('{}f'.format(nstp), 
                    f.read(nstp*4)) )
                self.isc[rtime][raz][rel]['lat'] = array( unpack('{}f'.format(nstp), 
                    f.read(nstp*4)) )
                self.isc[rtime][raz][rel]['lon'] = array( unpack('{}f'.format(nstp), 
                    f.read(nstp*4)) )
                self.isc[rtime][raz][rel]['h'] = array( unpack('{}f'.format(nstp), 
                    f.read(nstp*4)) )


    def plot(self, time, beam=None, maxground=2000, maxalt=500,
        iscat=True, gscat=True, title=False, weighted=False, cmap='hot_r', 
        fig=None, rect=111, ax=None, aax=None, zorder=4):
        """Plot scatter on ground/altitude profile
        
        **Args**: 
            * **time** (datetime.datetime): time of profile
            * [**beam**]: beam number
            * [**iscat**] (bool): show ionospheric scatter
            * [**gscat**] (bool): show ground scatter
            * [**maxground**]: maximum ground range [km]
            * [**maxalt**]: highest altitude limit [km]
            * [**rect**]: subplot spcification
            * [**fig**]: A pylab.figure object (default to gcf)
            * [**ax**]: Existing main axes
            * [**aax**]: Existing auxialary axes
            * [**title**]: Show default title
            * [**weighted**] (bool): plot ionospheric scatter relative strength (based on background density and range)
            * [**cmap**]: colormap used for weighted ionospheric scatter
        **Returns**:
            * **ax**: matplotlib.axes object containing formatting
            * **aax**: matplotlib.axes object containing data
            * **cbax**: matplotlib.axes object containing colorbar
        **Example**:
            ::

                # Show ionospheric scatter
                import datetime as dt
                from models import raydarn
                sTime = dt.datetime(2012, 11, 18, 5)
                rto = raydarn.RtRun(sTime, rCode='bks', beam=12)
                rto.readRays() # read rays into memory
                ax, aax, cbax = rto.rays.plot(sTime, title=True)
                rto.readScatter() # read scatter into memory
                rto.scatter.plot(sTime, ax=ax, aax=aax)
                ax.grid()
                
        written by Sebastien, 2013-04
        """
        from utils import plotUtils
        from matplotlib.collections import LineCollection
        import matplotlib.pyplot as plt
        import numpy as np

        # Set up axes
        if not ax and not aax:
            ax, aax = plotUtils.curvedEarthAxes(fig=fig, rect=rect, 
                maxground=maxground, maxalt=maxalt)
        else:
            ax = ax
            aax = aax
            if hasattr(ax, 'beam'):
                beam = ax.beam

        # make sure that the required time and beam are present
        assert (time in self.isc.keys()), 'Unkown time %s' % time
        if beam:
            assert (beam in self.isc[time].keys()), 'Unkown beam %s' % beam
        else:
            beam = self.isc[time].keys()[0]

        if gscat:
            for ir, (el, rays) in enumerate( sorted(self.gsc[time][beam].items()) ):
                if len(rays['r']) == 0: continue
                _ = aax.scatter(rays['th'], ax.Re*np.ones(rays['th'].shape), 
                    color='0', zorder=zorder)

        if iscat:
            if weighted:
                wmin = np.min( [ r['w'].min() for r in self.isc[time][beam].values() if r['nstp'] > 0] )
                wmax = np.max( [ r['w'].max() for r in self.isc[time][beam].values() if r['nstp'] > 0] )

            for ir, (el, rays) in enumerate( sorted(self.isc[time][beam].items()) ):
                if rays['nstp'] == 0: continue
                t = rays['th']
                r = rays['r']*1e-3
                spts = np.array([t, r]).T.reshape(-1, 1, 2)
                h = rays['h']*1e-3
                rel = np.radians( rays['rel'] )
                r = np.sqrt( r**2 + h**2 + 2*r*h*np.sin( rel ) )
                t = t + np.arcsin( h/r * np.cos( rel ) )
                epts = np.array([t, r]).T.reshape(-1, 1, 2)
                segments = np.concatenate([spts, epts], axis=1)
                lcol = LineCollection( segments, zorder=zorder )
                if weighted:
                    _ = lcol.set_cmap( cmap )
                    _ = lcol.set_norm( plt.Normalize(0, 1) )
                    _ = lcol.set_array( ( rays['w'] - wmin ) / wmax )
                else:
                    _ = lcol.set_color('0')
                _ = aax.add_collection( lcol )

            # Plot title with date ut time and local time
            if title:
                stitle = _getTitle(time, beam, self.header, None)
                ax.set_title( stitle )

            # If weighted, plot ionospheric scatter with colormap
            if weighted:
                # Add a colorbar
                cbax = plotUtils.addColorbar(lcol, ax)
                _ = cbax.set_ylabel("Ionospheric Scatter")
            else: cbax = None

        ax.beam = beam
        return ax, aax, cbax
        

#########################################################################
# Rays
#########################################################################
class Rays(object):
    """Store and process individual rays after ray tracing

    **Args**:
        * **readFrom** (str): rays.dat file to read the rays from
        * [**site**] (:class:`pydarn.radar.site): radar site object
        * [**radar**] (:class:`pydarn.radar.radar): radar object
        * [**saveToAscii**] (str): file name where to output ray positions
        * [**debug**] (bool): verbose mode
    """
    def __init__(self, readFrom, 
        site=None, radar=None, 
        saveToAscii=None, debug=False):
        self.readFrom = readFrom
        self.paths = {}

        self.name = ''
        if radar:
            self.name = radar.code[0].upper()

        # Read rays
        self.readRays(site=site, debug=debug)

        # If required, save to ascii
        if saveToAscii:
            self.writeToAscii(saveToAscii)


    def readRays(self, site=None, debug=False):
        """Read rays.dat fortran output

        **Args**:
            * [**site**] (pydarn.radar.radStrict.site): site object of current radar
            * [**debug**] (bool): print some i/o diagnostics
        **Returns**:
            * Populate member paths :class:`rt.Rays`
        """
        from struct import unpack
        import datetime as dt
        from numpy import round, array

        # Read binary file
        with open(self.readFrom, 'rb') as f:
            # read header
            if debug:
                print self.readFrom+' header: '
            self.header = _readHeader(f, debug=debug)
            # Then read ray data, one ray at a time
            while True:
                bytes = f.read(4*4)
                # Check for eof
                if not bytes: break
                # read number of ray steps, time, azimuth and elevation
                nrstep, rhr, raz, rel = unpack('4f', bytes)
                nrstep = int(nrstep)
                # Convert azimuth to beam number
                raz = site.azimToBeam(raz) if site else round(raz, 2)
                # convert time to python datetime
                rhr = rhr - 25.
                mm = self.header['mmdd']/100
                dd = self.header['mmdd'] - mm*100
                rtime = dt.datetime(self.header['year'], mm, dd) + dt.timedelta(hours=rhr)
                # Create new entries in rays dict
                if rtime not in self.paths.keys(): self.paths[rtime] = {}
                if raz not in self.paths[rtime].keys(): self.paths[rtime][raz] = {}
                self.paths[rtime][raz][rel] = {}
                # Read to paths dict
                self.paths[rtime][raz][rel]['nrstep'] = nrstep
                self.paths[rtime][raz][rel]['r'] = array( unpack('{}f'.format(nrstep), 
                    f.read(nrstep*4)) )
                self.paths[rtime][raz][rel]['th'] = array( unpack('{}f'.format(nrstep), 
                    f.read(nrstep*4)) )
                self.paths[rtime][raz][rel]['gran'] = array( unpack('{}f'.format(nrstep), 
                    f.read(nrstep*4)) )
                # self.paths[rtime][raz][rel]['pran'] = array( unpack('{}f'.format(nrstep), 
                #     f.read(nrstep*4)) )
                self.paths[rtime][raz][rel]['nr'] = array( unpack('{}f'.format(nrstep), 
                    f.read(nrstep*4)) )


    def writeToAscii(self, fname):
        """Save rays to ASCII file (limited use)
        """

        with open(fname, 'w') as f:
            f.write('## HEADER ##\n')
            [f.write('{:>10s}'.format(k)) for k in self.header.keys()]
            f.write('\n')
            for v in self.header.values():
                if isinstance(v, float): strFmt = '{:10.2f}'
                elif isinstance(v, int): strFmt = '{:10d}'
                elif isinstance(v, str): strFmt = '{:10s}'
                f.write(strFmt.format(v))
            f.write('\n')
            f.write('##  RAYS  ##\n')
            for kt in sorted(self.paths.keys()):
                f.write('Time: {:%Y %m %d %H %M}\n'.format(kt))
                for kb in sorted(self.paths[kt].keys()):
                    f.write('--Beam/Azimuth: {}\n'.format(kb))
                    for ke in sorted(self.paths[kt][kb].keys()):
                        f.write('----Elevation: {:4.2f}\n'.format(ke))
                        f.write('------r\n')
                        [f.write('{:10.3f}\t'.format(r*1e-3)) for r in self.paths[kt][kb][ke]['r']]
                        f.write('\n')
                        f.write('------theta\n')
                        [f.write('{:10.5f}\t'.format(th)) for th in self.paths[kt][kb][ke]['th']]
                        f.write('\n')


    def plot(self, time, beam=None, 
        maxground=2000, maxalt=500, step=1,
        showrefract=False, nr_cmap='jet_r', nr_lim=[0.8, 1.], 
        raycolor='0.3', title=False, 
        fig=None, rect=111, ax=None, aax=None):
        """Plot ray paths
        
        **Args**: 
            * **time** (datetime.datetime): time of rays
            * [**beam**]: beam number
            * [**maxground**]: maximum ground range [km]
            * [**maxalt**]: highest altitude limit [km]
            * [**step**]: step between each plotted ray (in number of ray steps)
            * [**showrefract**]: show refractive index along ray paths (supersedes raycolor)
            * [**nr_cmap**]: color map name for refractive index coloring
            * [**nr_lim**]: refractive index plotting limits
            * [**raycolor**]: color of ray paths
            * [**rect**]: subplot spcification
            * [**fig**]: A pylab.figure object (default to gcf)
            * [**title**]: Show default title
            * [**ax**]: Existing main axes
            * [**aax**]: Existing auxialary axes
        **Returns**:
            * **ax**: matplotlib.axes object containing formatting
            * **aax**: matplotlib.axes object containing data
            * **cbax**: matplotlib.axes object containing colorbar
        **Example**:
            ::

                # Show ray paths with colored refractive index along path
                import datetime as dt
                from models import raydarn
                sTime = dt.datetime(2012, 11, 18, 5)
                rto = raydarn.RtRun(sTime, rCode='bks', beam=12, title=True)
                rto.readRays() # read rays into memory
                ax, aax, cbax = rto.rays.plot(sTime, step=10, showrefract=True, nr_lim=[.85,1])
                ax.grid()
                
        written by Sebastien, 2013-04
        """
        from utils import plotUtils
        from matplotlib.collections import LineCollection
        import matplotlib.pyplot as plt
        import numpy as np
        from types import MethodType

        # Set up axes
        if not ax and not aax:
            ax, aax = plotUtils.curvedEarthAxes(fig=fig, rect=rect, 
                maxground=maxground, maxalt=maxalt)
        else:
            ax = ax
            aax = aax
            if hasattr(ax, 'time'):
                time = ax.time
            if hasattr(ax, 'beam'):
                beam = ax.beam

        # make sure that the required time and beam are present
        assert (time in self.paths.keys()), 'Unkown time %s' % time
        if beam:
            assert (beam in self.paths[time].keys()), 'Unkown beam %s' % beam
        else:
            beam = self.paths[time].keys()[0]
        
        for ir, (el, rays) in enumerate( sorted(self.paths[time][beam].items()) ):
            if not ir % step:
                if not showrefract:
                    aax.plot(rays['th'], rays['r']*1e-3, c=raycolor, zorder=2)
                else:
                    points = np.array([rays['th'], rays['r']*1e-3]).T.reshape(-1, 1, 2)
                    segments = np.concatenate([points[:-1], points[1:]], axis=1)
                    lcol = LineCollection( segments )
                    _ = lcol.set_cmap( nr_cmap )
                    _ = lcol.set_norm( plt.Normalize(*nr_lim) )
                    _ = lcol.set_array( rays['nr'] )
                    _ = aax.add_collection( lcol )

        # Plot title with date ut time and local time
        if title:
            stitle = _getTitle(time, beam, self.header, self.name)
            ax.set_title( stitle )

        # Add a colorbar when plotting refractive index
        if showrefract:
            cbax = plotUtils.addColorbar(lcol, ax)
            _ = cbax.set_ylabel("refractive index")
        else: cbax = None

        # Declare a new method to show range markers
        # This method is only available after rays have been plotted
        # This ensures that the markers match the plotted rays
        def showRange(self, markers=None, 
            color='.8', s=2, zorder=3, 
            **kwargs):
            """Plot ray paths
            
            **Args**: 
                * [**markers**]: range markers. Defaults to every 250 km
                * All other keywords are borrowed from :func:`matplotlib.pyplot.scatter`
            **Returns**:
                * **coll**: a collection of range markers
            **Example**:
                ::

                    # Add range markers to an existing ray plot
                    ax, aax, cbax = rto.rays.plot(sTime, step=10)
                    rto.rays.showRange()
                    
            written by Sebastien, 2013-04
            """

            if not markers:
                markers = np.arange(0, 5000, 250)
            
            x, y = [], []
            for el, rays in self.paths[time][beam].items():
                for rm in markers:
                    inds = (rays['gran']*1e-3 >= rm)
                    if inds.any():
                        x.append( rays['th'][inds][0] )
                        y.append( rays['r'][inds][0]*1e-3 )
            coll = aax.scatter(x, y, 
                color=color, s=s, zorder=zorder, **kwargs)

            return coll
        # End of new method

        # Assign new method
        self.showRange = MethodType(showRange, self)

        ax.beam = beam
        return ax, aax, cbax



#########################################################################
# Misc.
#########################################################################
def _readHeader(fObj, debug=False):
    """Read the header part of ray-tracing *.dat files

    **Args**:
        * **fObj**: file object
        * [**debug**] (bool): print some i/o diagnostics
    **Returns**:
        * **header**: a dictionary of header values
    """
    from struct import unpack
    import datetime as dt
    from collections import OrderedDict
    import os

    # Declare header parameters
    params = ('nhour', 'nazim', 'nelev', 
        'tlat', 'tlon', 
        'saz', 'eaz', 'daz', 
        'sel', 'eel', 'del', 
        'freq', 'nhop', 'year', 'mmdd', 
        'shour', 'ehour', 'dhour', 
        'hmf2', 'nmf2')
    # Read header
    header = OrderedDict( zip( params, unpack('3i9f3i5f', fObj.read(3*4 + 9*4 + 3*4 + 5*4)) ) )
    header['fext'] = unpack('10s', fObj.read(10))[0].strip()
    header['outdir'] = unpack('100s', fObj.read(100))[0].strip()
    # Only print header if in debug mode
    if debug:
        for k, v in header.items(): print '{:10s} :: {}'.format(k,v)
    header.pop('fext'); header.pop('outdir')

    return header


def _getTitle(time, beam, header, name):
    """Create a title for ground/altitude plots

    **Args**:
        * **time** (datetime.datetime): time shown in plot
        * **beam**: beam shown in plot
        * **header** (dict): header of fortran uotput file
        * **name** (str): radar name
    **Returns**:
        * **title** (str): a title string
    """
    from numpy import floor, round

    utdec = time.hour + time.minute/60.
    tlon = (header['tlon'] % 360.)
    ctlon = tlon if tlon <=180. else tlon - 360.
    ltdec = ( utdec + ( ctlon/360.*24.) ) % 24.
    lthr = floor(ltdec)
    ltmn = round( (ltdec - lthr)*60 )
    title = '{:%Y-%b-%d at %H:%M} UT (~{:02.0f}:{:02.0f} LT)'.format(
        time, lthr, ltmn)
    title += '\n(IRI-2011) {} beam {}; freq {:.1f}MHz'.format(name, beam, header['freq'])

    return title