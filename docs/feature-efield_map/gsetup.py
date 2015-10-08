"""
Initialize igrf model

Reads an input data file of IGRF coefficients and formats them for use in the emap
package. 

DATA:
flnm: path and file name of coefficients of csv file
yrlast: Integer. Latest year of model (second last column heading)
dyr: string. Heading of secular variation (SV) column.

NOTES:
When this module is first imported it is executed. The IGRF coefficients from 
the desired IGRF release are read and reformatted.

The reformatting involves separating the g and h coefficients and storing them in 
one dimensional arrays, gdata and hdata, with the same size. This involves explicitly 
inserting zeros in hdata so that the indexing of each array is the same.

Input data file:
This is a comma separated variable (csv) file of the coefficients.
The file supplied in the package is currently IGRF12 in the format supplied by the 
WDC for Solid Earth and Geophysics.

If other models are required the input file is best prepared by downloading the Excel 
file from http://www.ngdc.noaa.gov/IAGA/vmod/igrf.html and saving a csv version. 
For future IGRF releases ensure that the supplied format is unchanged. 


"""
import numpy as np
import pandas as pd
flnm = 'emap/igrf12coeffs.csv'
yrlast = 2015
dyr = '2015-20'
hmask = [0,1,3,6,10,15,21,28,36,45,55,66,78]
hval = np.zeros([13])
igrfdata = pd.read_csv(flnm,skiprows=1)
idx = igrfdata['g/h'].isin(['g'])
gdata = igrfdata[idx]
hdata = igrfdata[~idx]
ndata = igrfdata['n']
mdata = igrfdata['m']
nn = np.array(ndata[idx])
mm = np.array(mdata[idx])
