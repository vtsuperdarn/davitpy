import matplotlib,numpy
import matplotlib.pyplot as plot

def genCmap(fig,coll,param,scale,pos,cols='lasse'):

	"""
	******************************
	genCmap(fig,coll,param,scale,pos,[cols]):
	
	generates a colormap and plots a colorbar

	INPUTS:
		fig: the parent figure
		coll: the collection of items (e.g. polygons) being mapped 
			to this colormap
		param: the parameter being plotted, valid for 'velocity',
			'power', 'width'
		scale: the max and min values of the color scale in list form
		pos: the position of the parent plot, NOT of the COLORBAR
		[cols]: a string indicating which colorbar to use, valid 
			inputs are 'lasse', 'aj'
			default: 'lasse'
	OUTPUTS:

	EXAMPLE:
		genCmap(myFig,polyCollection,'velocity',[-200,200],pos)
		
	Written by AJ 20120820
	*******************************
	"""
	
	#the MPL colormaps we will be using
	cmj = matplotlib.cm.jet
	cmpr = matplotlib.cm.prism
	
	#check for a velocity plot
	if(param == 'velocity'):
		
		#check for what color scale we want to use
		if(cols == 'aj'):
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmpr(.142),cmpr(.125),cmpr(.11),cmpr(.1),\
			cmpr(.18),cmpr(.16),cmj(.32),cmj(.37)])
		else:
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmj(.9),cmj(.8),cmj(.7),cmj(.65),\
			cmpr(.142),cmj(.45),cmj(.3),cmj(.1)])
			
		#define the boundaries for color assignments
		bounds = numpy.round(numpy.linspace(scale[0],scale[1],7))
		bounds = numpy.insert(bounds,0,-9999999.)
		bounds = numpy.append(bounds,9999999.)
		norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
		
	#if its a non-velocity plot
	else:
		
		#check what color scale we want to use
		if(cols == 'aj'):
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmpr(.18),cmpr(.17),cmj(.32),cmj(.37),\
			cmpr(.142),cmpr(.13),cmpr(.11),cmpr(.10)])
		else:
			#define our discrete colorbar
			cmap = matplotlib.colors.ListedColormap([cmj(.1),cmj(.3),cmj(.45),cmpr(.142),\
			cmj(.65),cmj(.7),cmj(.8),cmj(.9)])
			
		#define the boundaries for color assignments
		bounds = numpy.round(numpy.linspace(scale[0],scale[1],8))
		bounds = numpy.append(bounds,9999999.)
		norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
		
	#set the colormap and boundaries for the collection
	#of plotted items
	coll.set_cmap(cmap)
	coll.set_norm(norm)
	
	
	#create a new axes for the colorbar
	cax = fig.add_axes([pos[0]+pos[2]+.03, pos[1], 0.03, pos[3]])
	cax.yaxis.set_tick_params(direction='out')
	cb = plot.colorbar(coll,cax=cax)
	
	l = []
	#define the colorbar labels
	for i in range(0,len(bounds)):
		if((i == 0 and param == 'velocity') or i == len(bounds)-1):
			l.append(' ')
			continue
		l.append(str(int(bounds[i])))
	cb.ax.set_yticklabels(l)
		
	#set colorbar ticklabel size
	for t in cb.ax.get_yticklabels():
		t.set_fontsize(9)
	
	#set colorbar label
	if(param == 'velocity'): cb.set_label('Velocity [m/s]',size=10)
	if(param == 'power'): cb.set_label('Power [dB]',size=10)
	if(param == 'width'): cb.set_label('Spec Wid [m/s]',size=10)
	
	return