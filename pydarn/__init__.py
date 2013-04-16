# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: pydarn
*********************
Module for everything SuperDARN

**Modules**:
    * :mod:`pydarn.sdio`: superdarn data I/O
    * :mod:`pydarn.radar`: radar structures and utilities
    * :mod:`pydarn.plotting`: radar plotting utilities
    * :mod:`pydarn.proc`: adanced data processing utilities

"""

try: import dmapio 
except Exception, e: 
	print 'problem importing pydarn.dmapio: ', e

try: import radar 
except Exception, e: 
	print 'problem importing pydarn.radar: ', e

try: import sdio 
except Exception, e: 
	print 'problem importing pydarn.sdio: ', e

try: import plotting 
except Exception, e: 
	print 'problem importing pydarn.plotting: ', e

try: import proc 
except Exception, e: 
	print 'problem importing pydarn.proc: ', e

