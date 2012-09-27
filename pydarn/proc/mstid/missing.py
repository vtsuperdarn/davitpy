#! /usr/bin/env python
import datetime
import os
import re

dateList = [datetime.date(2010,11,01)]
endDate = datetime.date(2011,11,01)
delta = datetime.timedelta(days=1)
currentDay = dateList[len(dateList)-1]
while (currentDay != endDate):
  currentDay = currentDay + delta
  dateList.append(currentDay)

#for x in dateList:
#  print x.strftime('%Y%m%d')

filename = 'missing.txt'

ls = os.listdir('../psdsav')

radar = ['pgr','sas','kap','gbr','cvw','fhe','bks','wal']

f = open(filename,'w')
f.close

for rad in radar:
  suffix = '.'+rad+'.power.300-1200.intpsd.sav'
  dates = [x.strftime('%Y%m%d')+suffix for x in dateList]

  pat = re.compile(r'.*'+rad+'.*intpsd.*')

  filtLs = []
  for x in ls:
    m = pat.match(x)
    if m:
      filtLs.append(m.string)
    else:
      pass

  missing = []
  for x in dates:
    if not filtLs.count(x):
      missing.append(x)

  with open(filename,'a') as f:
    s = rad+' is missing '+str(len(missing))+' files.  They are:\n'
    f.write(s)
    for x in missing:
      f.write(x+'\n')
    f.write('\n')
