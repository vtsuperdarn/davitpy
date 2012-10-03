import pydarn,utils,datetime

def fitPrintRec(yr, mo, dy, shr, smt, ehr, emt, rad, outfile, fileType='fitex', summ=0):
	
	myDate = datetime.datetime(yr,mo,dy)
	dateStr = utils.dateToYyyymmdd(myDate)
	
	sTime = shr*100+smt
	eTime = ehr*100+emt
	
	myData = pydarn.sdio.radDataRead(dateStr,rad,time=[sTime,eTime],fileType=fileType,vb=0)
	
	if(myData.nrecs == 0): return
	
	
	f = open(outfile, 'w')
	
	
	radar = pydarn.radar.network().getRadarByCode(rad)
	site = radar.getSiteByDate(myData.times[0])
	myFov = pydarn.radar.radFov.fov(site=site,rsep=myData[myData.times[0]]['prm']['rsep'])
	
	if(summ == 0):
		for t in myData.times:
			if(myData[t]['prm']['channel'] < 2): channel = 'A'
			elif(myData[t]['prm']['channel'] == 2): channel = 'B'
			elif(myData[t]['prm']['channel'] == 3): channel = 'C'
			elif(myData[t]['prm']['channel'] == 4): channel = 'D'
			
			f.write(t.strftime("%Y-%m-%d  "))
			f.write(t.strftime("%H:%M:%S  "))
			f.write(radar.name+'\n')
			f.write('bmnum = '+str(myData[t]['prm']['bmnum']))
			f.write('  tfreq = '+str(myData[t]['prm']['tfreq']))
			f.write('  sky_noise_lev = '+str(int(round(myData[t]['prm']['noise.sky']))))
			f.write('  search_noise_lev = '+str(int(round(myData[t]['prm']['noise.search']))))
			f.write('  xcf = '+str(myData[t]['prm']['xcf']))
			f.write('  scan = '+str(+myData[t]['prm']['scan'])+'\n')
			f.write('npnts = '+str(len(myData[t]['fit']['slist'])))
			f.write('  nrang = '+str(myData[t]['prm']['nrang']))
			f.write('  channel = '+channel)
			f.write('  cpid = '+str(myData[t]['prm']['cp'])+'\n')
			
			f.write('{0:>4s}  {1:>8s} / {2:<5s} {3:>8s}  {4:>5s} {5:>8s} {6:>8s} {7:>8s} {8:>8s}\n'.format\
			('gate','pwr_lag0','pwr_l','vel','gscat','vel_err','width_l','geo_lat','geo_lon'))
			
			for i in range(len(myData[t]['fit']['slist'])):
				f.write('{0:4d}  {1:>8.1f} / {2:<5.1f} {3:>8.1f}  {4:>5d} {5:>8.1f} {6:>8.1f} {7:>8.2f} {8:>8.2f}\n'.format\
				(myData[t]['fit']['slist'][i],myData[t]['fit']['pwr0'][i],myData[t]['fit']['p_l'][i],\
				myData[t]['fit']['v'][i],myData[t]['fit']['gflg'][i],myData[t]['fit']['v_e'][i],\
				myData[t]['fit']['w_l'][i],myFov.latFull[myData[t]['prm']['bmnum']][myData[t]['fit']['slist'][i]],\
				myFov.lonFull[myData[t]['prm']['bmnum']][myData[t]['fit']['slist'][i]]))
					
			f.write('\n')
	else:
		t= myData.times[0]
		f.write(t.strftime("%Y-%m-%d")+'\n')
		f.write('{0:8s} {1:>6s} {2:>6s} {3:>6s} {4:>6s} {5:>6s}\n'.format('time','beam','npnts','nrang','cpid','scan'))
		for t in myData.times:
			f.write(t.strftime("%H:%M:%S"))
			f.write('{0:6d} {1:6d} {2:6d} {3:6d} {4:6d}\n'.format(myData[t]['prm']['bmnum'],len(myData[t]['fit']['slist']),\
			myData[t]['prm']['nrang'],myData[t]['prm']['cp'],myData[t]['prm']['scan']))
			
			
	f.close()