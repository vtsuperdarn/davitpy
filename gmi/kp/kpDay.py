# -*- coding: utf-8 -*-
# gmi/kp/kpDay
"""
*******************************
** 
A class to contain a day of Kp data

Created by AJ
*******************************
"""

class kpDay:
	def __init__(self, d, vals):
		#the date of the Kp Indices
		self.day = d
		#the actual Kp indices
		self.vals = vals
		