/*
 * Copyright (C) 2012  VT SuperDARN Lab
 * Full license can be found in LICENSE.txt
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <stdio.h>
#include <Python.h>
#include <datetime.h>
#include <zlib.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include "rtypes.h"
#include "rtime.h"
#include "rconvert.h"
#include "dmap.h"
#include "structmember.h"
#include "rprm.h"
#include "fitdata.h"
#include "fitwrite.h"

/*
void parsePyPrm(struct RadarParm *prm, PyObject *pyprm)
{

}*/

static PyObject *
write_fit_rec(PyObject *self, PyObject *args)
{
  PyObject *pybeam, *f;
  double epoch;
  if(!PyArg_ParseTuple(args, "OdO", &pybeam,&epoch,&f))
    return NULL;
  else
  {
    /*declare variables*/
    PyObject *pyfit, *pyprm, *templist, *tempobj, *tempval;
    int size,i,yr,mo,dy,hr,mt, status, R;
    double sc;
    char * tempchar;
    FILE * fitfp = PyFile_AsFile(f);

    /*extract python objects*/
    tempval = Py_BuildValue("s", "fit");
    pyfit = PyObject_GetAttr(pybeam,tempval);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "prm");
    pyprm = PyObject_GetAttr(pybeam,tempval);
    Py_CLEAR(tempval);


    /*declare superdarn structures*/
    struct RadarParm *prm;
    prm=RadarParmMake();
    struct FitData *fit;
    fit=FitMake();

    time_t rawtime;
    struct tm * timeinfo;
    time (&rawtime);
    timeinfo = gmtime(&rawtime);
    RadarParmSetOriginTime(prm,asctime(timeinfo));
    RadarParmSetOriginCommand(prm,"masking data");
    TimeEpochToYMDHMS(epoch,&yr,&mo,&dy,&hr,&mt,&sc);
    prm->time.yr = (int16)yr;
    prm->time.mo = (int16)mo;
    prm->time.dy = (int16)dy;
    prm->time.hr = (int16)hr;
    prm->time.mt = (int16)mt;
    prm->time.sc = (int16)sc;
    prm->time.us = (int16)((sc-(int16)sc)*1e6);


    tempval = Py_BuildValue("s", "cp");
    tempobj = PyObject_GetAttr(pybeam,tempval);
    prm->cp = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "nrang");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->nrang = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "nave");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->nave = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "lagfr");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->lagfr = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "smsep");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->smsep = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    prm->txpow = 9000;
    prm->atten = 0;
    prm->ercod = 0;
    prm->stat.agc = 0;
    prm->stat.lopwr = 0;

    tempval = Py_BuildValue("s", "smsep");
    tempobj = PyObject_GetAttr(pyprm,Py_BuildValue("s", "noisesearch"));
    prm->noise.search = PyFloat_AsDouble(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "stid");
    tempobj = PyObject_GetAttr(pybeam,Py_BuildValue("s", "stid"));
    prm->stid = PyFloat_AsDouble(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "smsep");
    tempobj = PyObject_GetAttr(pyprm,Py_BuildValue("s", "noisemean"));
    prm->noise.mean = PyFloat_AsDouble(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "smsep");
    tempobj = PyObject_GetAttr(pybeam,Py_BuildValue("s", "channel"));
    tempchar = PyString_AsString(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    if(strcmp(tempchar,"a") == 0)
      if(prm->cp == 153)
        prm->channel = 1;
      else
        prm->channel = 0;
    else if(strcmp(tempchar,"b") == 0)
      prm->channel = 2;
    else if(strcmp(tempchar,"c") == 0)
      prm->channel = 3;
    else if(strcmp(tempchar,"d") == 0)
      prm->channel = 4;
    else if(strcmp(tempchar,"e") == 0)
      prm->channel = 5;
    else if(strcmp(tempchar,"f") == 0)
      prm->channel = 6;
    else if(strcmp(tempchar,"g") == 0)
      prm->channel = 7;
    else if(strcmp(tempchar,"h") == 0)
      prm->channel = 8;
    else
      prm->channel = 0;

    tempval = Py_BuildValue("s", "bmnum");
    tempobj = PyObject_GetAttr(pybeam,tempval);
    prm->bmnum = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "bmazm");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->bmazm = PyFloat_AsDouble(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "scan");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->scan = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "rxrise");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->rxrise = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "inttsc");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->intt.sc = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "inttus");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->intt.us = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    prm->txpl = 0;

    tempval = Py_BuildValue("s", "mpinc");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->mpinc = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "mppul");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->mppul = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "mplgs");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->mplgs = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "mplgexs");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->mplgexs = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "frang");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->frang = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "rsep");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->rsep = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "xcf");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->xcf = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    tempval = Py_BuildValue("s", "tfreq");
    tempobj = PyObject_GetAttr(pyprm,tempval);
    prm->tfreq = PyInt_AsLong(tempobj);
    Py_CLEAR(tempobj);
    Py_CLEAR(tempval);

    prm->offset = 0;
    prm->mxpwr = 1070000000;
    prm->lvmax = 20000;

    /*get the pulse table*/
    tempval = Py_BuildValue("s", "ptab");
    templist = PyObject_GetAttr(pyprm,tempval);
    Py_CLEAR(tempval);
    size = PyList_Size(templist);
    int16 temp_pul[size];
    for(i=0;i<size;i++)
      temp_pul[i] = PyInt_AsLong(PyList_GetItem(templist,i));
    RadarParmSetPulse(prm,size,temp_pul);
    Py_CLEAR(templist);

    /*get the lag table*/
    tempval = Py_BuildValue("s", "ltab");
    templist = PyObject_GetAttr(pyprm,tempval);
    Py_CLEAR(tempval);
    size = PyList_Size(templist);
    int16 temp_lag[size*2];
    for(i=0;i<size;i++)
    {
      temp_lag[i*2] = PyInt_AsLong(PyList_GetItem(PyList_GetItem(templist,i),0));
      temp_lag[i*2+1] = PyInt_AsLong(PyList_GetItem(PyList_GetItem(templist,i),1));
    }
    Py_CLEAR(templist);

    RadarParmSetLag(prm,size*2,temp_lag);
    RadarParmSetCombf(prm,"combf");

    FitSetRng(fit,prm->nrang);
    FitSetXrng(fit,prm->nrang);
    FitSetElv(fit,prm->nrang);

    tempval = Py_BuildValue("s", "pwr0");
    templist = PyObject_GetAttr(pyfit,tempval);
    Py_CLEAR(tempval);
    for(R=0;R<prm->nrang;R++)
    {
      fit->rng[R].v        = 0.;
      fit->rng[R].v_err    = 0.;
      fit->rng[R].p_0 = PyFloat_AsDouble(PyList_GetItem(templist,R));
      fit->rng[R].w_l      = 0.0;
      fit->rng[R].w_l_err  = 0.0;
      fit->rng[R].p_l      = 0.0;
      fit->rng[R].p_l_err  = 0.0;
      fit->rng[R].w_s      = 0.0;
      fit->rng[R].w_s_err  = 0.0;
      fit->rng[R].p_s      = 0.0;
      fit->rng[R].p_s_err  = 0.0;
      fit->rng[R].sdev_l   = 0.0;
      fit->rng[R].sdev_s   = 0.0;
      fit->rng[R].sdev_phi = 0.0;
      fit->rng[R].qflg     = 0;
      fit->rng[R].gsct     = 0;
      fit->rng[R].nump     = 0;
    }
    Py_CLEAR(templist);

    tempval = Py_BuildValue("s", "slist");
    templist = PyObject_GetAttr(pyfit,tempval);
    size = PyList_Size(templist);
    Py_CLEAR(templist);
    Py_CLEAR(tempval);

    for(i=0;i<size;i++)
    {

      tempval = Py_BuildValue("s", "slist");
      templist = PyObject_GetAttr(pyfit,tempval);
      R = PyInt_AsLong(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "v");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].v = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "v_e");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].v_err = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "w_l");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].w_l = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "w_l_e");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].w_l_err = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "p_l");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].p_l = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "p_l_e");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].p_l_err = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "w_s");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].w_s = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "w_s_e");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].w_s_err = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "p_s");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].p_s = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "p_s_e");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].p_s_err = PyFloat_AsDouble(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "qflg");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].qflg = PyInt_AsLong(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);

      tempval = Py_BuildValue("s", "gflg");
      templist = PyObject_GetAttr(pyfit,tempval);
      fit->rng[R].gsct = PyInt_AsLong(PyList_GetItem(templist,i));
      Py_CLEAR(templist);
      Py_CLEAR(tempval);
    }

    Py_CLEAR(pyfit);
    Py_CLEAR(pyprm);
    Py_CLEAR(pybeam);
    Py_CLEAR(templist);

    status=FitFwrite(fitfp,prm,fit);
    FitFree(fit);
    RadarParmFree(prm);

    PyObject *myObj = Py_BuildValue("i", 1);
    PyErr_PrintEx(0);
    return myObj;
  }
}

static PyObject *
read_dmap_rec(PyObject *self, PyObject *args)
{
  PyObject* f;
  if(!PyArg_ParseTuple(args, "O", &f))
    return NULL;
  else
  {
    PyObject *beamData = PyDict_New();
    int c,yr,mo,dy,hr,mt,sc,us,i,j,k,nrang;
    double epoch;
    struct DataMap *ptr;
    struct DataMapScalar *s;
    struct DataMapArray *a;
    FILE * fp = PyFile_AsFile(f);
    
    nrang=0;
    Py_BEGIN_ALLOW_THREADS
    PyFile_IncUseCount(f);
    ptr = DataMapRead(fileno(fp));
    PyFile_DecUseCount(f);
    Py_END_ALLOW_THREADS
    
    if(ptr == NULL)
      return Py_None;
    
    else
    {
      /*first, parse all of the scalars in the file*/
      for (c=0;c<ptr->snum;c++) 
      {
        s=ptr->scl[c];
        if ((strcmp(s->name,"nrang")==0) && (s->type==DATASHORT))
          nrang = *(s->data.sptr);
        if ((strcmp(s->name,"time.yr")==0) && (s->type==DATASHORT))
          yr=*(s->data.sptr);
        else if ((strcmp(s->name,"time.mo")==0) && (s->type==DATASHORT))
          mo=*(s->data.sptr);
        else if ((strcmp(s->name,"time.dy")==0) && (s->type==DATASHORT))
          dy=*(s->data.sptr);
        else if ((strcmp(s->name,"time.hr")==0) && (s->type==DATASHORT))
          hr=*(s->data.sptr);
        else if ((strcmp(s->name,"time.mt")==0) && (s->type==DATASHORT))
          mt=*(s->data.sptr);
        else if ((strcmp(s->name,"time.sc")==0) && (s->type==DATASHORT))
          sc=*(s->data.sptr);
        else if ((strcmp(s->name,"time.us")==0) && (s->type==DATAINT))
          us=(int)(((int)(*(s->data.iptr)*1e-3))*1e3);
        else
        {
          PyObject *myStr = Py_BuildValue("s", s->name);
          if(s->type==DATASHORT) 
          {
            PyObject *myNum = Py_BuildValue("i", *(s->data.sptr));
            PyDict_SetItem(beamData,myStr,myNum);
            Py_CLEAR(myNum);
          }
          else if(s->type==DATAINT)
          {
            PyObject *myNum = Py_BuildValue("i", *(s->data.iptr));
            PyDict_SetItem(beamData,myStr,myNum);
            Py_CLEAR(myNum);
          }
          else if(s->type==DATASTRING) 
          {
            PyObject *myNum = Py_BuildValue("s", *((char **) s->data.vptr));
            PyDict_SetItem(beamData,myStr,myNum);
            Py_CLEAR(myNum);
          }
          else if(s->type==DATAFLOAT) 
          {
            PyObject *myNum = Py_BuildValue("d", *(s->data.fptr));
            PyDict_SetItem(beamData,myStr,myNum);
            Py_CLEAR(myNum);
          }
          else if(s->type==DATACHAR) 
          {
            PyObject *myNum = Py_BuildValue("c", *(s->data.cptr));
            PyDict_SetItem(beamData,myStr,myNum);
            Py_CLEAR(myNum);    
          }
          else
          {
            PyObject *myNum = Py_BuildValue("i", -1);
            PyDict_SetItem(beamData,myStr,myNum);
            Py_CLEAR(myNum);
          }
          Py_CLEAR(myStr);
        }
      }
      /*now, parse the arrays*/
      for(c=0;c<ptr->anum;c++) 
      {
        a=ptr->arr[c];
        PyObject *myStr = Py_BuildValue("s", a->name);
        if ((strcmp(a->name,"ltab")==0) && (a->type==DATASHORT) && (a->dim==2))
        {
          PyObject *myList = PyList_New(0);
          for(i=0;i<a->rng[1]-1;i++)
          {
            PyObject *myNum = Py_BuildValue("[i,i]", a->data.sptr[i*2], a->data.sptr[i*2+1]);
            PyList_Append(myList,myNum);
            Py_CLEAR(myNum);
          }
          PyDict_SetItem(beamData,Py_BuildValue("s", "ltab"), myList);
          Py_CLEAR(myList);
        }
        else if((strcmp(a->name,"acfd")==0) && (a->type==DATAFLOAT) && (a->dim==3))
        {
          PyObject *myList = PyList_New(0);
          for(i=0;i<nrang;i++)
            for(j=0;j<a->rng[1];j++)
              for(k=0;k<2;k++)
              {
                PyObject *myNum = Py_BuildValue("f", a->data.fptr[(i*a->rng[1]+j)*2+k]);
                PyList_Append(myList,myNum);
                Py_CLEAR(myNum);
              }
          PyDict_SetItem(beamData,Py_BuildValue("s", "acfd"), myList);
          Py_CLEAR(myList);
        }
        else if((strcmp(a->name,"xcfd")==0) && (a->type==DATAFLOAT) && (a->dim==3))
        {
          PyObject *myList = PyList_New(0);
          for(i=0;i<nrang;i++)
            for(j=0;j<a->rng[1];j++)
              for(k=0;k<2;k++)
              {
                PyObject *myNum = Py_BuildValue("f", a->data.fptr[(i*a->rng[1]+j)*2+k]);
                PyList_Append(myList,myNum);
                Py_CLEAR(myNum);
              }
          PyDict_SetItem(beamData,Py_BuildValue("s", "xcfd"), myList);
          Py_CLEAR(myList);
        }
        else
        {
          PyObject *myList = PyList_New(0);
          for(i=0;i<a->rng[0];i++)
          {
            if(a->type==DATASHORT)
            {
              PyObject *myNum = Py_BuildValue("i", a->data.sptr[i]);
              PyList_Append(myList,myNum);
              Py_CLEAR(myNum);
            }
            else if(a->type==DATAINT) 
            {
              PyObject *myNum = Py_BuildValue("i", a->data.iptr[i]);
              PyList_Append(myList,myNum);
              Py_CLEAR(myNum);
            }
            else if(a->type==DATAFLOAT)
            {
              PyObject *myNum = Py_BuildValue("f", a->data.fptr[i]);
              PyList_Append(myList,myNum);
              Py_CLEAR(myNum);
            }
            else if(a->type==DATACHAR)
            {
              PyObject *myNum = Py_BuildValue("i", a->data.cptr[i]);
              PyList_Append(myList,myNum);
              Py_CLEAR(myNum);
            }
            else
            {
              PyObject *myNum = Py_BuildValue("i",-1);
              PyList_Append(myList,myNum);
              Py_CLEAR(myNum);
            }
          }
          PyDict_SetItem(beamData,myStr,myList);
          Py_CLEAR(myList);
        }
        Py_CLEAR(myStr);
      
      }
      
      epoch = TimeYMDHMSToEpoch(yr,mo,dy,hr,mt,(double)sc+us/1.e6);
      
      PyObject *myStr = Py_BuildValue("s", "time");
      PyObject *myNum = Py_BuildValue("d", epoch);
      PyDict_SetItem(beamData,myStr,myNum);
      Py_CLEAR(myStr);
      Py_CLEAR(myNum);
      
      DataMapFree(ptr);
    }
    return beamData;
  }
}


static PyMethodDef dmapioMethods[] = 
{
  {"readDmapRec",  read_dmap_rec, METH_VARARGS, "read a dmap record"},
  {"writeFitRec",  write_fit_rec, METH_VARARGS, "write a fitacf record"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initdmapio(void)
{
  (void) Py_InitModule("dmapio", dmapioMethods);
}
