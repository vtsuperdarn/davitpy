# Main DaViT-py module __init__.py
"""
*******************************
            DARNpy
*******************************
Main DaViT-py module

This includes the following submodules:
	io
		SuperDARN data I/O
	radar
		SuperDARN radars information
	plot
		
	proc
	utils

*******************************
"""

try: import dmapio 
except: 'problem importing dmapio'

try: import radar 
except: 'problem importing radar'

try: import sdio 
except: 'problem importing sdio'

try: import plot 
except: 'problem importing plot'

try: import proc 
except: 'problem importing proc'

