#include <stdio.h>

/*****************************************************************************
 * Author: Angeline G. Burrell, UTDallas, April 2017
 *
 * Comments: python wrapper to AACGM functions based on test_aacgm.c
 *           Based on wrapper built by C. Meeren
 *
 * References: Shepherd, S. G. (2014), Altitude‐adjusted corrected geomagnetic
 *             coordinates: Definition and functional approximations, Journal
 *             of Geophysical Research: Space Physics, 119, p 7501-7521, 
 *             doi:10.1002/2014JA020264
 *****************************************************************************/

#include <Python.h>

#include "aacgmlib_v2.h"
#include "mlt_v2.h"

PyObject *module;

static PyObject *aacgm_v2_setdatetime(PyObject *self, PyObject *args)
{
  int year, month, day, hour, minute, second, err;

  char *root;

  /* Parse the input as a tupple */
  if(!PyArg_ParseTuple(args, "iiiiiis", &year, &month, &day, &hour, &minute,
		       &second, &root))
    return(NULL);

  /* Call the AACGM routine */
  err = AACGM_v2_SetDateTime(year, month, day, hour, minute, second, root);

  if(err < 0)
    {
      PyErr_Format(PyExc_RuntimeError,
		   "AACGM_v2_SetDateTime returned error code %d", err);
      return(NULL);
    }

  Py_RETURN_NONE;
}

static PyObject *aacgm_v2_convert(PyObject *self, PyObject *args)
{
  int code, err;

  double in_lat, in_lon, in_h, out_lat, out_lon, out_r;

  char *igrf_file;

  /* Parse the input as a tupple */
  if(!PyArg_ParseTuple(args, "dddis", &in_lat, &in_lon, &in_h, &code,
		       &igrf_file))
    return(NULL);

  /* Call the AACGM routine */
  err = AACGM_v2_Convert(in_lat, in_lon, in_h, &out_lat, &out_lon, &out_r,
			 code, igrf_file);

  if(err < 0)
    {
      PyErr_Format(PyExc_RuntimeError,
		   "AACGM_v2_Convert returned error code %d", err);
      return(NULL);
    }

  return Py_BuildValue("ddd", out_lat, out_lon, out_r);
}

static PyObject *mltconvert_v2(PyObject *self, PyObject *args)
{ 
  int yr, mo, dy, hr, mt, sc;

  double mlon, mlt;

  char *igrf_file, *root;

  /* Parse the input as a tupple */
  if(!PyArg_ParseTuple(args, "iiiiiidss", &yr, &mo, &dy, &hr, &mt, &sc, &mlon,
		       &root, &igrf_file))
    return(NULL);

  /* Call the AACGM routine */
  mlt = MLTConvert_v2(yr, mo, dy, hr, mt, sc, mlon, root, igrf_file);
    
  return Py_BuildValue("d", mlt);
}

static PyObject *mltconvert_yrsec_v2(PyObject *self, PyObject *args)
{
  int yr, yr_sec;

  double mlon, mlt;

  char *igrf_file, *root;

  /* Parse the input as a tupple */
  if(!PyArg_ParseTuple(args, "iidss", &yr, &yr_sec, &mlon, &root, &igrf_file))
    return(NULL);

  /* Call the AACGM routine */
  mlt = MLTConvertYrsec_v2(yr, yr_sec, mlon, root, igrf_file);

  return Py_BuildValue("d", mlt);
}

static PyObject *inv_mltconvert_v2(PyObject *self, PyObject *args)
{ 
  int yr, mo, dy, hr, mt, sc;

  double mlon, mlt;

  char *igrf_file;

  /* Parse the input as a tupple */
  if(!PyArg_ParseTuple(args, "iiiiiids", &yr, &mo, &dy, &hr, &mt, &sc, &mlt,
		       &igrf_file))
    return(NULL);

  /* Call the AACGM routine */
  mlon = inv_MLTConvert_v2(yr, mo, dy, hr, mt, sc, mlt, igrf_file);
    
  return Py_BuildValue("d", mlon);
}

static PyObject *inv_mltconvert_yrsec_v2(PyObject *self, PyObject *args)
{
  int yr, yr_sec;

  double mlon, mlt;

  char *igrf_file;

  /* Parse the input as a tupple */
  if(!PyArg_ParseTuple(args, "iidss", &yr, &yr_sec, &mlt, &igrf_file))
    return(NULL);

  /* Call the AACGM routine */
  mlon = inv_MLTConvertYrsec_v2(yr, yr_sec, mlt, igrf_file);

  return Py_BuildValue("d", mlon);
}

static PyMethodDef aacgm_v2_methods[] = {
  { "set_datetime", aacgm_v2_setdatetime, METH_VARARGS,
    "set_datetime(year, month, day, hour, minute, second, root)\n\
\n\
Sets the date and time for the IGRF magnetic field.\n\
\n\
Parameters \n\
-------------\n\
year : (int)\n\
    Four digit year starting from 1900, ending 2020\n\
month : (int)\n\
    Month of year ranging from 1-12\n\
day : (int)\n\
    Day of month (1-31)\n\
hour : (int)\n\
    Hour of day (0-23)\n\
minute : (int)\n\
    Minute of hour (0-59)\n\
second : (int)\n\
    Seconds of minute (0-59)\n\
root : (str)\n\
    AACGM coefficient filename root\n\
    (e.g. /davitpydir/tables/aacgm/aacgm_coeffs-12-)\n\
\n\
Returns\n\
-------------\n\
Void\n" },
  { "convert", aacgm_v2_convert, METH_VARARGS,
    "convert(in_lat, in_lon, height, code, igrf_file)\n\
\n\
Converts between geographic/dedic and magnetic coordinates.\n\
\n\
Parameters\n\
-------------\n\
in_lat : (float)\n\
    Input latitude in degrees N (code specifies type of latitude)\n\
in_lon : (float)\n\
    Input longitude in degrees E (code specifies type of longitude)\n\
height : (float)\n\
    Altitude above the surface of the earth in km\n\
code : (int)	\n\
    Bitwise code for passing options into converter (default=0)\n\
    0  - G2A        - geographic (geodetic) to AACGM-v2	\n\
    1  - A2G        - AACGM-v2 to geographic (geodetic)	\n\
    2  - TRACE      - use field-line tracing, not coefficients\n\
    4  - ALLOWTRACE - use trace only above 2000 km\n\
    8  - BADIDEA    - use coefficients above 2000 km\n\
    16 - GEOCENTRIC - assume inputs are geocentric w/ RE=6371.2\n\
igrf_file : (str)\n\
    Full filename of IGRF coefficient file\n\
\n\
Returns	\n\
-------\n\
out_lat : (float)\n\
    Output latitude in degrees\n\
out_lon : (float)\n\
    Output longitude in degrees\n\
out_r : (float)\n\
    Geocentric radial distance in Re\n", },
  {"mlt_convert", mltconvert_v2, METH_VARARGS,
    "mlt_convert(yr, mo, dy, hr, mt, sc, mlon, root, igrf_file)\n\
\n\
Converts from universal time to magnetic local time.\n\
\n\
Parameters\n\
-------------\n\
yr : (int)\n\
    4 digit integer year (1900-2020)\n\
mo : (int)\n\
    Month of year (1-12)\n\
dy : (int)\n\
    Day of month (1-31)\n\
hr : (int)\n\
    hours of day (0-23)\n\
mt : (int)\n\
    Minutes of hour (0-59)\n\
sc : (int)\n\
    Seconds of minute (0-59)\n\
mlon : (float)\n\
    Magnetic longitude\n\
root : (str)\n\
    Root of the AACGM coefficient files\n\
    (e.g. /davitpydir/tables/aacgm/aacgm_coeffs-12-)\n\
igrf_file : (str)\n\
    Full filename of IGRF coefficient file\n\
\n\
Returns	\n\
-------\n\
mlt : (float)\n\
    Magnetic local time (hours)\n" },

  {"mlt_convert_yrsec", mltconvert_yrsec_v2, METH_VARARGS,
    "mlt_convert_yrsec(yr, yr_sec, mlon, root, igrf_file)\n\
\n\
Converts from universal time to magnetic local time.\n\
\n\
Parameters\n\
-------------\n\
yr : (int)\n\
    4 digit integer year (1900-2020)\n\
yr_sec : (int)\n\
    Seconds of year (0-31622400)\n\
mlon : (float)\n\
    Magnetic longitude\n\
root : (str)\n\
    Root of the AACGM coefficient files\n\
    (e.g. /davitpydir/tables/aacgm/aacgm_coeffs-12-)\n\
igrf_file : (str)\n\
    Full filename of IGRF coefficient file\n\
\n\
Returns	\n\
-------\n\
mlt : (float)\n\
    Magnetic local time (hours)\n" },
  {"inv_mlt_convert", inv_mltconvert_v2, METH_VARARGS,
    "inv_mlt_convert(yr, mo, dy, hr, mt, sc, mlt, igrf_file)\n\
\n\
Converts from universal time and magnetic local time to magnetic longitude.\n\
\n\
Parameters\n\
-------------\n\
yr : (int)\n\
    4 digit integer year (1900-2020)\n\
mo : (int)\n\
    Month of year (1-12)\n\
dy : (int)\n\
    Day of month (1-31)\n\
hr : (int)\n\
    hours of day (0-23)\n\
mt : (int)\n\
    Minutes of hour (0-59)\n\
sc : (int)\n\
    Seconds of minute (0-59)\n\
mlt : (float)\n\
    Magnetic local time\n\
igrf_file : (str)\n\
    Full filename of IGRF coefficient file\n\
\n\
Returns	\n\
-------\n\
mlon : (float)\n\
    Magnetic longitude (degrees)\n" },

  {"inv_mlt_convert_yrsec", inv_mltconvert_yrsec_v2, METH_VARARGS,
    "inv_mlt_convert_yrsec(yr, yr_sec, mlt, igrf_file)\n\
\n\
Converts from universal time and magnetic local time to magnetic longitude.\n\
\n\
Parameters\n\
-------------\n\
yr : (int)\n\
    4 digit integer year (1900-2020)\n\
yr_sec : (int)\n\
    Seconds of year (0-31622400)\n\
mlt : (float)\n\
    Magnetic local time\n\
igrf_file : (str)\n\
    Full filename of IGRF coefficient file\n\
\n\
Returns	\n\
-------\n\
mlon : (float)\n\
    Magnetic longitude (degrees)\n" },
  { NULL, NULL, 0, NULL }
};

/* Different versions of python require different constant declarations */

#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef aacgm_module = {
    PyModuleDef_HEAD_INIT,
    "aacgm",   /* name of module */
    "Interface to the AACGM-v2 C library.", /* module documentation */
    -1, /* size of per-interpreter state of the module,
	   or -1 if the module keeps state in global variables. */
    aacgm_v2_methods
  };

  PyMODINIT_FUNC PyInit_aacgm(void)
  {
    module = PyModule_Create(&aacgm_module);
    PyModule_AddIntConstant(module, "G2A", G2A);
    PyModule_AddIntConstant(module, "A2G", A2G);
    PyModule_AddIntConstant(module, "TRACE", TRACE);
    PyModule_AddIntConstant(module, "ALLOWTRACE", ALLOWTRACE);
    PyModule_AddIntConstant(module, "BADIDEA", BADIDEA);
    PyModule_AddIntConstant(module, "GEOCENTRIC", GEOCENTRIC);
    return module;
  }

#else

  PyMODINIT_FUNC initaacgm(void)
  {
    module = Py_InitModule("aacgm", aacgm_v2_methods);
    PyModule_AddIntConstant(module, "G2A", G2A);
    PyModule_AddIntConstant(module, "A2G", A2G);
    PyModule_AddIntConstant(module, "TRACE", TRACE);
    PyModule_AddIntConstant(module, "ALLOWTRACE", ALLOWTRACE);
    PyModule_AddIntConstant(module, "BADIDEA", BADIDEA);
    PyModule_AddIntConstant(module, "GEOCENTRIC", GEOCENTRIC);
  }

#endif
