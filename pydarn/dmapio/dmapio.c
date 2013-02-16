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
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include "rtypes.h"
#include "rtime.h"
#include "rconvert.h" 
#include "dmap.h"
#include "structmember.h" 
#include "rprm.h"

static PyObject *
read_dmap_rec(PyObject *self, PyObject *args)
{
	PyObject* f;
	if(!PyArg_ParseTuple(args, "O", &f))
		return NULL;
	else
	{
		PyObject *beamData = PyDict_New();
		int c,yr,mo,dy,hr,mt,sc,us,i,j,k,nrang,len,mplgs;
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


static PyObject *
read_dmap(PyObject *self, PyObject *args)
{
	int len;
	PyObject* filelist, *item;
	 
	if(!PyArg_ParseTuple(args, "iO", &len, &filelist))
		return NULL;
	else
	{
		PyObject *rawData = PyDict_New();
		int c,nRecs,yr,mo,dy,hr,mt,sc,us,i,j,k,l,nrang,chn;
		double epoch;
		struct DataMap *ptr;
		struct DataMapScalar *s;
		struct DataMapArray *a;
		FILE * fp = NULL;
		
		for (l=0;l<len;l++) 
		{
      /* get the element from the list*/
      item = PySequence_GetItem(filelist,l);

			nRecs=0,nrang=0,chn=0;
			
			fprintf(stderr,"reading: %s\n",PyString_AsString(item));
			
			fp = fopen(PyString_AsString(item),"r");
			
			Py_DECREF(item);
			
			ptr = DataMapRead(fileno(fp));
			
			if(ptr == NULL) continue;
			
			while(ptr != NULL)
			{
				
				PyObject *beamData = PyDict_New();
				
				/*first, parse all of the scalars in the file*/
				for (c=0;c<ptr->snum;c++) 
				{
					s=ptr->scl[c];
					if ((strcmp(s->name,"time.yr")==0) && (s->type==DATASHORT))
						yr=*(s->data.sptr);
					if ((strcmp(s->name,"time.mo")==0) && (s->type==DATASHORT))
						mo=*(s->data.sptr);
					if ((strcmp(s->name,"time.dy")==0) && (s->type==DATASHORT))
						dy=*(s->data.sptr);
					if ((strcmp(s->name,"time.hr")==0) && (s->type==DATASHORT))
						hr=*(s->data.sptr);
					if ((strcmp(s->name,"time.mt")==0) && (s->type==DATASHORT))
						mt=*(s->data.sptr);
					if ((strcmp(s->name,"time.sc")==0) && (s->type==DATASHORT))
						sc=*(s->data.sptr);
					if ((strcmp(s->name,"time.us")==0) && (s->type==DATAINT))
						us=*(s->data.iptr);
					if ((strcmp(s->name,"tfreq")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "tfreq"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"bmnum")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "bmnum"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"origin.command")==0) && (s->type==DATASTRING))
						PyDict_SetItem(beamData,Py_BuildValue("s", "origin.command"), Py_BuildValue("s", *((char **) s->data.vptr)));											
					if ((strcmp(s->name,"cp")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "cp"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"stid")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "stid"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"nave")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "nave"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"lagfr")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "lagfr"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"smsep")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "smsep"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"noise.search")==0) && (s->type==DATAFLOAT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "noise.search"), Py_BuildValue("d", *(s->data.fptr)));
					if ((strcmp(s->name,"noise.mean")==0) && (s->type==DATAFLOAT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "noise.mean"), Py_BuildValue("d", *(s->data.fptr)));
					if ((strcmp(s->name,"channel")==0) && (s->type==DATASHORT))
					{
						PyDict_SetItem(beamData,Py_BuildValue("s", "channel"), Py_BuildValue("i", *(s->data.sptr)));
						chn = *(s->data.sptr);
					}
					if ((strcmp(s->name,"bmazm")==0) && (s->type==DATAFLOAT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "bmazm"), Py_BuildValue("d", *(s->data.fptr)));
					if ((strcmp(s->name,"scan")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "scan"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"offset")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "offset"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"rxrise")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "rxrise"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"intt.sc")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "intt.sc"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"intt.us")==0) && (s->type==DATAINT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "intt.us"), Py_BuildValue("i", *(s->data.iptr)));
					if ((strcmp(s->name,"mpinc")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "mpinc"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"mppul")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "mppul"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"mplgs")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "mplgs"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"mplgexs")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "mplgexs"), Py_BuildValue("i", *(s->data.sptr)));
					/* Lasse Clausen's edit, to include the ifmode parameter*/
					if ( ( strcmp( s->name, "ifmode" ) == 0 ) && ( s->type == DATASHORT ) )
						PyDict_SetItem(beamData,Py_BuildValue("s", "ifmode"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"nrang")==0) && (s->type==DATASHORT))
					{
						PyDict_SetItem(beamData,Py_BuildValue("s", "nrang"), Py_BuildValue("i", *(s->data.sptr)));
						nrang = *(s->data.sptr);
					}
					if ((strcmp(s->name,"frang")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "frang"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"rsep")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "rsep"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"xcf")==0) && (s->type==DATASHORT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "xcf"), Py_BuildValue("i", *(s->data.sptr)));
					if ((strcmp(s->name,"noise.sky")==0) && (s->type==DATAFLOAT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "noise.sky"), Py_BuildValue("d", *(s->data.fptr)));
					if ((strcmp(s->name,"noise.lag0")==0) && (s->type==DATAFLOAT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "noise.lag0"), Py_BuildValue("d", *(s->data.fptr)));
					if ((strcmp(s->name,"noise.vel")==0) && (s->type==DATAFLOAT))
						PyDict_SetItem(beamData,Py_BuildValue("s", "noise.vel"), Py_BuildValue("d", *(s->data.fptr)));

				}
				
				/*now, parse the arrays*/
				for(c=0;c<ptr->anum;c++) 
				{
					a=ptr->arr[c];
					
					if ((strcmp(a->name,"ptab")==0) && (a->type==DATASHORT) && (a->dim==1)) 
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("i", a->data.sptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "ptab"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"ltab")==0) && (a->type==DATASHORT) && (a->dim==2)) 
					{
						PyObject *myList = PyList_New(a->rng[1]-1);
						for(i=0;i<a->rng[1]-1;i++)
							PyList_SetItem(myList,i,Py_BuildValue("[i,i]", a->data.sptr[i*2], a->data.sptr[i*2+1]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "ltab"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"slist")==0) && (a->type==DATASHORT) && (a->dim==1))
					{
						PyDict_SetItem(beamData,Py_BuildValue("s", "npnts"), Py_BuildValue("i",a->rng[0]));
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("i", a->data.sptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "slist"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"pwr0")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
						{
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						}
						PyDict_SetItem(beamData,Py_BuildValue("s", "pwr0"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"nlag")==0) && (a->type==DATASHORT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("i", a->data.sptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "nlag"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"qflg")==0) && (a->type==DATACHAR) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("i",a->data.cptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "qflg"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"gflg")==0) && (a->type==DATACHAR) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("i", a->data.cptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "gflg"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"p_l")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "p_l"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"p_l_e")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "p_l_e"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"p_s")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "p_s"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"p_s_e")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "p_s_e"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"v")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "v"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"v_e")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "v_e"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"w_l")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "w_l"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"w_l_e")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "w_l_e"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"w_s")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "w_s"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"w_s_e")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "w_s_e"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"sd_l")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "sd_l"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"sd_s")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "sd_s"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"sd_phi")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "sd_phi"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"x_qflg")==0) && (a->type==DATACHAR) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("i", a->data.cptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "x_qflg"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"x_gflg")==0) && (a->type==DATACHAR) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("i", a->data.cptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "x_gflg"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"elv_high")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "elv_high"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"elv_low")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "elv_low"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"elv")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "elv"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"phi0")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "phi0"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"phi0_e")==0) && (a->type==DATAFLOAT) && (a->dim==1))
					{
						PyObject *myList = PyList_New(a->rng[0]);
						for(i=0;i<a->rng[0];i++)
							PyList_SetItem(myList,i,Py_BuildValue("d", a->data.fptr[i]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "phi0_e"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"acfd")==0) && (a->type==DATAFLOAT) && (a->dim==3))
					{
						int mplgs = a->rng[1];
						PyObject *myList = PyList_New(nrang*mplgs*2);
						for(i=0;i<nrang;i++)
							for(j=0;j<mplgs;j++)
								for(k=0;k<2;k++)
									PyList_SetItem(myList,(i*mplgs+j)*2+k,Py_BuildValue("d", a->data.fptr[(i*mplgs+j)*2+k]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "acfd"), myList);
						Py_DECREF(myList);
					}
					if ((strcmp(a->name,"xcfd")==0) && (a->type==DATAFLOAT) && (a->dim==3))
					{
						int mplgs = a->rng[1];
						PyObject *myList = PyList_New(nrang*mplgs*2);
						for(i=0;i<nrang;i++)
							for(j=0;j<mplgs;j++)
								for(k=0;k<2;k++)
									PyList_SetItem(myList,(i*mplgs+j)*2+k,Py_BuildValue("d", a->data.fptr[(i*mplgs+j)*2+k]));
						PyDict_SetItem(beamData,Py_BuildValue("s", "xcfd"), myList);
						Py_DECREF(myList);
					}
				}
				
				/*convert time to epoch time (key)*/
				if(chn > 1) us += chn-1;
				epoch = TimeYMDHMSToEpoch(yr,mo,dy,hr,mt,(double)sc+us/1.e6);
				
				/*add the beam to the radData dict*/
				PyDict_SetItem(rawData,Py_BuildValue("d", epoch), beamData);
				
				/*free beam data object*/
				Py_DECREF(beamData);
				
				DataMapFree(ptr);
				ptr = DataMapRead(fileno(fp));
			}
			fclose(fp);
		}
		
		return rawData;
	}
}

static PyMethodDef dmapioMethods[] = 
{
	{"readDmap",  read_dmap, METH_VARARGS, "read a dmap file"},
	{"readDmapRec",  read_dmap_rec, METH_VARARGS, "read a dmap record"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initdmapio(void)
{
	(void) Py_InitModule("dmapio", dmapioMethods);
}