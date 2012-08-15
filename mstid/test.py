import h5py
import numpy
from matplotlib import pyplot
import spacepy
import spacepy.time as spt
import datetime
import dateutil.parser
#import matplotlib as mplot

print "Hello World."
f = h5py.File('20111101-gbr.h5')

jul_node = f['doyJulVec']
psd_node = f['doyPsdVec']

jul = jul_node.value
psd = psd_node.value
t = spt.Ticktock(jul,'JD')
#ep = t.

now = datetime.datetime.now()
a = range(len(psd))
b = [now + datetime.timedelta(x) for x in a]
#NaN = numpy.NAN



pyplot.interactive(True)
pyplot.close('all')
fig = pyplot.figure(1)
#pyplot.title('MSDTID Occurence')
#ax1 = fig.add_subplot(241)
pyplot.plot(b,psd)
pyplot.xlabel('Day of Year')
pyplot.ylabel('Integrated PSD')
pyplot.title('GBR')
#pyplot.show()
#pyplot.savefig('foo.eps')
#pyplot.savefig('foo.pdf')
#pyplot.savefig('foo.png')
#

