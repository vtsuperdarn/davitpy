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
#include "invmag.h"
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

static PyObject * 
rposazm_wrap(PyObject *self, PyObject *args)
{
	double lat,lon,azm,eTime,frang,rsep,rx,height,sc,elv;
	int bm,rng,yr,mo,dy,hr,mt,stid,magflg=0; 
	
	if(!PyArg_ParseTuple(args, "iiidddddi", &bm,&rng,&stid,&eTime,&frang,&rsep,&rx,&height,&magflg)) 
		return NULL;
	else
	{ 
		
		struct RadarNetwork *network;  
		struct Radar *radar;
		struct RadarSite *site;
		FILE * fp;
		
		char *envstr;
		
		envstr=getenv("SD_RADAR");
		if (envstr==NULL) 
		{
			fprintf(stderr,"Environment variable 'SD_RADAR' must be defined.\n");
			exit(-1);
		}

		fp=fopen(envstr,"r");

		if (fp==NULL) 
		{
			fprintf(stderr,"Could not locate radar information file.\n");
			exit(-1);
		}

		network=RadarLoad(fp);
		fclose(fp); 
		if (network==NULL) 
		{
			fprintf(stderr,"Failed to read radar information.\n");
			exit(-1);
		}

		envstr=getenv("SD_HDWPATH");
		if (envstr==NULL) 
		{
			fprintf(stderr,"Environment variable 'SD_HDWPATH' must be defined.\n");
			exit(-1);
		}

		RadarLoadHardware(envstr,network);
			
		radar=RadarGetRadar(network,stid);
		if (radar==NULL)
		{
			fprintf(stderr,"Failed to get radar information.\n");
			return NULL;
		}
		TimeEpochToYMDHMS(eTime,&yr,&mo,&dy,&hr,&mt,&sc);
		
		site=RadarYMDHMSGetSite(radar,yr,mo,dy,hr,mt,(int)sc);
						
		
		if(magflg)
			RPosInvMag(bm,rng,yr,site,frang,rsep,rx,height,&lat,&lon,&azm);
		else
		{
			RPosGeo(1,bm,rng,site,(int)(frang/.15),(int)(rsep/.15),(int)rx,height,&azm,&lat,&lon);
			RPosRngBmAzmElv(bm,rng,yr,site,frang,rsep,rx,height,&azm,&elv);
		}
		
		PyObject *outList = PyList_New(0);
		PyList_Append(outList,PyFloat_FromDouble(lat)); 
		PyList_Append(outList,PyFloat_FromDouble(lon));
		PyList_Append(outList,PyFloat_FromDouble(azm)); 
		 
		return outList;
	}

}

static PyMethodDef aacgmMethods[] = 
{
	{"aacgmConv",  aacgm_wrap, METH_VARARGS, "convert to aacgm coords\nformat: [lat,lon,lt]=aacgmConv(inLat,inLon,height,flg)\nflg=0: geo to aacgm, flg=1: aacgm to geo"},
 	{"mltFromEpoch",  MLTConvertEpoch_wrap, METH_VARARGS, "calculate mlt from epoch time and mag lon\nformat:mlt=mltFromEpoch(epoch,mLon)"},
	{"mltFromYmdhms",  MLTConvertYMDHMS_wrap, METH_VARARGS, "calculate mlt from y,mn,d,h,m,s and mag lon\nformat:mlt=mltFromYmdhms(yr,mo,dy,hr,mt,sc,mLon)"},
 	{"mltFromYrsec", MLTConvertYrsec_wrap , METH_VARARGS, "calculate mlt from yr seconds and mag lon\nformat:mlt=mltFromEpoch(year,yrsec,mLon)"},
 	{"rPosAzm",  rposazm_wrap, METH_VARARGS, "wraper for rpos\nformat:pos=rPosAzm(bm,rng,stid,eTime,frang,rsep,rx,height,magflg)"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initaacgmlib(void)
{
	(void) Py_InitModule("aacgmlib", aacgmMethods);
}