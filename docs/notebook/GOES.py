# This notebook shows how to download and plot GOES data.

# In[1]:

# Import required libraries.
from __future__ import absolute_import
from matplotlib.pyplot import figure,show
import datetime
from davitpy import gme #This is the DavitPy GeoMagnetic Environment module


# In[2]:

# Define the start time, end time, and which GOES Satellite to use.
# Make sure the satellite is available for your particular interval period.
# Data will be downloaded directly from NOAA at
# ftp://satdat.ngdc.noaa.gov/sem/goes/data/new_avg/

sTime       = datetime.datetime(2014,5,21)
eTime       = datetime.datetime(2014,5,24)
sat_nr      = 15


# In[3]:

# This routine will download the data from NOAA and populate a dictionary containing
# metadata and a dataframe with the GOES data data.
# This routine downloads the 1-min Avg X-Xray flux data for two bands
# (0.05-0.4 nm and 0.1-0.8 nm).

goes_data   = gme.sat.read_goes(sTime,eTime,sat_nr)


# In[4]:

# This routine will use the dictionary format provided above to plot the GOES data.

fig  = gme.sat.goes_plot(goes_data)


# # Finding and Plotting Large Flares

# In[5]:

#Load in a large amount of GOES data...
sTime       = datetime.datetime(2014,1,1)
eTime       = datetime.datetime(2014,6,30)
sat_nr      = 15
goes_data   = gme.sat.read_goes(sTime,eTime,sat_nr)

#Find all of the X-Class flares in that time period (using 60-minute windowing)
flares      = gme.sat.find_flares(goes_data,min_class='X1',window_minutes=60)
flares


#Now create a plot for each flare.
for key,flare in flares.iterrows():
    #Create the figure and axis.
    fig     = figure(figsize=(10,8))
    ax      = fig.add_subplot(111)

    #Label and plot just the flare max.
    label   = '{0} Class Flare @ {1}'.format(flare['class'],key.strftime('%H%M UT'))
    ax.plot(key,flare['B_AVG'],'o',label=label)

    #Now plot the GOES data around the flare.
    plot_sTime  = key - datetime.timedelta(hours=12)
    plot_eTime  = key + datetime.timedelta(hours=12)
    gme.sat.goes_plot(goes_data,ax=ax,sTime=plot_sTime,eTime=plot_eTime)


show()



