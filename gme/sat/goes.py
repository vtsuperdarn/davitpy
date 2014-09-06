import os
import datetime
import fnmatch
import glob

import numpy as np

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

import ftplib
import netCDF4
import pandas as pd

import calendar
def add_months(sourcedate,months=1):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

#url = 'ftp://satdat.ngdc.noaa.gov/sem/goes/data/new_avg/2014/08/goes15/netcdf/g15_xrs_1m_20140801_20140831.nc'
sat_nr      = 15
sTime       = datetime.datetime(2014,5,21)
eTime       = sTime + datetime.timedelta(days=3)

#Determine which months of data to download.
ym_list     = [datetime.date(sTime.year,sTime.month,1)]
eMonth      = datetime.date(eTime.year,eTime.month,1)
while ym_list[-1] < eMonth:
    ym_list.append(add_months(ym_list[-1]))

# Download Files from NOAA FTP #################################################
host        = 'satdat.ngdc.noaa.gov'

data_dir    = os.path.join('data','goes')
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
df = None
for file_path in file_paths:
    nc = netCDF4.Dataset(file_path)
    tt = nc.variables['time_tag']
    jd = np.array(netCDF4.num2date(tt[:],tt.units))

    myVars = ['A_QUAL_FLAG','A_NUM_PTS','A_AVG','B_QUAL_FLAG','B_NUM_PTS','B_AVG']
    data = {}
    for var in myVars:
        data[var] = nc.variables[var][:]
    
    df_tmp = pd.DataFrame(data,index=jd)
    if df is None:
        df = df_tmp
    else:
        df = df.append(df_tmp)

################################################################################
# Plotting code...
output_dir  = os.path.join('output','goes')
try:
    os.makedirs(output_dir)
except:
    pass

out_file        = '_'.join(['GOES{0:02d}'.format(sat_nr),sTime.strftime('%Y%m%d-%H%M'),eTime.strftime('%Y%m%d-%H%M')])
out_file_path   = os.path.join(output_dir,out_file)
fig     = plt.figure(figsize=(10,6))
axis    = fig.add_subplot(111)

var_tags = ['A_AVG','B_AVG']
for var_tag in var_tags:
    var     = nc.variables[var_tag]
    axis.plot(df.index,df[var_tag],label=var.long_label)

#Format the x-axis
axis.set_xlabel('Time [UT]')
axis.set_xlim(sTime,eTime)

major_ticks = [sTime]
while major_ticks[-1] <= eTime:
    major_ticks.append(major_ticks[-1] + datetime.timedelta(days=1))

axis.xaxis.set_ticks(major_ticks)
major_tick_labels = [dt.strftime('%H%M\n%d %b %Y') for dt in major_ticks]
axis.xaxis.set_ticklabels(major_tick_labels)

trans = matplotlib.transforms.blended_transform_factory(axis.transAxes, axis.transData)
classes = ['A', 'B', 'C', 'M', 'X']
decades = [  8,   7,   6,   5,   4]

for cls,dec in zip(classes,decades):
    axis.text(1.01,2.5*10**(-dec),cls,transform=trans)

#Format the y-axis
axis.set_ylabel(r'watts m$^{-2}$')
axis.set_yscale('log')
axis.set_ylim(1e-9,1e-2)

axis.grid()
axis.legend(prop={'size':10})

title = ' '.join([nc.institution,nc.satellite_id,'-',nc.instrument])
axis.set_title(title)

fig.tight_layout()
fig.savefig(out_file_path,bbox_inches='tight')
