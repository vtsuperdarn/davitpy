/* rtypes.h
   ========
   Author: R.J.Barnes, J.Spaleta
*/

/*
 (c) 2011 JHU/APL & Others - Please Consult LICENSE.datamap.txt for more information.
*/


#include <stdio.h>
#include <limits.h>
#include <Python.h>

typedef int ipcid_t;

/* This defines the int16, int32, and int64 types */


#ifdef WORD_BIT
  #if WORD_BIT == 16
    typedef char int8;
    typedef unsigned char uint8;
    typedef int int16;                                                                                                           typedef unsigned int uint16;
    typedef long int32;
    typedef unsigned long uint32;
    typedef double int64;
    typedef unsigned double uint64;
  #endif
  #if WORD_BIT == 32
    typedef char int8;
    typedef unsigned char uint8;
    typedef short int16;
    typedef unsigned short uint16;
    typedef int int32;
    typedef unsigned int uint32;
    typedef long long int64;
    typedef unsigned long long uint64;
  #endif
#endif
#ifdef LONG_BIT
  #if LONG_BIT == 32
    typedef char int8;
    typedef unsigned char uint8;
    typedef short int16;
    typedef unsigned short uint16;
    typedef long int32;
    typedef unsigned long uint32;
    typedef long long int64;
    typedef unsigned long long uint64;
  #endif
  #if LONG_BIT == 64
    typedef char int8;
    typedef unsigned char uint8;
    typedef short int16;
    typedef unsigned short uint16;
    typedef int int32;
    typedef unsigned int uint32;
    typedef long int64;
    typedef unsigned long uint64;
  #endif
#endif
#ifdef __INT_BITS__
  #if __INT_BITS__== 16
    typedef char int8;
    typedef unsigned char uint8;
    typedef int int16;
    typedef unsigned int uint16;
    typedef long int32;
    typedef unsigned long uint32;
    typedef double int64;
    typedef unsigned double uint64;
  #endif
  #if __INT_BITS__== 32
    typedef char int8;
    typedef unsigned char uint8;
    typedef short int16;
    typedef unsigned short uint16;
    typedef int int32;
    typedef unsigned int uint32;
    typedef long long int64;
    typedef unsigned long long uint64;
  #endif
#endif

