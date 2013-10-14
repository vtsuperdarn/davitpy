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
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include "rtypes.h"
#include "rconvert.h"
#include "rtime.h"
#include "dmap.h"
#include "structmember.h"

/*
void parsePyPrm(struct RadarParm *prm, PyObject *pyprm)
{

}*/

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
          else if(s->type==DATADOUBLE) 
          {
            PyObject *myNum = Py_BuildValue("d", *(s->data.dptr));
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
            else if(a->type==DATADOUBLE)
            {
              PyObject *myNum = Py_BuildValue("f", a->data.dptr[i]);
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
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initdmapio(void)
{
  (void) Py_InitModule("dmapio", dmapioMethods);
}