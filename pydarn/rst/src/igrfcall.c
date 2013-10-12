/* igrfcall.c
   ==========
   Author: R.J.Barnes
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




/* store the co-efficients up here */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "interpshc.h"
#include "extrapshc.h"
#include "getshc.h"
#include "shval3.h"

double igrf_date=-1;


char filmod[256][256];
double dtemod[256];

int dtemax=0;

double gh1[400],gh2[400],gha[400],ghb[400];
double erad;
int nmax,nmax1,nmax2;

int IGRFCall(double date, double flat, double flon, 
             double elev, double *x, double *y, double *z) {
 
    int i;
    char *envstr;
    char file1[256];
    char file2[256];
    char line[256];
    FILE *fp;
    double ext[3]={0.0,0.0,0.0};
    double a2 = 40680925.0;
    double b2 = 40408588.0;                       
	
    if (dtemax==0) {
      envstr=getenv("IGRF_PATH");
      sprintf(file1,"%s/%s",envstr,"coef.dat");
      fp=fopen(file1,"r");
      if (fp==NULL) return -1;
      int i=0;
      while (fgets(line,255,fp) !=NULL) {
        sscanf(line,"%s %lf",filmod[i],&dtemod[i]);
        i++;
      }
      dtemod[i]=0;
      dtemax=i-2;
      fclose(fp);
    }

    if (igrf_date !=date) {
      for (i=0;(dtemod[i] !=0) && (dtemod[i]<date);i++);
      if (i==0) return -1;
      i--;

      igrf_date=date;
      envstr=getenv("IGRF_PATH");
      
      sprintf(file1,"%s/%s",envstr,filmod[i]);
      getshc(file1, &nmax1, &erad, gh1);

      sprintf(file2,"%s/%s",envstr,filmod[i+1]);
      getshc(file2, &nmax2, &erad, gh2);
          
      if (i < dtemax) {
	  interpshc(date, dtemod[i], 
                    nmax1, gh1, dtemod[i+1], nmax2, gh2, &nmax, gha);
  	  interpshc(date+1,dtemod[i], 
                    nmax1, gh1, dtemod[i+1], nmax2, gh2, &nmax, ghb);
      } else {
	  extrapshc(date, dtemod[i], 
                    nmax1, gh1, nmax2, gh2, &nmax, gha);
  	  extrapshc(date+1,dtemod[i], 
                    nmax1, gh1, nmax2, gh2, &nmax, ghb);
      }
      

    }

    
    shval3(2, flat, flon, elev, erad, a2, b2, nmax, gha, 0,
	   ext, x, y, z);

    return 0;
} 



