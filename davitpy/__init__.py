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

try: import pydarn 
except Exception, e: 
  print 'problem importing pydarn: ', e

try: import gme 
except Exception, e: 
  print 'problem importing gme: ', e

try: import utils 
except Exception, e: 
  print 'problem importing utils: ', e

try: import models 
except Exception, e: 
  print 'problem importing models: ', e


