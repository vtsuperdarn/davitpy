#include <Python.h>
#include <datetime.h>
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

#if PY_VERSION_HEX < 0x02050000
  typedef int Py_ssize_t;
#endif

static PyObject *
aacgm_wrap(PyObject *self, PyObject *args)
{
    
    double inlat, inlon, height, outLat, outLon, r; 
    int flg,year;
    
    if(!PyArg_ParseTuple(args, "dddii", &inlat,&inlon,&height,&year,&flg))
        return NULL;
    else
    {
        inlon = fmod(inlon, 360.);
        /*fprintf(stderr,"%d\n",year);*/
        AACGMInit(year);
        
        AACGMConvert(inlat, inlon, height, &outLat, &outLon, &r, flg);
        /*fprintf(stderr,"in\n");*/
        return Py_BuildValue("ddd", outLat, outLon, r);
    }
    
}

static PyObject *
aacgm_arr_wrap(PyObject *self, PyObject *args)
{
    
    PyObject *latList;
    PyObject *lonList;
    PyObject *heightList;
    double inlat, inlon, height, outLat, outLon, r; 
    int year, flg;
    Py_ssize_t nElem, i;
    
    if(!PyArg_ParseTuple(args, "OOOii", &latList,&lonList,&heightList,&year,&flg))
        return NULL;
    else
    {
        /* get the number of lines passed to us */
        nElem = PyList_Size(latList);
        /* should raise an error here. */
        if (nElem < 0)  return NULL; /* Not a list */
        
        PyObject *latOut = PyList_New(0);
        PyObject *lonOut = PyList_New(0);
        PyObject *heightOut = PyList_New(0);
        AACGMInit(year);
        for (i=0; i<nElem; i++) {
            inlat = PyFloat_AsDouble( PyList_GetItem(latList, i) );
            inlon = PyFloat_AsDouble( PyList_GetItem(lonList, i) );
            inlon = fmod(inlon, 360.);
            height = PyFloat_AsDouble( PyList_GetItem(heightList, i) );
            AACGMConvert(inlat, inlon, height, &outLat, &outLon, &r, flg);

            PyList_Append(latOut, PyFloat_FromDouble(outLat)); 
            PyList_Append(lonOut, PyFloat_FromDouble(outLon));
            PyList_Append(heightOut, PyFloat_FromDouble(r)); 
        }
        
        // PyObject *outList = PyList_New(0);
        
        // PyList_Append(outList,PyFloat_FromDouble(outLat)); 
        // PyList_Append(outList,PyFloat_FromDouble(outLon));
        // PyList_Append(outList,PyFloat_FromDouble(height)); 
         
        return Py_BuildValue("OOO", latOut, lonOut, heightOut);
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
/*
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
*/
static PyMethodDef aacgmMethods[] = 
{
    {"aacgmConv",  aacgm_wrap, METH_VARARGS, "convert to aacgm coords\nformat: lat, lon, r = aacgmConv(inLat, inLon, height, year, flg)\nheight in km; flg=0: geo to aacgm; flg=1: aacgm to geo"},
    {"aacgmConvArr",  aacgm_arr_wrap, METH_VARARGS, "convert to aacgm coords when inputs are lists\nformat: lat, lon, r = aacgmConvArr(inLatList, inLonList, heightList, year, flg)\nflg=0: geo to aacgm, flg=1: aacgm to geo"},
    {"mltFromEpoch",  MLTConvertEpoch_wrap, METH_VARARGS, "calculate mlt from epoch time and mag lon\nformat:mlt=mltFromEpoch(epoch,mLon)"},
    {"mltFromYmdhms",  MLTConvertYMDHMS_wrap, METH_VARARGS, "calculate mlt from y,mn,d,h,m,s and mag lon\nformat:mlt=mltFromYmdhms(yr,mo,dy,hr,mt,sc,mLon)"},
    {"mltFromYrsec", MLTConvertYrsec_wrap , METH_VARARGS, "calculate mlt from yr seconds and mag lon\nformat:mlt=mltFromEpoch(year,yrsec,mLon)"},
//  {"rPosAzm",  rposazm_wrap, METH_VARARGS, "wraper for rpos, MAY NOT be right\nformat:pos=rPosAzm(bm,rng,stid,eTime,frang,rsep,rx,height,magflg)"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initaacgm(void)
{
    (void) Py_InitModule("aacgm", aacgmMethods);
}
