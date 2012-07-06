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
//#include "option.h"
#include "rtime.h"
#include "rconvert.h"
#include "dmap.h"
#include "structmember.h"

#define ORIG_MAX_RANGE 300

int ConvertGZReadInt(void *gf,int32 *val) {
  unsigned char tmp[4];
  int s=0,o=0,l=4;
  while (o<4) {
    s=gzread(gf,tmp+o,l);
    o=o+s;
    l=l-s;
    if (s==0) return -1;
    if (s==-1) return -1;
  }
  ConvertToInt(tmp,val);
  return 0;
}


struct DataMap *DataMapGZReadBlock(gzFile *gf,int *s) {
  unsigned char *buf=NULL;
  struct DataMap *ptr;
  int32 code,sze,*iptr;
  int size=0,cnt=0,num=0,st=0;   
  st=ConvertGZReadInt(gf,&code);
  if (st==-1) return NULL;
  st=ConvertGZReadInt(gf,&sze);
  if (st==-1) return NULL;
  if (sze==0) return NULL;
  size=sze;
  buf=malloc(size);
  if (buf==NULL) return NULL;
  iptr=(int32 *) buf;
  iptr[0]=code;
  iptr[1]=sze;
    
  cnt=0;
  num=size-2*sizeof(int32);
  while (cnt<num) {
    st=gzread(gf,buf+2*sizeof(int32)+cnt,num-cnt);
    if (st<=0) break;
    cnt+=st;
  }
  if (cnt<num) {
    free(buf);
    return NULL;
  }

  ptr=DataMapDecodeBuffer(buf,size);
  free(buf);
  if (s !=NULL) *s=size+2*sizeof(int32);
  return ptr;
}

struct DataMap *DataMapGZread(void *gf) {
  return DataMapGZReadBlock(gf,NULL);
}

typedef struct {
    PyObject_HEAD
    PyObject *files;
    PyObject *fileaddress;
    PyObject *cache; /*dictionary of received variables */
    PyObject *cache_limit; /*limit of cached items */
    PyObject *offsets; /*dictionary using timeformat as keys */
    PyObject *fileindex; /*dictionary using timeformat as keys */
    PyObject *badtimes; /* list using timeformat as keys */
    PyObject *requiredvars; /* list */
    PyObject *rangevar;  /* string */
    PyObject *rangearrs; /* list */
    PyObject *times; /* list using timeformat as keys */
    PyObject *datetimes; /* list using datetimes as keys */
    PyObject *epochtimes; /* list using epochs as keys */
    PyObject *fractimes; /* list using dayfraction as keys */
    PyObject *timeformat; /* 'd', 'e', 'f' */
    PyObject *starttime;  /* datetime */
    PyObject *endtime;    /* datetime */
    PyObject *outputtype;  /* list, dict, array */
    PyObject *arraytype;  /* list, dict, array */
} PyDMapObject;

double TimeYMDHMSToDayFrac(int yr,int mo,int dy,int hr,int mt,double sec)
{
  static int epochconvert=719163;  // days from 01-01-01 to 01-01-1971
  double epoch=0; // seconds from 01-01-1971 00:00:00 UTC
  double dayfraction;  // days from 01-01-01 00:00:00 UTC
  static int secsinaday=86400;
  epoch=TimeYMDHMSToEpoch(yr,mo,dy,hr,mt,sec);
  dayfraction=epoch/secsinaday+epochconvert;
  return dayfraction;
}

void TimeDayFracToYMDHMS(double dayfraction, int *yr,int *mo,int *dy,int *hr,int *mt,double *sec)
{
  static int epochconvert=719163;  // days from 01-01-01 to 01-01-1971
  double epoch=0; // seconds from 01-01-1971 00:00:00 UTC
  static int secsinaday=86400;
  epoch=(dayfraction-epochconvert)*secsinaday;
  if (epoch < 0) return;
  TimeEpochToYMDHMS(epoch,(int *)&yr,(int *)&mo,(int *)&dy,(int *)&hr,(int *)&mt,(double *)&sec);
  return;
}

static PyObject *
timestamp(struct DataMap *ptr,char format) 
{
  int c;
  struct DataMapScalar *s;
  int yr=0,mo=0,dy=0,hr=0,mt=0,sc=0,us=0;
  double sec=0;
  PyDateTime_IMPORT;
         for (c=0;c<ptr->snum;c++) {
            s=ptr->scl[c];
            if (strcmp(s->name,"time.yr")==0 ) {
              yr=*(s->data.sptr);
            }
            if (strcmp(s->name,"time.mo")==0 ) {
              mo=*(s->data.sptr);
            }
            if (strcmp(s->name,"time.dy")==0 ) {
              dy=*(s->data.sptr);
            }
            if (strcmp(s->name,"time.hr")==0 ) {
              hr=*(s->data.sptr);
            }
            if (strcmp(s->name,"time.mt")==0 ) {
              mt=*(s->data.sptr);
            }
            if (strcmp(s->name,"time.sc")==0 ) {
              sc=*(s->data.sptr);
            }
            if (strcmp(s->name,"time.us")==0 ) {
              us=*(s->data.iptr);
            }
         }
          sec=sc+us*1E-6;
          if (format==0 || format=='d') return PyDateTime_FromDateAndTime(yr,mo,dy,hr,mt,sc,us);
          if (format==1 || format=='e') return Py_BuildValue("d",TimeYMDHMSToEpoch(yr,mo,dy,hr,mt,sec));
          if (format==2 || format=='f') return Py_BuildValue("d",TimeYMDHMSToDayFrac(yr,mo,dy,hr,mt,sec));
          else Py_RETURN_NONE;
}


static PyObject *
dt2ts(PyObject *self, PyObject *args, PyObject *kwds)
{
  static char *kwlist[] = {"datetime", NULL};
  PyObject *datetime=NULL;
  double dayfraction,sec;  // days from 01-01-01 00:00:00 UTC
  PyDateTime_IMPORT;

  if (! PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, 
                                      &datetime ))
     Py_RETURN_NONE; 
  if (PyDateTime_Check(datetime)){
    sec=PyDateTime_DATE_GET_SECOND(datetime)+PyDateTime_DATE_GET_MICROSECOND(datetime)*1E-6; 
    dayfraction=TimeYMDHMSToDayFrac(PyDateTime_GET_YEAR(datetime),
                PyDateTime_GET_MONTH(datetime),PyDateTime_GET_DAY(datetime),
                PyDateTime_DATE_GET_HOUR(datetime),PyDateTime_DATE_GET_MINUTE(datetime),sec);
    return Py_BuildValue("d",dayfraction);
  } else Py_RETURN_NONE;
}

static PyObject *
dt2e(PyObject *self, PyObject *args, PyObject *kwds)
{
  static char *kwlist[] = {"datetime", NULL};
  PyObject *datetime=NULL;
  double epoch=0; // seconds from 01-01-1971 00:00:00 UTC
  double sec,usec;
  PyDateTime_IMPORT;

  if (! PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, 
                                      &datetime ))
     Py_RETURN_NONE; 
  if (PyDateTime_Check(datetime)){
    usec=PyDateTime_DATE_GET_MICROSECOND(datetime);
    sec=PyDateTime_DATE_GET_SECOND(datetime)+usec*1E-6; 
    epoch=TimeYMDHMSToEpoch(PyDateTime_GET_YEAR(datetime),PyDateTime_GET_MONTH(datetime),PyDateTime_GET_DAY(datetime),
        PyDateTime_DATE_GET_HOUR(datetime),PyDateTime_DATE_GET_MINUTE(datetime),sec);
    if ( epoch < 0 ) {
      fprintf(stderr,"Bad Epoch %lf\n",epoch);
      fprintf(stderr,"%i ",PyDateTime_GET_YEAR(datetime));
      fprintf(stderr,"%i ",PyDateTime_GET_MONTH(datetime));
      fprintf(stderr,"%i \n",PyDateTime_GET_DAY(datetime));
      fprintf(stderr,"%i ",PyDateTime_TIME_GET_HOUR(datetime));
      fprintf(stderr,"%i ",PyDateTime_TIME_GET_MINUTE(datetime));
      fprintf(stderr,"%i ",PyDateTime_TIME_GET_SECOND(datetime));
      fprintf(stderr,"%i ",PyDateTime_TIME_GET_MICROSECOND(datetime));
    }
    return Py_BuildValue("d",epoch);
  } else Py_RETURN_NONE;
}

static PyObject *
ts2dt(PyObject *self, PyObject *args, PyObject *kwds)
{
  static char *kwlist[] = {"dayfraction", NULL};
  PyObject *datetime=NULL;
  double dayfraction;  // days from 01-01-01 00:00:00 UTC
  double sec;
  int yr=0,mo=0,dy=0,hr=0,mt=0,sc=0,us=0;
  PyDateTime_IMPORT;
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "d", kwlist, 
                                      &dayfraction ))
     Py_RETURN_NONE; 
  TimeDayFracToYMDHMS(dayfraction,&yr,&mo,&dy,&hr,&mt,&sec);
  sc=sec;
  us=(sec-sc)*1E6;
  datetime=PyDateTime_FromDateAndTime(yr,mo,dy,hr,mt,sc,us);
  return datetime;
}

static PyObject *
e2dt(PyObject *self, PyObject *args, PyObject *kwds)
{
  static char *kwlist[] = {"epoch", NULL};
  PyObject *datetime=NULL;
  double epoch=0; // seconds from 01-01-1971 00:00:00 UTC
  double sec;
  int yr=0,mo=0,dy=0,hr=0,mt=0,sc=0,us=0;
  PyDateTime_IMPORT;
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "d", kwlist, 
                                      &epoch ))
     Py_RETURN_NONE; 
  if (epoch < 0) Py_RETURN_NONE;
  TimeEpochToYMDHMS(epoch,&yr,&mo,&dy,&hr,&mt,&sec);
  sc=sec;
  us=(sec-sc)*1E6;
  datetime=PyDateTime_FromDateAndTime(yr,mo,dy,hr,mt,sc,us);
  return datetime;
}

static PyObject *
timespan(PyObject *self, PyObject *args, PyObject *kwds)
{
  PyObject *tuple=NULL,*format=NULL;
  static char *kwlist[] = {"filename","format", NULL};
  gzFile *fp;
  struct DataMap *ptr;
  char *fname,*tmpstr; 
  char fmt='d';
  PyObject *start=NULL,*end=NULL;
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "s|O", kwlist, 
                                      &fname,&format ))
     Py_RETURN_NONE;
  fp=gzopen(fname,"rb");
  if (fp==NULL) {
      fprintf(stderr,"File not found.\n");
      Py_RETURN_NONE;
  }  
  if(format!=NULL){
    if(PyInt_Check(format)) {
      fmt=(char)PyInt_AsLong(format);
    } else {
        if (PyString_Check(format)) {
          tmpstr=PyString_AsString(format);
          fmt=tmpstr[0];
        } 
    } 
  }
  ptr=DataMapGZread(fp);
  start=timestamp(ptr,fmt);
  end=timestamp(ptr,fmt);
  while ( ptr !=NULL) {
    Py_XDECREF(end);
    end=NULL;
    end=timestamp(ptr,fmt);
    DataMapFree(ptr);
    ptr=DataMapGZread(fp);
  }
  gzclose(fp);
  tuple=Py_BuildValue("(OO)",start,end);
  return tuple;  
}


int badrecord(struct DataMap *ptr,char *varname)
{
  int c,flag=1;
  struct DataMapScalar *s;
  struct DataMapArray *a;
          for (c=0;c<ptr->snum;c++) {
            if (flag==0) break;
            s=ptr->scl[c];
            if (strcmp(s->name,varname)==0 ) flag=0;
          }
          for (c=0;c<ptr->anum;c++) {
            if (flag==0) break;
            a=ptr->arr[c];
            if (strcmp(a->name,varname)==0 ) flag=0;
          }
  return flag;
}

static PyObject *
PyDMapObject_close(PyDMapObject *self, PyObject *args, PyObject *kwds) {
  gzFile *fp;
  PyObject *fname=NULL,*time=NULL;
  int errnum,index=-1,i,min,max;
  static char *kwlist[] = {"index","name","time",NULL};

  if (args==NULL && kwds==NULL) {
      min=0;
      max=PyList_Size(self->files);
  } else {
    if (! PyArg_ParseTupleAndKeywords(args, kwds, "iOO", kwlist, &index,&fname,&time)) 
      Py_RETURN_FALSE;
    if (fname!=NULL) index=PySequence_Index(self->files,fname);
    else if (time!=NULL) index=PyLong_AsLong(PyDict_GetItem(self->fileindex,time));
    if (index >=0 && index < PyList_Size(self->fileaddress)) {
      min=index;
      max=index+1;
    } else {
      min=0;
      max=PyList_Size(self->files);
    }
  }
  for(i=min;i<max;i++) {
    index=i;
    fp=PyLong_AsLong(PyList_GetItem(self->fileaddress,index));
    if (fp!=NULL) {
      errnum=gzclose(fp);
      if (errnum==0) fp=NULL;
      PyList_SetItem(self->fileaddress,index,Py_BuildValue("l",fp));
      if (fp!=NULL) {
        Py_RETURN_FALSE;
      }
    }
  } 
  Py_RETURN_TRUE;

}

static PyObject *
PyDMapObject_open(PyDMapObject *self, PyObject *args, PyObject *kwds) {
  gzFile *fp;
  PyObject *fname=NULL,*time=NULL;
  int index=-1,i,min,max;
  static char *kwlist[] = {"index","name","time",NULL};

  
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "iOO", kwlist, &index,&fname,&time)) {
        Py_RETURN_FALSE;
  }
  if (fname!=NULL) index=PySequence_Index(self->files,fname);
  else if (time!=NULL) index=PyLong_AsLong(PyDict_GetItem(self->fileindex,time));
  if (index >=0 && index < PyList_Size(self->fileaddress)) {
    min=index;
    max=index+1;
  } else {
    min=0;
    max=PyList_Size(self->files);
  } 
  for(i=min;i<max;i++) {
    index=i;
    fp=PyLong_AsLong(PyList_GetItem(self->fileaddress,index));
    if (fp==NULL) {
      fp=gzopen(PyString_AsString(PyList_GetItem(self->files,index)),"rb");
      PyList_SetItem(self->fileaddress,index,Py_BuildValue("l",fp));
      if (fp==NULL) Py_RETURN_FALSE;
    }
  } 
  Py_RETURN_TRUE;
}


static void
PyDMapObject_dealloc(PyDMapObject* self)
{
  int i;  

//    PyDMapObject_close(self, NULL, NULL); 
    Py_CLEAR(self->files);
    Py_CLEAR(self->cache);
    Py_CLEAR(self->cache_limit);
    Py_CLEAR(self->offsets);
    Py_CLEAR(self->fileindex);
    Py_CLEAR(self->times);
    Py_CLEAR(self->datetimes);
    Py_CLEAR(self->fractimes);
    Py_CLEAR(self->epochtimes);
    Py_CLEAR(self->timeformat);
    Py_CLEAR(self->starttime);
    Py_CLEAR(self->endtime);
    Py_CLEAR(self->outputtype);
    Py_CLEAR(self->arraytype);
    Py_CLEAR(self->badtimes);
    Py_CLEAR(self->requiredvars);
    Py_CLEAR(self->rangevar);
    Py_CLEAR(self->rangearrs);

//    for (i=0;i<PyList_Size(self->fileaddress);i++) {
//      gzclose(PyLong_AsLong(PyList_GetItem(self->fileaddress,i)));     
//    }

    Py_CLEAR(self->fileaddress);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
PyDMapObject_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyDMapObject *self;

    self = (PyDMapObject *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int
PyDMapObject_init(PyDMapObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *files=NULL,*required=NULL,*badtimes=NULL,*tmp=NULL;
    PyObject *dayfraction=NULL,*epoch=NULL,*datetime=NULL;
    PyObject *closed=NULL,*start=NULL,*end=NULL,*time=NULL;
    PyObject *rangevar=NULL, *rangearrs=NULL, *format=NULL;
    PyObject *fdict=NULL,*tlist=NULL,*elist=NULL,*dtlist=NULL,*blist=NULL,*odict=NULL;

    static char *kwlist[] ={"files","required","badtimes","starttime","endtime",
                            "rangevar","rangearrs","format","closed",NULL};
    char *filename=NULL;
    gzFile *fp=NULL;
    struct DataMap *ptr;
    unsigned long byte;
    int i,errnum,b,result,sflag,eflag;
    char *tmpstr;
    PyDateTime_IMPORT;

    closed=Py_False;
    if (! PyArg_ParseTupleAndKeywords(args, kwds, "O|OOOOOOOO", kwlist, 
                                      &files,&required,&badtimes,&start,&end,&rangevar,&rangearrs,&format,&closed))
        return -1; 

    tlist = PyList_New(0);
    elist = PyList_New(0);
    dtlist = PyList_New(0);
    blist = PyList_New(0);
    fdict = PyDict_New();
    odict = PyDict_New();

    if(PySequence_Check(files)) {
      self->files=files;
      Py_XINCREF(self->files);
    } else {
      if(PyString_Check(files)) {
        self->files=PyList_New(0);
        PyList_Append(self->files,files);
        Py_DECREF(files);
      }
    }

    if(start!=NULL){
      if(PyDateTime_Check(start)) {
        self->starttime=start;
      } else self->starttime=Py_None;
    } else self->starttime=Py_None;
    Py_INCREF(self->starttime);
    if(end!=NULL){
      if(PyDateTime_Check(end)) {
        self->endtime=end;
      } else self->endtime=Py_None;
    } else self->endtime=Py_None;
    Py_INCREF(self->endtime);

    if(required!=NULL){
      if(PyString_Check(required)) {
        self->requiredvars=PyList_New(0);
        PyList_Append(self->requiredvars,required);
        Py_DECREF(required);
      } else {
        if(PySequence_Check(required)) {
          self->requiredvars=PySequence_List(required);
        } else self->requiredvars=PyList_New(0);
      }
    } else self->requiredvars=PyList_New(0);

    if(badtimes!=NULL){
      if(PySequence_Check(badtimes)) {
        self->badtimes=PySequence_List(badtimes);
      } else {
        if(PyString_Check(badtimes)) {
          self->badtimes=PyList_New(0);
          PyList_Append(self->badtimes,badtimes);
          Py_DECREF(badtimes);
        }
      }
    } else {
      self->badtimes=PyList_New(0);
    }

    if(rangevar!=NULL){
      if(PyString_Check(rangevar)) {
        self->rangevar=rangevar;
      } else self->rangevar=Py_None;
    } else self->rangevar=Py_None;
    Py_INCREF(self->rangevar);


    if(rangearrs!=NULL){
      if(PyString_Check(rangearrs)) {
        self->rangearrs=PyList_New(0);
        PyList_Append(self->rangearrs,rangearrs);
        Py_DECREF(rangearrs);
      } else {
        if(PySequence_Check(rangearrs)) {
          self->rangearrs=PySequence_List(rangearrs);
        } else self->rangearrs=PyList_New(0);
      }
    } else self->rangearrs=PyList_New(0);


    if(format!=NULL){
      if(PyInt_Check(format)) {
        self->timeformat=format;
        Py_INCREF(self->timeformat);
      } else {
        if (PyString_Check(format)) {
          tmpstr=PyString_AsString(format);
          self->timeformat=Py_BuildValue("b",tmpstr[0]);
        } else  self->timeformat=Py_BuildValue("b",'d');
      }
    } else {
      self->timeformat=Py_BuildValue("b",'d');
    }

    self->fileaddress=PyList_New(0);

    for (i=0;i<PyList_Size(self->files);i++) {


        fp=gzopen(PyString_AsString(PyList_GetItem(self->files,i)),"rb");
        if (fp==NULL) {
          fprintf(stderr,"File not found.\n");
          return -1;
        }  
        byte=gztell(fp);

        while ( (ptr=DataMapGZread(fp)) !=NULL) {
          datetime=timestamp(ptr,'d');
          dayfraction=dt2ts(self,Py_BuildValue("(O)",datetime),NULL);
          epoch=dt2e(self,Py_BuildValue("(O)",datetime),NULL);
          if ((char)PyInt_AsLong(self->timeformat)==0 || (char)PyInt_AsLong(self->timeformat)=='d') time=datetime;
          else if ((char)PyInt_AsLong(self->timeformat)==1 || (char)PyInt_AsLong(self->timeformat)=='e') time=epoch;
          else if ((char)PyInt_AsLong(self->timeformat)==2 || (char)PyInt_AsLong(self->timeformat)=='f') time=dayfraction;
          else time=datetime;
          Py_INCREF(time);
          if (end!=NULL) {
            if (PyDateTime_Check(end)) {
              if ( PyFloat_AsDouble(epoch) < 
                   PyFloat_AsDouble(dt2e(self,Py_BuildValue("(O)",end),NULL)) ) {
                eflag=1;
              } else eflag=0;
            } else eflag=1;
          } else eflag=1;
          if (start!=NULL) {
            if (PyDateTime_Check(start)) {
              if ( PyFloat_AsDouble(epoch) > 
                   PyFloat_AsDouble(dt2e(self,Py_BuildValue("(O)",start),NULL)) ) {
                sflag=1;
              } else eflag=0;
            } else sflag=1;
          } else sflag=1;
          if ((eflag==1) && (sflag==1)) {
            if(PyList_Check(self->requiredvars)) {
              result=0; 
              for (b=0;b<PyList_Size(self->requiredvars);b++) {
                result+=badrecord(ptr,PyString_AsString(PyList_GetItem(self->requiredvars,b)));
              }
              if (result > 0) {
                PyList_Append(blist,time);
                Py_DECREF(time);
              } else {
                PyList_Append(tlist,dayfraction);
                Py_DECREF(dayfraction);
                PyList_Append(elist,epoch);
                Py_DECREF(epoch);
                PyList_Append(dtlist,datetime);
                Py_DECREF(datetime);
              } 
            } 
            PyDict_SetItem(odict,time,Py_BuildValue("l",byte));     
//            Py_INCREF(time);
            PyDict_SetItem(fdict,time,Py_BuildValue("i",i));     
//            Py_INCREF(time);
          }
          DataMapFree(ptr);
          byte=gztell(fp);
        } 

        if (closed!=NULL) {
          if (PyInt_Check(closed)) {
            if (PyInt_AsLong(closed)) {
              errnum=gzclose(fp);
              if (errnum==0) {
                fp=NULL;
              }
            }
          }
        }
        PyList_Append(self->fileaddress,Py_BuildValue("l",fp));
    }
    self->outputtype=PyDict_New();
    self->offsets=odict;
    self->fileindex=fdict;
    self->epochtimes=elist;
    self->fractimes=tlist;
    self->datetimes=dtlist;
    tmp=PySequence_Concat(self->badtimes,blist);	
    Py_XDECREF(self->badtimes);
    Py_XDECREF(blist);
    self->badtimes=PySequence_List(tmp);    
    if ((char)PyInt_AsLong(self->timeformat)==0 || (char)PyInt_AsLong(self->timeformat)=='d') self->times=self->datetimes;
    else if ((char)PyInt_AsLong(self->timeformat)==1 || (char)PyInt_AsLong(self->timeformat)=='e')
      self->times=self->epochtimes;
    else if ((char)PyInt_AsLong(self->timeformat)==2 || (char)PyInt_AsLong(self->timeformat)=='f') 
      self->times=self->fractimes;
    else self->times=self->datetimes;
    Py_INCREF(self->times);
    PyList_Sort(self->times);
    PyList_Sort(self->datetimes);
    PyList_Sort(self->epochtimes);
    PyList_Sort(self->fractimes);
    PyList_Sort(self->badtimes);
    self->cache=PyDict_New();
    self->cache_limit=Py_BuildValue("l",-1);

    Py_XDECREF(tmp);
    Py_XDECREF(time);
    Py_XDECREF(dayfraction);
    Py_XDECREF(epoch);
    Py_XDECREF(datetime);
//    printf("Hmm\n");
    return 0;
}

static PyObject *
PyDMapObject_is_cache_full(PyDMapObject *self)
{
  if(PyInt_AsLong(self->cache_limit) >= 0) { 
    if(PyDict_Size(self->cache)>PyInt_AsLong(self->cache_limit)) Py_RETURN_TRUE;
    else Py_RETURN_FALSE;
  } else Py_RETURN_FALSE;
}

static PyObject *
PyDMapObject_purge_cache(PyDMapObject *self,PyObject *args, PyObject *kwds)
{
  PyObject *data=NULL, *varname=NULL;
  static char *kwlist[] = {"varname",NULL};
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, 
                                      &varname)) {
     fprintf(stderr,"Bad purge_cache keywords\n");
     Py_RETURN_FALSE; 
  }
  if (varname !=NULL) {
    if(PyDict_DelItem(self->cache,varname)==0) {
      Py_RETURN_TRUE;
    } else Py_RETURN_FALSE; 
  } else {
    PyDict_Clear(self->cache);
    Py_RETURN_TRUE;
  }  
}


static PyObject *
PyDMapObject_fill_cache(PyDMapObject *self,PyObject *args, PyObject *kwds)
{
  PyObject *data=NULL, *varname=NULL;
  static char *kwlist[] = {"varname","data",NULL};
  if (PyInt_AsLong(PyDMapObject_is_cache_full(self))) {
    Py_RETURN_FALSE; 
  } 

  if (! PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, 
                                      &varname,&data)) {
     fprintf(stderr,"Bad fill_cache keywords\n");
     Py_RETURN_FALSE; 
  }
  if (PyDict_SetItem(self->cache,varname,data)==0) {
//    Py_INCREF(varname);
//    Py_INCREF(data);
    Py_RETURN_TRUE;
  } 
  Py_RETURN_FALSE; 
}


static PyObject *
PyDMapObject_getscalar(PyDMapObject *self, PyObject *time,PyObject *varname)
{
  struct DataMap *ptr;
  struct DataMapScalar *s;
  gzFile *fp;
  PyObject *tmp=NULL;
  int c,close=0;
  char **tmpstr;
    fp=PyLong_AsLong(PyList_GetItem(self->fileaddress,
         PyInt_AsLong(PyDict_GetItem(self->fileindex,time))));
    if (fp==NULL) {
      fprintf(stderr,"File Not Open\n");
      fp=gzopen(PyString_AsString(PyList_GetItem(self->files,
           PyInt_AsLong(PyDict_GetItem(self->fileindex,time)))),"rb");
      close=1; 
      if (fp==NULL) {
        fprintf(stderr,"File not found.\n");
        Py_RETURN_NONE;
      }
    }  
    if (PyLong_AsLong(PyDict_GetItem(self->offsets,time))!=gztell(fp)) {
      gzseek(fp,PyLong_AsLong(PyDict_GetItem(self->offsets,time)),SEEK_SET);
    }
    if ((ptr=DataMapGZread(fp)) !=NULL) {
        for (c=0;c<ptr->snum;c++) {
          s=ptr->scl[c];
          if (varname != NULL ) {
            if (strcmp(s->name,PyString_AsString(varname))==0 ) {
              switch (s->type) {
                case DATACHAR:
                  tmp=Py_BuildValue("i",*(s->data.cptr));
                break;
                case DATASHORT:
                  tmp=Py_BuildValue("h",*(s->data.sptr));
                break;
                case DATAINT:
                  tmp=Py_BuildValue("l",*(s->data.iptr));
                break;
                case DATAFLOAT:
                  tmp=Py_BuildValue("f",*(s->data.fptr));
                break;
                case DATADOUBLE:
                  tmp=Py_BuildValue("d",*(s->data.dptr));
                break;
                case DATASTRING:
                  tmpstr=(char **) s->data.vptr;
                  tmp=Py_BuildValue("s",*tmpstr);
                break;
              } 
              break;  
            }
          }
        } 
      DataMapFree(ptr);
    }
    if (close==1) {
      gzclose(fp);
    }
    if (tmp == NULL) {
      Py_RETURN_NONE;
    } else {
      return tmp;
    }
}

static PyObject *
PyDMapObject_getarray(PyDMapObject *self, PyObject *time,PyObject *varname)
{
  struct DataMap *ptr;
  struct DataMapArray *a;
  gzFile *fp;
  PyObject *tmp=NULL, *rdict=NULL, *aitems=NULL, *bitems=NULL, *citems=NULL;
  int c,n,x,d=0,close=0;
  char **tmpstr;
    fp=PyLong_AsLong(PyList_GetItem(self->fileaddress,
         PyInt_AsLong(PyDict_GetItem(self->fileindex,time))));
    if (fp==NULL) {
      fprintf(stderr,"File Not Open\n");
      fp=gzopen(PyString_AsString(PyList_GetItem(self->files,
        PyInt_AsLong(PyDict_GetItem(self->fileindex,time)))),"rb");
      close=1; 
      if (fp==NULL) {
        fprintf(stderr,"File not found.\n");
        Py_RETURN_NONE;
      }
    }  

    gzseek(fp,PyLong_AsLong(PyDict_GetItem(self->offsets,time)),SEEK_SET);
    if ((ptr=DataMapGZread(fp)) !=NULL) {
      for (c=0;c<ptr->anum;c++) {
            a=ptr->arr[c];
            if (strcmp(a->name,PyString_AsString(varname))==0 ) {
              if (aitems==NULL) {      
                aitems=PyList_New(0); 
              } else break; 
              d=a->dim;
              if (a->dim==2  /*|| a->dim==3*/ ) {
                if (bitems==NULL) {      
                  bitems=PyList_New(0);
                } else break;
              }
/*              if (a->dim==3) {
                citems=PyList_New(0);
              }*/
              n=1;
              for (x=0;x<a->dim;x++) {
                n=a->rng[x]*n;
              }
              for (x=0;x<n;x++) {
                if (aitems==NULL) {      
                  aitems = PyList_New(0);
                }
                switch (a->type) {
                  case DATACHAR:
                  tmp=Py_BuildValue("i",(a->data.cptr[x]));
                  PyList_Append(aitems,tmp);
                  break;
                  case DATASHORT:
                  tmp=Py_BuildValue("h",(a->data.sptr[x]));
                  PyList_Append(aitems,tmp);
                  break;
                  case DATAINT:
                  tmp=Py_BuildValue("l",(a->data.iptr[x]));
                  PyList_Append(aitems,tmp);
                  break;
                  case DATAFLOAT:
                  tmp=Py_BuildValue("f",(a->data.fptr[x]));
                  PyList_Append(aitems,tmp);
                  break;
                  case DATADOUBLE:
                  tmp=Py_BuildValue("d",(a->data.dptr[x]));
                  PyList_Append(aitems,tmp);
                  break;          
                  case DATASTRING:
                  tmpstr=(char **) a->data.vptr;
                  tmp=Py_BuildValue("s",tmpstr[x]);
                  PyList_Append(aitems,tmp);
                  break;
                }
                Py_XDECREF(tmp);
                tmp=NULL;
                if (a->dim==2) {
                  if ((x+1) % a->rng[0]==0) {
                    if (PyList_Size(aitems)!=0) {
                      PyList_Append(bitems,aitems);
                      Py_XDECREF(aitems);
                      aitems=NULL;
                    }
                  }
                }
              }   
            }
      }
/* end array stuff */
      DataMapFree(ptr);
    }
    if (close==1) {
      gzclose(fp);
    }

    if (d==2) {
      if (bitems == NULL) {
        Py_RETURN_NONE;
      } else return bitems;
    } else {
      if (aitems == NULL) {
        Py_RETURN_NONE;
      } else return aitems;
    }

}

static PyObject *
PyDMapObject_getrangearray(PyDMapObject *self, PyObject *time,PyObject *varname)
{
  struct DataMap *ptr;
  struct DataMapArray *a,*indexvar=NULL,*var=NULL;
  gzFile *fp;
  PyObject *tmp=NULL,*tmpkey=NULL, *rdict=NULL, *aitems=NULL, *bitems=NULL, *citems=NULL;
  int c,n,x,d=0,close=0;
  char **tmpstr;
    fp=PyLong_AsLong(PyList_GetItem(self->fileaddress,
         PyInt_AsLong(PyDict_GetItem(self->fileindex,time))));
    if (fp==NULL) {
      fprintf(stderr,"File Not Open\n");
      fp=gzopen(PyString_AsString(PyList_GetItem(self->files,
        PyInt_AsLong(PyDict_GetItem(self->fileindex,time)))),"rb");
      close=1; 
      if (fp==NULL) {
        fprintf(stderr,"File not found.\n");
        Py_RETURN_NONE;
      }
    }  
    if (gztell(fp)!=PyLong_AsLong(PyDict_GetItem(self->offsets,time))) {
      gzseek(fp,PyLong_AsLong(PyDict_GetItem(self->offsets,time)),SEEK_SET);
    }
    if ((ptr=DataMapGZread(fp)) !=NULL) {
      for (c=0;c<ptr->anum;c++) {
        a=ptr->arr[c];
        if (strcmp(a->name,PyString_AsString(self->rangevar))==0 ) {
          indexvar=a;
        }
        if (strcmp(a->name,PyString_AsString(varname))==0 ) {
          var=a;
        }
      }
      if (indexvar==NULL || var==NULL) Py_RETURN_NONE;

      if (var->dim!=1 || ( var->rng[0] != indexvar->rng[0])) {
        fprintf(stderr,"This is not a range array\n");
        fflush(stderr);
        Py_RETURN_NONE;
      }
      if (aitems==NULL) {      
        aitems=PyDict_New(); 
      } else Py_RETURN_NONE; 
      for (x=0;x < var->rng[0];x++) {
        tmpkey=Py_BuildValue("h",(indexvar->data.sptr[x]));
        switch (var->type) {
          case DATACHAR:
          tmp=Py_BuildValue("i",(var->data.cptr[x]));
          break;
          case DATASHORT:
          tmp=Py_BuildValue("h",(var->data.sptr[x]));
          break;
          case DATAINT:
          tmp=Py_BuildValue("l",(var->data.iptr[x]));
          break;
          case DATAFLOAT:
          tmp=Py_BuildValue("f",(var->data.fptr[x]));
          break;
          case DATADOUBLE:
          tmp=Py_BuildValue("d",(var->data.dptr[x]));
          break;          
          case DATASTRING:
          tmpstr=(char **) var->data.vptr;
          tmp=Py_BuildValue("s",tmpstr[x]);
          break;
        }
        PyDict_SetItem(aitems,tmpkey,tmp);
        Py_XDECREF(tmp);
        tmp=NULL;
        Py_XDECREF(tmpkey);
        tmpkey=NULL;
      }
/* end array stuff */
      DataMapFree(ptr);
    }
    if (close==1) {
      gzclose(fp);
    }

    if (aitems == NULL) {
      Py_RETURN_NONE;
    } else return aitems;

}


static PyObject *
PyDMapObject_getscalars(PyDMapObject *self,PyObject *args, PyObject *kwds)
{
  struct DataMap *ptr;
  struct DataMapScalar *s,*indexvar;
  PyObject *tmp=NULL,*list=NULL, *time=NULL;
  static char *kwlist[] = {"time",NULL};
  gzFile *fp;
  int close=0; 
  int c;
  char **tmpstr;
  unsigned long last;
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, 
                                      &time)) {
     fprintf(stderr,"Bad keywords\n");
     Py_RETURN_NONE; 
  }
  fp=PyLong_AsLong(PyList_GetItem(self->fileaddress,
       PyInt_AsLong(PyDict_GetItem(self->fileindex,time))));
  if (fp==NULL) {
    fprintf(stderr,"File Not Open\n");
    fp=gzopen(PyString_AsString(PyList_GetItem(self->files,
      PyInt_AsLong(PyDict_GetItem(self->fileindex,time)))),"rb");
    close=1; 
    if (fp==NULL) {
      fprintf(stderr,"File not found.\n");
      Py_RETURN_NONE;
    }
  }  
  list = PyList_New(0);
  if ( ! PyDict_Contains(self->offsets,time)) {
    fprintf(stderr,"bad time in offsets\n");
  }
//  gzrewind(fp);
  if (PyLong_AsLong(PyDict_GetItem(self->offsets,time))!=gztell(fp)) {
    gzseek(fp,PyLong_AsLong(PyDict_GetItem(self->offsets,time)),SEEK_SET);
  }
  last=gztell(fp);
  if ((ptr=DataMapGZread(fp)) !=NULL) {
        for (c=0;c<ptr->snum;c++) {
          s=ptr->scl[c];
          tmpstr=(char **) s->name;
          tmp=Py_BuildValue("s",tmpstr);
          PyList_Append(list,tmp);
          Py_XDECREF(tmp);
        } 
      DataMapFree(ptr);
  } else {
    if (close==1) {
      gzclose(fp);
    }
    Py_RETURN_NONE;
  }
  if (close==1) {
    gzclose(fp);
  } else {
    if (last!=gztell(fp)) {
      gzseek(fp,last,SEEK_SET);
    }
  }
  return list;
}

static PyObject *
PyDMapObject_getarrays(PyDMapObject *self,PyObject *args, PyObject *kwds)
{
  struct DataMap *ptr;
  struct DataMapArray *a;
  PyObject *tmp=NULL,*list=NULL, *time=NULL;
  static char *kwlist[] = {"time",NULL};
  gzFile *fp;
  int close=0; 
  int c;
  char **tmpstr;
  unsigned long last;
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, 
                                      &time))
     Py_RETURN_NONE; 
  fp=PyLong_AsLong(PyList_GetItem(self->fileaddress,
       PyInt_AsLong(PyDict_GetItem(self->fileindex,time))));
  if (fp==NULL) {
    fprintf(stderr,"File Not Open\n");
    fp=gzopen(PyString_AsString(PyList_GetItem(self->files,
      PyInt_AsLong(PyDict_GetItem(self->fileindex,time)))),"rb");
    close=1; 
    if (fp==NULL) {
      fprintf(stderr,"File not found.\n");
      Py_RETURN_NONE;
    }
  }  

  list = PyList_New(0);
  
  if ( ! PyDict_Contains(self->offsets,time)) {
    fprintf(stderr,"bad time in offsets\n");
  }
  if (PyLong_AsLong(PyDict_GetItem(self->offsets,time))!=gztell(fp)) {
    gzseek(fp,PyLong_AsLong(PyDict_GetItem(self->offsets,time)),SEEK_SET);
  }
  last=gztell(fp);
  gzseek(fp,PyLong_AsLong(PyDict_GetItem(self->offsets,time)),SEEK_SET);
  if ((ptr=DataMapGZread(fp)) !=NULL) {
        for (c=0;c<ptr->anum;c++) {
          a=ptr->arr[c];
          tmpstr=(char **) a->name;
          tmp=Py_BuildValue("s",tmpstr);
          PyList_Append(list,tmp);
          Py_XDECREF(tmp);
        } 
      DataMapFree(ptr);
  } else {
    if (close==1) {
      gzclose(fp);
    }
    Py_RETURN_NONE;
  }
  if (close==1) {
    gzclose(fp);
  } else {
    if (last!=gztell(fp)) {
      gzseek(fp,last,SEEK_SET);
    }
  }
  return list;
}

static PyObject *
PyDMapObject_getvar_timevalues(PyDMapObject *self, PyObject *args, PyObject *kwds)
{
  PyObject  *list=NULL, *time=NULL, *tmp=NULL, *varname=NULL, *vars=NULL, *nargs=NULL;
  static char *kwlist[] = {"varname",NULL};
  long p;
  if (PyDict_Check(self->outputtype)) {
    list = PyDict_New();
  } else {
    list = PyList_New(0);
  }
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, 
                                      &varname)){
     fprintf(stderr,"Bad arguments\n");
     Py_RETURN_NONE; 
  }
  if (PyDict_Contains(self->cache,varname)) {
    tmp=PyDict_GetItem(self->cache,varname);
    Py_INCREF(tmp);
    return tmp;
  }
  p=-1;
  for (p=0;p<PyList_Size(self->times);p++) {
    time=PyList_GetItem(self->times,p);
    Py_INCREF(time);
    nargs=PyTuple_New(1);
    PyTuple_SetItem(nargs,0, time);
    vars=PyDMapObject_getscalars(self,nargs,NULL);
    if (PySequence_Check(vars)) {
      if (PySequence_Contains(vars, varname)==1){
        tmp=PyDMapObject_getscalar(self, time,varname);
      } else {
        Py_XDECREF(vars);
        vars=NULL;
        vars=PyDMapObject_getarrays(self,nargs,NULL);
        if (PySequence_Check(vars)) {
          if (PySequence_Contains(vars, varname)==1){
            if (
             (PySequence_Contains(self->rangearrs,varname)==1)  && 
             (PySequence_Contains(vars,self->rangevar)==1) 
             ) {
              tmp=PyDMapObject_getrangearray(self, time,varname);
            } else {
              tmp=PyDMapObject_getarray(self, time,varname);
            }
          } else {
            tmp=Py_None;
            Py_INCREF(tmp);
          }
        } else {
          tmp=Py_None;
          Py_INCREF(tmp);
        }
      }
    } else {
      tmp=Py_None;
      Py_INCREF(tmp);
    }
    Py_XDECREF(nargs);
    nargs=NULL; 
    Py_XDECREF(vars);
    vars=NULL;
    if (PyDict_Check(self->outputtype)) {
      PyDict_SetItem(list,time,tmp);
/*
      Py_INCREF(time);
      Py_INCREF(tmp);
*/
    } else {
      PyList_Append(list,tmp);
      Py_DECREF(tmp);
    }
    Py_XDECREF(tmp);
    tmp=NULL;
    Py_XDECREF(time);
    time=NULL;
  }
//  fprintf(stdout,"Adding varname to cache\n");
  PyDMapObject_fill_cache(self,Py_BuildValue("(OO)",varname,list), NULL);
  return list; 
}

static PyObject *
PyDMapObject_gettime_values(PyDMapObject *self, PyObject *args, PyObject *kwds)
{
  PyObject  *list=NULL, *time=NULL, *tmp=NULL, *scalars=NULL, *arrays=NULL, *varname=NULL;
  static char *kwlist[] = {"time",NULL};
  long p;
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, 
                                      &time))
     Py_RETURN_NONE; 
  if (PyDict_Check(self->outputtype)) {
    list = PyDict_New();
  } else {
    list = PyList_New(0);
  }

  p=-1;

  scalars=PyDMapObject_getscalars(self,Py_BuildValue("(O)",time),NULL);
  for (p=0;p<PyList_Size(scalars);p++) {
      varname=PyList_GetItem(scalars,p);
      tmp=PyDMapObject_getscalar(self, time,varname);
      if (PyDict_Check(self->outputtype)) {
        PyDict_SetItem(list,varname,tmp);
//        Py_INCREF(varname);
//        Py_INCREF(tmp);
      } else {
        PyList_Append(list,tmp);
        Py_DECREF(tmp);
      }
      Py_XDECREF(tmp);
      tmp=NULL;
  }
  Py_XDECREF(scalars);
  scalars=NULL;


  arrays=PyDMapObject_getarrays(self,Py_BuildValue("(O)",time),NULL);
  for (p=0;p<PyList_Size(arrays);p++) {
      varname=PyList_GetItem(arrays,p);
      if (
       (PySequence_Contains(self->rangearrs,varname)==1)  && 
       (PySequence_Contains(arrays,self->rangevar)==1) 
       ) {
        tmp=PyDMapObject_getrangearray(self, time,varname);
       } else {
        tmp=PyDMapObject_getarray(self, time,varname);
      }
      if (PyDict_Check(self->outputtype)) {
        PyDict_SetItem(list,varname,tmp);
/*
        Py_INCREF(varname);
        Py_INCREF(tmp);
*/
      } else {
        PyList_Append(list,tmp);
        Py_DECREF(tmp);
      }
      Py_XDECREF(tmp);
      tmp=NULL;
  }
  Py_XDECREF(arrays);
  arrays=NULL;
  return list;  
}
static PyMethodDef PyDMapObject_methods[] = {
//    {"getvar_timevalues", (PyCFunction)PyDMapObject_getvar_timevalues, METH_VARARGS | METH_KEYWORDS,
//     "Get variable values at all times in file for selected records"
//    },
//    {"gettime_values", (PyCFunction)PyDMapObject_gettime_values, METH_VARARGS | METH_KEYWORDS,
//     "Get variable values at specified time record"
//    },
    {"get_scalars", (PyCFunction)PyDMapObject_getscalars, METH_VARARGS | METH_KEYWORDS,
     "Get scalar names associated with time record"
    },
    {"get_arrays", (PyCFunction)PyDMapObject_getarrays, METH_VARARGS | METH_KEYWORDS,
     "Get array names associated with time record"
    },
    {"close", (PyCFunction)PyDMapObject_close, METH_VARARGS | METH_KEYWORDS,
     "close file pointer associated with DMapFile Object"
    },
    {"open", (PyCFunction)PyDMapObject_open, METH_VARARGS | METH_KEYWORDS,
     "open file pointer associated with DMapFile Object"
    },
    {"purge_cache", (PyCFunction)PyDMapObject_purge_cache, METH_VARARGS | METH_KEYWORDS,
     "purge cached data"
    },
    {"is_cache_full", (PyCFunction)PyDMapObject_is_cache_full, METH_VARARGS | METH_KEYWORDS,
     "check to see if cache is full"
    },
    {NULL}
};
static PyMemberDef PyDMapObject_members[] = {

    {"files", T_OBJECT_EX, offsetof(PyDMapObject, files), 0,
     "files"},
    {"cache_limit", T_OBJECT_EX, offsetof(PyDMapObject, cache_limit), 0,
     "cache_limit"},
    {"cache", T_OBJECT_EX, offsetof(PyDMapObject, cache), 0,
     "cache"},
    {"fileindex", T_OBJECT_EX, offsetof(PyDMapObject, fileindex), 0,
     "fileindex"},
    {"offsets", T_OBJECT_EX, offsetof(PyDMapObject, offsets), 0,
     "offsets"},
    {"times", T_OBJECT_EX, offsetof(PyDMapObject, times), 0,
     "times"},
    {"datetimes", T_OBJECT_EX, offsetof(PyDMapObject, datetimes), 0,
     "datetimes"},
    {"epochtimes", T_OBJECT_EX, offsetof(PyDMapObject, epochtimes), 0,
     "epochtimes"},
    {"fractimes", T_OBJECT_EX, offsetof(PyDMapObject, fractimes), 0,
     "fractimes"},
    {"badtimes", T_OBJECT_EX, offsetof(PyDMapObject, badtimes), 0,
     "badtimes"},
    {"requiredvars", T_OBJECT_EX, offsetof(PyDMapObject, requiredvars), 0,
     "requiredvars"},
    {"rangevar", T_OBJECT_EX, offsetof(PyDMapObject, rangevar), 0,
     "rangevar"},
    {"rangearrs", T_OBJECT_EX, offsetof(PyDMapObject, rangearrs), 0,
     "rangearrs"},
    {"outputtype", T_OBJECT_EX, offsetof(PyDMapObject, outputtype), 0,
     "outputtype"},
    {NULL}
};

static int
PyDMapObject_length(PyDMapObject * s)
         /*@*/
{
    return PySequence_Size(s->times);
}
static PyObject *
PyDMapObject_subscript(PyDMapObject * s, PyObject * key)
        /*@*/
{
    if (PyString_Check(key)){
      return PyDMapObject_getvar_timevalues(s,Py_BuildValue("(O)",key),NULL);
    }
    if (PyFloat_Check(key)){
      return PyDMapObject_gettime_values(s,Py_BuildValue("(O)",key), NULL);
    }
    if (PyDateTime_Check(key)){
      return PyDMapObject_gettime_values(s,Py_BuildValue("(O)",key), NULL);
    }
    Py_RETURN_NONE;
}
static int
PyDMapObject_ass_subscript(PyDMapObject * s, PyObject * key, PyObject * value)
        /*@*/
{
    /*Assigning a value does nothing*/
    return 0;
}
static PyMappingMethods PyDMapObject_as_mapping = {
    PyDMapObject_length,               /* mp_length */
    PyDMapObject_subscript,            /* mp_subscript */
    PyDMapObject_ass_subscript,                /* mp_ass_subscript */
};



static PyTypeObject PyDMapObjectType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "pydmap.PyDMapObject",             /*tp_name*/
    sizeof(PyDMapObject),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)PyDMapObject_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    &PyDMapObject_as_mapping,         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "PyDMapObject objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    PyDMapObject_methods,             /* tp_methods */
    PyDMapObject_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)PyDMapObject_init,      /* tp_init */
    0,                         /* tp_alloc */
    PyDMapObject_new,                 /* tp_new */
};




static PyMethodDef module_methods[] = {
   	{ "timespan", (PyCFunction) timespan, METH_VARARGS | METH_KEYWORDS, NULL },
   	{ "dt2ts", (PyCFunction) dt2ts, METH_VARARGS | METH_KEYWORDS, NULL },
   	{ "ts2dt", (PyCFunction) ts2dt, METH_VARARGS | METH_KEYWORDS, NULL },
   	{ "dt2e", (PyCFunction) dt2e, METH_VARARGS | METH_KEYWORDS, NULL },
   	{ "e2dt", (PyCFunction) e2dt, METH_VARARGS | METH_KEYWORDS, NULL },
	{ NULL, NULL, 0, NULL } /* Sentinel */
};
 
PyMODINIT_FUNC
initpydmap(void) 
{
    PyObject* m;

    if (PyType_Ready(&PyDMapObjectType) < 0)
        return;

    m = Py_InitModule3("pydmap", module_methods,
                       "Module for accessing dmap files.");

    if (m == NULL)
      return;

    Py_INCREF(&PyDMapObjectType);
    PyModule_AddObject(m, "DMapFile", (PyObject *)&PyDMapObjectType);
}
