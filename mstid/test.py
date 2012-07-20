import h5py
import numpy
from matplotlib import pyplot
import spacepy
import spacepy.time as spt

#import matplotlib as mplot

print "Hello World."
f = h5py.File('20111101-gbr.h5')

jul_node = f['doyJulVec']
psd_node = f['doyPsdVec']

jul = jul_node.value
psd = psd_node.value

#NaN = numpy.NAN

pyplot.interactive(True)
pyplot.figure(1)
pyplot.plot(psd)
#pyplot.show()
#pyplot.close('all')
pyplot.savefig('foo.eps')
pyplot.savefig('foo.pdf')
pyplot.savefig('foo.png')


t = spt.Ticktock(jul,'JD')
