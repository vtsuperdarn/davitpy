/*-----------------------------------------------------------------------------
;
; NAME:
;       dayno
;
; PURPOSE:
;       Function to compute the day of the year and the number of days in the
;       year.
;
; CALLING SEQUENCE:
;       doy = dayno(year, month, day, diy);
;     
;     Input Arguments:
;       year          - year [1965-2014]
;       month         - month of year [01-12]
;       day           - day of month [01-31]
;
;     Output Arguments (integer pointers):  
;       diy           - number of days in the given year
;
;     Return Value:
;       error code
;
;+-----------------------------------------------------------------------------
*/

int dayno(int year, int month, int day, int *diy)
{
  int k,tot;
  int ndays[] = {31,28,31,30,31,30,31,31,30,31,30,31};

  *diy = 365;
  if(((year%4==0)&&(year%100!=0))||(year%400==0)) {
    ndays[1]++;
    *diy = 366;
  }

  tot = 0;
  for (k=0; k<month-1; k++) tot += ndays[k];
  tot += day;

  return tot;
}

