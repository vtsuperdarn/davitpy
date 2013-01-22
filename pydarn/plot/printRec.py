"""
*******************************
MODULE: pydarn.plot.printRec
*******************************

This module contains the following functions:

	fitPrintRec

"""

def fitPrintRec(sTime, eTime, rad, outfile, fileType='fitex', summ=0):
	
	"""
|	**PACKAGE**: pydarn.plot.printRec
|	**FUNCTION**: fitPrintRec(sTime, eTime, rad, outfile, fileType='fitex', summ=0)
|	**PURPOSE**: prints out the contents of a fit file
|
|	**INPUTS**:
|		**sTime**: the start time as a datetime
|		**eTime**: the end time as a datetime
|		**rad**: the 3 letter radar code, eg 'bks'
|		**outfile**: the txt file we are outputting to
|		**[fileType]**: the filetype to read, 'fitex','fitacf','lmfit'; 
|			default = 'fitex'
|		**[summ]**: option to output a beam summary instead of all data
|
|	**OUTPUTS**:
|		NONE
|	
|	**EXAMPLES**:
|		fitPrintRec(datetime(2011,1,1,1,0),datetime(2011,1,1,2,0),'bks','myoutfile.txt',summ=1)
|		
|	Written by AJ 20121003
	"""
	import pydarn
	
	myPtr = pydarn.sdio.radDataOpen(sTime,rad,eTime=eTime,fileType=fileType)
	if(myPtr == None): return None
	
	myData = pydarn.sdio.radDataReadRec(myPtr)
	if(myData == None): return None
	
	
	radar = pydarn.radar.network().getRadarByCode(rad)
	site = radar.getSiteByDate(myData.time)
	myFov = pydarn.radar.radFov.fov(site=site,rsep=myData.prm.rsep,ngates=myData.prm.nrang)
	
	
	f = open(outfile, 'w')
	
	
	t = myData.time
	
	if(summ == 1):
		f.write('{0:10s} {1:3s} {2:7s}\n'.format(t.strftime("%Y-%m-%d"),radar.name,myData))
		f.write('{0:9s} {11:6s} {1:>4s} {2:>5s} {3:>5s} {12:4s} {4:>7s} {5:>7s} {6:>5s} {7:>5s} {8:>5s} {9:>5s} {10:>4s}\n'.\
		format('time','beam','npnts','nrang','cpid','channel','tfreq','lagfr','smsep','intt','scan','us','rsep'))
			
			
	while(myData != None and myData.time <= eTime):
		t = myData.time
		if(summ == 0):
			f.write(t.strftime("%Y-%m-%d  "))
			f.write(t.strftime("%H:%M:%S  "))
			f.write(radar.name+' ')
			f.write(myData.fType+'\n')
			f.write('bmnum = '+str(myData.bmnum))
			f.write('  tfreq = '+str(myData.prm.tfreq))
			f.write('  sky_noise_lev = '+str(int(round(float(myData.prm.noisesky)))))
			f.write('  search_noise_lev = '+str(int(round(float(myData.prm.noisesearch)))))
			f.write('  xcf = '+str(myData.prm.xcf))
			f.write('  scan = '+str(+myData.prm.scan)+'\n')
			f.write('npnts = '+str(len(myData.fit.slist)))
			f.write('  nrang = '+str(myData.prm.nrang))
			f.write('  channel = '+myData.channel)
			f.write('  cpid = '+str(myData.cp)+'\n')
			
			f.write('{0:>4s}  {1:>8s} / {2:<5s} {3:>8s}  {4:>5s} {5:>8s} {6:>8s} {7:>8s} {8:>8s}\n'.format\
			('gate','pwr_lag0','pwr_l','vel','gscat','vel_err','width_l','geo_lat','geo_lon'))
			
			for i in range(len(myData.fit.slist)):
				f.write('{0:4d}  {1:>8.1f} / {2:<5.1f} {3:>8.1f}  {4:>5d} {5:>8.1f} {6:>8.1f} {7:>8.2f} {8:>8.2f}\n'.format\
				(myData.fit.slist[i],myData.fit.pwr0[i],myData.fit.p_l[i],\
				myData.fit.v[i],myData.fit.gflg[i],myData.fit.v_e[i],\
				myData.fit.w_l[i],myFov.latFull[myData.bmnum][myData.fit.slist[i]],\
				myFov.lonFull[myData.bmnum][myData.fit.slist[i]]))
					
			f.write('\n')
			
		else:
			f.write('{0:9s} {11:6s} {1:>4d} {2:>5d} {3:>5d} {12:>4d} {4:>7d} {5:>7s} {6:>5d} {7:>5d} {8:>5d} {9:>5.2f} {10:>4d}\n'.\
			format(t.strftime("%H:%M:%S."),myData.bmnum,len(myData.fit.slist),\
			myData.prm.nrang,myData.cp,myData.channel,myData.prm.tfreq,\
			myData.prm.lagfr,myData.prm.smsep,myData.prm.inttsc+myData.prm.inttus/1e6,\
			myData.prm.scan,t.strftime("%f"),myData.prm.rsep))
			
		myData = pydarn.sdio.radDataReadRec(myPtr)
		if(myData == None): break
		