from pydarn.sdio import *
import datetime as dt

st = dt.datetime(2011,6,3,16,0,0)
et = dt.datetime(2011,6,3,23,0,0)
rad='fhe'
channel='a'
bmnum=7

print 'First, lets try local files'
t = dt.datetime.now()
ptr = radDataOpen(st,rad,eTime=et,channel=channel,bmnum=bmnum,cp=None,src='local')
d = radDataReadRec(ptr)
cnt1=0
while(d != None):
	d = radDataReadRec(ptr)
	cnt1 += 1
	
t1 = dt.datetime.now() - t


print 'Next, lets try sftp files'
t = dt.datetime.now()
ptr = radDataOpen(st,rad,eTime=et,channel=channel,bmnum=bmnum,cp=None,src='sftp')
d = radDataReadRec(ptr)
cnt2=0
while(d != None):
	d = radDataReadRec(ptr)
	cnt2 += 1
	
t2 = dt.datetime.now() - t


print 'Last, lets try mongodb data'
t = dt.datetime.now()
ptr = radDataOpen(st,rad,eTime=et,channel=channel,bmnum=bmnum,cp=None,src='mongo')
d = radDataReadRec(ptr)
cnt3=0
while(d != None):
	d = radDataReadRec(ptr)
	cnt3 += 1
	
t3 = dt.datetime.now() - t

print cnt1,cnt2,cnt3
print 'local files took: ',t1
print 'sftp files took: ',t2
print 'mongo files took: ',t3