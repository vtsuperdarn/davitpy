/* nrfit.c
   =======
   Numerical Recipes 
*/

/*
 LICENSE AND DISCLAIMER
 
 Copyright (c) 2012 The Johns Hopkins University/Applied Physics Laboratory
 
 This file is part of the Radar Software Toolkit (RST).
 
 RST is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 any later version.
 
 RST is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.
 
 You should have received a copy of the GNU Lesser General Public License
 along with RST.  If not, see <http://www.gnu.org/licenses/>.
 
 
 
*/


#include <stdio.h>
#include <stdlib.h>
#include <math.h>




void nrfit(float *x,float *y,int ndata,float *sig,int mwt,
                  float *a,float *b,float *siga,float *sigb,float *chi2,
                  float *q) {

  int i;
  float wt,t,sxoss,sx=0.0,sy=0.0,st2=0.0,ss,sigdat;
 
  *b=0.0;

  if (mwt) {
    ss=0.0;
    for (i=0;i<ndata;i++) {
      wt=1.0/(sig[i]*sig[i]);
      ss+=wt;
      sx+=x[i]*wt;
      sy+=y[i]*wt;
    }
  } else {
    for (i=0;i<ndata;i++) {
      sx+=x[i];
      sy+=y[i];
    }
    ss=ndata;
  }
  sxoss=sx/ss;

  if (mwt) {
    for (i=0;i<ndata;i++) {
      t=(x[i]-sxoss)/sig[i];
      st2+=t*t;
      *b+=t*y[i]/sig[i];
    }
  } else {
    for (i=0;i<ndata;i++) {
      t=x[i]-sxoss;
      st2+=t*t;
      *b+=t*y[i];
    }
  }
  *b/=st2;
  *a=(sy-sx*(*b))/ss;
  *siga=sqrt((1.0+sx*sx/(ss*st2))/ss);
  *sigb=sqrt(1.0/st2);
  
  *chi2=0.0;
  if (mwt==0) {
    for (i=0;i<ndata;i++)
      *chi2+=(y[i]-(*a)-(*b)*x[i])*(y[i]-(*a)-(*b)*x[i]);
    *q=1.0;
    sigdat=sqrt((*chi2)/(ndata-2));
    *siga *= sigdat; 
    *sigb *= sigdat;
  } else {
    for (i=0;i<ndata;i++) 
      *chi2+=((y[i]-(*a)-(*b)*x[i])/sig[i])*((y[i]-(*a)-(*b)*x[i])/sig[i]);
    /*    *q=gammaq(0.5*(ndata-2),0.5*(*chi2)); */
    *q=1.0;
  }
}
