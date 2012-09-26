def davitpydoc():
	
	import os,string
	docPath = '/davitpy/sphinx'
	projPath = '/davitpy'
	
	f = open(docPath+'/index_backup.rst','r')
	index = f.readlines()
	f.close()
	ind = index.index('   :maxdepth: 2\n')
	ind = ind+1
	
	
	exclude = ['.git','sphinx','docs','install','bin','temp.linux-x86_64-2.7']
	for root, dirs, files in os.walk('/davitpy'):
		for name in dirs:
			
			cflg = 0
			for e in exclude:
				if(string.find(root+'/'+name+'/','/'+e+'/') != -1): cflg = 1
			if(cflg): continue
			
			if(root == '/davitpy'):
				if(not '   '+name+'\n' in index):
					index.insert(ind,'\n   '+name+'\n')
					ind = ind+1
					
			else:
				rlist = root.split('/')
				parent = rlist[len(rlist)-1]
				
				f = open(docPath+'/'+parent+'.rst','r')
				plines = f.readlines()
				f.close()
				ind = plines.index('   :maxdepth: 2\n')
				ind = ind+1
				if(not '   '+name+'\n' in plines):
					plines.insert(ind,'\n   '+name+'\n')
					f = open(docPath+'/'+parent+'.rst','w')
					f.writelines(plines)
					f.close()
				
				
			f = open(docPath+'/'+name+'.rst','w')
			f.write(string.replace(root, '/davitpy', '')+'/'+name+'\n')
			f.write('============================\n')
			f.write('.. toctree::\n')
			f.write('   :maxdepth: 2\n')
			f.close
			
			print root,name
			
			
		for name in files:
			cflg = 0
			if(root == '/davitpy' or name == '__init__.py' or name == 'setup.py'): continue
			if(os.path.splitext(name)[1] != '.py'): continue
			for e in exclude:
				if(string.find(root+'/','/'+e+'/') != -1): cflg = 1
			if(cflg == 1): continue
			
			rlist = root.split('/')
			parent = rlist[len(rlist)-1]
			f = open(docPath+'/'+parent+'.rst','r')
			plines = f.readlines()
			f.close()
		
			ind = plines.index('   :maxdepth: 2\n')
			ind = ind+1
			if(not '   '+name+'\n' in plines):
				plines.insert(ind,'\n   '+string.replace(name, '.py', '')+'\n')
				f = open(docPath+'/'+parent+'.rst','w')
				f.writelines(plines)
				f.close()
			
				
			f = open(docPath+'/'+string.replace(name, '.py', '')+'.rst','w')
			f.write(string.replace(root, '/davitpy', '')+'/'+name+'\n')
			f.write('============================\n')
			f.write('.. toctree::\n')
			f.write('   :maxdepth: 2\n')
			f.write('\n.. automodule:: '+string.replace(name, '.py', '')+'\n')
			f.write('   :members:\n')
			f.write('\n.. autoclass:: '+string.replace(name, '.py', '')+'\n')
			f.write('   :members:\n')
			f.close
			
			
			
			#if(not '.. automodule:: '+string.replace(name, '.py', '')+'\n' in plines):
				#ind = plines.index('   :maxdepth: 2\n')
				#ind = ind+1
				#plines.insert(ind,'\n.. automodule:: '+string.replace(name, '.py', '')+'\n')
				#ind += 1
				#plines.insert(ind,'   :members:\n')
				#f = open(docPath+'/'+parent+'.rst','w')
				#f.writelines(plines)
				#f.close()
			os.system('ln -s '+root+'/'+name+' '+docPath+'/'+name)
					
				
			
		f = open(docPath+'/index.rst','w')
		f.writelines(index)
		f.close()
        
	
	

	#exclude = ['.git','doc','docs','install','bin']
	

	
	#dirs = []
	
	#for d in os.listdir(projPath):
		
		#if(not os.path.isdir(d)): 
			#ext = os.path.splitext(d)[1]
			#if(ext == '.py'): print d
			
		#elif(not d in exclude and not '   '+d+'\n' in lines):
			#lines.insert(ind+1,'   '+d+'\n')
			#ind = ind+1
			#print 'directory : '+d
			#dirs.append(d)
			
			#f = open(docPath+d+'.rst','w')
			#f.write(projPath+'/'+d+'\n')
			#f.write('==========\n')
			#f.write('.. toctree::\n')
			#f.write('   :maxdepth: 2\n')
			
	#f = open(docPath+'index.rst','w')
	#f.writelines(lines)
	#f.close()


