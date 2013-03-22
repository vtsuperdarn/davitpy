#%connect_info
import numpy as np
import scipy as sp
import matplotlib.pyplot as mp

import pydarn
import pydarn.proc.music as music
import utils

msc = music.music()
msc.params

myPtr = pydarn.sdio.radDataOpen(
    (msc.params['datetime'])[0],
    msc.params['radar'],
    eTime=(msc.params['datetime'])[1],
    channel=msc.params['channel'],
    bmnum=msc.params['bmnum'],
    filtered=msc.options['filtered'])

myScan = pydarn.sdio.radDataReadScan(myPtr)


