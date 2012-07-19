from pydarn.pydmap import DMapFile, timespan, dt2ts, ts2dt
import os,datetime,glob,math 

def fitRead(dateStr,rad,time=[0159,2400]):
	
	#this needs to be changed when the network is good
	myDir = os.environ['SD_FIT_PATH']