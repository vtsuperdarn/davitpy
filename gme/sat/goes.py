# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
.. module:: goes
   :synopsis: A module for working with GOES data.

.. moduleauthor:: N.A. Frissell, 6 Sept 2014

*********************
**Module**: gme.sat.goes
*********************
**Functions**:
	* :func:`gme.sat.read_goes`
"""

def read_goes(sTime,eTime=None,sat_nr=15):
    """Download GOES X-Ray Flux data from the NOAA FTP Site and return a dictionary containing the metadata and a dataframe.

        * Data is downloaded from ftp://satdat.ngdc.noaa.gov/sem/goes/data/new_avg/2014/08/goes15/netcdf/
        * Currently, 1-m averaged x-ray spectrum in two bands (0.5-4.0 A and 1.0-8.0 A).
        * NOAA NetCDF files are cached in $DAVIT_TMPDIR
    
    **Args**: 
        * [**sTime**] (datetime.datetime): Starting datetime for data.
        * [**eTime**] (datetime.datetime): Ending datetime for data.  If None, eTime will be set to sTime + 1 day.
        * [**sat_nr**] (int): GOES Satellite number.  Defaults to 15.

    **Returns**:
      * Dictionary containing metadata, pandas dataframe with GOES data.

    **Example**:
      ::
      
        goes_data = read_goes(datetime.datetime(2014,6,21))
      
    written by N.A. Frissell, 6 Sept 2014
    """
    import os
    import datetime
    import fnmatch
    import glob

    import numpy as np

    import ftplib
    import netCDF4
    import pandas as pd

    import calendar

    def add_months(sourcedate,months=1):
        """
        Add 1 month to a datetime object.
        """
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month / 12
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)

    if eTime is None: eTime = sTime + datetime.timedelta(days=1)

    #Determine which months of data to download.
    ym_list     = [datetime.date(sTime.year,sTime.month,1)]
    eMonth      = datetime.date(eTime.year,eTime.month,1)
    while ym_list[-1] < eMonth:
        ym_list.append(add_months(ym_list[-1]))

    # Download Files from NOAA FTP #################################################
    host        = 'satdat.ngdc.noaa.gov'

    data_dir    = os.getenv('DAVIT_TMPDIR')
    if data_dir.endswith('/'): data_dir = data_dir[:-1]
    
    try:
        os.makedirs(data_dir)
    except:
        pass

    #rem_file    = '/sem/goes/data/new_avg/2014/08/goes15/netcdf/g15_xrs_1m_20140801_20140831.nc' #Example file.
    file_paths  = []
    for myTime in ym_list:
        #Check to see if we already have a matcing file...
        local_files = glob.glob(os.path.join(data_dir,'g{sat_nr:02d}_xrs_1m_{year:d}{month:02d}*.nc'.format(year=myTime.year,month=myTime.month,sat_nr=sat_nr)))
        if len(local_files) > 0:
            print 'Using locally cached file: {0}'.format(local_files[0])
            file_paths.append(local_files[0])
            continue

        rem_path    = '/sem/goes/data/new_avg/{year:d}/{month:02d}/goes{sat_nr:d}/netcdf'.format(year=myTime.year,month=myTime.month,sat_nr=sat_nr)
        ftp         = ftplib.FTP(host,'anonymous','@anonymous')
        s           = ftp.cwd(rem_path)
        file_list   = ftp.nlst()
        dl_list     = [x for x in file_list if fnmatch.fnmatch(x,'g*_xrs_1m_*')]
        filename    = dl_list[0]

        #Figure out where to save the file locally...
        file_path   = os.path.join(data_dir,filename)
        file_paths.append(file_path)

        #Go retrieve the file...
        print 'Downloading {0}...'.format(filename)
        ftp.retrbinary('RETR {0}'.format(filename), open(file_path, 'wb').write)

    # Load data into memory. #######################################################
    df_xray     = None
    df_orbit    = None

    data_dict   = {}
    data_dict['metadata']               = {}
    data_dict['metadata']['variables']  = {}

    for file_path in file_paths:
        nc = netCDF4.Dataset(file_path)

        #Put metadata into dictionary.
        fn  = os.path.basename(file_path)
        data_dict['metadata'][fn] = {}
        md_keys = ['NOAA_scaling_factors','archiving_agency','creation_date','end_date',
                   'institution','instrument','originating_agency','satellite_id','start_date','title']
        for md_key in md_keys:
            try:
                data_dict['metadata'][fn][md_key] = getattr(nc,md_key)
            except:
                pass

        #Store Orbit Data
        tt = nc.variables['time_tag_orbit']
        jd = np.array(netCDF4.num2date(tt[:],tt.units))

        orbit_vars = ['west_longitude','inclination']
        data    = {}
        for var in orbit_vars:
            data[var] = nc.variables[var][:]
        
        df_tmp = pd.DataFrame(data,index=jd)
        if df_orbit is None:
            df_orbit = df_tmp
        else:
            df_orbit = df_orbit.append(df_tmp)

        #Store X-Ray Data
        tt = nc.variables['time_tag']
        jd = np.array(netCDF4.num2date(tt[:],tt.units))

        myVars = ['A_QUAL_FLAG','A_NUM_PTS','A_AVG','B_QUAL_FLAG','B_NUM_PTS','B_AVG']
        data = {}
        for var in myVars:
            data[var] = nc.variables[var][:]
        
        df_tmp = pd.DataFrame(data,index=jd)
        if df_xray is None:
            df_xray = df_tmp
        else:
            df_xray = df_xray.append(df_tmp)

        #Store info about units
        for var in (myVars+orbit_vars):
            data_dict['metadata']['variables'][var] = {}
            var_info_keys = ['description','dtype','long_label','missing_value','nominal_max','nominal_min','plot_label','short_label','units']
            for var_info_key in var_info_keys:
                try:
                    data_dict['metadata']['variables'][var][var_info_key] = getattr(nc.variables[var],var_info_key)
                except:
                    pass

    df_xray = df_xray[np.logical_and(df_xray.index >= sTime,df_xray.index < eTime)]
    data_dict['xray']   = df_xray
    df_orbit = df_orbit[np.logical_and(df_orbit.index >= sTime,df_orbit.index < eTime)]
    data_dict['orbit']  = df_orbit

    return data_dict

def goes_plot(goes_data,sTime=None,eTime=None,ymin=1e-9,ymax=1e-2,legendSize=10,ax=None):
    """Plot GOES X-Ray Data.

    **Args**:
        * **goes_data**: data dictionary returned by read_goes()
        * **[sTime]**: datetime.datetime object for start of plotting.
        * **[eTime]**: datetime.datetime object for end of plotting.
        * **[ymin]**: Y-Axis minimum limit
        * **[ymax]**: Y-Axis maximum limit
        * **[legendSize]**: Character size of the legend

    **Returns**:
        * **fig**:      matplotlib figure object that was plotted to

    .. note::
        If a matplotlib figure currently exists, it will be modified by this routine.  If not, a new one will be created.

    Written by Nathaniel Frissell 2014 Sept 06
    """
    import datetime
    import matplotlib

    if ax is None:
        from matplotlib import pyplot as plt
        fig     = plt.figure(figsize=(10,6))
        ax      = fig.add_subplot(111)

    if sTime is None: sTime = goes_data['xray'].index.min()
    if eTime is None: eTime = goes_data['xray'].index.max()

    var_tags = ['A_AVG','B_AVG']
    for var_tag in var_tags:
        ax.plot(goes_data['xray'].index,goes_data['xray'][var_tag],label=goes_data['metadata']['variables'][var_tag]['long_label'])

    #Format the x-axis
    ax.set_xlabel('Time [UT]')
    ax.set_xlim(sTime,eTime)

    major_ticks = [sTime]
    while major_ticks[-1] <= eTime:
        major_ticks.append(major_ticks[-1] + datetime.timedelta(days=1))

    ax.xaxis.set_ticks(major_ticks)
    major_tick_labels = [dt.strftime('%H%M\n%d %b %Y') for dt in major_ticks]
    ax.xaxis.set_ticklabels(major_tick_labels)

    trans = matplotlib.transforms.blended_transform_factory(ax.transAxes, ax.transData)
    classes = ['A', 'B', 'C', 'M', 'X']
    decades = [  8,   7,   6,   5,   4]

    for cls,dec in zip(classes,decades):
        ax.text(1.01,2.5*10**(-dec),cls,transform=trans)

    #Format the y-axis
    ax.set_ylabel(r'watts m$^{-2}$')
    ax.set_yscale('log')
    ax.set_ylim(1e-9,1e-2)

    ax.grid()
    ax.legend(prop={'size':legendSize})

    file_keys = goes_data['metadata'].keys() 
    file_keys.remove('variables')
    file_keys.sort()
    md      = goes_data['metadata'][file_keys[-1]]
    title   = ' '.join([md['institution'],md['satellite_id'],'-',md['instrument']])
    ax.set_title(title)
    return fig


if __name__ == '__main__':
    print "This test will download GOES15 X-Ray data from 21-24 May 2014 and produce a PNG plot."

    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    import datetime

    sTime       = datetime.datetime(2014,5,21)
    eTime       = datetime.datetime(2014,5,24)
    sat_nr      = 15

    goes_data   = read_goes(sTime,eTime,sat_nr)

    fig         = goes_plot(goes_data)

    out_file        = '_'.join(['GOES{0:02d}'.format(sat_nr),sTime.strftime('%Y%m%d-%H%M'),eTime.strftime('%Y%m%d-%H%M')])
    fig.tight_layout()
    fig.savefig(out_file,bbox_inches='tight')
