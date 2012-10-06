import numpy as np
from models import iri

# Inputs
jf = np.ones(50)
jf[3:5] = 0
jf[20] = 0
jf[22] = 0
jf[27:29] = 0
jf[32] = 0
jf[34] = 0
jmag = 0.
alati = 40.
along = -80.
iyyyy = 2012
mmdd = 806
dhour = 12.
heibeg, heiend, heistp = 80., 500., 10.
oarr = np.zeros(100)
# Call fortran subroutine
oarr = iri.iri_sub(jf,jmag,alati,along,iyyyy,mmdd,dhour,heibeg,heiend,heistp,oarr)
print 'IRI has run'
