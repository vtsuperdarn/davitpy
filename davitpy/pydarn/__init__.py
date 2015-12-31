# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
pydarn
------

Module for everything SuperDARN

Modules
-------------------------------------------
sdio     superdarn data I/O
radar    radar structures and utilities
plotting radar plotting utilities
proc     adanced data processing utilities
-------- ----------------------------------

"""

import logging

try:
	import dmapio
except Exception, e:
    logging.exception('problem importing dmapio: ' + e)

try:
	import radar
except Exception, e:
    logging.exception('problem importing radar: ' + e)

try:
	import sdio
except Exception, e:
    logging.exception('problem importing sdio: ' + e)

try:
	import plotting
except Exception, e:
    logging.exception('problem importing plotting: ' + e)

try:
	import proc
except Exception, e:
    logging.exception('problem importing proc: ' + e)