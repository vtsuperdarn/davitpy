# Main DaViT-py module __init__.py
"""
*******************************
            pydarn
*******************************
Module for everything SuperDARN

This includes the following submodules:
  * **sdio**: SuperDARN data I/O
  * **radar**:SuperDARN radars information
  * **plot**: plotting routines
  * **proc**: misc
  * **utils**: general utilities

*******************************
"""

try: import dmapio 
except Exception, e: 
  print 'problem importing dmapio: ', e

try: import radar 
except Exception, e: 
  print 'problem importing radar: ', e

try: import sdio 
except Exception, e: 
  print 'problem importing sdio: ', e

try: import plotting 
except Exception, e: 
  print 'problem importing plotting: ', e

try: import proc 
except Exception, e: 
  print 'problem importing proc: ', e

try: import tools 
except Exception, e: 
  print 'problem importing proc: ', e

