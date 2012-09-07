#include <Python.h>
#include <datetime.h>
#include <zlib.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <math.h>
#include "rtime.h"
#include "aacgm.h"
#include "mlt.h"
#include "AstAlg.h"

static PyObject *
aacgm_wrap(PyObject *self, PyObject *args)
{
	double inLat,inLon,height,outLat,outLon,r; 
	int flg;
	
	if(!PyArg_ParseTuple(args, "dddi", &inLat,&inLon,&height,&flg))
		return NULL;
	else
	{
		/* get inlat from the list*/
		AACGMConvert(inLat,inLon,height,&outLat,&outLon,&r,flg);
		
		PyObject *outList = PyList_New(0);
		
		PyList_Append(outList,PyFloat_FromDouble(outLat)); 
		PyList_Append(outList,PyFloat_FromDouble(outLon));
		PyList_Append(outList,PyFloat_FromDouble(height)); 
		 
		return outList;
	}
	
}
 
static PyObject *
MLTConvertYMDHMS_wrap(PyObject *self, PyObject *args)
{
	double mLon,mlt;
	int yr,mo,dy,hr,mt,sc;
	
	if(!PyArg_ParseTuple(args, "iiiiiid", &yr,&mo,&dy,&hr,&mt,&sc,&mLon))
		return NULL;
	else
	{ 
		mlt = MLTConvertYMDHMS(yr,mo,dy,hr,mt,sc,mLon); 
		return PyFloat_FromDouble(mlt);
	}
	
}

static PyObject *
MLTConvertEpoch_wrap(PyObject *self, PyObject *args)
{
	double mLon,mlt,epoch;
	
	if(!PyArg_ParseTuple(args, "dd", &epoch,&mLon))
		return NULL;
	else
	{ 
		mlt = MLTConvertEpoch(epoch,mLon); 
		return PyFloat_FromDouble(mlt);
	}
	
}

static PyObject *
MLTConvertYrsec_wrap(PyObject *self, PyObject *args)
{
	double mLon,mlt;
	int yrSec,yr;
	
	if(!PyArg_ParseTuple(args, "iid", &yr,&yrSec,&mLon)) 
		return NULL;
	else
	{
		mlt = MLTConvertYrsec(yr,yrSec,mLon); 
		return PyFloat_FromDouble(mlt);
	}

}

static PyMethodDef aacgmMethods[] = 
{
	{"aacgmConv",  aacgm_wrap, METH_VARARGS, "convert to aacgm coords\nformat: [lat,lon,lt]=aacgmConv(inLat,inLon,height,flg)\nflg=0: geo to aacgm, flg=1: aacgm to geo"},
 	{"mltFromEpoch",  MLTConvertEpoch_wrap, METH_VARARGS, "calculate mlt from epoch time and mag lon\nformat:mlt=mltFromEpoch(epoch,mLon)"},
	{"mltFromYmdhms",  MLTConvertYMDHMS_wrap, METH_VARARGS, "calculate mlt from y,mn,d,h,m,s and mag lon\nformat:mlt=mltFromYmdhms(yr,mo,dy,hr,mt,sc,mLon)"},
 	{"mltFromYrsec", MLTConvertYrsec_wrap , METH_VARARGS, "calculate mlt from yr seconds and mag lon\nformat:mlt=mltFromEpoch(year,yrsec,mLon)"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initaacgmlib(void)
{
	(void) Py_InitModule("aacgmlib", aacgmMethods);
}