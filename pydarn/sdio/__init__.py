# I/O module __init__.py
"""
*******************************
            IO
*******************************
This subpackage contains various I/O routines for DaViT-py
DEV: functions/modules/classes with a * have not been developed yet

This includes the following module(s):
	radDataTypes
		defines the fundamental radar data types
	radDataRead
		contains the functions necessary for reading radar data
	pygridIo
		library for reading and writing pygrid files
	dbUtils
		general utilities for database maintenance
	dbRead
		library for reading records from the database


*******************************
"""
try:
	import radDataTypes
	from radDataTypes import *
except: print 'problem importing radDataTypes'
	
try:
	import radDataRead
	from radDataRead import *
except: print 'problem importing radDataRead'
	
try:
	import pygridIo
	from pygridIo import *
except: print 'problem importing pygridIo'
	
try:
	import dbUtils
	from dbUtils import *
except Exception,e: 
	print 'problem importing dbUtils: ', e