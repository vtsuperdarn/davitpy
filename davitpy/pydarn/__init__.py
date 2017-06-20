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


from __future__ import absolute_import
import logging

try:
	from . import dmapio
except Exception as e:
    logging.exception('problem importing dmapio: ' + str(e))

try:
	from . import radar
except Exception as e:
    logging.exception('problem importing radar: ' + str(e))

try:
	from . import sdio
except Exception as e:
    logging.exception('problem importing sdio: ' + str(e))

try:
	from . import plotting
except Exception as e:
    logging.exception('problem importing plotting: ' + str(e))

try:
	from . import proc
except Exception as e:
    logging.exception('problem importing proc: ' + str(e))
