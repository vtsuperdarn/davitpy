from pydmap import DMapFile, timespan, dt2ts, ts2dt
import os,datetime 

def main():
  import pydmap
  import time
  test_file="/home/jspaleta/data/fitacf/2012/03.01/20120301.2201.00.mcm.a.fitacf"
# Format::
#  d: datetime object
#  f: matplotlib fractional day object 

  format="d"
#  format="f"
  print "Test of Dmap"
  print dir(DMapFile)
  print "Opening a dmap filelist"
  dfile=DMapFile(files=[test_file,],format=format) 
  print "Dmap Files processed"
  times=dfile.times
  print "Number of records in file:",len(times)
# Cache can be used internally in the DMapFile object to prevent re-reading information
# from the same file repeatedly.
# 0 turns it off 
  dfile.cache_limit=0
  print "Cache limit",dfile.cache_limit
  print "Comparing variable key dictionary to time key dictionary lookup in 3 seconds"
  time.sleep(3)
  for var in dfile.get_scalars(times[0]):
# h is a dictionary for a single variable, keys are record times
    h=dfile[var]
    print "Var:",var
    for t in times:
# g is a dictionary for a single record, keys are variable names 
      g=dfile[t] 
      if h[t]!=g[var]: 
        print "%s Problem at time:" % (var),t
        print var,t,"::",h[t],g[var]
        exit(0)
  dfile.purge_cache()
  print "Cache full?",dfile.is_cache_full()
  print "Cache length",len(dfile.cache)
  h=dfile['tfreq']
  g=dfile['tfreq']
  print "Combf:",dfile['combf'][dfile.times[0]]

  del dfile

## More advanced test which for file locator and for handling specific record format verification
## Used in my fitacf and rawacf modules. 
#from filelocator import locate_files
#  variables={
#      'scalars': [
#        'radar.revision.major', 'radar.revision.minor', 'origin.code', 'origin.time', 'origin.command', 'cp', 'stid',  
#        'time.yr', 'time.mo', 'time.dy', 'time.hr', 'time.mt', 'time.sc', 'time.us', 'txpow', 'nave', 'atten', 'lagfr', 
#        'smsep', 'ercod', 'stat.agc', 'stat.lopwr', 'noise.search', 'noise.mean', 'channel', 'bmnum', 'bmazm', 'scan', 
#        'offset', 'rxrise', 'intt.sc', 'intt.us', 'txpl', 'mpinc', 'mppul', 'mplgs', 'nrang', 'frang', 'rsep', 'xcf', 
#        'tfreq', 'mxpwr', 'lvmax', 'rawacf.revision.major', 'rawacf.revision.minor', 'combf', 'thr'
#        ]
#      ,'pulse_arrays': [
#        'ptab','ltab']
#      ,'variable_range_arrays': []
#      ,'index_range_array': ['slist']
#      ,'full_range_arrays': ['pwr0']
#      ,'raw_data_arrays': ['acfd']
#  }
#  required=['slist']
#  rangevar='slist'
#  format='d'
#  pathlist=fitpath=os.environ['SD_RAW_PATH'].strip().split(":")  
#  print pathlist
#  startdate=datetime.datetime(2008,9,1,17)
#  enddate=datetime.datetime(2008,9,1,18)
#  ext=['.rawacf','.rawacf.gz']
#  radarcode='kod'
#  files=locate_files(startdate,enddate,pathlist,ext,radarcode,verbose=True)
#  print files
   
#  dfile=DMapFile(files=files,required=required
#      ,starttime=startdate,endtime=enddate
#      ,rangevar=rangevar,rangearrs=variables['variable_range_arrays']
#      ,format=format)


if __name__ == '__main__':
    main()

