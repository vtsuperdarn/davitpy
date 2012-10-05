# WAVER

def readsav(radar,date,time,param,bandLim,procType,dataDir):
	"""
	*******************************
	
        dataObj = readsav(radar,date,time,param,bandlim)
	

	INPUTS:
	OUTPUTS:

	Written by Nathaniel 14AUG2012
	*******************************
	"""

        from scipy.io.idl import readsav
        import numpy as np
        import os.path
         
        dateSt = str(date[0])
        timeSt = '.'.join(["%s" % el for el in time])
        bandLim = np.array(bandLim) * 1.e6
        bandSt = '-'.join(["%i" % el for el in bandLim])

        a = [dateSt,radar,param,bandSt,procType,'sav']
        fileName = '.'.join(a)

        path = '/'.join([dataDir,fileName])

        if os.path.exists(path):
          dataObj = readsav(path)
          return dataObj
        else:
          print ' '.join([fileName,'does not exist.'])
          sys.exit()
