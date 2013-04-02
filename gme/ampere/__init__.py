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

# from pytesser import *

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
			s.system( "rm "+file_Amp_North )
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
		print 'Error - Data could not be retrieved'
		
		
# def ampereDownload(sTime, move_to_sddata = False):

# 	import datetime as dt, time, os
# 	from selenium import webdriver
# 	from PIL import Image
# 	import selenium.webdriver.common.alert as alert
	
# 	#login
# 	driver = webdriver.Chrome()
# 	driver.get('http://ampere.jhuapl.edu/dataget/index.html')
# 	x=driver.find_element_by_id("register.div")
# 	y=x.find_element_by_id('register.logon')
# 	z=y.find_element_by_id('logon')
# 	z.send_keys('username')
# 	z=y.find_element_by_id('submit')
# 	z.click()
	
# 	#set the date
# 	m=driver.find_element_by_id('main')
# 	t=m.find_element_by_id('tool')
# 	rts=t.find_elements_by_class_name('rTool')
# 	rt=rts[1]
	
# 	sels=rt.find_elements_by_tag_name('select')
	
# 	dates = sels[0].find_elements_by_tag_name('option')
# 	for d in dates:
# 		if(d.text == str(sTime.day)):
# 			d.click()
			
# 	months = sels[1].find_elements_by_tag_name('option')
# 	for mt in months:
# 		if(mt.text == sTime.strftime("%B")):
# 			mt.click()
# 			break
			
			
# 	years = sels[2].find_elements_by_tag_name('option')
# 	for d in years:
# 		if(d.text == str(sTime.year)):
# 			d.click()
			
# 	sels[3].find_elements_by_tag_name('option')[0].click()
# 	sels[4].find_elements_by_tag_name('option')[0].click()
# 	sels[5].find_elements_by_tag_name('option')[7].click()
# 	sels[6].find_elements_by_tag_name('option')[0].click()
	
# 	while(1):
# 		imgs=driver.find_elements_by_tag_name('img')
# 		i = imgs[24]
		
# 		addr = i.get_attribute('src')
# 		bin = addr[22:]
		
# 		fh = open("code.png", "wb")
# 		fh.write(bin.decode('base64'))
# 		fh.close()
		
# 		img = Image.open("code.png")
# 		r, g, b, a = img.split()
# 		img = Image.merge("RGB", (r, g, b))
# 		img.save("code.bmp")
		
# 		os.system('convert code.bmp -negate code.inv.bmp')
# 		os.system('mogrify -resize 800x200 code.inv.bmp')
# 		im = Image.open('code.inv.bmp')
# 		text = image_to_string(im)
		
# 		dl=m.find_element_by_id('download')
# 		rt=dl.find_element_by_class_name('rTool')
# 		div=rt.find_element_by_tag_name('div')
# 		sp=div.find_element_by_tag_name('span')
# 		ip=sp.find_element_by_tag_name('input')
# 		ip.send_keys(text)
# 		ips=div.find_elements_by_tag_name('input')
# 		ips[2].click()
# 		al = alert.Alert(driver)
# 		al.accept()
# 		st = m.find_element_by_id('status')
# 		divs=st.find_elements_by_class_name('rTool')
# 		rt2=divs[4]
# 		if(rt2.is_displayed()):
# 			divs2=rt2.find_elements_by_tag_name('div')
# 			divs2[1].find_element_by_tag_name('input').click()
# 			continue
# 		else:
# 			break
# 	rt2=divs[1]
# 	a=rt2.find_element_by_tag_name('a')
# 	print a.text
# 	a.click()
	
# 	os.system('convert code.bmp -negate code.inv.bmp')
# 	#al = alert.Alert(driver)