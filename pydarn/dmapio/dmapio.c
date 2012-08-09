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

static PyObject *
read_dmap(PyObject *self, PyObject *args)
{
	const char *filename;
	
	if (!PyArg_ParseTuple(args, "s", &filename))
		return NULL;
	else
	{
		
		struct DataMap *ptr;
		FILE * fp = fopen(filename,"r");
		
		ptr = DataMapRead(fileno(fp));
		
		if (ptr==NULL) 
			return NULL;
		
		DataMapFree(ptr);
		
		return Py_BuildValue("s", filename);
		
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