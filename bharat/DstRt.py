import urllib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math
import datetime
from time import gmtime, strftime
import matplotlib



def DstRtPlot():


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