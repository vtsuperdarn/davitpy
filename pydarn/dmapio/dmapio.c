#include <Python.h>
#include <datetime.h>
#include <stdio.h>
#include <zlib.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include "rtypes.h"
#include "rtime.h"
#include "rconvert.h"
#include "dmap.h"
#include "structmember.h"
#include "rprm.h"

static PyObject *
read_dmap(PyObject *self, PyObject *args)
{
	const char *filename;
	
	if (!PyArg_ParseTuple(args, "s", &filename))
		return NULL;
	else
	{
		char *command;
		int c,nRecs=0,yr,mo,dy,hr,mt,sc,us,i;
		double epoch;
		struct DataMap *ptr;
		struct DataMapScalar *s;
		struct DataMapArray *a;
		
		FILE * fp = fopen(filename,"r");
		PyObject *rawData = PyDict_New();
		
		while(1)
		{
			ptr = DataMapRead(fileno(fp));
			
			if(ptr==NULL && nRecs == 0) 
				return NULL;
			else if(ptr==NULL) 
			{
				fclose(fp);
				return rawData;
			}
			else
				nRecs++;
			
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
					PyDict_SetItem(beamData,Py_BuildValue("s", "channel"), Py_BuildValue("i", *(s->data.sptr)));
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
					PyDict_SetItem(beamData,Py_BuildValue("s", "intt.us"), Py_BuildValue("i", *(s->data.sptr)));
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
					PyDict_SetItem(beamData,Py_BuildValue("s", "nrang"), Py_BuildValue("i", *(s->data.sptr)));
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
			}
			/*convert time to epoch time (key)*/
			epoch = TimeYMDHMSToEpoch(yr,mo,dy,hr,mt,(double)sc+us/1.e6);
			
			/*add the beam to the radData dict*/
			PyDict_SetItem(rawData,Py_BuildValue("d", epoch), beamData);
			
			Py_DECREF(beamData);
			
			DataMapFree(ptr);
		}
		
		
	}
}

static PyMethodDef dmapioMethods[] = 
{
	{"readDmap",  read_dmap, METH_VARARGS, "read a dmap file"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initdmapio(void)
{
	(void) Py_InitModule("dmapio", dmapioMethods);
}