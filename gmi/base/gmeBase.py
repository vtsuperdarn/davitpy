"""
.. module:: gmeBase
   :synopsis: A base class for gme data.  Allows definition of common routines

.. moduleauthor:: AJ, 20130129

*********************
**Module**: gme.base.gmeBase
*********************
**Classes**:
	* :class:`gmeData`
**Functions**:
	* :func:`readData`
	* :func:`readOmniFtp`
	* :func:`mapOmniMongo`
"""
class omniRec:
	
	def parseDb(self,dbDict):
		"""This method is used to parse a dictionary of gme data from the mongodb into a :class:`omniRec` object.  
		
		.. note:: 
			In general, users will not need to use this.
		
		**Belongs to**: :class:`omniRec`
		
		**Args**: 
			* **dbDict** (dict): the dictionary from the mongodb
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myOmniObj.parseDb(mongoDbOmniDict)
			
		written by AJ, 20130128
		"""
		#iterate over the mongo dict
		for attr, val in dbDict.iteritems():
			#check for mongo _id attribute
			if(attr == '_id'): pass
			else:
				#assign the value to our object
				try: setattr(self,attr,val)
				except Exception,e:
					print e
					print 'problem assigning',attr