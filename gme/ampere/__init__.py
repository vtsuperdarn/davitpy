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

# gmi.ampere
'''
GMI.AMPERE module

Contains:
* ampereDownloadData: Downloads AMPERE data (both northern and southern hemisphere) into the current working directory and gives an option to move it to sd-data (for VT SD users)

'''


def ampereDownloadData( Date_Dwl , move_to_sddata = False ) :
	"""
	|	**PACKAGE**: gmi.ampere.ampereDownloadData
	|	**FUNCTION**: ampereDownloadData( Date_Dwl, move_to_sddata = False )
	|	**PURPOSE**: Downloads AMPERE data (both hemispheres) of a given date and saves it in the current working directory
	|
	|	**INPUTS**:
	|	**Date_Dwl**: Date in python datetime format
	|	**move_to_sddata**: set this to True to move the downloaded data into sd-data (this is for VT-SuperDARNERS)
	|
	|	**OUTPUTS**:
	|	NONE
	|	
	|	**EXAMPLES**:
	|	ampereDownloadData( 20121231, move_to_sddata = False )
	|	
	|	Written by Bharat Kunduri 20121210
  """
    import datetime
    import calendar
    import urllib
    import urllib2
    import os 
    

    
    #Get the year from the date
    year_of_date = Date_Dwl.year
    
    #Get the UNIX time stamp for the given date
    Unix_Date_Stamp = calendar.timegm(Date_Dwl.utctimetuple())
    
    # We download data for the entire day
    Secs_Day_Dwnld = 24 * 60 * 60
    
    # The min Time Res goes for 2 min(600 sec) for some reason...need to check it again
    Time_Res_Sec = 2 * 60
    
    #Construct the required URLs
    Amp_Base_Url = "http://ampere.jhuapl.edu"
    Amp_Base_Url_Response = "http://ampere.jhuapl.edu/dataget/lib/php/download.ampere.php?cli="
    
    #For northern hemisphere
    Amp_Event_Url_North = str( Unix_Date_Stamp ) + "%20" + str( Secs_Day_Dwnld ) + "%20" + str( Time_Res_Sec ) + "%20%20" + "north" + "%20" + "grd.ncdf"
    #For southern hemisphere
    Amp_Event_Url_South = str( Unix_Date_Stamp ) + "%20" + str( Secs_Day_Dwnld ) + "%20" + str( Time_Res_Sec ) + "%20%20" + "south" + "%20" + "grd.ncdf"
    
    # Construct the final URLs to setup the download
    # This is a just a page that sends in the requests..... you need to wait and download the data from a different page
    Amp_DwnldUrl_North = Amp_Base_Url_Response + Amp_Event_Url_North
    Amp_DwnldUrl_South = Amp_Base_Url_Response + Amp_Event_Url_South
    
    
    # Get the data for the northern hemisphere
    file_Amp_North = Date_Dwl.strftime('%Y%m%d') + ".ampere.north.netcdf"
    
    Amp_Response_North = urllib.urlopen( Amp_DwnldUrl_North )
    
    # Now we have the Url where the data is stored...need to download the data from that URL
    Amp_getData_Url_North =  Amp_Base_Url + Amp_Response_North.read()
    
    #(If) we get the data...we need to transfer it to sd-data
    Amp_fldr_sd_data_north = "/sd-data/ampere/" + str( year_of_date ) + "/north/"
    
    try:
       urllib2.urlopen(Amp_getData_Url_North)
       check_url_Amp = 'yes'
    except urllib2.HTTPError, e:
       print e.code
       check_url_Amp = 'no'
    except urllib2.URLError, e:
       print e.args
       check_url_Amp = 'no'
            
            
    if ( check_url_Amp == 'yes' ) :
        urllib.urlretrieve( Amp_getData_Url_North, file_Amp_North )
        if move_to_sddata :
		os.system( "scp "+file_Amp_North+" sd-data@sd-data.ece.vt.edu:"+Amp_fldr_sd_data_north )
        	os.system( "rm "+file_Amp_North )

    else :
        print 'Error - Data could not be retreived'
        
    
        
    # Do the same for the southern hemisphere...
    file_Amp_South = Date_Dwl.strftime('%Y%m%d') + ".ampere.south.netcdf"
    
    Amp_Response_South = urllib.urlopen( Amp_DwnldUrl_South )
    
    # Now we have the Url where the data is stored...need to download the data from that URL
    Amp_getData_Url_South =  Amp_Base_Url + Amp_Response_South.read()
    Amp_fldr_sd_data_south = "/sd-data/ampere/" + str( year_of_date ) + "/south/"
    print Amp_fldr_sd_data_south
    print Amp_fldr_sd_data_north
    try:
       urllib2.urlopen(Amp_getData_Url_South)
       check_url_Amp = 'yes'
    except urllib2.HTTPError, e:
       print e.code
       check_url_Amp = 'no'
    except urllib2.URLError, e:
       print e.args
       check_url_Amp = 'no'
            
            
    if ( check_url_Amp == 'yes' ) :
        urllib.urlretrieve( Amp_getData_Url_South, file_Amp_South )
        if move_to_sddata :
		os.system( "scp "+file_Amp_South+" sd-data@sd-data.ece.vt.edu:"+Amp_fldr_sd_data_south )
        	os.system( "rm "+file_Amp_South )
        
    else :
        print 'Error - Data could not be retreived'
