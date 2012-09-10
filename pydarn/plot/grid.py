import pydarn,numpy,utils
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from mpl_toolkits.basemap import Basemap

def plotGrid(myGrid=None,grid=1,vmax=500):
	
	if(myGrid == None): myGrid = pydarn.proc.grid()
	myFig = plt.figure()
	myMap = pydarn.plot.map(boundingLat=-.01, lon_0=0.,grid=False,fillContinents='none',fillLakes='none')	
	#myMap = Basemap(projection='aea',lat_0=0,lon_0=0,llcrnrlat=1,llcrnrlon=315,urcrnrlat=1,urcrnrlon=135)
	myMap.drawmeridians(numpy.arange(0,360,30))
	myMap.drawparallels([0,20,40,60,80])
	myMap.boundinglat=0.

	
	for i in [20,40,60,80]:
		x=myMap(2.,i+1)
		plt.text(x[0],x[1],str(i),fontweight='bold',fontsize=13.)
		
	ha = ['center','left','center','right']
	va = ['top','center','bottom','center']
	for i in numpy.arange(0,360,90):
		x=myMap(i,-1)
		plt.text(x[0],x[1],str(int(i/360.*24)),fontweight='bold',ha=ha[i/90],va=va[i/90])
	
	verts,lines=[],[]
	for i in range(0,myGrid.nLats):
		for j in range(0,myGrid.lats[i].nCells):

			if(grid):
				x1,y1 = myMap(myGrid.lats[i].cells[j].bl[1]*360./24.,myGrid.lats[i].cells[j].bl[0])
				x2,y2 = myMap(myGrid.lats[i].cells[j].tl[1]*360./24.,myGrid.lats[i].cells[j].tl[0])
				x3,y3 = myMap(myGrid.lats[i].cells[j].tr[1]*360./24.,myGrid.lats[i].cells[j].tr[0])
				x4,y4 = myMap(myGrid.lats[i].cells[j].br[1]*360./24.,myGrid.lats[i].cells[j].br[0])
				x,y = myMap(myGrid.lats[i].cells[j].center[1]*360./24.,myGrid.lats[i].cells[j].center[0])
				verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))
			
			if(myGrid.lats[i].cells[j].nVecs > 0):
				for k in range(0,myGrid.lats[i].cells[j].nVecs):
					print myGrid.lats[i].cells[j].vecs[k].v,myGrid.lats[i].cells[j].vecs[k].v/vmax
					ept = utils.geoPack.greatCircleMove(myGrid.lats[i].cells[j].center[0],\
					myGrid.lats[i].cells[j].center[1]*360./24.,myGrid.lats[i].cells[j].vecs[k].v/vmax*110e3,\
					myGrid.lats[i].cells[j].vecs[k].azm)
					
					x1,y1 = myMap(myGrid.lats[i].cells[j].center[1]*360./24., myGrid.lats[i].cells[j].center[0])
					x2,y2 = myMap(ept[1],ept[0])
					lines.append(((x1,y1),(x2,y2)))
			
	if(grid == 1):
		pcoll = PolyCollection(numpy.array(verts),edgecolors='k',facecolors='none',linewidths=.3,closed=False,zorder=5)
		myFig.gca().add_collection(pcoll)
	
	lcoll = LineCollection(numpy.array(lines),linewidths=.3)
	myFig.gca().add_collection(lcoll)
	
	
	
	
	
	myFig.show()