# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
"""
*********************
**Module**: davipty
*********************
Module for everything SuperDARN

**Modules**:
    * :mod:`davipty.pydarn`: superdarn data I/O and plotting utilities
"""

rc_params = {'test':'It worked!'}

try: from davitpy import pydarn
except Exception, e: 
  print 'problem importing pydarn: ', e

try: from davitpy import gme 
except Exception, e: 
  print 'problem importing gme: ', e

try: from davitpy import utils 
except Exception, e: 
  print 'problem importing utils: ', e

try: from davitpy import models 
except Exception, e: 
  print 'problem importing models: ', e


