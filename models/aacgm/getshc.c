/* getshc.c
   ========
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



#include <stdio.h>
#include <stdlib.h>


int getshc(char *fname,int *nmax,double *erad,double *gh) {

  char dummy[256];
  int nn,mm,n,m;
  double g,h;
  double yr;
  FILE *fp;
  int stat;
  int i=0;
  fp=fopen(fname,"r");
  if (fp==NULL) return -1;
   
   stat=(fgets(dummy,256,fp)==NULL);
   if (stat !=0) {
     fclose(fp);
     return -1;
   }
    
   stat=(fscanf(fp,"%d %lg %lg",nmax,erad,&yr) !=3);
   if (stat !=0) {
     fclose(fp);
     return -1;
   }
   
   for (nn=1;nn<=*nmax;nn++) {
     for (mm=0;mm<=nn;mm++) {
    
       stat=(fscanf(fp,"%d %d  %lg %lg ",&n,&m,&g,&h) !=4);
       if (stat !=0) {
         fclose(fp);
         return -1;
       }
       gh[i]=g;
       i++;
       if (m !=0) {
         gh[i]=h;
         i++; 
       } 
     }
   }
   fclose(fp);
   return 0;
}


