#!/home/opt-user/Enthought/Canopy_64bit/User/bin/python
#from threading import Lock
#lock=Lock()
#import matplotlib
#matplotlib.use('Agg')
import datetime
import csv
import cgi
import os
import calendar
#import matplotlib.pyplot as plt
import numpy as np
import math
import random

# 30.06.2015 - now works with 'old; and 'new' METFiDAS-3 observations

# 29.07.2015 - This version now works from off-campus

# 31.07.2015 - Additional variables included

# 13.08.2015 - Addition of Sonic Licor data - available from 11.08.2015

# 27-30.09.2015 - Some code re-installed after original lost on corrupted disk without a system backup

# 6.2.2017 - markmuetz: Add a DATATYPES list for easier extraction of useful data.
DATATYPES = ["1sec_Level1", "5min_Level1", "5min_Level1_maxmin", "5min_Level2", \
                    "5min_Level2_maxmin", "1hour_Level2", "1hour_Level2_maxmin", "climat0900", \
                    "soniclicor_Level1", "Vertical_profiles", "eddy_cov", "cloudbase_5min", \
                    "cloudbase_1min"]

def main():

  print "Content-type: text/html"
  print

  dateform = cgi.FieldStorage()

  data_type=dateform.getvalue("data_type")
  if 'extraction' in dateform:
    # Perform the extraction
    print '<html>'
    print '<head><title>Perform the METFiDAS observation extractions</title></head>'
    print '<body>'
    print '<p>'
    print '<h3>Perform the data extraction...</h3>'
  
    # copy the required datafile to /tmp and open it
    if data_type in DATATYPES:
      null=general_data_extractor(dateform,data_type)

    print '<h3>...extraction completed</h3>'

    print '<h3>Click <a href='"MODE3.cgi"'>here</a> to process a new extraction</h3>'

    print'</body>'
    print '</html>'
    exit()
    
  print '<html>'
  print '<head><title>METFiDAS-3 extractions</title></head>'
  print '<body>'
#  print '<h3><font color="blue">New version - pseudo-climat 0900 UTC obs extraction enabled - released 10 November 2014<font color="black"></h3>'
#  print '<h3><font color="blue">New version - pressure/MSL pressure extraction enabled - released 29 December 2014<font color="black"></h3>'
#  print '<h3><font color="blue">New version - Up/down-welling radiation added - released 30 June 2015<font color="black"></h3>'
#  print '<h3><font color="blue">New version - Mast wind speeds added - released 31 July 2015<font color="black"></h3>'
#  print '<h3><font color="blue">New version - SonicLicor data added - released 13 August 2015<font color="black"></h3>'
#  print '<h3><font color="blue">New version - SonicLicor data added - modified 17 August 2015<font color="black"></h3>'
#  print '<h3><font color="blue">New version - Vertical profiles data added - modified 27 November 2015<font color="black"></h3>'
#  print '<h3><font color="blue">New version - Eddy covariances added - modified 29 November 2015<font color="black"></h3>'
#  print '<h3><font color="blue">New version - 5-min cloud base sata added - modified 29 November 2015<font color="black"></h3>'
#  print '<h3><font color="blue">New version - 1-min cloud base data added - modified 29 November 2015<font color="black"></h3>'
  print '<h3><font color="blue">Additional soniclicor data added - modified 3 December 2015<font color="black"></h3>'
  print '<h4><font color="red">Note that this code is still under test - please let Roger know of any issues/problems.</h4>'
  print '<h3>**** The code has been re-written after an earlier software loss.<font color="black"></h3>'
  print '<h3>Define data type requirements</h3>'

  print 'Note sure what dataset you need - see <a target="blank" href="./MODE3_help.html">here</a> for advice in a new tab</p>'

  print '<form action="MODE3.cgi" method="post">'

  step1='done'
  if 'data_type' not in dateform:
    null=set_data_type()
    step1='notdone'
  else:
    data_type=show_data_type(dateform)

  if step1=='notdone':
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="continue"><p>'
    print '<INPUT TYPE="Reset"> <i>to reset all option to their default values</i><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()
  
  step23='done'
  if 'start_year' not in dateform:
    null=set_user_datetime(data_type)
    step23='notdone'
  else:
    start_year,start_month,start_day,start_time,end_year,end_month,end_day,end_time= \
        show_datetime(dateform,data_type)

  if step23=='notdone':
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="continue"><p>'
    print '<INPUT TYPE="Reset"> <i>to reset all option to their default values</i><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()

  step4='done'
  if 'MDVAL' not in dateform:
    null=set_mdval()
    step4='notdone'
  else:
    missing_data_value=show_mdval(dateform)

  if step4=='notdone':
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="continue"><p>'
    print '<INPUT TYPE="Reset"> <i>to reset all option to their default values</i><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()

  step5='done'
  if 'TYPES' not in dateform:
    null=set_types()
    step5='notdone'
#  else:
#    missing_data_value=show_types(dateform)

  if step5=='notdone':
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="continue"><p>'
    print '<INPUT TYPE="Reset"> <i>to reset all option to their default values</i><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()
    
  step6='done'
  if 'VARS' not in dateform:
    #define available variables
    var_list,name_list,type_list=define_vars(data_type,'true')
    null=set_vars(data_type,var_list,name_list,type_list,dateform)
    step6='notdone'
  else:
    #define available variables
    var_list,name_list,type_list=define_vars(data_type,'false')
    vars_to_get=show_vars(dateform,var_list,name_list,type_list)

  if step6=='notdone':
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="continue"><p>'
    print '<INPUT TYPE="Reset"> <i>to reset all option to their default values</i><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()

  print '<hr>'
  print 'Click here to <INPUT TYPE="submit" VALUE="continue"><p>'

  print'</form>'
  print'</body>'
  print '</html>'

  exit()
#======================
def general_data_extractor(dateform,data_type):
  # Extract required data from the 5min AVG Level1 files

  null=''
  mlist=["Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
  oneday=datetime.timedelta(days=1)
  now=str(datetime.datetime.now()).replace(' ','_').replace(':','_')
  MDVAL=dateform.getvalue("MDVAL")
  if MDVAL=='blank': MDVAL=''
  var_list,name_list,type_list=define_vars(data_type,'false')

  if data_type=="cloudbase_5min" or data_type=="cloudbase_1min":
    extract_list=['Date']
  else:
    extract_list=['TimeStamp']     # this list will contain the required variables, beginning with time
  if data_type=="5min_Level2" or data_type=="5min_Level2_maxmin" or \
        data_type=="1hour_Level2" or data_type=="1hour_Level2_maxmin" or data_type=="Vertical_profiles":
    extract_list.append('Time')
  elif data_type=="climat0900" or data_type=="cloudbase_5min" or data_type=="cloudbase_1min":
    extract_list.append('Time')
  elif data_type=="eddy_cov":
    extract_list=['TIME']
  for i in range(0,len(var_list)):
    if var_list[i] in dateform: extract_list.append(var_list[i].replace('%',' '))
  extract_list.append('XXXXtest')

  # Column headers can be copied from the entries in extract_list
  # Now set up column units list
  # Set up lists to hold the extracted data
  obsdata={'TimeStamp':[]}
  unitsdata={'TimeStamp':[]}
  for i in range(0,len(extract_list)):
    obsdata[extract_list[i]]=[]
    unitsdata[extract_list[i]]=[]
    unitsdata[extract_list[i]].append('')

  #Step 1 - create a list of files required = filelist[...]
  filelist=[]
  # There is one file per day of data
  hhmm1=int(dateform.getvalue("start_time"))
  d1=int(dateform.getvalue("start_day")  )
  mon1=dateform.getvalue("start_month") 
  y1=int(dateform.getvalue("start_year")  )
  hhmm2=int(dateform.getvalue("end_time"))
  d2=int(dateform.getvalue("end_day"))
  mon2=dateform.getvalue("end_month")  
  y2=int(dateform.getvalue("end_year"))

  for i in range(0,len(mlist)):
    if mlist[i]==mon1: m1=i
    if mlist[i]==mon2: m2=i
  date1=datetime.date(y1,m1,d1)
  date2=datetime.date(y2,m2,d2)

  ymdhm1=hhmm1+d1*10000+m1*1000000+y1*100000000
  ymdhm2=hhmm2+d2*10000+m2*1000000+y2*100000000

  d=date1     # starting date for the file loop
  endloop='false'
  while endloop=='false':
    dtuple=d.timetuple()
    ymd_file=int(dtuple[0])*10000+int(dtuple[1])*100+int(dtuple[2])

    if data_type=="eddy_cov" and ymd_file >= 20150923:
        datadir='/home/webbie/micromet/LUMA/RUAO'
        datafile='ReadingFlux_'+str(dtuple[0]).zfill(3)+str(dtuple[7]).zfill(3)+'.csv'
    elif data_type=="cloudbase_5min" and ymd_file >= 20150319:
        datadir='/export/its/labs/Ceilometer-Incoming/Level2/5min/'+str(dtuple[0])
        datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min.csv'
    elif data_type=="cloudbase_1min":
        datadir='/export/its/labs/Ceilometer-Incoming/Level2/1min/'+str(dtuple[0])
        datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1min.csv'
    elif data_type=="climat0900":
      if ymd_file >= 20150416:
        # datadir='/export/labserver/data/METFiDAS-3/Level2/climat'
        datadir='/export/its/labs/METFiDAS-Incoming/Level2/climat'
        datafile=str(dtuple[0])+'climat.csv'
      elif ymd_file >= 20140901:
        datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/climat'
        datafile=str(dtuple[0])+'climat.csv'
    elif data_type=="Vertical_profiles":
      if ymd_file >= 20150819:
        # datadir='/export/labserver/data/METFiDAS-3/Level2/climat'
        datadir='/export/its/labs/METFiDAS-Incoming/Level2/profile/'+str(dtuple[0])
        datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_UTprofile.csv'
    else:
      if ymd_file >= 20150429:
        if data_type=="1sec_Level1":
          # datadir='/export/labserver/data/METFiDAS-3/Level1/'+str(dtuple[0])
          datadir='/export/its/labs/METFiDAS-Incoming/Level1/'+str(dtuple[0])
          datafile=str(dtuple[0]).zfill(3)+'-SMP1-'+str(dtuple[7]).zfill(3)+'.csv'
        elif data_type=="5min_Level1":
          # datadir='/export/labserver/data/METFiDAS-3/Level1/'+str(dtuple[0])
          datadir='/export/its/labs/METFiDAS-Incoming/Level1/'+str(dtuple[0])
          datafile=str(dtuple[0]).zfill(3)+'-AVG5-'+str(dtuple[7]).zfill(3)+'.csv'
        elif data_type=="5min_Level1_maxmin":
          # datadir='/export/labserver/data/METFiDAS-3/Level1/'+str(dtuple[0])
          datadir='/export/its/labs/METFiDAS-Incoming/Level1/'+str(dtuple[0])
          datafile=str(dtuple[0]).zfill(3)+'-MMX5-'+str(dtuple[7]).zfill(3)+'.csv'
        elif data_type=="5min_Level2":
          # datadir='/export/labserver/data/METFiDAS-3/Level2/5min/'+str(dtuple[0])
          datadir='/export/its/labs/METFiDAS-Incoming/Level2/5min/'+str(dtuple[0])
          datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min.csv'
        elif data_type=="5min_Level2_maxmin":
          # datadir='/export/labserver/data/METFiDAS-3/Level2/5min/'+str(dtuple[0])
          datadir='/export/its/labs/METFiDAS-Incoming/Level2/5min/'+str(dtuple[0])
          datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min_maxmin.csv'
        elif data_type=="1hour_Level2":
          # datadir='/export/labserver/data/METFiDAS-3/Level2/1hour/'+str(dtuple[0])
          datadir='/export/its/labs/METFiDAS-Incoming/Level2/1hour/'+str(dtuple[0])
          datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1hour.csv'
        elif data_type=="1hour_Level2_maxmin":
          # datadir='/export/labserver/data/METFiDAS-3/Level2/1hour/'+str(dtuple[0])
          datadir='/export/its/labs/METFiDAS-Incoming/Level2/1hour/'+str(dtuple[0])
          datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1hour_maxmin.csv'
        elif data_type=="soniclicor_Level1":
          datadir='/export/its/labs/SonicLicor-Incoming/Level1/'+str(dtuple[0])
          datafile=str(dtuple[0]).zfill(3)+'-SMP-'+str(dtuple[7]).zfill(3)+'.csv'
      elif ymd_file >= 20140901:
        if data_type=="1sec_Level1":
          datadir='/export/its/labs/labserver_files/METFiDAS-3/Level1/'+str(dtuple[0])
          datafile=str(dtuple[0]).zfill(3)+'-SMP1-'+str(dtuple[7]).zfill(3)+'.csv'
        elif data_type=="5min_Level1":
          datadir='/export/its/labs/labserver_files/METFiDAS-3/Level1/'+str(dtuple[0])
          datafile=str(dtuple[0]).zfill(3)+'-AVG5-'+str(dtuple[7]).zfill(3)+'.csv'
        elif data_type=="5min_Level1_maxmin":
          datadir='/export/its/labs/labserver_files/METFiDAS-3/Level1/'+str(dtuple[0])
          datafile=str(dtuple[0]).zfill(3)+'-MMX5-'+str(dtuple[7]).zfill(3)+'.csv'
        elif data_type=="5min_Level2":
          datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/5min/'+str(dtuple[0])
          datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min.csv'
        elif data_type=="5min_Level2_maxmin":
          datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/5min/'+str(dtuple[0])
          datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_5min_maxmin.csv'
        elif data_type=="1hour_Level2":
          datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/1hour/'+str(dtuple[0])
          datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1hour.csv'
        elif data_type=="1hour_Level2_maxmin":
          datadir='/export/its/labs/labserver_files/METFiDAS-3/Level2/1hour/'+str(dtuple[0])
          datafile=str(dtuple[0])+str(dtuple[1]).zfill(2)+str(dtuple[2]).zfill(2)+'_1hour_maxmin.csv'

    if data_type=="climat0900":
      if datadir+'/'+datafile not in filelist:
        filelist.append(datadir+'/'+datafile)
    else:
      #modified 01.12.2015 in case datafile is missing in sequence
      dfile=datadir+'/'+datafile
      if os.path.lexists(dfile) == True: filelist.append(dfile)
    d=d+oneday
    if d > date2: endloop='true' # causes the looping to end

  # Process each file in turn
  data_records=0
  for file in filelist:
    #Step2 - take a copy of each file and place in /tmp/timenow_filename
    if data_type=="5min_Level2_maxmin":
      filename=file[len(file)-24:len(file)]
    elif data_type=="1hour_Level2":
      filename=file[len(file)-18:len(file)]
    elif data_type=="1hour_Level2_maxmin":
      filename=file[len(file)-25:len(file)]
    elif data_type=="climat0900":
      filename=file[len(file)-14:len(file)]
    elif data_type=="soniclicor_Level1":
      filename=file[len(file)-16:len(file)]
    elif data_type=="Vertical_profiles":
      filename=file[len(file)-22:len(file)]
    elif data_type=="eddy_cov":
      filename=file[len(file)-23:len(file)]
    else:
      filename=file[len(file)-17:len(file)]
    
    random_numberf=random.random()
    rrf=int(random_numberf*1000000.0)
    tempfile='/tmp/'+now+str(rrf)+filename
    tempfile='/tmp/'+str(rrf)+filename
    os.system('cp '+file+' '+tempfile)
    # open the file
    print '<b>processing file ',filename,'</b><br>'
    obs=open(tempfile,'r')
    obs_rows=csv.reader(obs)
    
    rec=0
    cols_to_use=[]
    header=[]
    # i.e. TimeStamp = 25/09/2014 00:00:01
    for row in obs_rows:
      if rec==0:
        ientry=0
        for entry in extract_list:
          cols_to_use.append(-99) # increment the list by one dummy (-99) value
          for i in range(0,len(row)):
	    if ientry==0: header.append(row[i]) # ientry means we only do this for first 'entry' value
	    if entry==row[i]: cols_to_use[len(cols_to_use)-1]=i # update the last entry
	  ientry=1
        if len(cols_to_use)!=len(extract_list):
          print ' Warning - some data not found at this time<p>'
      elif rec==1:
        for i in range(0,len(header)):
          for j in range(0,len(extract_list)):
            if header[i]==extract_list[j]: 
	      unitsdata[header[i]][0]=row[i]
      else:
        # check time
        ok1='true'
	ok2='true'
        if file==filelist[0]:
          if data_type=="5min_Level2" or data_type=="5min_Level2_maxmin" or \
	        data_type=="1hour_Level2" or data_type=="1hour_Level2_maxmin" or \
		data_type=="climat0900" or data_type=="Vertical_profiles" or \
		data_type=="cloudbase_5min" or data_type=="cloudbase_1min":
	    yymmdd_now=int(row[0]) ; hhmm_now=int(row[1])
	  elif data_type=='eddy_cov' :
	    yymmdd_now=int(row[0][0:4])*10000+int(row[0][5:7])*100+int(row[0][8:10])
            hhmm_now=int(row[0][11:13])*100+int(row[0][14:16])
          else:
	    yymmdd_now=int(row[0][6:10])*10000+int(row[0][3:5])*100+int(row[0][0:2])
            hhmm_now=int(row[0][11:13])*100+int(row[0][14:16])
          time_now=yymmdd_now*10000+hhmm_now
          if time_now<ymdhm1: ok1='false'
        if file==filelist[len(filelist)-1]:
          if data_type=="5min_Level2" or data_type=="5min_Level2_maxmin" or \
	        data_type=="1hour_Level2" or data_type=="1hour_Level2_maxmin" or \
		data_type=="climat0900" or data_type=="Vertical_profiles" or \
		data_type=="cloudbase_5min" or data_type=="cloudbase_1min":
	    yymmdd_now=int(row[0]) ; hhmm_now=int(row[1])
	  elif data_type=='eddy_cov' :
	    yymmdd_now=int(row[0][0:4])*10000+int(row[0][5:7])*100+int(row[0][8:10])
            hhmm_now=int(row[0][11:13])*100+int(row[0][14:16])
	  else:
	    yymmdd_now=int(row[0][6:10])*10000+int(row[0][3:5])*100+int(row[0][0:2])
	    hhmm_now=int(row[0][11:13])*100+int(row[0][14:16])
          time_now=yymmdd_now*10000+hhmm_now
          if time_now>ymdhm2: 
	    ok2='false'
        if ok1=='true' and ok2=='true':
          for i in range(0,len(cols_to_use)):
	    if cols_to_use[i]>=0:
              if data_type=='eddy_cov' and row[cols_to_use[i]].strip()=='NA':
                # final two characters 'NA' are preceded by a varying number of blanks
	        obsdata[extract_list[i]].append(MDVAL)
	      elif row[cols_to_use[i]]!='':
  	        obsdata[extract_list[i]].append(row[cols_to_use[i]])
	      else:
	        obsdata[extract_list[i]].append(MDVAL)	    
  	    else:
	      obsdata[extract_list[i]].append(MDVAL)
          data_records=data_records+1
      rec=rec+1
   
    # close and delete the file
    obs.close()
    os.system('/bin/rm -r '+tempfile)

  # Now save the data to a file
  random_number=random.random()
  rr=int(random_number*1000000.0)
  outputfile='/home/webbie/Data/EPHEMERAL/MODE3_'+now[0:10]+'_'+str(date1)+'_'+str(date2)+'_d'+str(rr)+'LU.csv'
  webfile='http://www.met.rdg.ac.uk/Data/EPHEMERAL/MODE3_'+now[0:10]+'_'+str(date1)+'_'+str(date2)+'_d'+str(rr)+'LU.csv'
  # print '<i>NOTE for Roger: add code to delete old outputfile files</i><p>\n'
  #os.system('/bin/rm -r /home/webbie/Data/EPHEMERAL/MODE3_*')
  output=open(outputfile,'w')

  # code added 20150731 to delete older files
  NOW=datetime.datetime.now()
  twomonths=datetime.timedelta(weeks=10)
  d1=NOW-twomonths
  cutoff=NOW-oneday
  while d1< cutoff:
    os.system('/bin/rm -f /home/webbie/Data/EPHEMERAL/MODE3_'+str(d1)[0:10]+'*LU.csv')
    d1=d1+oneday

  # write header
  if data_type=='eddy_cov':
    #split TIME into data and time
    output.write('DATE,TIME')
  else:
    output.write(str(extract_list[0]))
  for i in range(1,len(extract_list)-1):
    output.write(','+str(extract_list[i]))
  output.write('\n')

  # write units
  if data_type=='eddy_cov':
    #split TIME into data and time
    output.write('yyyy-mm-dd,hh:mm:ss')
  else:
    output.write(str(unitsdata[extract_list[0]][0]))
  for i in range(1,len(extract_list)-1):
    output.write(','+str(unitsdata[extract_list[i]][0]))
  output.write('\n')

  # Finally output the data
  if data_type=='eddy_cov':
    for rec in range(0,data_records):
      #split TIME into data and time
      output.write(str(obsdata[extract_list[0]][rec][0:10]))
      output.write(','+str(obsdata[extract_list[0]][rec][11:19]))
      for i in range(1,len(extract_list)-1):
        output.write(','+str(obsdata[extract_list[i]][rec]))
      output.write('\n')
  else:
    for rec in range(0,data_records):
      output.write(str(obsdata[extract_list[0]][rec]))
      for i in range(1,len(extract_list)-1):
        output.write(','+str(obsdata[extract_list[i]][rec]))
      output.write('\n')

  output.close()
  print 'Your output can be found <a href="'+webfile+'">here</a>.<br>'
  return null
#======================
def show_vars(dateform,var_list,name_list,type_list):
  vars_to_get=[]
  x=dateform.getvalue("VARS")
  strval=str(x)
  count=0
  
  print '<font color="blue">Variables chosen:</p>'
  for i in range(len(var_list)): 
    if var_list[i] in dateform: 
      count=count+1
      vars_to_get.append(var_list[i])
      print '<input type="hidden" name='+var_list[i]+' value=',"T",'>'
      print name_list[i],'<br>'

  print '<font color="black"></p>'
  if count!=0: 
    print '<p><input type="hidden" name="extraction" value=',"true",'>'
    print '<p><input type="hidden" name="VARS" value=',"done",'>'
    print '<p><input type="hidden" name="TYPES" value=',"done",'>'
  else:
    print '<b><font color="red">No variables selected</b><font color="black">'

  return vars_to_get
#======================
def set_types():
  null=''
  print '<p><b>Step 5 - select the general variables types of interest</b></p>'
  print '<p><input type="hidden" name="TYPES" value=',"true",'>'

  print 'Note that your exact choice will be refined in the next step.<br>'
  print '<b><i>You can keep all these boxes unticked and click "continue" if you wish.</i></b><p>'
  print '<table>'
  print '<tr><td> <input type="checkbox" name=typetemp value="y">Temperature'
  print '<tr><td> <input type="checkbox" name=typerain value="y">Rainfall'
  print '<tr><td> <input type="checkbox" name=typesrad value="y">Sun/radiation'
  print '<tr><td> <input type="checkbox" name=typewind value="y">Wind'
  print '<tr><td> <input type="checkbox" name=typepres value="y">Pressure'
  print '</table>'
  return null
#======================
def set_vars(data_type,var_list,name_list,type_list,dateform):
  null=''
  print '<p><b>Step 6 - select the variables to be extracted</b></p>'
  print '<p><input type="hidden" name="VARS" value=',"true",'>'
  print '<p><input type="hidden" name="TYPES" value=',"true",'>'

  print 'If the data you expect to find are not shown below, please contact Roger Brugge<p>'
  print '<table>'

  for i in range(0,len(var_list),4):
    checked=' '
    if data_type=='soniclicor_Level1' or data_type=='eddy_cov': checked=' checked'
    if type_list[i] in dateform: checked=' checked'
    print '<tr><td> <input type="checkbox" name=',var_list[i],checked,' value="y">',name_list[i],'<br>'

    if i+1<=len(var_list)-1: 
      checked=' '
      if data_type=='soniclicor_Level1' or data_type=='eddy_cov': checked=' checked'
      if type_list[i+1] in dateform: checked=' checked'
      print '<td> <input type="checkbox" name=',var_list[i+1],checked,' value="y">',name_list[i+1],'<br>'

    if i+2<=len(var_list)-1: 
      checked=' '
      if data_type=='soniclicor_Level1' or data_type=='eddy_cov': checked=' checked'
      if type_list[i+2] in dateform: checked=' checked'
      print '<td> <input type="checkbox" name=',var_list[i+2],checked,' value="y">',name_list[i+2],'<br>'

    if i+3<=len(var_list)-1: 
      checked=' '
      if data_type=='soniclicor_Level1' or data_type=='eddy_cov': checked=' checked'
      if type_list[i+3] in dateform: checked=' checked'
      print '<td> <input type="checkbox" name=',var_list[i+3],checked,' value="y">',name_list[i+3],'<br>'
  print '</table>'
  return null
#======================
def define_vars(data_type,header):
  # define variables available for output; these may evolve in time and the lists below will
  # then need to be updated - as will ther variable lists defined for each data_type
  var_list=[]; name_list=[]; type_list=[]

  # typenull is used for a variable that will not be selected by default in Step 5
  
  if data_type=="1sec_Level1":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 31.Jul.2015<p>'
    var_list=['RH','Sdur','Td','Tconc','Tgrass','Tsoil','TSoil5','TSoil10','TSoil20','TSoil30', \
              'TSoil50','TSoil100','Sb','Tw','Ch28','Rn','Sg','Sd','Ch32','Ch33','G','PG','R38', \
	      'iCP','iFP','Dirn5','U2','U5','Rain','P','Dirn10','U10', \
	      'Sdw','Suw','Ldw(uc)','Luw(uc)','CNR4T', \
	      'Sb(csd3)','PointDischarge','U0.56','U0.8','U1.12','U1.6','U2.24','U3.2','U4.48','U6.4', \
	      'T0.56','T1.12','T2.24','T4.48','U','V','W']

    name_list=['Relative humidity', \
               '1sec sunshine','Dry bulb temperature', \
               'Concrete temperature','Grass temperature', \
	       'Bare soil temperature','5cm soil temperatrure', \
	       '10cm soil temperature','20cm soil temperature', \
	       '30cm soil temperature','50cm soil temperature', \
	       '100cm soil temperature','Direct beam solar radiation', \
	       'Measured wet bulb temperature','Channel 28', \
	       'Net radiative heat flux','Global solar radiation', \
	       'Diffuse solar radiation','Channel 32', \
	       'Channel 33','Ground heat flux', \
	       'Potential gradient','R38', \
	       'Corrugated plate current','Flat plate current', \
	       '5m wind direction','2m wind speed','5m wind speed','1sec rainfall','Station pressure', \
	       '10m wind direction','10m wind speed', \
	       'Shortwave-down','Shortwave-up','Longwave-down(uncorrected)','Longwave-up(uncorrected)', \
	       'CNR4 radiometer temp', \
	       'Sb(csd3)','PointDischarge','0.56m wind','0.8m wind','1.12m wind','1.6m wind','2.24m wind', \
	       '3.2m wind','4.48m wind','6.4m wind','0.56m temperature','1.12m temperature',\
	       '2.24m temperature','4.48m temperature','Propeller U','Propellor V','Propellor W' ]
    type_list=['typetemp','typesrad','typetemp','typetemp','typetemp','typetemp', \
               'typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
	       'typesrad','typetemp','typenull','typesrad','typesrad','typesrad', \
	       'typenull','typenull','typesrad','typenull','typenull', \
	       'typenull','typenull','typewind','typewind','typewind','typerain','typepres', \
	       'typewind','typewind','typesrad','typesrad','typesrad','typesrad','typesrad', \
	       'typesrad','typenull','typewind','typewind','typewind','typewind', \
	       'typewind','typewind','typewind','typewind','typetemp','typetemp','typetemp','typetemp', \
	       'typewind','typewind','typewind']
	       
  elif data_type=="5min_Level1":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 31.Jul.2015<p>'
    var_list=['RH','Sdur','Td','Tconc','Tgrass','Tsoil','TSoil5','TSoil10','TSoil20','TSoil30', \
              'TSoil50','TSoil100','Sb','Tw','Ch28','Rn','Sg','Sd','Ch32','Ch33','G','PG','R38', \
	      'iCP','iFP','Dirn5','U2','U5','Rain','P','Dirn10','U10', \
	      'Sdw','Suw','Ldw(uc)','Luw(uc)','CNR4T', \
	      'Sb(csd3)','PointDischarge','U0.56','U0.8','U1.12','U1.6','U2.24','U3.2','U4.48','U6.4', \
	      'T0.56','T1.12','T2.24','T4.48','U','V','W']

    name_list=['Relative humidity', \
               '1sec sunshine','Dry bulb temperature', \
               'Concrete temperature','Grass temperature', \
	       'Bare soil temperature','5cm soil temperatrure', \
	       '10cm soil temperature','20cm soil temperature', \
	       '30cm soil temperature','50cm soil temperature', \
	       '100cm soil temperature','Direct beam solar radiation', \
	       'Measured wet bulb temperature','Channel 28', \
	       'Net radiative heat flux','Global solar radiation', \
	       'Diffuse solar radiation','Channel 32', \
	       'Channel 33','Ground heat flux', \
	       'Potential gradient','R38', \
	       'Corrugated plate current','Flat plate current', \
	       '5m wind direction','2m wind speed','5m wind speed','1sec rainfall','Station pressure', \
	       '10m wind direction','10m wind speed', \
	       'Shortwave-down','Shortwave-up','Longwave-down(uncorrected)','Longwave-up(uncorrected)', \
	       'CNR4 radiometer temp', \
	       'Sb(csd3)','PointDischarge','0.56m wind','0.8m wind','1.12m wind','1.6m wind','2.24m wind', \
	       '3.2m wind','4.48m wind','6.4m wind','0.56m temperature','1.12m temperature','2.24m temperature', \
	       '4.48m temperature','Propeller U','Propellor V','Propellor W']
    type_list=['typetemp','typesrad','typetemp','typetemp','typetemp','typetemp', \
               'typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
	       'typesrad','typetemp','typenull','typesrad','typesrad','typesrad', \
	       'typenull','typenull','typesrad','typenull','typenull', \
	       'typenull','typenull','typewind','typewind','typewind','typerain','typepres', \
	       'typewind','typewind','typesrad','typesrad','typesrad','typesrad','typesrad', \
	       'typesrad','typenull','typewind','typewind','typewind','typewind', \
	       'typewind','typewind','typewind','typewind','typetemp','typetemp','typetemp','typetemp', \
	       'typewind','typewind','typewind']

  elif data_type=="5min_Level1_maxmin":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 31.Jul.2015<p>'
    # Note to programmer: any entry like 'XX[yyy t]' will be handled via dateform as XX[yyy]'  - so replace spaces here with '%'
    # But remember to change these %'s later inhe data extraction routine
    var_list=['RH[min]','RH[max]','RH[min%t]','RH[max%t]', \
	      'Sdur[min]','Sdur[max]','Sdur[min%t]','Sdur[max%t]', \
	      'Td[min]','Td[max]','Td[min%t]','Td[max%t]', \
	      'Tconc[min]','Tconc[max]','Tconc[min%t]','Tconc[max%t]', \
	      'Tgrass[min]','Tgrass[max]','Tgrass[min%t]','Tgrass[max%t]', \
	      'Tsoil[min]','Tsoil[max]','Tsoil[min%t]','Tsoil[max%t]', \
	      'TSoil5[min]','TSoil5[max]','TSoil5[min%t]','TSoil5[max%t]', \
	      'TSoil10[min]','TSoil10[max]','TSoil10[min%t]','TSoil10[max%t]', \
	      'TSoil20[min]','TSoil20[max]','TSoil20[min%t]','TSoil20[max%t]', \
	      'TSoil30[min]','TSoil30[max]','TSoil30[min%t]','TSoil30[max%t]', \
	      'TSoil50[min]','TSoil50[max]','TSoil50[min%t]','TSoil50[max%t]', \
	      'TSoil100[min]','TSoil100[max]','TSoil100[min%t]','TSoil100[max%t]', \
	      'Sb[min]','Sb[max]','Sb[min%t]','Sb[max%t]', \
	      'Tw[min]','Tw[max]','Tw[min%t]','Tw[max%t]', \
	      'Ch28[min]','Ch28[max]','Ch28[min%t]','Ch28[max%t]', \
	      'Rn[min]','Rn[max]','Rn[min%t]','Rn[max%t]', \
	      'Sg[min]','Sg[max]','Sg[min%t]','Sg[max%t]', \
	      'Sd[min]','Sd[max]','Sd[min%t]','Sd[max%t]', \
	      'Ch32[min]','Ch32[max]','Ch32[min%t]','Ch32[max%t]', \
	      'Ch33[min]','Ch33[max]','Ch33[min%t]','Ch33[max%t]', \
	      'G[min]','G[max]','G[min%t]','G[max%t]', \
	      'PG[min]','PG[max]','PG[min%t]','PG[max%t]', \
	      'R38[min]','R38[max]','R38[min%t]','R38[max%t]', \
	      'iCP[min]','iCP[max]','iCP[min%t]','iCP[max%t]', \
	      'iFP[min]','iFP[max]','iFP[min%t]','iFP[max%t]', \
	      'Dirn5[min]','Dirn5[max]','Dirn5[min%t]','Dirn5[max%t]', \
	      'U2[min]','U2[max]','U2[min%t]','U2[max%t]', \
	      'U5[min]','U5[max]','U5[min%t]','U5[max%t]', \
	      'Rain[min]','Rain[max]','Rain[min%t]','Rain[max%t]', \
	      'P[min]','P[max]','P[min%t]','P[max%t]', \
	      'Dirn10[min]','Dirn10[max]','Dirn10[min%t]','Dirn10[max%t]', \
	      'U10[min]','U10[max]','U10[min%t]','U10[max%t]', \
	      'Sdw[min]','Sdw[max]','Sdw[min%t]','Sdw[max%t]', \
	      'Suw[min]','Suw[max]','Suw[min%t]','Suw[max%t]', \
	      'Ldw(uc)[min]','Ldw(uc)[max]','Ldw(uc)[min%t]','Ldw(uc)[max%t]', \
	      'Luw(uc)[min]','Luw(uc)[max]','Luw(uc)[min%t]','Luw(uc)[max%t]', \
	      'CNR4T[min]','CNR4T[max]','CNR4T[min%t]','CNR4T[max%t]', \
              'Sb(csd3)[min]','Sb(csd3)[max]','Sb(csd3)[min%t]','Sb(csd3)[max%t]', \
              'PointDischarge[min]','PointDischarge[max]','PointDischarge[min%t]','PointDischarge[max%t]', \
              'U0.56[min]','U0.56[max]','U0.56[min%t]','U0.56[max%t]', \
              'U0.8[min]','U0.8[max]','U0.8[min%t]','U0.8[max%t]', \
              'U1.12[min]','U1.12[max]','U1.12[min%t]','U1.12[max%t]', \
              'U1.6[min]','U1.6[max]','U1.6[min%t]','U1.6[max%t]', \
              'U2.24[min]','U2.24[max]','U2.24[min%t]','U2.24[max%t]', \
              'U3.2[min]','U3.2[max]','U3.2[min%t]','U3.2[max%t]', \
              'U4.48[min]','U4.48[max]','U4.48[min%t]','U4.48[max%t]', \
              'U6.4[min]','U6.4[max]','U6.4[min%t]','U6.4[max%t]', \
              'T0.56[min]','T0.56[max]','T0.56[min%t]','T0.56[max%t]', \
              'T1.12[min]','T1.12[max]','T1.12[min%t]','T1.12[max%t]', \
              'T2.24[min]','T2.24[max]','T2.24[min%t]','T2.24[max%t]', \
              'T4.48[min]','T4.48[max]','T4.48[min%t]','T4.48[max%t]' ]

    name_list=['Relative humidity[min]','Relative humidity[max]', \
              'Relative humidity[min t]','Relative humidity[max t]', \
	      '5min sunshine[min]','5min sunshine[max]', \
	      '5min sunshine[min t]','5min sunshine[max t]', \
	      'Dry bulb temperature[min]','Dry bulb temperature[max]', \
	      'Dry bulb temperature[min t]','Dry bulb temperature[max t]', \
	      'Concrete temperature[min]','Concrete temperature[max]', \
	      'Concrete temperature[min t]','Concrete temperature[max t]', \
	      'Grass temperature[min]','Grass temperature[max]', \
	      'Grass temperature[min t]','Grass temperature[max t]', \
	      'Bare soil temperature[min]','Bare soil temperature[max]', \
	      'Bare soil temperature[min t]','Bare soil temperature[max t]', \
	      '5cm soil temperature[min]','5cm soil temperature[max]', \
	      '5cm soil temperature[min t]','5cm soil temperature[max t]', \
	      '10cm soil temperature[min]','10cm soil temperature[max]', \
	      '10cm soil temperature[min t]','10cm soil temperature[max t]', \
	      '20cm soil temperature[min]','20cm soil temperature[max]', \
	      '20cm soil temperature[min t]','20cm soil temperature[max t]', \
	      '30cm soil temperature[min]','30cm soil temperature[max]', \
	      '30cm soil temperature[min t]','30cm soil temperature[max t]',
	      '50cm soil temperature[min]','50cm soil temperature[max]', \
	      '50cm soil temperature[min t]','50cm soil temperature[max t]', \
	      '100cm soil temperature[min]','100cm soil temperature[max]', \
	      '100cm soil temperature[min t]','100cm soil temperature[max t]', \
	      'Direct beam solar radiation[min]','Direct beam solar radiation[max]', \
	      'Direct beam solar radiation[min t]','Direct beam solar radiation[max t]', \
	      'Measured wet bulb temperature[min]','Measured wet bulb temperature[max]', \
	      'Measured wet bulb temperature[min t]','Measured wet bulb temperature[max t]', \
	      'Ch28[min]','Ch28[max]','Ch28[min t]','Ch28[max t]', \
	      'Net radiative heat flux[min]','Net radiative heat flux[max]', \
	      'Net radiative heat flux[min t]','Net radiative heat flux[max t]', \
	      'Global solar radiation[min]','Global solar radiation[max]', \
	      'Global solar radiation[min t]','Global solar radiation[max t]', \
	      'Diffuse solar radiation[min]','Diffuse solar radiation[max]', \
	      'Diffuse solar radiation[min t]','Diffuse solar radiation[max t]', \
	      'Ch32[min]','Ch32[max]','Ch32[min t]','Ch32[max t]', \
	      'Ch33[min]','Ch33[max]','Ch33[min t]','Ch33[max t]', \
	      'Ground heat flux[min]','Ground heat flux[max]', \
	      'Ground heat flux[min t]','Ground heat flux[max t]', \
	      'Potential gradient[min]','Potential gradient[max]', \
	      'Potential gradient[min t]','Potential gradient[max t]', \
	      'R38[min]','R38[max]','R38[min t]','R38[max t]', \
	      'Corrugated plate current[min]','Corrugated plate current[max]', \
	      'Corrugated plate current[min t]','Corrugated plate current[max t]', \
	      'Flat plate current[min]','Flat plate current[max]', \
	      'Flat plate current[min t]','Flat plate current[max t]', \
	      '5m wind direction[min]','5m wind direction[max]', \
	      '5m wind direction[min t]','5m wind direction[max t]', \
	      '2m wind speed[min]','2m wind speed[max]', \
	      '2m wind speed[min t]','2m wind speed[max t]', \
	      '5m wind speed[min]','5m wind speed[max]', \
	      '5m wind speed[min t]','5m wind speed[max t]', \
	      '5min rainfall[min]','5min rainfall[max]', \
	      '5min rainfall[min t]','5min rainfall[max t]', \
	      'Station pressure[min]','Station pressure[max]', \
	      'Station pressure[min t]','Station pressure[max t]', \
	      '10m wind direction[min]','10m wind direction[max]', \
	      '10m wind direction[min t]','10m wind direction[max t]', \
	      '10m wind speed[min]','10m wind speed[max]', \
	      '10m wind speed[min t]','10m wind speed[max t]', \
	      'Sdw[min]','Sdw[max]','Sdw[min t]','Sdw[max t]', \
	      'Suw[min]','Suw[max]','Suw[min t]','Suw[max t]', \
	      'Ldw(uc)[min]','Ldw(uc)[max]','Ldw(uc)[min t]','Ldw(uc)[max t]', \
              'Luw(uc)[min]','Luw(uc)[max]','Luw(uc)[min t]','Luw(uc)[max t]', \
	      'CNR4T[min]','CNR4T[max]','CNR4T[min t]','CNR4T[max t]', \
	      'Sb(csd3)[min]','Sb(csd3)[max]','Sb(csd3)[min t]','Sb(csd3)[max t]', \
              'PointDischarge[min]','PointDischarge[max]','PointDischarge[min t]','PointDischarge[max t]', \
              'U0.56[min]','U0.56[max]','U0.56[min t]','U0.56[max t]', \
              'U0.8[min]','U0.8[max]','U0.8[min t]','U0.8[max t]', \
              'U1.12[min]','U1.12[max]','U1.12[min t]','U1.12[max t]', \
              'U1.6[min]','U1.6[max]','U1.6[min t]','U1.6[max t]', \
              'U2.24[min]','U2.24[max]','U2.24[min t]','U2.24[max t]', \
              'U3.2[min]','U3.2[max]','U3.2[min t]','U3.2[max t]', \
              'U4.48[min]','U4.48[max]','U4.48[min t]','U4.48[max t]', \
              'U6.4[min]','U6.4[max]','U6.4[min t]','U6.4[max t]', \
              'T0.56[min]','T0.56[max]','T0.56[min t]','T0.56[max t]', \
              'T1.12[min]','T1.12[max]','T1.12[min t]','T1.12[max t]', \
              'T2.24[min]','T2.24[max]','T2.24[min t]','T2.24[max t]', \
              'T4.48[min]','T4.48[max]','T4.48[min t]','T4.48[max t]' ]
    type_list=['typetemp','typetemp','typetemp','typetemp', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typenull','typenull','typenull','typenull', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typenull','typenull','typenull','typenull', \
	      'typenull','typenull','typenull','typenull', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typenull','typenull','typenull','typenull', \
	      'typenull','typenull','typenull','typenull', \
	      'typenull','typenull','typenull','typenull', \
	      'typenull','typenull','typenull','typenull', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typerain','typerain','typerain','typerain', \
	      'typepres','typepres','typepres','typepres', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typesrad','typesrad','typesrad','typesrad', \
	      'typenull','typenull','typenull','typenull', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typewind','typewind','typewind','typewind', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp' ]
 
  elif data_type=="5min_Level2":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 31.Jul.2015<p>'
    var_list=['Td','Tw','RH','Twet_der','VP_der','Tdew_der','Sdur','Sdur_accum_der','Tgrass', \
              'Tconc','Tsoil','TSoil5','TSoil10','TSoil20','TSoil30','TSoil50','TSoil100','Sb', \
	      'Sd','Sg','Sg_accum_der','Rn','G','Rain','Rain_accum_der','U2run_der', \
	      'U5run_der','U5','Dirn5','U5max_der','P','Pmsl','U10run_der','U10','Dirn10','U10max_der', \
	      'CNR4T','Sdw','Suw','Ldw(uc)','Luw(uc)','Ldw','Luw','Sb(csd3)']
    name_list=['Dry bulb temperature','Measured wet bulb temperature','Relative humidity', \
               'Derived wet bulb temperature','Derived vapour pressure','Derived dew point', \
	       '5min sunshine','Accumulated sunshine since 0000UTC', \
	       'Grass temperature','Concrete temperature', \
	       'Bare soil temperature','5cm soil temperature', \
	       '10cm soil temperature','20cm soil temperature', \
	       '30cm soil temperature','50cm soil temperature', \
	       '100cm soil temperature','Direct beam solar radiation', \
	       'Diffuse solar radiation','Global solar radiation', \
	       'Accumulated global solar radiation since 0000UTC','Net radiative heat flux', \
	       'Ground heat flux','5min rainfall', \
	       'Accumulated rainfall since 0000UTC','2m run of wind', \
	       '5m run of wind','5m wind speed','5m wind direction','5m maximum wind gust', \
	       'Station pressure','MSL pressure', \
	       '10m run of wind','10m wind speed','10m wind direction','10m maximum wind gust', \
	       'CNR4 radiometer temp','Shortwave-down','Shortwave-up', \
	       'Longwave-down(uncorrected)','Longwave-up(uncorrected)','Longwave-down','Longwave-up', \
	       'Sb(csd3)' ]
	       
    type_list=['typetemp','typetemp','typetemp','typetemp','typetemp','typetemp','typesrad', \
              'typesrad','typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typesrad','typesrad','typesrad','typesrad', \
	      'typesrad','typesrad','typerain','typerain','typewind','typewind','typewind', \
	      'typewind','typewind','typepres','typepres','typewind','typewind','typewind','typewind', \
	      'typesrad','typesrad','typesrad','typesrad','typesrad','typesrad','typesrad', \
	      'typesrad']

  elif data_type=="5min_Level2_maxmin":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 30.Jun.2015<p>'
    var_list=['Td_max','Td_maxt','Td_min','Td_mint','Tw_max','Tw_maxt','Tw_min','Tw_mint', \
              'RH_max','RH_maxt','RH_min','RH_mint','Tgrass_max','Tgrass_maxt','Tgrass_min', \
	      'Tgrass_mint','Tconc_max','Tconc_maxt','Tconc_min','Tconc_mint','Tsoil_max', \
	      'Tsoil_maxt','Tsoil_min','Tsoil_mint','TSoil5_max','TSoil5_maxt','TSoil5_min', \
	      'TSoil5_mint','TSoil10_max','TSoil10_maxt','TSoil10_min','TSoil10_mint', \
	      'TSoil20_max','TSoil20_maxt','TSoil20_min','TSoil20_mint','TSoil30_max', \
	      'TSoil30_maxt','TSoil30_min','TSoil30_mint','TSoil50_max','TSoil50_maxt', \
	      'TSoil50_min','TSoil50_mint','TSoil100_max','TSoil100_maxt','TSoil100_min', \
	      'TSoil100_mint','Sg_max','Sg_maxt','Sg_min','Sg_mint','Rn_max','Rn_maxt', \
	      'Rn_min','Rn_mint','G_max','G_maxt','G_min','G_mint','Sb_max','Sb_maxt', \
	      'Sb_min','Sb_mint','Sd_max','Sd_maxt','Sd_min','Sd_mint', \
	      'P_max','P_maxt','P_min','P_mint','Pmsl_max','Pmsl_maxt','Pmsl_min','Pmsl_mint', \
	      'CNR4T_max','CNR4T_maxt','CNR4T_min','CNR4T_mint', \
              'Sdw_max','Sdw_maxt','Sdw_min','Sdw_mint', \
	      'Suw_max','Suw_maxt','Suw_min','Suw_mint', \
	      'Ldwuc_max','Ldwuc_maxt','Ldwuc_min','Ldwuc_mint', \
	      'Luwuc_max','Luwuc_maxt','Luwuc_min','Luwuc_mint', \
	      'Ldw_max','Ldw_maxt','Ldw_min','Ldw_mint', \
	      'Luw_max','Luw_maxt','Luw_min','Luw_mint' ]
    name_list=['Dry bulb temperature max','Dry bulb temperature max time', \
               'Dry bulb temperature min','Dry bulb temperature min time', \
	       'Measured wet bulb temperature max','Measured wet bulb temperature max time', \
	       'Measured wet bulb temperature min','Measured wet bulb temperature min time', \
               'Relative humidity max','Relative humidity max time', \
	       'Relative humidity min','Relative humidity min time', \
	       'Grass temperature max','Grass temperature max time', \
	       'Grass temperature min','Grass temperature min time', \
	       'Concrete temperature max','Concrete temperature max time', \
	       'Concrete temperature min','Concrete temperature min time', \
	       'Bare soil temperature max','Bare soil temperature max time', \
	       'Bare soil temperature min','Bare soil temperature min time', \
	       '5cm soil temperature max','5cm soil temperature max time', \
	       '5cm soil temperature min','5cm soil temperature min time', \
	       '10cm soil temperature max','10cm soil temperature max time', \
	       '10cm soil temperature min','10cm soil temperature min time', \
	       '20cm soil temperature max','20cm soil temperature max time', \
	       '20cm soil temperature min','20cm soil temperature min time', \
	       '30cm soil temperature max','30cm soil temperature max time', \
	       '30cm soil temperature min','30cm soil temperature min time', \
	       '50cm soil temperature max','50cm soil temperature max time', \
	       '50cm soil temperature min','50cm soil temperature min time', \
	       '100cm soil temperature max','100cm soil temperature max time', \
	       '100cm soil temperature min','100cm soil temperature min time', \
	       'Global solar radiation max','Global solar radiation max time', \
	       'Global solar radiation min','Global solar radiation min time', \
	       'Net radiative heat flux max','Net radiative heat flux max time', \
	       'Net radiative heat flux min','Net radiative heat flux min time', \
	       'Ground heat flux max','Ground heat flux max time', \
	       'Ground heat flux min','Ground heat flux min time', \
	       'Direct beam solar radiation max','Direct beam solar radiation max time', \
	       'Direct beam solar radiation min','Direct beam solar radiation min time', \
	       'Diffuse solar radiation max','Diffuse solar radiation max time', \
	       'Diffuse solar radiation min','Diffuse solar radiation min time', \
	       'P max','P max time','P min','P min time', \
	       'Pmsl max','Pmsl max time','Pmsl min','Pmsl min time', \
 	       'CNR4 radiomater temp max','CNR4T radiomater temp max time', \
	       'CNR4T radiomater temp  min','CNR4T radiomater temp min time', \
               'Shortwave down max','Shortwave down max time', \
               'Shortwave down min','Shortwave down min time', \
               'Shortwave up max','Shortwave up max time', \
               'Shortwave up min','Shortwave up min time', \
               'Longwave down uncorr max','Longwave down uncorr max time', \
               'Longwave down min','Longwave down uncorr min time', \
               'Longwave up uncorr max','Longwave up uncorr max time', \
               'Longwave up uncortr min','Longwave up uncorr min time', \
               'Longwave down max','Longwave down max time', \
               'Longwave down min','Longwave down min time', \
               'Longwave up max','Longwave up max time', \
               'Longwave up min','Longwave up min time' ]
    type_list=['typetemp','typetemp','typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
               'typetemp','typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
	       'typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
	       'typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
	       'typetemp','typetemp','typetemp','typetemp','typetemp', \
	       'typetemp','typetemp','typetemp','typetemp','typetemp', \
	       'typetemp','typetemp','typetemp','typetemp','typetemp', \
	       'typetemp','typetemp','typetemp','typetemp','typetemp', \
	       'typetemp','typesrad','typesrad','typesrad','typesrad','typesrad','typesrad', \
	       'typesrad','typesrad','typesrad','typesrad','typesrad','typesrad','typesrad','typesrad', \
	       'typesrad','typesrad','typesrad','typesrad','typesrad','typesrad', \
	       'typepres','typepres','typepres','typepres','typepres','typepres','typepres','typepres', \
	       'typesrad','typesrad','typesrad','typesrad','typesrad','typesrad','typesrad', \
	       'typesrad','typesrad','typesrad','typesrad','typesrad','typesrad','typesrad', \
	       'typesrad','typesrad','typesrad','typesrad','typesrad','typesrad','typesrad', \
	       'typesrad','typesrad','typesrad','typesrad','typesrad','typesrad','typesrad' ]

  elif data_type=="1hour_Level2":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 31.Ju1.2015<p>'
    var_list=['Td','Tw','RH','Twet_der','VP_der','Tdew_der','Sdur','Sdur_accum_der','Tgrass', \
              'Tconc','TSoil','TSoil5','TSoil10','TSoil20','TSoil30','TSoil50','TSoil100','Sb', \
	      'Sd','Sg','Sg_accum_der','Rn','G','Rain','Rain_accum_der','U2run_der','U5run_der', \
	      'U5','Dirn5','U5max_der','U5max_accum_der','P','Pmsl','U10run_der', \
	      'U10','Dirn10','U10max_der','U10max_accum_der', \
	      'CNR4T','Sdw','Suw','Ldw(uc)','Luw(uc)','Ldw','Luw','Sb(csd3)']
    name_list=['Dry bulb temperature','Measured wet bulb temperature', \
               'Relative humidity','Derived wet bulb temperature', \
	       'Derived vapour pressure','Derived dew point', \
	       '1hour sunshine','Accumulated sunshine since 0000UTC', \
	       'Grass temperature','Concrete temperature', \
	       'Bare soil temperature','5cm soil temperature', \
	       '10cm soil temperature','20cm soil temperature', \
	       '30cm soil temperature','50cm soil temperature', \
	       '100cm soil temperature','Direct beam solar radiation', \
	       'Diffuse solar radiation','Global solar radiation', \
	       'Accumulated global solar radiation since 0000UTC','Net radiative heat flux', \
	       'Ground heat flux','5min rainfall','Accumulated rainfall since 0000UTC', \
	       '2m run of wind','5m run of wind', \
	       '5m wind speed','5m wind direction', \
	       '5m maximum wind gust','5m maximum wind gust since 0000UTC', \
	       'Station pressure','MSL pressure','10m run of wind', \
	       '10m wind speed','10m wind direction', \
	       '10m maximum wind gust','10m maximum wind gust since 0000UTC', \
	       'CNR4 radiometer temp','Shortwave-down','Shortwave-up', \
	       'Longwave-down(uncorrected)','Longwave-up(uncorrected)','Longwave-down','Longwave-up', \
	       'Sb(csd3)' ]
    type_list=['typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
               'typesrad','typesrad','typetemp','typetemp','typetemp','typetemp', \
	       'typetemp','typetemp','typetemp','typetemp','typetemp','typesrad', \
	       'typesrad','typesrad','typesrad','typesrad','typesrad','typerain', \
	       'typerain','typewind','typewind', \
	       'typewind','typewind','typewind','typewind','typepres','typepres', \
	       'typewind','typewind','typewind','typewind','typewind', \
	       'typesrad','typesrad','typesrad','typesrad','typesrad','typesrad','typesrad',
	       'typesrad']

  elif data_type=="1hour_Level2_maxmin":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 29.Dec.2014<p>'
    var_list=['Td_max','Td_maxt','Td_min','Td_mint','Tw_max','Tw_maxt','Tw_min','Tw_mint', \
              'RH_max','RH_maxt','RH_min','RH_mint','Tgrass_max','Tgrass_maxt','Tgrass_min', \
	      'Tgrass_mint','Tconc_max','Tconc_maxt','Tconc_min','Tconc_mint','Tsoil_max', \
	      'Tsoil_maxt','Tsoil_min','Tsoil_mint','TSoil5_max','TSoil5_maxt','TSoil5_min', \
	      'TSoil5_mint','TSoil10_max','TSoil10_maxt','TSoil10_min','TSoil10_mint', \
	      'TSoil20_max','TSoil20_maxt','TSoil20_min','TSoil20_mint','TSoil30_max', \
	      'TSoil30_maxt','TSoil30_min','TSoil30_mint','TSoil50_max','TSoil50_maxt', \
	      'TSoil50_min','TSoil50_mint','TSoil100_max','TSoil100_maxt','TSoil100_min','TSoil100_mint', \
	      'P_max','P_maxt','P_min','P_mint','Pmsl_max','Pmsl_maxt','Pmsl_min','Pmsl_mint']
    name_list=['Dry bulb temperature max','Dry bulb temperature maxt', \
               'Dry bulb temperature min','Dry bulb temperature mint', \
	       'Measured wet bulb temperature max','Measured wet bulb temperature maxt', \
	       'Measured wet bulb temperature min','Measured wet bulb temperature mint', \
               'Relative humidity max','Relative humidity maxt', \
	       'Relative humidity min','Relative humidity mint', \
	       'Grass temperature max','Grass temperature maxt', \
	       'Grass temperature min','Grass temperature mint', \
	       'Concrete temperature max','Concrete temperature maxt', \
	       'Concrete temperature min','Concrete temperature mint', \
	       'Bare soil temperature max','Bare soil temperature maxt', \
	       'Bare soil temperature min','Bare soil temperature mint', \
	       '5cm soil temperature max','5cm soil temperature maxt', \
	       '5cm soil temperature min','5cm soil temperature mint', \
	       '10cm soil temperature max','10cm soil temperature maxt', \
	       '10cm soil temperature min','10cm soil temperature mint', \
	       '20cm soil temperature max','20cm soil temperature maxt', \
	       '20cm soil temperature min','20cm soil temperature mint', \
	       '30cm soil temperature max','30cm soil temperature maxt', \
	       '30cm soil temperature min','30cm soil temperature mint', \
	       '50cm soil temperature max','50cm soil temperature maxt', \
	       '50cm soil temperature min','50cm soil temperature mint', \
	       '100cm soil temperature max','100cm soil temperature maxt', \
	       '100cm soil temperature min','100cm soil temperature mint', \
	       'P max','P max time','P min','P min time', \
	       'Pmsl max','Pmsl max time','Pmsl min','Pmsl min time']
    type_list=['typetemp','typetemp','typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
              'typetemp','typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp','typetemp','typetemp',
	      'typepres','typepres','typepres','typepres','typepres','typepres','typepres','typepres']

  elif data_type=="climat0900":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 10.Nov.2014<p>'
    var_list=['Td_09','Twet_der_09','Tdew_der_09','VP_der_09','RH_09','Tx_0909', \
              'Tn_0909','Tgrass_0909','Tconc_0909','Tsoil_0909','TSoil5_09', \
	      'TSoil10_09','TSoil20_09','TSoil30_09','TSoil50_09','TSoil100_09', \
	      'Dirn10_09','U10_09','Pmsl_09','Rain_accum_0909','Sdur_0024', \
	      'srad_0024','U10max_0024','U2run_0909','U10run_0909']
    name_list=['0900 dry bulb temperature','0900 wet bulb temperatures derived', \
               '0900 dew point derived','0900 vapour pressure derived',
	       '0900 relative humidity','Maximum temperature for yesterday ending 0900', \
               'Minimum temperature ending 0900','Grass minimum temperature ending 0900', \
	       'Concrete minimum temperature ending 0900','Soil minimum temperature ending 0900', \
	       '0900 5 cm soil temperature', \
	       '0900 10 cm soil temperature','0900 20 cm soil temperature', \
	       '0900 30 cm soil temperature','0900 50 cm soil temperature', \
	       '0900 100 cm soil temperature', \
	       '0900 wind direction at 10 m','0900 wind speed at 10 m', \
	       '0900 MSL pressure','Rainfall for yesterday ending 0900', \
	       'Sunshine duration for yesterday', \
	       'Global solar radiation accumulation for yesterday', \
	       '00-24 maximum wind gust at 10 m for yesterday', \
	       '2m run of wind for yesterday ending 0900', \
	       '2m run of wind for yesterday ending 0900']
    type_list=['typetemp','typetemp','typetemp','typetemp','typetemp','typetemp', \
              'typetemp','typetemp','typetemp','typetemp','typetemp', \
	      'typetemp','typetemp','typetemp','typetemp','typetemp', \
	      'typewind','typewind','typepres','typerain','typesrad', \
	      'typesrad','typewind','typewind','typewind']

  if data_type=="soniclicor_Level1":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 13.Aug.2015<p>'
    var_list=['U','V','T','W','H2O','CO2','P']

    name_list=['U', 'V', 'T', 'W','H2O', 'CO2','P']

    type_list=['typewind','typewind','typetemp','typewind','typenull','typenull', \
               'typepres']

  if data_type=="Vertical_profiles":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 27.Nov.2015<p>'
    var_list=['U0.56','U0.8','U1.12','U1.6','U2','U2.24','U3.2', 'U4.48',\
              'U5','U6.4','U10','T0.56','T1.12','T2.24','T4.48']

    name_list=['U0.56','U0.8','U1.12','U1.6','U2','U2.24','U3.2', 'U4.48','U5',\
               'U6.4','U10','T0.56','T1.12','T2.24','T4.48']

    type_list=['typewind','typewind','typewind','typewind','typewind','typewind', \
               'typewind','typewind','typewind','typewind','typewind', \
               'typetemp','typetemp','typetemp','typetemp' ]

  if data_type=="eddy_cov":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 27.Nov.2015<p>'
    var_list=['q','WS','dir','zL','L','Tsonic', 'ustar','nSamples','cov_uv','cov_uw', 'cov_vw',\
              'Q_H','Q_E','C_CO2','F_CO2','sd_Tsonic','sd_u','sd_v','sd_w','sd_C_CO2','sd_q']

    name_list=['specific humidity','horizontal wind speed','wind direction','atmospheric stability parameter (z=3m)', \
               'Monin-Obhukov length','mean sonic temperature', 'friction velocity', \
	       'number of time samples in data','covariance of u,v wind components', \
	       'covariance of u,w wind components', 'covariance of v,w wind components',\
               'turbulent sensible heat flux','turbulent latent heat flux','carbon dioxide concentration', \
	       'turbulent carbon dioxide flux','standard deviation of sonic temperature', \
	       'standard deviation of u wind component','standard deviation of v wind component', \
	       'standard deviation of w wind component','standard deviation of CO2', \
	       'standard deviation of specific humidity']

    type_list=['typenull','typewind','typewind','typenull','typenull','typenull', 'typenull', \
               'typenull','typenull','typenull', 'typenull','typenull','typenull', \
               'typenull','typenull','typenull','typenull','typenull', 'typenull','typenull','typenull']


  if data_type=="cloudbase_5min":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 27.Nov.2015<p>'
    var_list=['Base1_mean','Base1_sd','Base2_mean','Base2_sd','Base3_mean','Base3_sd','Base1_min' ]

    name_list=['Base1_mean','Base1_sd','Base2_mean','Base2_sd','Base3_mean','Base3_sd','Base1_min' ]

    type_list=['typenull','typenull','typenull','typenull','typenull','typenull','typenull' ]

  if data_type=="cloudbase_1min":
    if header=='true': 
      print 'List of variables available for the chosen data type last updated 27.Nov.2015<p>'
    var_list=['Base1_mean','Base1_sd','Base2_mean','Base2_sd','Base3_mean','Base3_sd' ]

    name_list=['Base1_mean','Base1_sd','Base2_mean','Base2_sd','Base3_mean','Base3_sd' ]

    type_list=['typenull','typenull','typenull','typenull','typenull','typenull' ]

  return var_list, name_list, type_list
#======================
def show_mdval(dateform):
  null=''
  x=dateform.getvalue("MDVAL")
  strval=str(x)
  print '<p><input type="hidden" name="MDVAL" value=',strval,'>'
  print '<font color="blue">Missing data value selected: ',x,'<font color="black"></p>'
  return strval
#======================
def set_mdval():
  null=''
  print '<p><b>Step 4 - select the missing_data value in output file</b></p>'
  print '<dl><dt><input type="radio", name="MDVAL" value="blank" checked>'+'blank/empty value'
  print '<dt><input type="radio", name="MDVAL" value="9999.9">'+'9999.9'
  print '<dt><input type="radio", name="MDVAL" value="x">'+'x'
  print '</dl>'
  return null
#======================
def show_datetime(dateform,data_type):
  null=''
  mlist=["Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

  # date/time now
  x=datetime.datetime.utcnow()
  p=x.timetuple() ; yearnow=p[0] ; monthnow=p[1] ; daynow=p[2]
  hh=int(p[3]) ; mm=int(p[4]) ; hournow=str(hh*100+mm)

  yy1=dateform.getvalue("start_year")
  mon1=dateform.getvalue("start_month")
  for i in range(0,len(mlist)):
    if mon1==mlist[i]: mm1=i
  dd1=dateform.getvalue("start_day")
  hhmm1=dateform.getvalue("start_time")
  strval1=str(yy1)+'-'+str(mon1)+'-'+str(dd1)+':'+str(hhmm1)

  if data_type != 'soniclicor_Level1':
    yy2=dateform.getvalue("end_year")
    mon2=dateform.getvalue("end_month")
    for i in range(0,len(mlist)):
      if mon2==mlist[i]: mm2=i
    dd2=dateform.getvalue("end_day")
    hhmm2=dateform.getvalue("end_time")
  else:
    sly1=int(yy1)
    slm1=int(mm1)
    sld1=int(dd1)
    slh1=int(hhmm1)/100

    slt2=datetime.datetime(sly1,slm1,sld1,slh1)+datetime.timedelta(hours=1)
    slend=str(slt2)
    yy2=str(slend[0:4])
    mm2=str(slend[5:7])
    dd2=str(slend[8:10])
    hhmm2=str(slend[11:13])+'00'
    mon2=mlist[int(mm2)]
	
  strval2=str(yy2)+'-'+str(mon2)+'-'+str(dd2)+':'+str(hhmm2)

  print '<p><font color="blue">Start time: ',strval1,' UTC','<font color="black">'
  print '<br><font color="blue">End time: ',strval2,' UTC','<font color="black"></p>'

  # check valid time period
  startup=int(hhmm1)/100+100*int(dd1)+10000*int(mm1)+1000000*int(yy1)
  ending= int(hhmm2)/100+100*int(dd2)+10000*int(mm2)+1000000*int(yy2)
  nowtime=int(hournow)/100+100*int(daynow)+10000*int(monthnow)+1000000*int(yearnow)

  # Need to check for dates not in the database
  databasestart=0+100*1+10000*9+1000000*2014  # no data before 1 September 2014
  start_words='1 Sept 2014'
  if data_type=='soniclicor_Level1':
    databasestart=0+100*11+10000*8+1000000*2015  # no data before 11 August 2015
    start_words='11 Aug 2015'
  elif data_type=='Vertical_levels':
    databasestart=0+100*19+10000*8+1000000*2015  # no data before 19 August 2015
    start_words='19 Aug 2015'
  elif data_type=='cloudbase_5min' or data_type=='cloudbase_1min' :
    databasestart=0+100*19+10000*3+1000000*2015  # no data before 19 March 2015
    start_words='19 Mar 2015'
  elif data_type=='eddy_cov' :
    databasestart=0+100*23+10000*9+1000000*2015  # no data before 23 September 2015
    start_words='23 Sep 2015'

  datesok='yes'
  if calendar.monthrange(int(yy1),int(mm1))[1]<int(dd1):
    datesok='no'
    print '<b><font color="red">Day of start month [',dd1,' ',mon1,'] is not valid - re-enter the dates</b><font color="black">'
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="re-enter dates"><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()
  
  if calendar.monthrange(int(yy2),int(mm2))[1]<int(dd2):
    datesok='no'
    print '<b><font color="red">Day of end month [',dd2,' ',mon2,'] is not valid - re-enter the dates</b><font color="black">'
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="re-enter dates"><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()

  if ending<startup:
    datesok='no'
    print '<b><font color="red">End time is before the start time - re-enter the dates</b><font color="black">'
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="re-enter dates"><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()

  if startup>nowtime:
    datesok='no'
    print '<b><font color="red">Start time is after the current time - re-enter the dates</b><font color="black">'
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="re-enter dates"><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()

  if ending>nowtime:
    datesok='no'
    print '<b><font color="red">End time is after the current time - re-enter the dates</b><font color="black">'
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="re-enter dates"><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()

  if int(ending)/100==int(nowtime)/100 and data_type=='eddy_cov':
    # Eddy covariance datafile is not available until after date of the data
    datesok='no'
    print '<b><font color="red">End date equals the current date (not allowed for eddy covariances) - re-enter the dates</b><font color="black">'
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="re-enter dates"><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()

  if startup<databasestart:
    datesok='no'
    print '<b><font color="red">Start time is before '+start_words+' when data became available - re-enter the dates</b><font color="black">'
    print '<hr>'
    print 'Click here to <INPUT TYPE="submit" VALUE="re-enter dates"><p>'
    print'</form>'
    print'</body>'
    print '</html>'
    exit()

  # period is OK
  print '<p><input type="hidden" name="start_year" value=',str(yy1),'>'
  print '<input type="hidden" name="start_month" value=',str(mon1),'>'
  print '<input type="hidden" name="start_day" value=',str(dd1),'>'
  print '<input type="hidden" name="start_time" value=',str(hhmm1),'>'
  print '<p><input type="hidden" name="end_year" value=',str(yy2),'>'
  print '<input type="hidden" name="end_month" value=',str(mon2),'>'
  print '<input type="hidden" name="end_day" value=',str(dd2),'>'
  print '<input type="hidden" name="end_time" value=',str(hhmm2),'>'

  return yy1,mon1,dd1,hhmm1,yy2,mon2,dd2,hhmm2
#======================
def set_user_datetime(data_type):
  null=''
  mlist=["Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

  # date/time now
  x=datetime.datetime.utcnow()
  p=x.timetuple() ; yearnow=p[0] ; monthnow=p[1] ; daynow=p[2]
  
  print '<p><b>Step 2 - select the start time (y,m,d,hm) of the plot</b></p>'
  print '<select name="start_year" size="1"> <option selected>',yearnow
  yy=yearnow
  for i in range(2014,yearnow):
    yy=yy-1
    print '<option>',yy
  print '</select>'

  print '<select name="start_month" size="1"> <option selected>',mlist[monthnow]
  for i in range(1,13):
    if i != monthnow: print '<option>',mlist[i]
  print '</select>'

  daystart=max(1,daynow-1)
  print '<select name="start_day" size="1"> <option selected>',str(daystart).zfill(2)
  for i in range(1,32):
    if i != daystart: print '<option>',str(i).zfill(2)
  print '</select>'

  print '<select name="start_time" size="1"> <option selected>','0000'
  for i in range(100,2500,100):
    print '<option>',str(i).zfill(4)
  print '</select>'

  if data_type != 'soniclicor_Level1':
    print '<p><b>Step 3 - select the end time (y, m, d, hm) of the plot</b></p>'
    print '<select name="end_year" size="1"> <option selected>',yearnow
    yy=yearnow
    for i in range(2014,yearnow):
      yy=yy-1
      print '<option>',yy
    print '</select>'
    
    print '<select name="end_month" size="1"> <option selected>',mlist[monthnow]
    for i in range(1,13):
      if i != monthnow: print '<option>',mlist[i]
    print '</select>'

    print '<select name="end_day" size="1"> <option selected>',str(daynow).zfill(2)
    for i in range(1,32):
      if i != daynow: print '<option>',str(i).zfill(2)
    print '</select>'

    print '<select name="end_time" size="1"> <option selected>','0000'
    for i in range(100,2500,100):
      print '<option>',str(i).zfill(4)
    print '</select>'
  
  else:
    print '<p><b>SonicLicor data will be extracted for a one-hour duration</b></p>'

  return null
#======================
def set_data_type():
  null=''
  print '<p><b>Step 1 - select the type of data</b></p>'
  print '<dl><dt><input type="radio", name="data_type" value="1sec_Level1">'\
        +'1-sec "instantaneous" logger output'
  print '<dt><input type="radio", name="data_type" value="5min_Level1">5-min averaged logger output'
  print '<dt><input type="radio", name="data_type" value="5min_Level1_maxmin">5-min max/min logger output'
  print '<dt><input type="radio", name="data_type" value="5min_Level2" checked>'\
        +'5-min WMO-standard processed output'
  print '<dt><input type="radio", name="data_type" value="5min_Level2_maxmin">5-min max/min processed output'
  print '<dt><input type="radio", name="data_type" value="1hour_Level2">1-hour WMO-standard processed output'
  print '<dt><input type="radio", name="data_type" value="1hour_Level2_maxmin">1-hour max/min processed output'
  print '<dt><input type="radio", name="data_type" value="climat0900">0900 UTC climat observation - no data thrown back'
  print '<dt><input type="radio", name="data_type" value="soniclicor_Level1">'\
        +'0.1-sec sonic licor output'
  print '<dt><input type="radio", name="data_type" value="Vertical_profiles">Vertical profiles of wind and temperature'
  print '<dt><input type="radio", name="data_type" value="eddy_cov">Eddy covariances - 30-min averages'
  print '<dt><input type="radio", name="data_type" value="cloudbase_5min">Cloud base averages at 5 minute intervals'
  print '<dt><input type="radio", name="data_type" value="cloudbase_1min">Cloud base averages at 1 minute intervals'
  print '</dl>'
  return null
#======================
def show_data_type(dateform):
  null=''
  x=dateform.getvalue("data_type")
  strval=str(x)
  print '<p><input type="hidden" name="data_type" value=',strval,'>'
  print '<font color="blue">Data type chosen: ',x,'<font color="black"></p>'
  return strval
#======================

if __name__ == '__main__':
  main()
