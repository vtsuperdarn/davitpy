class datapoint:
	def __init__(self,mo,lt,ae,dst,kp,lat,vel):
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
from pybrain.structure import SigmoidLayer, FeedForwardNetwork, FullConnection

ds = SupervisedDataSet(6, 1)

f = open('set.txt', 'r')
dataset=[]
for line in f:
	cols = line.split()
	mo = (int(cols[0][4:6])-1)/11
	mlt = (int(cols[1])/100+(int(cols[1])-(int(cols[1])/100)*100)/60.)/24.
	ae = float(cols[2])
	dst = float(cols[3])
	kp = float(cols[4])
	lat = float(cols[5])
	vel = float(cols[6])
	dataset.append(datapoint(mo,mlt,ae,dst,kp,lat,vel))
f.close

for d in dataset:
	ds.addSample([d.month,d.mlt,d.ae,d.dst,d.kp,d.lat],[d.vel,])

net = FeedForwardNetwork()


inLayer = SigmoidLayer(6)
net.addInputModule(inLayer)
hiddenLayer = SigmoidLayer(9)
net.addModule(hiddenLayer)
outLayer = SigmoidLayer(1)
net.addOutputModule(outLayer)

in_to_hidden = FullConnection(inLayer, hiddenLayer)
net.addConnection(in_to_hidden)
hidden_to_out = FullConnection(hiddenLayer, outLayer)
net.addConnection(hidden_to_out)

net.sortModules()


trainer = BackpropTrainer(net, ds,learningrate=1.,momentum=.5)

print 'using',len(ds),'sample to train'
for i in range(100):
	print 'epoch',i
	print trainer.train()
