# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.raydarn.rt
*********************
This module runs the raytracing code

**Class**:
    * :class:`rt.RtRun`: run the code
    * :class:`rt.Edens`: store and process electron density profiles
    * :class:`rt.Rays`: store and process individual rays

**Functions**:
    * :func:`rt.readHeader`: read the header of each output file from the ray tracing fortran code

.. note:: The ray tracing requires mpi to run. You can adjust the number of processors, but be wise about it and do not assign more than you have

"""


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
            f.write( "{:18.2f}  Transmitter latitude (degrees N)\n".format( self.site.geolat ) )
            f.write( "{:18.2f}  Transmitter Longitude (degrees E\n".format( self.site.geolon ) )
            f.write( "{:18.2f}  Azimuth (degrees E) (begin)\n".format( self.azim[0] ) )
            f.write( "{:18.2f}  Azimuth (degrees E) (end)\n".format( self.azim[1] ) )
            f.write( "{:18.2f}  Azimuth (degrees E) (step)\n".format( self.azim[2] ) )
            f.write( "{:18.2f}  Elevation angle (begin)\n".format( self.elev[0] ) )
            f.write( "{:18.2f}  Elevation angle (end)\n".format( self.elev[1] ) )
            f.write( "{:18.2f}  Elevation angle (step)\n".format( self.elev[2] ) )
            f.write( "{:18.2f}  Frequency (Mhz)\n".format( self.freq ) )
            f.write( "{:18d}  nubmer of hops (minimum 1)\n".format( self.nhops) )
            f.write( "{:18d}  Year (yyyy)\n".format( self.time[0].year ) )
            f.write( "{:18d}  Month and day (mmdd)\n".format( self.time[0].month*100 + self.time[0].day ) )
            tt = self.time[0].hour + self.time[0].minute/60.
            tt += 25.
            f.write( "{:18.2f}  hour (add 25 for UT) (begin)\n".format( tt ) )
            tt = self.time[1].hour + self.time[1].minute/60.
            tt += (self.time[1].day - self.time[0].day) * 24.
            tt += 25.
            f.write( "{:18.2f}  hour (add 25 for UT) (end)\n".format( tt ) )
            f.write( "{:18.2f}  hour (step)\n".format( self.dTime ) )
            f.write( "{:18.2f}  hmf2 (km, if 0 then ignored)\n".format( self.hmf2 ) )
            f.write( "{:18.2f}  nmf2 (log10, if 0 then ignored)\n".format( self.nmf2 ) )

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
        # Initialize rays output
        self.rays = Rays(fName, site=self.site, radar=self.radar,
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
        # Initialize rays output
        self.ionos = Edens(fName, site=self.site, radar=self.radar,
            debug=debug)
        # Remove Input file
        # subp.call(['rm',fName])


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


class Edens(object):
    """Store and process electron density profiles after ray tracing

    **Args**:
        * **readFrom** (str): edens.dat file to read the rays from
        * [**site**] (:class:`pydarn.radar.site): radar site object
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
            header = readHeader(f, debug=debug)
            self.edens = {}
            while True:
                bytes = f.read(2*4)
                # Check for eof
                if not bytes: break
                # read hour and azimuth
                hour, azim = unpack('2f', bytes)
                # format time index
                hour = hour - 25.
                mm = header['mmdd']/100
                dd = header['mmdd'] - mm*100
                rtime = dt.datetime(header['year'], mm, dd) + dt.timedelta(hours=hour)
                # format azimuth index (beam)
                raz = site.azimToBeam(azim) if site else round(raz, 2)
                # Initialize dicts
                if rtime not in self.edens.keys(): self.edens[rtime] = {}
                self.edens[rtime][raz] = {}
                # Read edens dict
                # self.edens[rtime][raz]['pos'] = array( unpack('{}f'.format(250*2), f.read(250*2*4)) )
                self.edens[rtime][raz]['th'] = array( unpack('{}f'.format(250), f.read(250*4)) )
                self.edens[rtime][raz]['nel'] = array( unpack('{}f'.format(250*250), f.read(250*250*4)) ).reshape((250,250), order='F')
                self.edens[rtime][raz]['dip'] = array( unpack('{}f'.format(250*2), f.read(250*2*4)) ).reshape((250,2), order='F')


    def plot(self, time, beam=None, maxground=2000, maxalt=500,
        nel_cmap='jet', nel_lim=[10, 12], 
        showblines=False, blinescolor=(.9, 0, .4), 
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
                ax, aax, cbax = rto.ionos.plot(sTime)
                ax.grid()
                
        written by Sebastien, 2013-04
        """
        from utils import plotUtils
        from mpl_toolkits.axes_grid1 import SubplotDivider, LocatableAxes, Size
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from matplotlib.collections import LineCollection
        import matplotlib.pyplot as plt
        import numpy as np
        from math import floor

        if not ax and not aax:
            ax, aax = plotUtils.curvedEarthAxes(fig=fig, rect=rect, 
                maxground=maxground, maxalt=maxalt)
        else:
            ax = ax
            aax = aax

        # make sure that the required time and beam are present
        assert (time in self.edens.keys()), 'Unkown time %s' % time
        if beam:
            assert (beam in self.edens[time].keys()), 'Unkown beam %s' % beam
        else:
            beam = self.edens[time].keys()[0]

        X, Y = np.meshgrid(self.edens[time][beam]['th'], 6370. + np.linspace(60,560,250))
        im = aax.pcolormesh(X, Y, np.log10( self.edens[time][beam]['nel'] ), 
            vmin=nel_lim[0], vmax=nel_lim[1], cmap=nel_cmap)

        # Plot title with date ut time and local time
        title = '{:%Y-%b-%d at %H:%M} UT'.format(time)
        title += '\n(IRI-2011) {} beam {}'.format(self.name, beam)
        ax.set_title( title )

        # Add a colorbar when plotting refractive index
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

        _ = plt.colorbar(im, cax=cbax)
        _ = cbax.set_ylabel(r"N$_{el}$ [$\log_{10}(m^{-3})$]")

        return ax, aax, cbax


class Rays(object):
    """Store and process individual rays after ray tracing

    **Args**:
        * **readFrom** (str): rays.dat file to read the rays from
        * [**site**] (:class:`pydarn.radar.site): radar site object
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
            self.header = readHeader(f, debug=debug)
            # Then read ray data, one ray at a time
            while True:
                bytes = f.read(4*4)
                # Check for eof
                if not bytes: break
                # read number of ray steps, time, azimuth and elevation
                nrstep, rhr, raz, rel = unpack('4f3', bytes)
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
                self.paths[rtime][raz][rel]['r'] = array( unpack('{}f'.format(nrstep), f.read(nrstep*4)) )
                self.paths[rtime][raz][rel]['th'] = array( unpack('{}f'.format(nrstep), f.read(nrstep*4)) )
                self.paths[rtime][raz][rel]['gran'] = array( unpack('{}f'.format(nrstep), f.read(nrstep*4)) )
                self.paths[rtime][raz][rel]['pran'] = array( unpack('{}f'.format(nrstep), f.read(nrstep*4)) )
                self.paths[rtime][raz][rel]['nr'] = array( unpack('{}f'.format(nrstep), f.read(nrstep*4)) )


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


    def plot(self, time, beam=None, maxground=2000, maxalt=500, step=1,
        showrefract=False, nr_cmap='jet_r', nr_lim=[0.8, 1.], 
        raycolor='0.3', 
        showrange=False, rangecolor='0.9',
        fig=None, rect=111):
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
                rto = raydarn.RtRun(sTime, rCode='bks', beam=12)
                rto.readRays() # read rays into memory
                ax, aax, cbax = rto.rays.plot(sTime, step=2, showrefract=True, nr_lim=[.85,1])
                ax.grid()
                
        written by Sebastien, 2013-04
        """
        from utils import plotUtils
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from matplotlib.collections import LineCollection
        import matplotlib.pyplot as plt
        import numpy as np
        from math import floor

        ax, aax = plotUtils.curvedEarthAxes(fig=fig, rect=rect, 
            maxground=maxground, maxalt=maxalt)

        # make sure that the required time and beam are present
        assert (time in self.paths.keys()), 'Unkown time %s' % time
        if beam:
            assert (beam in self.paths[time].keys()), 'Unkown beam %s' % beam
        else:
            beam = self.paths[time].keys()[0]

        if showrange:
            rangemarkers = np.arange(0, 5000, 250)
        
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
                # Plot range markers if requested
                if showrange:
                    for rm in rangemarkers:
                        inds = (rays['gran']*1e-3 >= rm)
                        if inds.any():
                            aax.scatter(rays['th'][inds][0], rays['r'][inds][0]*1e-3, 
                                color=rangecolor, s=5, zorder=3)

        # Plot title with date ut time and local time
        utdec = time.hour + time.minute/60.
        tlon = (self.header['tlon'] % 360.)
        ctlon = tlon if tlon <=180. else tlon - 360.
        ltdec = ( utdec + ( ctlon/360.*24.) ) % 24.
        lthr = floor(ltdec)
        ltmn = round( (ltdec - lthr)*60 )
        title = '{:%Y-%b-%d at %H:%M} UT (~{:02.0f}:{:02.0f} LT)'.format(
            time, lthr, ltmn)
        title += '\n(IRI-2011) {} beam {}; freq {:.1f}MHz'.format(self.name, beam, self.header['freq'])
        ax.set_title( title )

        # Add a colorbar when plotting refractive index
        if showrefract:
            from mpl_toolkits.axes_grid1 import SubplotDivider, LocatableAxes, Size

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

            _ = plt.colorbar(lcol, cax=cbax)
            _ = cbax.set_ylabel("refractive index")
        else: cbax = None

        return ax, aax, cbax


def readHeader(fObj, debug=False):
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