import datetime


def AceDstRd( last_email_time = datetime.datetime.today(), nemails = 0 ) :

    
    import time
    import datetime
    import urllib
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    import math
    from time import gmtime, strftime
    import matplotlib
    import urllib2

    # Files to be downloaded and read

    url_acesw = 'http://www.swpc.noaa.gov/ftpdir/lists/ace/ace_swepam_1m.txt'
    url_acemag = 'http://www.swpc.noaa.gov/ftpdir/lists/ace/ace_mag_1m.txt'
    file_acesw = '/home/bharat/Desktop/file_acesw.txt'
    file_acemag = '/home/bharat/Desktop/file_acemag.txt'

    
# First check if the files exist...then proceed otherwise quit    
    try:
       urllib2.urlopen(url_acemag)
       check_url_acemag_exist = 'yes'
    except urllib2.HTTPError, e:
       print e.code
       check_url_acemag_exist = 'no'
    except urllib2.URLError, e:
       print e.args
       check_url_acemag_exist = 'no'
       
    try:
       urllib2.urlopen(url_acesw)
       check_url_acesw_exist = 'yes'
    except urllib2.HTTPError, e:
       print e.code
       check_url_acesw_exist = 'no'
    except urllib2.URLError, e:
       print e.args
       check_url_acesw_exist = 'no'    
    
    if (check_url_acemag_exist == 'yes' and check_url_acesw_exist == 'yes' ) :
	urllib.urlretrieve(url_acesw,file_acesw)
        urllib.urlretrieve(url_acemag,file_acemag)
        
        
        # open the files...loop through them and read data into arrays
        # start with the swepam files...
        f_acesw = open(file_acesw, 'r')
        
        for line in range(0,18):
            header = f_acesw.readline()
        
        np_sw=[]
        vt_sw=[]
        time_sw=[]
    
        
        for line in f_acesw:
            line = line.strip()
            columns = line.split()
        
            hh_sw = int(int(columns[3])/100)
            mm_sw = int(int(columns[3]) % 100)
            time_sw.append(datetime.datetime(int(columns[0]), int(columns[1]), int(columns[2]), hh_sw, mm_sw))
        
            # check for garbage values in the data
            if abs(float(columns[7])) > 100.:
                columns[7] = float('nan')
        
            if abs(float(columns[8])) > 2000.:
                columns[8] = float('nan')
        
            np_sw.append(float(columns[7]))
            vt_sw.append(float(columns[8]))
        
        f_acesw.close()
        
        # Now the mag files...
        f_acemag = open(file_acemag, 'r')
        
        for line in range(0,20):
            header = f_acemag.readline()
        
        
        Bx_mag=[]
        By_mag=[]
        Bz_mag=[]
        time_mag=[]
    
       
        
        for line in f_acemag:
            line = line.strip()
            columns = line.split()
        
            hh_mag = int(int(columns[3])/100)
            mm_mag = int(int(columns[3]) % 100)
            time_mag.append(datetime.datetime(int(columns[0]), int(columns[1]), int(columns[2]), hh_mag, mm_mag))
        
        
            # check for garbage values in the data
            if abs(float(columns[7])) > 100.:
                columns[7] = float('nan')
        
            if abs(float(columns[8])) > 100.:
                columns[8] = float('nan')
        
            if abs(float(columns[9])) > 100.:
                columns[9] = 0.#float('nan')
        
            Bx_mag.append(float(columns[7]))
            By_mag.append(float(columns[8]))
            Bz_mag.append(float(columns[9]))
        
        
        f_acemag.close()
        
        
        # Files to be downloaded and read
        # The url_dst1 is not the complete url, we still have more stuff needed to
        # download data
        url_dst1 = 'http://geomag.usgs.gov/data/indices/Dst_minute/'
        file_dst = '/home/bharat/Desktop/file_dstcurr.txt'
        
        #get the current date parameters for downloading stuff
        cur_UT_year = strftime("%Y", gmtime())
        cur_UT_mon = strftime("%m", gmtime())
        cur_UT_day = strftime("%d", gmtime())
        cur_UT_hour = strftime("%H", gmtime())
        
        # the name of Dst file to download
        Dst_dwnload_file = 'Dst4_'+str(cur_UT_mon)+str(cur_UT_day)+str(cur_UT_year)+'.min'
        
        #Now get the Dst file url you want to download
        url_Dst = url_dst1+Dst_dwnload_file
        
        urllib.urlretrieve(url_Dst,file_dst)
        
        #Open the downloaded Dst file for reading the data
        f_dst = open(file_dst, 'r')
        
        for line in range(0,14):
            header = f_dst.readline()
        
        Dst_val=[]
        datime_Dst=[]
     
        # The data from the files are read into arrays defined above...
        for line in f_dst:
            line = line.strip()
            columns = line.split()
            #first read the date and time from the file and convert it into a datetime object
            date_Dst = datetime.datetime.strptime(columns[0], "%Y-%m-%d").date()
            time_Dst = datetime.datetime.strptime(columns[1], "%H:%M:%S.%f").time()
            datime_Dst.append(datetime.datetime.combine(date_Dst, time_Dst))
            Dst_val.append(float(columns[2]))
        
        
        f_dst.close()
    
        # Calculate the IMF Ey, Boyle Index and Kp-estimated from Boyle required
        # Check if we are multiplying vt and Bz at the same time....
        Ey_IMF_Bz = []
        Boyle_Index = []
        Time_Par = []
        Kp_Boyle = []
        Pdyn = []
            
        # Notes :
        # Boyle index above 100 indicates the presence of geomagnetic activity...
        
        for tmg, tsw, vs, np, bz, by, bx  in zip( time_mag, time_sw, vt_sw, np_sw, Bz_mag, By_mag, Bx_mag ):
            if ( tmg.hour == tsw.hour and tmg.min == tsw.min and not math.isnan( bz )) :
                Time_Par.append( tmg )
                Ey_IMF_Bz.append( -1 * vs * 1000 * bz * 1e-9 * 1e3) # This is in mV/m
                Pdyn.append( 1.6726e-6 * np * math.pow( vs, 2 ) )
                Bt = math.sqrt( math.pow( bz, 2) + math.pow( by, 2 ) + math.pow( bx, 2 ) )
                btheta = math.acos( bz / Bt )
                Boyle_Index.append( 1e-4* math.pow( vs, 2 ) + 11.7*Bt*math.pow( math.sin(btheta/2), 3 ) ) # This is in kV ...
                Kp_Boyle.append( 8.93*math.log10( Boyle_Index[-1] ) - 12.55 )
        
    
        # Calculate the estimated Dst index
        # Constants used
        EDst_a = 3.6 * 1e-5 #/s
        EDst_b = .20 #nT/sqrt(eV/cm^3)
        EDst_c = 20 #nT
        EDst_d = -1.5 * 1e-3 #nT/(s mV/m)
        EDst_d2 = -1.2 * 1e-3 #nT/(s mV/m)
        
        # get the latest updated (real) Dst value from the Dst data
        # This is required as input for the next values....
        
        for dv in reversed( range( len( Dst_val ) ) ) :
            if not math.isnan( Dst_val[ dv ] ) :
                Dst_act_Val_init = Dst_val[ dv ]
                Time_start_init = datime_Dst[ dv ]
                break
                
                
        try :
           Dst_act_Val_init
        except NameError :
           Dst_act_Val_init = 0
        
        Est_Dst_Val = []
        Est_Dst_Time = []
        Dst_Prev_val = Dst_act_Val_init
        for jj in range( len( Time_Par ) ) :
            if ( Time_Par[ jj ].hour >= Time_start_init.hour and Time_Par[ jj ].min >= Time_start_init.min ) :
                Est_Dst_Time.append( Time_Par[ jj ] )
                EDst_FE = EDst_d2 * math.pow( Pdyn[ jj ], 1./3) * (Ey_IMF_Bz[ jj ] - 0.5)
                Est_dst_star = Dst_act_Val_init - EDst_b * math.sqrt( Pdyn[ jj ] ) + EDst_c
                Est_dst_star_ddt = EDst_FE - EDst_a * Est_dst_star
                Est_Dst_Val.append(Dst_Prev_val + Est_dst_star_ddt * 60. ) # Since this is rate of change we multiply 60.
                Dst_Prev_val = Est_Dst_Val[ -1 ]
        
        
        
        #	set the format of the ticks -- major ticks are set for 0,15,30,45 and 60th mins of the hour
        #	minor ticks are set every 5 min.
        xtickHours = matplotlib.dates.HourLocator()
        xtickMins_major = matplotlib.dates.MinuteLocator(byminute=range(0,60,15))
        xtickMins_minor = matplotlib.dates.MinuteLocator(byminute=range(0,60,5))
        
        HMFmt = matplotlib.dates.DateFormatter('%H:%M')
        
        #Plot the ACE data
        
        fig = plt.figure()
        
        ax = fig.add_subplot(611)
        ax.fill_between(time_mag, 0,Bz_mag,label='Bz_GSM',color='r', facecolor = 'gray')
        ax.plot([time_mag[0], time_mag[-1]],[0,0],color='k',linestyle='-')
        ax.plot(time_mag,By_mag,label='By_GSM',color='b',linestyle='--')
        
        #format the ticks
        ax.xaxis.set_major_formatter(HMFmt)
        ax.xaxis.set_major_locator(xtickMins_major)
        ax.xaxis.set_minor_locator(xtickMins_minor)
        ax.set_xticklabels([])
        
        #	set the labels for the plots
        plt.ylabel('IMF [nT]', fontsize=4.5)
        plt.yticks( fontsize=4.5 )
        plt.axis([Time_Par[0],Time_Par[-1],-10.,10.])
        plt.title('REAL TIME ACE DATA : '+str(datetime.datetime.date(time_mag[-1])))
        plt.legend(loc=3,prop={'size':5},shadow=True,fancybox=True)
        
        
        #Plot the solarwind velocity data
        
        ax2 = fig.add_subplot(612)
        ax2.plot(time_sw,vt_sw,color='r')
        
        
        #format the ticks
        ax2.xaxis.set_major_formatter(HMFmt)
        ax2.xaxis.set_major_locator(xtickMins_major)
        ax2.xaxis.set_minor_locator(xtickMins_minor)
        ax2.set_xticklabels([])
        
        plt.ylabel('SW.Vel [km/s]', fontsize=4.5)
        plt.yticks( fontsize=4.5 )
        plt.axis([Time_Par[0],Time_Par[-1],200.,700.])
        
        
        
        #Plot the solarwind Proton Density data
        
        ax3 = fig.add_subplot(613)
        ax3.plot(time_sw,np_sw,color='r')
        
        
        #format the ticks
        ax3.xaxis.set_major_formatter(HMFmt)
        ax3.xaxis.set_major_locator(xtickMins_major)
        ax3.xaxis.set_minor_locator(xtickMins_minor)
        ax3.set_xticklabels([])
        
        #	set the labels for the plots
        plt.ylabel('Np [p/cc]', fontsize=4.5)
        plt.yticks( fontsize=4.5 )
        plt.axis([Time_Par[0],Time_Par[-1],0.,10.])
        
        
        
        # Plot the parameters derived from ACE
        
        ax4 = fig.add_subplot(614)
        ax4.plot_date( Time_Par, Boyle_Index, 'r-' )
        
        ax4.xaxis.set_major_formatter(HMFmt)
        ax4.xaxis.set_major_locator(xtickMins_major)
        ax4.xaxis.set_minor_locator(xtickMins_minor)
        ax4.set_xticklabels([])
        
        #	set the labels for the plots
        plt.ylabel('Boyle-Index [kV]', fontsize=4.5)
        plt.yticks( fontsize=4.5 )
        plt.axis([Time_Par[0],Time_Par[-1],0.,200.])
        
        ax5 = fig.add_subplot(615)
        ax5.plot_date(Time_Par,Kp_Boyle,'r-')
        
        
        #format the ticks
        ax5.xaxis.set_major_formatter(HMFmt)
        ax5.xaxis.set_major_locator(xtickMins_major)
        ax5.xaxis.set_minor_locator(xtickMins_minor)
        ax5.set_xticklabels([])
        
        plt.ylabel('Est. Kp', fontsize=4.5)
        plt.axis([Time_Par[0],Time_Par[-1],0.,9.])
        plt.yticks( [0, 3, 6, 9], fontsize=4.5 )
        
        ax6 = fig.add_subplot(616)
        ax6.plot_date(datime_Dst, Dst_val,'r-')
        #ax6.plot_date(Est_Dst_Time,Est_Dst_Val,'b--')
        
        
        #format the ticks
        ax6.xaxis.set_major_formatter(HMFmt)
        ax6.xaxis.set_major_locator(xtickMins_major)
        ax6.xaxis.set_minor_locator(xtickMins_minor)
        
        
        #	set the labels for the plots
        plt.ylabel('Dst [nT]', fontsize=4.5)
        plt.xticks(rotation=25)
        plt.yticks( fontsize=4.5 )
        plt.axis([Time_Par[0],Time_Par[-1],-150.,50.])
        plt.xlabel('Time (UT)')
        #SAVE The figure
        
        
        #matplotlib.rc('ytick', labelsize = 5.)
        
        fig.savefig('/home/bharat/Desktop/ACE-PAR-RT.pdf',orientation='portrait',papertype='a4',format='pdf')
        plt.close(fig)
        fig.clear()
        
        
        # Now for knowing if there is a storm going on..
        # Get the latest good values of all the parameters...
        for kb in Kp_Boyle[ ::-1 ] :
            if not math.isnan( kb ) :
                Kp_Boyle_latest = kb
                break
        
        for bi in Boyle_Index[ ::-1 ] :
            if not math.isnan( bi ) :
                Boyle_Index_latest = bi
                break        
        
                
        for bz,tm in zip( Bz_mag[ ::-1 ], time_mag[::-1] ) :
            if not math.isnan( bz ) :
                Bz_mag_latest = bz
                Time_mag_latest = tm
                break
        
                
        for by in By_mag[ ::-1 ] :
            if not math.isnan( by ) :
                By_mag_latest = by
                break
                
        for vss in vt_sw[ ::-1 ] :
            if not math.isnan( vss ) :
                vt_sw_latest = vss
                break
        
                
        for npp in np_sw[ ::-1 ] :
            if not math.isnan( npp ) :
                np_sw_latest = npp
                break        
                
                
        for ed in Est_Dst_Val[ ::-1 ] :
            if not math.isnan( ed ) :
                Est_Dst_Val_latest = ed
                break
        
        
        diff_last_latest_time = time_mag[-1] - Time_mag_latest
        
        
        # Storm predictions...
        # Note - Cannot use Np since sometimes it is nan and not reliable
        # Lev 0 : Probably substorm : Bz < -5 but Vsw < = 450, np < 3, BI < 100, Kp < 4
        # Lev 1a : Probably storm : abs(Bz) or abs(By) > 10., vs  > 500
        # Lev 1b : Probably storm : BI > 100. or Kp > 5.
        # Lev 2 : Most likely storm : abs(Bz) > 10., vs > 500, np > 4, BI > 100, Kp > 5
        
        # you dont want to send emails at every run...send them only once in 30 min and 2 at the most
    
        
        #try :
            #last_email_time
        #except NameError :
            #last_email_time = datetime.datetime( 2011, 1, 1 )
        
        now_email_time = datetime.datetime.today()
        diff_email_time = now_email_time - last_email_time
        last_mail_sent = 'no'
        #print last_email_time, new_email_time
        
        
        # Reset the email clock back if it has been more than 24 hours since the last email...
        # We are changing the email clock thingy when sending emails
        #if ( diff_email_time.days >= 1 ) :
            #nemails = 0
            #last_email_time = datetime.datetime( 2011, 1, 1 )
    
        if ( Bz_mag_latest <= -5. and vt_sw_latest <= 450. and np_sw_latest < 3. and Boyle_Index_latest < 100. and Kp_Boyle_latest < 4. and diff_last_latest_time.seconds / 60. < 20. ) :
            ace_subject = ' ACE UPDATE : Substorm activity predicted '
            text_send_mail = 'Current Condition : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest )
            gmail_mail_to = [ "bharatr@vt.edu"  , "mikeruo@vt.edu" ]
            attach = "/home/bharat/Desktop/ACE-PAR-RT.pdf"
            if ( diff_email_time.seconds / 60. > 20. and nemails < 2 ) :
                #send the email
                
                AceDstAlertCall( attach, text_send_mail, ace_subject )
                print 'sending mail..'
                last_email_time = now_email_time
                last_mail_sent = 'yes'
                
                
            
        elif ( ( math.fabs( Bz_mag_latest ) > 10. or math.fabs( By_mag_latest ) > 10. ) and ( vt_sw_latest > 500. ) and ( diff_last_latest_time.seconds / 60. < 20. ) ) :
            ace_subject = ' ACE UPDATE : Probable geomagnetic storm'
            text_send_mail = 'Current Condition : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest )
            gmail_mail_to = [ "bharatr@vt.edu"  , "mikeruo@vt.edu" ]
            attach = "/home/bharat/Desktop/ACE-PAR-RT.pdf"
            if ( diff_email_time.seconds / 60. > 20. and nemails < 2 ) :
                #send the email
                
                AceDstAlertCall( attach, text_send_mail, ace_subject )
                print 'sending mail..'
                last_email_time = now_email_time     
                last_mail_sent = 'yes'
    
            
            
        elif ( ( Boyle_Index_latest > 100. or Kp_Boyle_latest > 5. ) and  ( diff_last_latest_time.seconds / 60. < 20. ) ) :
            ace_subject = ' ACE UPDATE : Probable geomagnetic storm'
            text_send_mail = 'Current Condition : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest )
            gmail_mail_to = [ "bharatr@vt.edu"  , "mikeruo@vt.edu" ]
            attach = "/home/bharat/Desktop/ACE-PAR-RT.pdf"
            if ( diff_email_time.seconds / 60. > 20. and nemails < 2 ) :
                #send the email
                
                AceDstAlertCall( attach, text_send_mail, ace_subject )
                print 'sending mail..'
                last_email_time = now_email_time 
                last_mail_sent = 'yes'
            
            
        elif ( math.fabs( Bz_mag_latest ) > 10. and vt_sw_latest > 500. and np_sw_latest > 4. and Boyle_Index_latest > 100. and Kp_Boyle_latest > 5.  and diff_last_latest_time.seconds / 60. < 20.) :
            ace_subject = ' ACE UPDATE : High possibility of geomagnetic storm'
            text_send_mail = 'Current Condition : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest )
            gmail_mail_to = [ "bharatr@vt.edu" , "mikeruo@vt.edu"  ]
            attach = "/home/bharat/Desktop/ACE-PAR-RT.pdf"
            if ( diff_email_time.seconds / 60. > 20. and nemails < 2 ) :
                #send the email
                
                AceDstAlertCall( attach, text_send_mail, ace_subject )
                print 'sending mail..'
                last_email_time = now_email_time
                last_mail_sent = 'yes'
            
            
        else :
            ace_subject = ' ACE UPDATE : Quiet conditions '
            text_send_mail = 'Current Condition : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest )
            gmail_mail_to = [ "bharatr@vt.edu" , "mikeruo@vt.edu" ]
            attach = "/home/bharat/Desktop/ACE-PAR-RT.pdf"
               
    
        del np_sw, vt_sw, time_sw, Bx_mag, By_mag, Bz_mag, Dst_val, datime_Dst, Ey_IMF_Bz, Boyle_Index, Time_Par, Kp_Boyle, Pdyn, Est_Dst_Val, Est_Dst_Time, 
        ax.clear()
        ax2.clear()
        ax3.clear()
        ax4.clear()
        ax5.clear()
        ax6.clear()
        
        return last_mail_sent
     
    else :
	last_mail_sent = 'no'
	return last_mail_sent
    
       
            
            

def AceDstAlertCall( attach, text, ace_subject ) :
	
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email import Encoders
    import os
    
    gmail_user = "vt.sd.sw@gmail.com"
    gmail_pwd = "more ace"
    gmail_mail_to = [ "bharatr@vt.edu", "mikeruo@vt.edu", "bakerjb@vt.edu" ]
#    ace_subject = "ACE UPDATES"
#    text = "TESTING ACE UPDATE MECHANISM"
#    attach = "/home/bharat/Desktop/ACE-PAR-RT.pdf"
#    gmail_mail_to = [ "bharatr@vt.edu"  ]
    
    msg = MIMEMultipart()
    
    msg['From'] = gmail_user
    msg['To'] = "bharatr@vt.edu"
    msg['Subject'] = ace_subject
    
    msg.attach(MIMEText(text))
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(attach, 'rb').read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
    msg.attach(part)
    
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, gmail_mail_to, msg.as_string())
    mailServer.close()
    
    cmd_alert = "mplayer /usr/share/sounds/gnome/default/alerts/bark.ogg"
    cmd_op_file = "xdg-open /home/bharat/Desktop/ACE-PAR-RT.pdf"
    
#    os.system( cmd_op_file )
    
    for brk in range( 5 ):
        check = os.popen( cmd_alert )
        check.read()
        check.close()

	
def AceDstRunDays():
	import time
	import datetime
	import urllib
	import matplotlib.pyplot as plt
	import matplotlib.gridspec as gridspec
	import math
    	from time import gmtime, strftime
    	import matplotlib
	
	while True:
		
		
		try :
			nemails
		except NameError :
			nemails = 0
		
		try :
			last_email_time
		except NameError :
			last_email_time = datetime.datetime( 2011, 1, 1 )
		
		now_email_time = datetime.datetime.today()
		diff_email_time = now_email_time - last_email_time
		print now_email_time
		
		
		# Reset the email clock back if it has been more than 24 hours since the last email...
    		# We are changing the email clock thingy when sending emails
		if ( diff_email_time.days >= 1 ) :
        		nemails = 0
        		last_email_time = datetime.datetime( 2011, 1, 1 )
			
		last_mail_yesno = AceDstRd( last_email_time = last_email_time, nemails = nemails )
		
		if last_mail_yesno == 'yes' :
			 last_email_time = now_email_time
			 nemails = nemails + 1
		
		time.sleep(60)
