SuperDARN data files in order of processing:

1. `*.iqdat`: Raw voltage measurements, lowest level of data.  Archived by some groups, but not distributed or widely used.
2. `*.rawacf`: Raw autocorrelation files produced at each radar.  Routinely archived and distributed amongst all the SuperDARN institutions, not typically used for science.
3. `*.fitacf/*.fitex`: Usable geophysical data for each radar, including doppler velocities, scatter power, spectral width, etc.  This has been derived from *.rawacf using `make_fit` or `make_fitex2` from the Radar Software Toolkit (RST).
4. `*.grdmap/*.grdex`:  Combines data from all radars in a hemisphere into a single file into a grid with roughly equi-sized cells using make_grid from the RST.
5. `*.cnvmap/*.mapex`: Contains everything the gridex file has plus the fitted coefficients giving the convection pattern.  This is created from grdex files in a multi-step process using tools from the RST.

Notes:
FITEX2 has been developed to overcome certain fitting errors in the FITACF process.  For an explanation of the differences and the fitting process in general, see Ribeiro et al. 2013.  

For an explanation of the gridding and map potential fitting process, see Ruohoniemi and Baker 1998.

Prior to 2006, plain text files were used to store data.  Here is the key relating old format to new format:

* `*.dat — > *.rawacf`
* `*.fit   —> *.fitacf/*.fitex`
* `*.grd —> *.grdmap/*.grdex`
* `*.map —> *.cnvmap/*.mapex`

IMPORTANT WARNING:  When old formats were used, both *.dat and *.fit were created at the radar site during the time of observations.  However, the old *.dat format was lossy.  Therefore, it is not possible to generate a good *.fit file from a *.dat file.  Instead, you should use the *.fit that was actually created at the radar.

The easiest way to tell the difference between old format and new format is to try and open the file in a text editor.  If it shows up as plain text, you know you are working with an old format file.  New format files must be read using the dmapdump -d routine in RST.  All low-level processing of these data files is done by the RST.

DavitPy loads these data files into memory by using C routines in davitpy/pydarn/dmapio.  This module must be built on each machine you install DavitPy on (see davitpy/mastermake).  This routines also depend on a working build of the RST.

DavitPy looks first in a local directory (currently setup to work with the path structure on Virginia Tech’s servers) for data.  If not found there, DavitPy will use SFTP to get the data from Virginia Tech’s Servers.  Other local files may be specified, see implementation in davitpy/pydarn/sdio/.

References

Ribeiro, A. J., J. M. Ruohoniemi, P. V. Ponomarenko, L. B. N. Clausen, J. B. H. Baker, R. A. Greenwald, K. Oksavik, and S. de Larquier (2013), A comparison of SuperDARN ACF fitting methods, Radio Sci., 48, 274-282, doi:10.1002/rds.20031.

Ruohoniemi, J. M., and K. B. Baker (1998), Large-scale imaging of high-latitude convection with Super Dual Auroral Radar Network HF radar observations, J. Geophys. Res., 103(A9),20797–20811, doi:10.1029/98JA01288.
