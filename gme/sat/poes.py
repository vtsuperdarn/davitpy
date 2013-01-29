"""
.. module:: poes
   :synopsis: A module for reading, writing, and storing poes Data

.. moduleauthor:: AJ, 20130129

*********************
**Module**: gmi.sat.poes
*********************
**Classes**:
	* :class:`poesRec`
**Functions**:
	* :func:`readOmni`
	* :func:`readOmniFtp`
	* :func:`mapOmniMongo`
"""

import gme
class poesRec(gme.base.gmeBase.gmeData):
	"""a class to represent a record of poes data.  Extends gmeData.  Insight on the class members can be obtained from `the NOAA NGDC site <ftp://satdat.ngdc.noaa.gov/sem/poes/data/readme.txt>`_.  Note that Poes data is available from 1998-present day (or whatever the latest NOAA has uploaded is).
	"""
	
	
		def __init__(self, ftpLine=None, dbDict=None):
		#note about where data came from
		self.dataSet = 'Poes'
		self.info = 'These data were downloaded from NASA SPDF.  *Please be courteous and give credit to data providers when credit is due.*'
		self.satnum = None
		self.sslat = None
		self.sslon = None
		self.sslon = None
		self.folon = None
		self.lval = None
		self.mlt = None
		self.pas0 = None
		self.pas90 = None
		self.mep0e1 = None
		self.mep0e2 = None
		self.mep0e3 = None
		self.mep0p1 = None
		self.mep0p2 = None
		self.mep0p3 = None
		self.mep0p4 = None
		self.mep0p5 = None
		self.mep0p6 = None
		self.mep90e1 = None
		self.mep90e2 = None
		self.mep90e3 = None
		self.mep90p1 = None
		self.mep90p2 = None
		self.mep90p3 = None
		self.mep90p4 = None
		self.mep90p5 = None
		self.mep90p6 = None
		self.mepomp6 = None
		self.mepomp7 = None
		self.mepomp8 = None
		self.mepomp9 = None
		self.ted = None
		self.echar = None
		self.pchar = None
		self.econtr = None
		
		

		
		#if we're initializing from an object, do it!
		if(ftpLine != None): self.parseFtp(ftpLine)
		if(dbDict != None): self.parseDb(dbDict)