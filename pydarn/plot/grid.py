import pydarn,numpy
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection

def plotGrid():
	
	myGrid = pydarn.proc.grid()
	myFig = plt.figure()
	myMap = pydarn.plot.map(boundingLat=30, grid=False)	
	
	verts=[]
	
	for i in range(0,myGrid.nLats):
		for j in range(0,myGrid.lats[i].nCells):

			x1,y1 = myMap(myGrid.lats[i].cells[j].bl[1]*360./24.,myGrid.lats[i].cells[j].bl[0])
			x2,y2 = myMap(myGrid.lats[i].cells[j].tl[1]*360./24.,myGrid.lats[i].cells[j].tl[0])
			x3,y3 = myMap(myGrid.lats[i].cells[j].tr[1]*360./24.,myGrid.lats[i].cells[j].tr[0])
			x4,y4 = myMap(myGrid.lats[i].cells[j].br[1]*360./24.,myGrid.lats[i].cells[j].br[0])
			
			verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))
			
			
	pcoll = PolyCollection(numpy.array(verts),edgecolors='k',facecolors='none',linewidths=.3,closed=False,zorder=5)
	
	myFig.gca().add_collection(pcoll)
	
	
	
	
	
	myFig.show()