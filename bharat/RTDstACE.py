#****************************
# This code has two functions - ACERtDwnldPlt() and DstRtDwnldPlot()
#
# The ACERtDwnldPlt downloads ACE data files from the NOAA website and plots IMF and solarwind data
# The files are updated every minute on the website
#
#The DstRtDwnldPlot downloads Dst data files from the USGS website and plots the Dst index
#The time resolution of the Dst index is 1-min. The files are updated online every few minutes.
#
#Created by Bharat Kunduri 20120919
#*******************************

import urllib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math
import datetime
from time import gmtime, strftime
import matplotlib

## This part is for downloading and plotting ACE data

def ACERtDwnldPlt():

	# Files to be downloaded and read
	url_acesw = 'http://www.swpc.noaa.gov/ftpdir/lists/ace/ace_swepam_1m.txt'
	url_acemag = 'http://www.swpc.noaa.gov/ftpdir/lists/ace/ace_mag_1m.txt'
	file_acesw = '/home/bharat/Desktop/file_acesw.txt'
	file_acemag = '/home/bharat/Desktop/file_acemag.txt'

	urllib.urlretrieve(url_acesw,file_acesw)
	urllib.urlretrieve(url_acemag,file_acemag)


	# open the files...loop through them and read data into arrays
	# start with the swepam files...
	f_acesw = open(file_acesw, 'r')

	for line in range(0,18):
		header = f_acesw.readline()

	np_sw=[]
	vt_sw=[]
	time_sw=[]


	for line in f_acesw:
		line = line.strip()
		columns = line.split()

		hh_sw = int(int(columns[3])/100)
		mm_sw = int(int(columns[3]) % 100)
		time_sw.append(datetime.datetime(int(columns[0]), int(columns[1]), int(columns[2]), hh_sw, mm_sw))

		# check for garbage values in the data
		if abs(float(columns[7])) > 100.:
			columns[7] = float('nan')

		if abs(float(columns[8])) > 2000.:
			columns[8] = float('nan')

		np_sw.append(float(columns[7]))
		vt_sw.append(float(columns[8]))

	f_acesw.close()

	# Now the mag files...
	f_acemag = open(file_acemag, 'r')

	for line in range(0,20):
		header = f_acemag.readline()


	Bx_mag=[]
	By_mag=[]
	Bz_mag=[]
	time_mag=[]


	for line in f_acemag:
		line = line.strip()
		columns = line.split()

		hh_mag = int(int(columns[3])/100)
		mm_mag = int(int(columns[3]) % 100)
		time_mag.append(datetime.datetime(int(columns[0]), int(columns[1]), int(columns[2]), hh_mag, mm_mag))


		# check for garbage values in the data
		if abs(float(columns[7])) > 100.:
			columns[7] = float('nan')

		if abs(float(columns[8])) > 100.:
			columns[8] = float('nan')

		if abs(float(columns[9])) > 100.:
			columns[9] = float('nan')

		Bx_mag.append(float(columns[7]))
		By_mag.append(float(columns[8]))
		Bz_mag.append(float(columns[9]))


	f_acemag.close()

	
#	set the format of the ticks -- major ticks are set for 0,15,30,45 and 60th mins of the hour
#	minor ticks are set every 5 min.
	xtickHours = matplotlib.dates.HourLocator()
	xtickMins_major = matplotlib.dates.MinuteLocator(byminute=range(0,60,15))
	xtickMins_minor = matplotlib.dates.MinuteLocator(byminute=range(0,60,5))

	HMFmt = matplotlib.dates.DateFormatter('%H:%M')

	#Plot the IMF data
	fig = plt.figure()
	ax = fig.add_subplot(311)
	ax.plot(time_mag,Bz_mag,label='Bz_GSM',color='r')
	ax.plot(time_mag,By_mag,label='By_GSM',color='b',linestyle='--')

	#format the ticks
	ax.xaxis.set_major_formatter(HMFmt)
	ax.xaxis.set_major_locator(xtickMins_major)
	ax.xaxis.set_minor_locator(xtickMins_minor)
	ax.set_xticklabels([])

#	set the labels for the plots
	plt.ylabel('IMF [nT]')
	plt.axis([time_mag[0],time_mag[-1],-10.,10.])
	plt.title('REAL TIME ACE DATA : '+str(datetime.datetime.date(time_mag[-1])))
	plt.legend(loc=3,prop={'size':6},shadow=True,fancybox=True)


	#Plot the solarwind velocity data

	ax2 = fig.add_subplot(312)
	ax2.plot(time_sw,vt_sw,color='r')


	#format the ticks
	ax2.xaxis.set_major_formatter(HMFmt)
	ax2.xaxis.set_major_locator(xtickMins_major)
	ax2.xaxis.set_minor_locator(xtickMins_minor)
	ax2.set_xticklabels([])

	plt.ylabel('SW.Vel [km/s]')
	plt.axis([time_mag[0],time_mag[-1],200.,700.])



	#Plot the solarwind Proton Density data

	ax3 = fig.add_subplot(313)
	ax3.plot(time_sw,np_sw,color='r')


	#format the ticks
	ax3.xaxis.set_major_formatter(HMFmt)
	ax3.xaxis.set_major_locator(xtickMins_major)
	ax3.xaxis.set_minor_locator(xtickMins_minor)


#	set the labels for the plots
	plt.ylabel('Np [p/cc]')
	plt.xticks(rotation=25)
	plt.axis([time_mag[0],time_mag[-1],0.,10.])
	plt.xlabel('Time (UT)')

	#SAVE The figure

	fig.savefig('/home/bharat/Desktop/ACE-RT.pdf',orientation='portrait',papertype='a4',format='pdf')
	
	
	
## This part is for downloading and plotting Dst Data


def DstRtDwnldPlot():


	# Files to be downloaded and read
	# The url_dst1 is not the complete url, we still have more stuff needed to
	# download data
	url_dst1 = 'http://geomag.usgs.gov/data/indices/Dst_minute/'
	file_dst = '/home/bharat/Desktop/DST-RT/file_dstcurr.txt'

	#get the current date parameters for downloading stuff	
	cur_UT_year = strftime("%Y", gmtime())
	cur_UT_mon = strftime("%m", gmtime())
	cur_UT_day = strftime("%d", gmtime())
	cur_UT_hour = strftime("%H", gmtime())

	# the name of Dst file to download
	Dst_dwnload_file = 'Dst4_'+str(cur_UT_mon)+str(cur_UT_day)+str(cur_UT_year)+'.min'

	#Now get the Dst file url you want to download
	url_Dst = url_dst1+Dst_dwnload_file
	
	urllib.urlretrieve(url_Dst,file_dst)

	#Open the downloaded Dst file for reading the data
	f_dst = open(file_dst, 'r')

	for line in range(0,14):
		header = f_dst.readline()

	Dst_val=[]
	datime_Dst=[]

	# The data from the files are read into arrays defined above...
	for line in f_dst:
		line = line.strip()
		columns = line.split()
		#first read the date and time from the file and convert it into a datetime object
    		date_Dst = datetime.datetime.strptime(columns[0], "%Y-%m-%d").date()
    		time_Dst = datetime.datetime.strptime(columns[1], "%H:%M:%S.%f").time()
    		datime_Dst.append(datetime.datetime.combine(date_Dst, time_Dst))
    		Dst_val.append(float(columns[2]))
	
	
	f_dst.close()
	
	#set the formatting for plotting
	HMFmt = matplotlib.dates.DateFormatter('%H:%M')
	xtickMins_major = matplotlib.dates.HourLocator(byhour=range(0,24,3))
	xtickMins_minor = matplotlib.dates.MinuteLocator(byminute=range(0,60,30))

	#Plot the Dst data
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(datime_Dst,Dst_val,color='r')

	#format the ticks
	ax.xaxis.set_major_formatter(HMFmt)
	ax.xaxis.set_major_locator(xtickMins_major)
	ax.xaxis.set_minor_locator(xtickMins_minor)
	#ax.set_xticklabels([])
	
	#set the labels for the plots
	plt.ylabel('Dst Index [nT]')
	plt.xlabel('Time (UT)')
	plt.xticks(rotation=25)
	plt.axis([datime_Dst[0],datime_Dst[-1],-60.,30.])
	plt.title('REAL TIME Dst index : '+str(date_Dst))
	
	fig.savefig('/home/bharat/Desktop/DST-RT.pdf',orientation='portrait',papertype='letter',format='pdf')