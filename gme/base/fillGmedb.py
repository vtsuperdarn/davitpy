def fillGmeDb(time='recent'):
	import gme, os
	import pydarn.sdio.dbUtils as dbu
	from multiprocessing import Process
	import datetime as dt
	now = dt.datetime.now()
	
	if(time == 'recent'):
		sYear = dt.datetime.now().year-5
		#fill the omni database
		p0 = Process(target=gme.mapOmniMongo, args=(sYear,now.year,1))
		#fill the omni database
		p1 = Process(target=gme.mapOmniMongo, args=(sYear,now.year))
		#fill the poes database
		p2 = Process(target=gme.mapPoesMongo, args=(sYear,now.year))
		#fill the kp database
		p3 = Process(target=gme.mapKpMongo, args=(sYear,now.year))
		#fill the kp database
		p4 = Process(target=gme.mapDstMongo, args=(sYear,now.year))
		#fill the kp database
		p5 = Process(target=gme.mapAeMongo, args=(sYear,now.year))
		#fill the kp database
		p6 = Process(target=gme.mapSymAsyMongo, args=(sYear,now.year))
	else:
		db = dbu.getDbConn(username=os.environ['DBWRITEUSER'],password=os.environ['DBWRITEPASS'],dbName='gme')
		db.command('repairDatabase')
		#fill the omni database
		p0 = Process(target=gme.mapOmniMongo, args=(1995,now.year,1))
		#fill the omni database
		p1 = Process(target=gme.mapOmniMongo, args=(1995,now.year))
		#fill the poes database
		p2 = Process(target=gme.mapPoesMongo, args=(1998,now.year))
		#fill the kp database
		p3 = Process(target=gme.mapKpMongo, args=(1980,now.year))
		#fill the kp database
		p4 = Process(target=gme.mapDstMongo, args=(1980,now.year))
		#fill the kp database
		p5 = Process(target=gme.mapAeMongo, args=(1980,now.year))
		#fill the kp database
		p6 = Process(target=gme.mapSymAsyMongo, args=(1980,now.year))
		
	try: p0.start()
	except Exception,e:
		print e
		print 'problem filling Omni db'
		
	try: p1.start()
	except Exception,e:
		print e
		print 'problem filling Omni db'
		
	try: p2.start()
	except Exception,e:
		print e
		print 'problem filling Poes db'
		
	try: p3.start()
	except Exception,e:
		print e
		print 'problem filling Kp db'
		
	try: p4.start()
	except Exception,e:
		print e
		print 'problem filling Dst db'
		
	try: p5.start()
	except Exception,e:
		print e
		print 'problem filling AE db'
		
	try: p6.start()
	except Exception,e:
		print e
		print 'problem filling AE db'
		
		
	p0.join()
	p1.join()
	p2.join()
	p3.join()
	p4.join()
	p5.join()
	p6.join()