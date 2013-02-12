class datapoint:
	def __init__(self,mo=0,lt=0,ae=0,dst=0,kp=0,lat=0,vel=0):
		self.month = mo
		self.mlt = lt
		self.ae = ae
		self.dst = dst
		self.kp = kp
		self.lat = lat
		self.vel = vel

from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import SigmoidLayer, FeedForwardNetwork, FullConnection, LinearLayer
import numpy

ds = SupervisedDataSet(6, 1)

f = open('set.txt', 'r')
f2 = open('set2.txt', 'w')
dataset=[]
for line in f:
	cols = line.split()
	mo = (int(cols[0][4:6])-1)/11.
	mlt = float(cols[2])/24.
	ae = float(cols[3])
	dst = float(cols[4])
	kp = float(cols[5])
	lat = float(cols[7])
	vel = float(cols[6])
	dataset.append(datapoint(mo,mlt,ae,dst,kp,lat,vel))

f.close()


mean = datapoint()
for d in dataset:
	mean.ae += d.ae
	mean.dst += d.dst
	mean.kp += d.kp
	mean.lat += d.lat
	mean.vel += d.vel
	
mean.ae /= float(len(dataset))
mean.dst /= float(len(dataset))
mean.kp /= float(len(dataset))
mean.lat /= float(len(dataset))
mean.vel /= float(len(dataset))

sig = datapoint()
for d in dataset:
	sig.ae += (d.ae-mean.ae)**2
	sig.dst += (d.dst-mean.dst)**2
	sig.kp += (d.kp-mean.kp)**2
	sig.lat += (d.lat-mean.lat)**2
	sig.vel += (d.vel-mean.vel)**2
sig.ae /= float(len(dataset))
sig.dst /= float(len(dataset))
sig.kp /= float(len(dataset))
sig.lat /= float(len(dataset))
sig.vel /= float(len(dataset))
sig.ae = numpy.sqrt(sig.ae)
sig.dst = numpy.sqrt(sig.dst)
sig.kp = numpy.sqrt(sig.kp)
sig.lat = numpy.sqrt(sig.lat)
sig.vel = numpy.sqrt(sig.vel)
for d in dataset:
	d.ae = (d.ae-mean.ae)/sig.ae
	d.dst = (d.dst-mean.dst)/sig.dst
	d.kp = (d.kp-mean.kp)/sig.kp
	d.lat = (d.lat-mean.lat)/sig.lat
	d.vel = (d.vel-mean.vel)/sig.vel
	f2.write(str(d.month)+','+str(d.mlt)+','+str(d.ae)+','+str(d.dst)+','+str(d.kp)+','+str(d.lat)+','+str(d.vel)+'\n')
f2.close()

for i in range(int(len(dataset)*.8)):
	d=dataset[i]
	ds.addSample([d.month,d.mlt,d.ae,d.dst,d.kp,d.lat],[d.vel,])

net = FeedForwardNetwork()


inLayer = SigmoidLayer(6)
net.addInputModule(inLayer)
hiddenLayer = SigmoidLayer(9)
net.addModule(hiddenLayer)
hiddenLayer2 = SigmoidLayer(9)
net.addModule(hiddenLayer2)
outLayer = SigmoidLayer(1)
net.addOutputModule(outLayer)

in_to_hidden = FullConnection(inLayer, hiddenLayer)
net.addConnection(in_to_hidden)
hidden_to_hidden = FullConnection(hiddenLayer, hiddenLayer2)
net.addConnection(hidden_to_hidden)
hidden_to_out = FullConnection(hiddenLayer2, outLayer)
net.addConnection(hidden_to_out)

net.sortModules()


trainer = BackpropTrainer(net, ds, learningrate=.05)

print 'using',len(ds),'sample to train'
for i in range(100):
	print 'epoch',i
	y = trainer.train()
	errs,err,np=[],0.,0
	for j in range(int(len(dataset)*.8),len(dataset)):
		d=dataset[j]
		x= net.activate([d.month,d.mlt,d.ae,d.dst,d.kp,d.lat])
		print d.vel,x
		err += abs(d.vel-x)
		errs.append(abs(d.vel-x))
		np += 1.
	print (err*sig.vel+mean.vel)/np,numpy.median(errs)*sig.vel+mean.vel
