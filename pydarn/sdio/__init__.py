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
	fitexfilter
		functions to filter fitex data
	dbUtils
		general utilities for database maintenance
	fetchUtils
		functions to retrieve remote or local files

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
	import sdDataTypes
	from sdDataTypes import *
except: print 'problem importing sdDataTypes'
	
try:
	import sdDataRead
	from sdDataRead import *
except Exception,e: 
	print e
	print 'problem importing sdDataRead'
	
# try:
# 	import pygridIo
# 	from pygridIo import *
# except: print 'problem importing pygridIo'

try:
	import fitexfilter
	from fitexfilter import *
except Exception,e: 
	print e
	print 'problem importing fitexfilter'
	
try:
	import dbUtils
	from dbUtils import *
except Exception,e: 
	print 'problem importing dbUtils: ', e

try:
	import fetchUtils
	from fetchUtils import *
except Exception,e: 
	print 'problem importing fetchUtils: ', e
