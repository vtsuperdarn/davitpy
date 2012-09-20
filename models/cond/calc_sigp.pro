pro	calc_sigp

; Input date and time
year = 2010
doy = 100
hourut = 12
; Input lat and lon (geog)
glat = 40.
glon = -80.

; Execute code
input = STRTRIM(year,2)+','+STRTRIM(doy,2)+','+STRTRIM(hourut,2)+','+STRTRIM(glat,2)+','+STRTRIM(glon,2)
spawn, 'rm inp_file'
spawn, 'echo '+input+' >> inp_file'
spawn, './sigp < inp_file'

; Read values
openr, unit, 'sigpout.dat', /get_lun
sigpint = 0.d
sigph = dblarr(500)
alt = fltarr(500)
readf, unit, sigpint, format='(E19.11)'
readf, unit, sigph, format='(500E19.11)'
readf, unit, alt, format='(500F7.2)'
free_lun, unit

clear_page
charsize = 2
plot, sigph, alt, /xlog, $
    xrange=[1e-10,1e-4], yrange=[100.,600.], $
    xstyle=1, ystyle=1, charsize=charsize, $
    xtitle=textoidl('\sigma_1 [S/m]'), ytitle='Alt. [km]'
xyouts, .5, .85, textoidl('Height integrated \sigma_1 = ')+STRTRIM(string(sigpint,format='(E9.3)'),2), $
    /normal, charsize=charsize


end