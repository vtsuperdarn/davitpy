# -*- coding: utf-8 -*-
# gmi/kp/kpDay
"""
*******************************
** 
Parse YYYYMMDD dates in YYYY, MM, DD and vice versa

Created by AJ
*******************************
"""

class kpDay:
	def __init__(self, d, vals):
		#the date of the Kp Indices
		self.date = d
		#the actual Kp indices
		self.vals = vals