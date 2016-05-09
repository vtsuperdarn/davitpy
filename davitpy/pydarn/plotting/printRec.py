# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Functions for printing radar data records to plain text

Module author: AJ, 20130327

Functions
------------------------------------------
fitPrintRec     Print fit-type files
readPrintRec    Read printrec output files
------------------------------------------

"""


def readPrintRec(filename):
    """A function to read the output of fitPrintRec

    Parameters
    ----------
    filename : str
        the name of the file

    Returns
    -------
    Nothing

    Example
    -------
        pydarn.plotting.readPrintRec('myfile.txt')

    Written by AJ 20130327

    """
    import datetime as dt

    # open the file
    try: fp = open(filename)
    except Exception, e:
        logging.exception(e)
        logging.exception('problem opening the file %s', filename)
        return None

    # read the first line
    line = fp.readline()
    cnt = 1

    # read until the end of the file
    while line:
        # split the lines by whitespace
        cols = line.split()
        # check for first header line
        if cnt == 1:
            d, t = cols[0], cols[1]
            # parse the line into a datetime object
            time = dt.datetime(int(d[:4]), int(d[5:7]), int(d[8:]),
                               int(t[:2]), int(t[3:5]), int(t[6:]))
            radname = cols[2]
            filetype = cols[3]
            logging.debug(str(time))
        # check for second header line
        elif cnt == 2:
            bmnum = int(cols[2])
            tfreq = int(cols[5])
            scanflg = cols[17]
        # check for third header line
        elif cnt == 3:
            npnts = int(cols[2])
            nrang = int(cols[5])
            channel = cols[8]
            cpid = int(cols[11])
        # check for fourth header line
        elif cnt == 4:
            # empty lists to hold the fitted parameters
            gates, pwr, vel, gsct, vel_err, width = [], [], [], [], [], []
            glat, glon, gazm, mlat, mlon, mazm = [], [], [], [], [], []

            # read all of the reange gates
            for i in range(npnts):
                line = fp.readline()
                cols = line.split()
                # parse the line into the corresponding lists
                gates.append(int(cols[0]))
                pwr.append(float(cols[3]))
                vel.append(float(cols[4]))
                gsct.append(int(cols[5]))
                vel_err.append(float(cols[6]))
                width.append(float(cols[7]))
                glat.append(float(cols[8]))
                glon.append(float(cols[9]))
                gazm.append(float(cols[10]))
                mlat.append(float(cols[11]))
                mlon.append(float(cols[12]))
                mazm.append(float(cols[13]))
            # read the blank line after each record
            line = fp.readline()
            # reset the count
            cnt = 0

        # read the next line
        line = fp.readline()
        cnt += 1

    # close the file
    fp.close()
    # close the pointer created here as well
    myPtr.close()


def fitPrintRec(sTime, eTime, rad, outfile, fileType='fitex', summ=0):
    """A function to print the contents of a fit-type file

    Parameters
    ----------
    sTime : datetime
        the start time as a datetime
    eTime : datetime
        the end time as a datetime
    rad : str 
        the 3 letter radar code, eg 'bks'
    outfile : str
        the txt file we are outputting to
    fileType : Optional[str]
        the filetype to read, 'fitex','fitacf','lmfit';
        default = 'fitex'
    summ : Optional[int]
        option to output a beam summary instead of all data

    Returns
    -------
    Nothing

    Example
    -------
        pydarn.plotting.fitPrintRec(datetime(2011,1,1,1,0),
                                    datetime(2011,1,1,2,0),
                                    'bks', 'myoutfile.txt', summ=1)

    Written by AJ 20130327

    """
    from davitpy import pydarn
    from davitpy import utils
    from davitpy import models

    file_format = ['{date}.{hour}......{radar}.{ftype}',
                   '{date}.{hour}......{radar}...{ftype}']
    myPtr = pydarn.sdio.radDataOpen(sTime, rad, eTime=eTime, fileType=fileType,
                                    local_fnamefmt=file_format,
                                    remote_fnamefmt=file_format)
    if(myPtr is None): return None

    myData = pydarn.sdio.radDataReadRec(myPtr)
    if(myData is None): return None

    radar = pydarn.radar.network().getRadarByCode(rad)
    site = radar.getSiteByDate(myData.time)
    myFov = pydarn.radar.radFov.fov(site=site, rsep=myData.prm.rsep,
                                    ngates=myData.prm.nrang, model=None,
                                    altitude=300.)

    f = open(outfile, 'w')

    t = myData.time

    if(summ == 1):
        f.write('{0:10s} {1:3s} {2:7s}\n'.format(t.strftime("%Y-%m-%d"),
                radar.name, myData))
        f.write('{0:9s} {11:6s} {1:>4s} {2:>5s} {3:>5s} {12:4s} {4:>7s} '
                '{5:>7s} {6:>5s} {7:>5s} {8:>5s} {9:>5s} {10:>4s}\n'.
                format('time', 'beam', 'npnts', 'nrang', 'cpid', 'channel',
                       'tfreq', 'lagfr', 'smsep', 'intt', 'scan', 'us',
                       'rsep'))

    while(myData is not None and myData.time <= eTime):
        t = myData.time
        if(summ == 0):
            # If not interested in the summary, lets print all of the range
            # gate values.  We'll start with the header for each beam sounding.
            f.write(t.strftime("%Y-%m-%d  "))
            f.write(t.strftime("%H:%M:%S  "))
            f.write(radar.name + ' ')
            f.write(myData.fType + '\n')
            f.write('bmnum = ' + str(myData.bmnum))
            f.write('  tfreq = ' + str(myData.prm.tfreq))
            f.write('  sky_noise_lev = ' +
                    str(int(round(float(myData.prm.noisesky)))))
            f.write('  search_noise_lev = ' +
                    str(int(round(float(myData.prm.noisesearch)))))
            f.write('  xcf = ' + str(myData.prm.xcf))
            f.write('  scan = ' + str(+myData.prm.scan) + '\n')
            f.write('npnts = ' + str(len(myData.fit.slist)))
            f.write('  nrang = ' + str(myData.prm.nrang))
            f.write('  channel = ' + str(myData.channel))
            f.write('  cpid = ' + str(myData.cp) + '\n')

            # Write the table column header
            f.write('{0:>4s} {13:>5s} {1:>5s} / {2:<5s} {3:>8s} {4:>3s} '
                    '{5:>8s} {6:>8s} {7:>8s} {8:>8s} {9:>8s} {10:>8s} '
                    '{11:>8s} {12:>8s}\n'.
                    format('gate', 'pwr_0', 'pwr_l', 'vel', 'gsf', 'vel_err',
                           'width_l', 'geo_lat', 'geo_lon', 'geo_azm',
                           'mag_lat', 'mag_lon', 'mag_azm', 'range'))

            # Cycle through each range gate identified as having scatter in
            # the slist
            for i in range(len(myData.fit.slist)):

                d = utils.geoPack.calcDistPnt(
                    myFov.latFull[myData.bmnum][myData.fit.slist[i]],
                    myFov.lonFull[myData.bmnum][myData.fit.slist[i]], 300,
                    distLat=myFov.latFull[myData.bmnum]
                    [myData.fit.slist[i] + 1],
                    distLon=myFov.lonFull[myData.bmnum]
                    [myData.fit.slist[i] + 1],
                    distAlt=300)

                gazm = d['az']

                mlat, mlon, a = models.aacgm.aacgmConv(
                    myFov.latFull[myData.bmnum][myData.fit.slist[i]],
                    myFov.lonFull[myData.bmnum][myData.fit.slist[i]],
                    300, t.year, 0)

                mlat2, mlon2, b = models.aacgm.aacgmConv(
                    myFov.latFull[myData.bmnum][myData.fit.slist[i] + 1],
                    myFov.lonFull[myData.bmnum][myData.fit.slist[i] + 1], 300,
                    t.year, 0)

                d = utils.geoPack.calcDistPnt(mlat, mlon, 300, distLat=mlat2,
                                              distLon=mlon2, distAlt=300)

                mazm = d['az']

                f.write('{0:4d} {13:5d} {1:>5.1f} / {2:<5.1f} {3:>8.1f} '
                        '{4:>3d} {5:>8.1f} {6:>8.1f} {7:>8.2f} {8:>8.2f} '
                        '{9:>8.2f} {10:>8.2f} {11:>8.2f} {12:>8.2f}\n'.
                        format(myData.fit.slist[i], myData.fit.pwr0[i],
                               myData.fit.p_l[i], myData.fit.v[i],
                               myData.fit.gflg[i], myData.fit.v_e[i],
                               myData.fit.w_l[i],
                               myFov.latFull[myData.bmnum]
                               [myData.fit.slist[i]],
                               myFov.lonFull[myData.bmnum]
                               [myData.fit.slist[i]], gazm, mlat, mlon, mazm,
                               myData.prm.frang +
                               myData.fit.slist[i] * myData.prm.rsep))

            f.write('\n')
        # Else write the beam summary for each sounding
        else:
            f.write('{0:9s} {11:6s} {1:>4d} {2:>5d} {3:>5d} {12:>4d} {4:>7d} '
                    '{5:>7d} {6:>5d} {7:>5d} {8:>5d} {9:>5.2f} {10:>4d}\n'.
                    format(t.strftime("%H:%M:%S."), myData.bmnum,
                           len(myData.fit.slist), myData.prm.nrang,
                           myData.cp, myData.channel, myData.prm.tfreq,
                           myData.prm.lagfr, myData.prm.smsep,
                           myData.prm.inttsc + myData.prm.inttus / 1e6,
                           myData.prm.scan, t.strftime("%f"), myData.prm.rsep))

        myData = pydarn.sdio.radDataReadRec(myPtr)
        if(myData is None): break
    # close the file
    f.close()
