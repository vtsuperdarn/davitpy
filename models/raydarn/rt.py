# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: models.raydarn.rt
*********************
This module runs the raytracing code

**Class**:
    * :class:`rt.rtRun`: run the code
    * :class:`rt.rays`: store and process individual rays

.. note:: The ray tracing requires mpi to run. You can adjust the number of processors, but be wise about it and do not assign more than you have

"""


class rtRun(object):
    """This class runs the raytracing code and processes the output

    **Args**: 
        * [**sTime**] (datetime.datetime): start time
        * [**eTime**] (datetime.datetime): end time (if not provided run for a single time sTime)
        * [**rCode**] (str): radar 3-letter code
        * [**radarObj**] (:class:`pydarn.radar.radar`): radar object (overrides rCode)
        * [**dTime**] (float): time step in Hours
        * [**ut**] (bool): specify it time is in UT
        * [**freq**] (float): operating frequency [MHz]
        * [**beam**] (int): beam number (if None run all beams)
        * [**nhops**] (int): number of hops
        * [**elev**] (tuple): (start elevation, end elevation, step elevation) [degrees]
        * [**azim**] (tuple): (start azimuth, end azimuth, step azimuth) [degrees East] (overrides beam specification)
        * [**hmf2**] (float): F2 peak alitude [km] (default: use IRI)
        * [**nmf2**] (float): F2 peak electron density [log10(m^-3)] (default: use IRI)
        * [**debug**] (bool): print some diagnostics of the fortran run and output processing
        * [**fext**] (str): output file id, max 10 character long (mostly used for multiple users environments, like a website)
        * [**loadFrom**] (str): file name where a pickled instance of rtRun was saved (supersedes all other args)
        * [**nprocs**] (int): number of processes to use with MPI
    **Returns**:
        * **rtRun** (:class:`rtRun`)
    **Example**:
        ::

            # Run a 2-hour ray trace from Blackstone on a random day
            sTime = dt.datetime(2012, 11, 18, 5)
            eTime = sTime + dt.timedelta(hours=2)
            radar = 'bks'
            # Save the results to your /tmp directory
            rto = raydarn.rtRun(sTime, eTime, rCode=radar, outDir='/tmp')

    """
    def __init__(self, sTime=None, eTime=None, 
        rCode=None, radarObj=None, 
        dTime=.5, ut=True, 
        freq=11, beam=None, nhops=1, 
        elev=(5, 60, .5), azim=None, 
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
            self.ut = ut

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
            if self.ut: tt += 25.
            f.write( "{:18.2f}  hour (add 25 for UT) (begin)\n".format( tt ) )
            tt = self.time[1].hour + self.time[1].minute/60.
            tt += (self.time[1].day - self.time[0].day) * 24.
            if self.ut: tt += 25.
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
            * Add a new member to :class:`rt.rtRun`: **rays**, of type :class:`rt.rays`
        """
        import subprocess as subp
        from os import path

        # File name and path
        fName = path.join(self.outDir, 'rays.{}.dat'.format(self.fExt))
        # Initialize rays output
        self.rays = rays(fName, site=self.site, saveToAscii=saveToAscii, debug=debug)
        # Remove Input file
        subp.call(['rm',fName])


    def save(self, filename):
        """Save :class:`rt.rtRun` to a file
        """
        import cPickle as pickle

        with open( filename, "wb" ) as f:
            pickle.dump(self, f)


    def load(self, filename):
        """Load :class:`rt.rtRun` from a file
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


class rays(object):
    """Store and process individual rays after ray tracing

    **Args**:
        * **readFrom** (str): rays.dat file to read the rays from
        * [**site**] (:class:`pydarn.radar.site): 
    """
    def __init__(self, readFrom, site=None, saveToAscii=None, debug=False):
        self.readFrom = readFrom
        self.paths = {}

        # Read rays
        self.readRays(site=site, debug=debug)

        # If required, save to ascii
        if saveToAscii:
            self.writeToAscii(saveToAscii)


    def readRays(self, site=None, debug=False):
        """Read rays.dat fortran output

        **Args**:
            * [**saveToAscii**] (str): output content to text file
            * [**debug**] (bool): print some i/o diagnostics
        **Returns**:
            * Add a new member to :class:`rt.rtRun`: **rays**, of type :class:`rt.rays`
        """
        from struct import unpack
        import datetime as dt
        from collections import OrderedDict
        import os
        from numpy import round, array

        # Declare header parameters
        params = ('nhour', 'nazim', 'nelev', 
            'tlat', 'tlon', 
            'saz', 'eaz', 'daz', 
            'sel', 'eel', 'del', 
            'freq', 'nhop', 'year', 'mmdd', 
            'shour', 'ehour', 'dhour', 
            'hmf2', 'nmf2')
        # Read binary file
        with open(self.readFrom, 'rb') as f:
            # Read header
            self.header = OrderedDict( zip( params, unpack('3i9f3i5f', f.read(3*4 + 9*4 + 3*4 + 5*4)) ) )
            self.header['fext'] = unpack('10s', f.read(10))[0].strip()
            self.header['outdir'] = unpack('100s', f.read(100))[0].strip()
            # Only print header if in debug mode
            if debug:
                print self.readFrom+' header: '
                for k, v in self.header.items(): print '{:10s} :: {}'.format(k,v)
            self.header.pop('fext'); self.header.pop('outdir')
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
                if rhr >= 25.: rhr = rhr - 25.
                mm = self.header['mmdd']/100
                dd = self.header['mmdd'] - mm*100
                rtime = dt.datetime(self.header['year'], mm, dd) + dt.timedelta(hours=rhr)
                # Create new entries in rays dict
                if rtime not in self.paths.keys(): self.paths[rtime] = {}
                if raz not in self.paths[rtime].keys(): self.paths[rtime][raz] = {}
                self.paths[rtime][raz][rel] = {}
                # Read and write to rays dict
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
        raycolor='0.4',  
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
                rto = raydarn.rtRun(sTime, rCode='bks', beam=12)
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

        ax, aax = plotUtils.curvedEarthAxes(fig=fig, rect=rect, 
            maxground=maxground, maxalt=maxalt)

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
                    lcol.set_cmap( nr_cmap )
                    lcol.set_norm( plt.Normalize(*nr_lim) )
                    lcol.set_array( rays['nr'] )
                    aax.add_collection( lcol )
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

            divider.set_horizontal(h)
            divider.set_vertical(v)

            ax.set_axes_locator(divider.new_locator(nx=0, ny=0))
            cbax.set_axes_locator(divider.new_locator(nx=2, ny=0))

            fig1.add_axes(cbax)

            cbax.axis["left"].toggle(all=False)
            cbax.axis["top"].toggle(all=False)
            cbax.axis["bottom"].toggle(all=False)
            cbax.axis["right"].toggle(ticklabels=True, label=True)

            plt.colorbar(lcol, cax=cbax)
            cbax.set_ylabel("refractive index")

        return ax, aax, cbax