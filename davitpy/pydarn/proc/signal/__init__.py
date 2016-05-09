# -*- coding: utf-8 -*-
# Waver module __init__.py
"""
Subpackage
----------
pydarn.proc.signal
    This subpackage contains various utilities for SIGNAL,
    the SuperDARN Signal Processing and Analysis Software Package.

"""

from signal import *
from sigproc import *
from compare import *
from xcor import *

# Define a few general-use constants
# Mean Earth radius [km]
Re = 6371.0
# Polar Earth radius [km]
RePol = 6378.1370
# Equatorial Earth radius [km]
ReEqu = 6356.7523
