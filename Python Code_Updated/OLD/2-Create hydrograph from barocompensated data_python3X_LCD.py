# -*- coding: utf-8 -*-
"""
Created on Fri May 19 12:11:47 2017

@author: alex.messina
"""
### BE SURE TO SET YOUR WORKING DIRECTORY TO:
## P:\Projects-South\Environmental - Schaedler\5025-18-0010 ESA COSD Continuous Flow\DATA\Python Code ##

#MAKE SURE LINE 347 IS SET TO THE PROPER LOGGING INTERVAL

# Import Custom Modules
from Excel_Plots import Excel_Plots    
from OvertoppingFlows_LCD import *
import string
import textwrap

# Import Standard modules
import datetime as dt
import matplotlib as mpl
from matplotlib import pyplot as plt
import pandas as pd
import os
import numpy as np
import calendar
#from scipy import signal

## Set Pandas display options
pd.set_option('display.large_repr', 'truncate')
pd.set_option('display.width', 180)
pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 13)
plt.ion()

## Input directories
maindir = '//sdg1-fs1/SDShare/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/Data Processing/'
data_processing_date = "05_17_2019"

raindir = maindir+'/0 - Rain Data Download/Data processing '+data_processing_date+'/'

## Output directories
hydrograph_fileoutput_dir =   maindir+'4a - Flow output Excel files - working drafts/Data Output '+data_processing_date+'/'
hydrograph_figureoutput_dir = maindir+'4b - Flow output figures - working hydrographs/Data Output '+data_processing_date+'/'
calibration_output_dir =      maindir+'4c - Level calibration files and figures/Data Output '+data_processing_date+'/'

## Dictionary of rain gauges for each site
## Data from  https://sandiego.onerain.com/rain.php
#2019 dictionary
raingauge_dict = {'LAB_TEST':'San_Marcos', 'CAR-070':'San_Marcos', 'CAR-070O':'San_Marcos', 'CAR-072':'San_Marcos', 'CAR-072B':'San_Marcos', 'CAR-072O':'San_Marcos', 'SDG-072':'Rancho_Bernardo', 'SDG-080':'Rancho_Bernardo', 'SDG-084':'Rancho_Bernardo', 'SDG-084J':'Rancho_Bernardo', 'SDG-085G':'Rancho_Bernardo', 'SDG-085':'Rancho_Bernardo', 'SDG-085M':'Rancho_Bernardo', 'SLR-045':'Deer_Springs', 'SLR-045A':'Deer_Springs', 'SLR-045B':'Deer_Springs', 'SLR-095':'Deer_Springs', 'SDR-036':'Flinn_Springs', 'SDR-041':'Los_Coches', 'SDR-064':'Cactus_County', 'SDR-097':'Cactus_County', 'SDR-098':'Los_Coches', 'SDR-127':'Flinn_Springs', 'SDR-127B':'Flinn_Springs', 'SDR-203A':'Los_Coches', 'SDR-204A':'Los_Coches', 'SDR-207':'Los_Coches', 'SDR-223':'Los_Coches', 'SDR-228':'Cactus_County', 'SDR-568':'Los_Coches', 'SDR-723':'Cactus_County', 'SDR-740':'Cactus_County', 'SDR-751':'Cactus_County', 'SDR-772':'Los_Coches', 'SDR-780':'Los_Coches', 'SDR-939':'Los_Coches', 'SDR-1024':'Cactus_County', 'SDR-1031':'Cactus_County', 'SWT-019':'Bonita', 'SWT-030':'Roads', 'SWT-055':'La_Mesa', 'SWT-055A':'La_Mesa', 'CAR-070T1':'San_Marcos', 'CAR-070T2':'San_Marcos', 'CAR-070T3':'San_Marcos', 'CAR-070T4':'San_Marcos', 'CAR-070T5':'San_Marcos', 'CAR-070T6':'San_Marcos', 'CAR-072T1':'San_Marcos', 'CAR-072T2':'San_Marcos', 'CAR-072T3':'San_Marcos', 'CAR-072T4':'San_Marcos', 'CAR-072T5':'San_Marcos', 'CAR-072T6':'San_Marcos', 'LAB_TESTT1':'San_Marcos', 'LAB_TESTT2':'San_Marcos', 'LAB_TESTT3':'San_Marcos', 'LAB_TESTT4':'San_Marcos', 'LAB_TESTT5':'San_Marcos', 'LAB_TESTT6':'San_Marcos', 'SDG-080T1':'Rancho_Bernardo', 'SDG-080T2':'Rancho_Bernardo', 'SDG-080T3':'Rancho_Bernardo', 'SDG-080T4':'Rancho_Bernardo', 'SDG-080T5':'Rancho_Bernardo', 'SDG-080T6':'Rancho_Bernardo'}

### OFFSET/ FIELD MEASUREMENTS
calibration_dir = maindir+'0 - Raw Data Download/Field Calibration Data/'

## Open HvF table
HvF = pd.read_excel(calibration_dir+'90 degree V-notch Lookup Table.xlsx',skiprows=3,index_col='Level (in)', parse_cols='B:C')

## Open spreadsheet
fds = pd.read_excel(calibration_dir+'Weir Calibration Field Form 2018 v1 (Responses) '+ data_processing_date +'.xlsx')
## Make a Datetime column (The TIMESTAMP column is when the form was submitted to Google, not the measurement)
fds['Datetime'] = pd.to_datetime((fds['Date'].astype('str') +' '+ fds['Time'].astype('str')), yearfirst=True)
## Round to 5Min
fds['Datetime'] = fds['Datetime'].apply(lambda x: dt.datetime(x.year, x.month, x.day, x.hour,5*(x.minute // 5)))
## Make Index line up with Excel row numbers for easy reference
fds.index+=2
fds['Line#'] = fds.index

#2018 site list
#site_list = ['CAR-015',	'CAR-059',	'CAR-069',	'CAR-070',	'CAR-072',	'CAR-072O',	'CAR-072Q',	'HST01',	'SDG-072',	'SDG-074',	'SDG-077',	'SDG-080',	'SDG-084',	'SDG-085',	'SDG-085M',	'SDG-115',	'SDG-115B',	'SDR-036',	'SDR-036J',	'SDR-041',	'SDR-064',	'SDR-097',	'SDR-098',	'SDR-127',	'SDR-127B',	'SDR-151',	'SDR-203A',	'SDR-204A',	'SDR-207',	'SDR-207G',	'SDR-207L',	'SDR-207M',	'SDR-228',	'SDR-554',	'SDR-607',	'SDR-754',	'SLR-041',	'SLR-045',	'SLR-095',	'SLR-150',	'SLR-152',	'SLR-152A',	'SLR-152H',	'SLR-155',	'SLR-155F',	'SWT-019',	'SWT-023',	'SWT-023E','SWT-030',	'SWT-055',	'SWT-055A',	'SWT-235']


#2019 site list
site_list = ['LAB_TEST', 'CAR-070', 'CAR-070O', 'CAR-072', 'CAR-072B', 'CAR-072O', 'SDG-072', 'SDG-080', 'SDG-084', 'SDG-084J', 'SDG-085G', 'SDG-085', 'SDG-085M', 'SLR-045', 'SLR-045A', 'SLR-045B', 'SLR-095', 'SDR-036', 'SDR-041', 'SDR-064', 'SDR-097', 'SDR-098', 'SDR-127', 'SDR-127B', 'SDR-203A', 'SDR-204A', 'SDR-207', 'SDR-223', 'SDR-228', 'SDR-568', 'SDR-723', 'SDR-740', 'SDR-751', 'SDR-772', 'SDR-780', 'SDR-939', 'SDR-1024', 'SDR-1031', 'SWT-019', 'SWT-030', 'SWT-055', 'SWT-055A']

site_list = site_list + ['CAR-070T1', 'CAR-070T2', 'CAR-070T3', 'CAR-070T4', 'CAR-070T5', 'CAR-070T6', 'CAR-072T1', 'CAR-072T2', 'CAR-072T3', 'CAR-072T4', 'CAR-072T5', 'CAR-072T6', 'LAB_TESTT1', 'LAB_TESTT2', 'LAB_TESTT3', 'LAB_TESTT4', 'LAB_TESTT5', 'LAB_TESTT6', 'SDG-080T1', 'SDG-080T2', 'SDG-080T3', 'SDG-080T4', 'SDG-080T5', 'SDG-080T6']

# Clean up Site Id's
## Make a New Series
fds['Site'] = pd.Series()
## Loop over site ids
for f in fds.iterrows():
    fid = f[1]['SITE ID']
    # Capitalize
    fid = fid.upper()
    #print fid
    # Make sure the site is in the list
    if fid not in site_list:
        print(fid + ' NOT IN SITE LIST')
        
fds.index = fds['SITE ID']
    
    
## UP to 2 level measurements
## cm to inches
fds['Level_above_V_cm_Before'] = fds['1. BEFORE: Height above (or below) v-notch (cm)']
fds['Level_above_V_cm_After'] = fds['2. AFTER: Height above (or below) v-notch (cm)']
#
fds['Level_above_V_in_Before'] = fds['Level_above_V_cm_Before'] / 2.54
fds['Level_above_V_in_After'] = fds['Level_above_V_cm_After'] / 2.54
#
## UP to 3 flow measurements
## Flow in cfs: mL to cfs divided by seconds
fds['Flow_cfs_1'] = (fds['1. Flow Measurement, Volume in mL']/28316.8) / fds['1. Flow Measurement, Time in Seconds']
fds['Flow_cfs_2'] = (fds['2. Flow Measurement, Volume in mL']/28316.8) / fds['2. Flow Measurement, Time in Seconds']
fds['Flow_cfs_3'] = (fds['3. Flow Measurement, Volume in mL']/28316.8) / fds['3. Flow Measurement, Time in Seconds']

## To gpm
fds['Flow_gpm_1'] = fds['Flow_cfs_1'] * 448.83
fds['Flow_gpm_2'] = fds['Flow_cfs_2'] * 448.83
fds['Flow_gpm_3'] = fds['Flow_cfs_3'] * 448.83
test1 = fds['1. Flow Measurement, Time in Seconds']
tester = (fds['1. Flow Measurement, Volume in mL']/28316.8) / fds['1. Flow Measurement, Time in Seconds']

## Drop any duplicate rows so it doesn't weight the average 
fds_len =  len(fds)
fds = fds.drop_duplicates(keep='first')
fds_len_no_dup = len(fds)
diff = fds_len - fds_len_no_dup
print ('')
print ('Dropped '+str(diff)+' duplicate rows')
print ('')

## WEIR DIMENSIONS FOR OVERTOPPING FLOWS
weir_dims = pd.read_excel(maindir+'2019 Weir Dims.xlsx',index_col='Site', sheetname='Sheet1')

#%% START HERE - SITE NAME

######## SITE NAME HERE #######################
SITE_YOU_WANT_TO_PROCESS = 'SDR-939'

###############################################

barocomp_outputdir = maindir+'3a - Baro compensated level data/Data processing '+data_processing_date+'/'
## GET FILE WITH running barometrically-compensated data
files = [f for f in os.listdir(barocomp_outputdir) if f.endswith('.xlsx') == True and str(f.split(' ')[0])==SITE_YOU_WANT_TO_PROCESS]  
for f in files: 
    #MaxFlow = HvF.ix[np.round(MaxLevel,2)]['Q (GPM)']
    print ('')
    print ('Filename: '+f)
    
    ## Read in the data
    site_name = f.split(' ')[0]     
    print ('Site name: '+site_name)
    print ('')
    WL = pd.read_excel(barocomp_outputdir+f, skiprows= [0,1], index_col=0, header=0)
    WL['Level_in'] = WL['mm Water Level'] / 25.4

# MANUAL DATA OFFSETS TO GET SERIES TO LINE 
## Two files so two people can have it open in Excel at one time
    try:
        offsets_RF = pd.read_excel(hydrograph_fileoutput_dir+'Offsets and Clip times_RF.xlsx',sheetname='Offsets',index_col=0,parse_cols='A:F')
    except:
        offsets_RF = pd.DataFrame()
    try:
        offsets_LD = pd.read_excel(hydrograph_fileoutput_dir+'Offsets and Clip times_LD.xlsx',sheetname='Offsets',index_col=0,parse_cols='A:F')
    except:
        offsets_LD = pd.DataFrame()
    try:
        offsets_combined = pd.read_excel(hydrograph_fileoutput_dir+'Offsets and Clip times.xlsx',sheetname='Offsets',index_col=0,parse_cols='A:F')
    except:
        offsets_combined = pd.DataFrame()
    offsets = pd.concat([offsets_LD, offsets_RF])
   
    offsets_list_for_site = offsets[offsets.index  == site_name]

    ## Add column of zero for data offset
    WL['data_offset'] = 0.
    overall_offset, negative_level_as_zero_flow = 0., 'False'
    ## iterate over list manual data offsets
    ## THIS IS AS TUPLES SO THE TUPLE IS INDEXED BY NUMBER NOT STRING
    for offset in offsets_list_for_site.itertuples():
        print ('Manual offset from Excel sheet: ')
        offset_start, offset_end = pd.to_datetime(offset[1]), pd.to_datetime(offset[2])
        offset_value = offset[3]
        overall_offset = offset[4]
        negative_level_as_zero_flow = offset[5]
       
        ## set data in bad_data indices to nan
        if pd.notnull(offset_start)==True and pd.notnull(offset_end)==True:
            print ('Manual offset data: '+offset_start.strftime('%m/%d/%y %H:%M')+' - '+offset_end.strftime('%m/%d/%y %H:%M')+' = '+str(offset_value)+ ' inches')
        ## add each offset value
            WL.loc[offset_start:offset_end, ['data_offset']] = offset_value
        else:
            pass
        print ('')   
    ## Apply all offsets for unique shifts due to bad data or other issues
    WL['Level_in'] = WL['Level_in'] + WL['data_offset']
    
    
# FIELD CALIBRATIONS DATA OFFSETS
    
    ## Get field measurements of water level in the weir notch
    field_meas_level = fds.loc[[site_name]][['Datetime','Level_above_V_in_Before','Level_above_V_in_After']]
    field_meas_level['Datetime_after'] = field_meas_level['Datetime'].apply(lambda x: x + dt.timedelta(minutes=5))
    field_meas_flow = fds.loc[[site_name]][['Datetime','Flow_gpm_1','Flow_gpm_2','Flow_gpm_3']]
    
    ##field_meas_level = field_meas_level[field_meas_level['Level_above_V_in_Before']>=0.0]
    print ('Water Level Field Measurements: ')
    print (field_meas_level[['Datetime','Level_above_V_in_Before','Datetime_after','Level_above_V_in_After']])
    print ('')

    
    ## Add PT level data to field measured level 
    for t in field_meas_level['Datetime'].values:
        t = pd.to_datetime(t)
        print ('Field measurement time:' + str(t))
        try:
            field_meas_level.loc[field_meas_level['Datetime']==t, 'Level_in'] = WL.ix[t]['Level_in']
        except:
            try:
                ' Shifting calibration time back 5 miutes....'
                t = t - dt.timedelta(minutes=5)
                field_meas_level.loc[field_meas_level['Datetime']==t, 'Level_in'] = WL.ix[t]['Level_in']
            except:
                try:
                    ' Shifting original calibration time forward 5 miutes....'
                    t = t + dt.timedelta(minutes=10)
                    field_meas_level.loc[field_meas_level['Datetime']==t, 'Level_in'] = WL.ix[t]['Level_in']
                except:
                    pass
    
    ## Add the flow that would be predicted from v-notch equation
    try: 
        field_meas_level.loc[:,'Predicted_flow_Before'] =  [HvF.ix[np.round(x,2)]['Q (GPM)'] for x in field_meas_level['Level_above_V_in_Before'].values]
        field_meas_level['Predicted_flow_After'] = [HvF.ix[np.round(x,2)]['Q (GPM)'] for x in field_meas_level['Level_above_V_in_After'].values]
    except KeyError:
        field_meas_level_nozeros = field_meas_level[field_meas_level['Level_above_V_in_Before'] >=0.]
        field_meas_level_nozeros.loc[:,'Predicted_flow_Before'] =  [HvF.ix[np.round(x,2)]['Q (GPM)'] for x in field_meas_level_nozeros['Level_above_V_in_Before'].values]
        field_meas_level_nozeros.loc[:,'Predicted_flow_After'] = [HvF.ix[np.round(x,2)]['Q (GPM)'] for x in field_meas_level_nozeros['Level_above_V_in_After'].values]
    
    
    ## Calculate average offset from field data
    field_meas_level['calculated offset'] = field_meas_level['Level_above_V_in_Before'] - field_meas_level['Level_in']
    
    ## Calculate total offset  
    calculated_offset = field_meas_level['calculated offset'].mean()
    
    ## If it has an Overall Offset in the Excel sheet then use it
    print ('')
    if pd.notnull(calculated_offset) == True and pd.notnull(overall_offset)== False:
        tot_offset =  calculated_offset
        print ('Calculated offset (mean)= '+"%.2f"%calculated_offset)
        print ('Total offset = '+"%.2f"%tot_offset)
    elif pd.notnull(calculated_offset)==False and pd.notnull(overall_offset)==True:
        tot_offset =  overall_offset
        print ('Overall offset from Excel sheet = '+str(overall_offset))
        print ('Total offset = '+"%.2f"%tot_offset)
    elif pd.notnull(calculated_offset)==True and pd.notnull(overall_offset)==True:
        tot_offset =  calculated_offset + overall_offset
        print ('Calculated offset (mean)= '+"%.2f"%calculated_offset)
        print ('Overall offset from Excel sheet ='+str(overall_offset))
        print ('Total offset = '+"%.2f"%tot_offset)
    else:
        tot_offset =  0.0
        print ('Total offset = '+"%.2f"%tot_offset)
#    tot_offset = overall_offset ## MANUAL OVERRIDE

    ###############################################
    
    ## Apply field calibration offset to PT data    
    WL['offset_raw_level'] = WL['Level_in'] + tot_offset

    ## Drop negative values or keep them as zeros
    WL['offset_corr_level'] =  WL['Level_in'] + tot_offset
    if negative_level_as_zero_flow == 'True' or negative_level_as_zero_flow == True:
        print ('Negative Levels are 0 flow')
        WL['offset_corr_level'] = WL['offset_corr_level'].where(WL['offset_corr_level'] >= 0., 0.)
        
    elif negative_level_as_zero_flow == 'False' or negative_level_as_zero_flow == False:
        print ('Negative Levels are NaN (no data during downloading)')
        WL['offset_corr_level'] = WL['offset_corr_level'].where((WL['offset_corr_level']>= 0.), np.nan)
    else:
        print ('Negative Levels NOT SET')
        WL['offset_corr_level'] = WL['offset_corr_level'].where((WL['offset_corr_level']>= 0.), np.nan)
 
###  CALCULATE FLOW
    ## Look up to v-notch flow table and make Flow data from corrected level data
    try:    
        WL['offset_flow']  = WL['offset_corr_level'].apply(lambda x: HvF.ix[np.round(x,2)]['Q (GPM)'])    
    except KeyError:
        print('KEY ERROR, level value over 35 inches')
        WL['offset_corr_level'] =  WL['offset_corr_level'][WL['offset_corr_level'] <= 35.0]
        WL['offset_flow']  =WL['offset_corr_level'].apply(lambda x: HvF.ix[np.round(x,2)]['Q (GPM)'])    
    
    ## Calculate flows when overtopping the weir
    WL['Flow_compound_weir'] = CTRSC_compound_weir(site_name, WL, weir_dims)#,  True, True)
    WL['Flow_compound_weir'] = WL['Flow_compound_weir']
    ## Get field measurements of flow
    print ('Flow Field Measurements: ')
    print (field_meas_flow)
    print ('')
    
# ADD PRECIP DATA 
    ## READ IN precip data    
    rainfile = [s for s in os.listdir(raindir) if raingauge_dict[site_name] in s][0]
    print ('')
    print ('Site: '+site_name+'  Precip file: '+rainfile)
    rain = pd.read_excel(raindir+rainfile)
    rain.index = pd.to_datetime(rain['Reading'])
    ## Resample to regular interval and fill non-data with zeros
    rain = rain.resample('15Min').sum()
    rain  = rain.fillna(0.)
    rain_1D = rain.resample('1D').sum()

# MANUAL CLIPS OF BAD DATA/STORMFLOW  
    try:  
        clips_RF = pd.read_excel(hydrograph_fileoutput_dir+'Offsets and Clip times_RF.xlsx',sheetname='Clips',index_col=0,parse_cols='A:F')   
    except:
        clips_RF = pd.DataFrame()
        pass
    try:  
        clips_LD = pd.read_excel(hydrograph_fileoutput_dir+'Offsets and Clip times_LD.xlsx',sheetname='Clips',index_col=0,parse_cols='A:F')   
    except:
        clips_LD = pd.DataFrame()
        pass
    try:
        clips_JN = pd.read_excel(hydrograph_fileoutput_dir+'Offsets and Clip times_JN.xlsx',sheetname='Clips',index_col=0,parse_cols='A:F')   
    except:
        clips_JN = pd.DataFrame()
        pass
    try:
        clips_combined = pd.read_excel(hydrograph_fileoutput_dir+'Offsets and Clip times.xlsx',sheetname='Clips',index_col=0,parse_cols='A:F')   
    except:
        clips_combined= pd.DataFrame()
        pass
        
    clips = pd.concat([clips_RF, clips_LD])#, clips_RF])
    clips_list_for_site = clips[clips.index  == site_name].drop_duplicates('Start')

    ## Copy flow over to new column...
    WL['offset_flow_clipped'] = WL['offset_flow']
    WL['Flow_compound_clipped'] = WL['Flow_compound_weir']
    
    ## iterate over list of bad data and clip from 'offset_flow_clipped'....
    for clip in clips_list_for_site.iterrows():
        clip_start, clip_end = clip[1]['Start'], clip[1]['End']
        reason = clip[1]['Reason']
        if pd.isnull(clip_start)==False and pd.isnull(clip_end) == False:
            print ('Clipping data....')
            print ('Clipped: '+clip_start.strftime('%m/%d/%y %H:%M')+'-'+clip_end.strftime('%m/%d/%y %H:%M')+' Reason: '+reason)
            ## set data in storm_clip_data indices to nan
            WL.loc[clip_start:clip_end, ['offset_flow_clipped']] = np.nan
            WL.loc[clip_start:clip_end, ['Flow_compound_clipped']] = np.nan
        else:
            print ('No data to clip...')
            pass
    start, end = dt.datetime(2019,5,1,0,0), dt.datetime(2019,5,15,23,59)
    WL = WL.reindex(index=pd.date_range(start,end,freq='5Min')) ######CHANGE TO 5Min OR 15Min depending on the data set

### PLOT QC hydrograph

    fig, (ax1, ax2, ax4) = plt.subplots(3,1,figsize=(18,10),sharex=True)
    ## Plot full scale level data
    ## raw
    ax1.plot_date(WL.index, WL['Level_in'], marker='None',ls='-',c='g',label='Raw level')
    ## raw + offset
    ax1.plot_date(WL.index, WL['offset_raw_level'], marker='None',ls='-',c='grey',alpha=0.5,label='Raw level + offset')
    ## Plot offset level
    ax1.plot_date(WL.index, WL['offset_corr_level'], marker='None',ls='-',c='orange',label='Offset Final Level ('+"%.2f"%tot_offset+' in.)')
    ## Plot field measurements
    ax1.plot_date(field_meas_level['Datetime'],field_meas_level['Level_above_V_in_Before'],marker='s',c='r',label='Field measurement BEFORE')
    ax1.plot_date(field_meas_level['Datetime'],field_meas_level['Level_above_V_in_After'],marker='o',c='g',label='Field measurement AFTER')
    ## Plot maximum v-notch height
    ax1.axhline(weir_dims.loc[site_name,'h2'],color='k')
    textstr = 'Weir crest height: '+str(weir_dims.loc[site_name,'h2'])+' inches'
    ax1.annotate(textstr, (mpl.dates.date2num(dt.datetime(2018,6,1)),weir_dims.loc[site_name,'h2']))
    ## Plot temp
    #ax1_1 = ax1.twinx()
    #ax1_1.plot_date(WL.index, WL['Temp_F'], marker='None',ls='-',c='grey',label='Temp F')
    
    ## Plot full scale flow data or
    ## Conductivity data if available
    if 'Spec_cond_uScm' in WL.columns:
        ax2.plot_date(WL.index, WL['Spec_cond_uScm'], marker='None',ls='-',c='orange',label='Spec_cond_uScm')
        ax2.set_ylabel('Sp.Cond (uS/cm)',color='orange'), 
    else:
        ax2.plot_date(WL.index, WL['offset_flow'], marker='None',ls='-',c='teal',label='Flow from raw level')
        ax2.set_ylabel('Flow (gpm)',color='b'), 
        
    ## Put notes on the plot
    if site_name == 'CAR-069':
        site_name = 'CAR-069L'
    for row in fds.loc[[site_name]][['Datetime','NOTES']].iterrows():
        note = '\n'.join(textwrap.wrap(row[1]['NOTES'], 16))
        ax2.annotate(note,xy=(pd.to_datetime(row[1]['Datetime']),WL['offset_flow'].max()),rotation=90,verticalalignment='bottom')
        ax2.axvline(pd.to_datetime(row[1]['Datetime']),color='grey',alpha=0.5)
    if site_name == 'CAR-069L':
        site_name = 'CAR-069'   
    ### Plot precip on inverted, secondary y axis
    ax3 = ax2.twinx()
    ax3.plot_date(rain.index, rain['Value'], marker='None',ls='steps-mid',color='b',label='Precip: '+raingauge_dict[site_name])
    
    ## Plot all flow data as greyed out bad data
    ax4.plot_date(WL.index, WL['offset_flow'], marker='None',ls='-',c='red',alpha=0.5,label='Simple V flow')
    ## Plot compound weir flow data (including correct flow for overtopping flows)
    ax4.plot_date(WL.index, WL['Flow_compound_weir'], marker='None',ls='-',c='grey',label='Clipped flow data (storm/bad)')
    ## Plot corrected data (offset and clipped)
    ax4.plot_date(WL.index, WL['Flow_compound_clipped'], marker='None',ls='-',c='blue',label='Corrected Flow, Compound, Clipped')
    
    ## Plot field measurements
    ax4.plot_date(field_meas_flow['Datetime'],field_meas_flow['Flow_gpm_1'],marker='o',c='r',label='Field meas. flow 1')
    ax4.plot_date(field_meas_flow['Datetime'],field_meas_flow['Flow_gpm_2'],marker='o',c='g',label='Field meas. flow 2')
    ax4.plot_date(field_meas_flow['Datetime'],field_meas_flow['Flow_gpm_3'],marker='o',c='darkorange',label='Field meas. flow 3')
    ## Flow predicted from field measurement of just level, using v-notch equation
#    try:
#        ax4.plot_date(field_meas_level['Datetime'],field_meas_level['Predicted_flow_Before'],marker='o',c='blue',label='Flow from level meas_before')
#        ax4.plot_date(field_meas_level['Datetime'],field_meas_level['Predicted_flow_After'],marker='o',c='black',label='Flow from level meas_after')
#    except:
#        #ax4.plot_date(field_meas_level_nozeros['Datetime'],field_meas_level_nozeros['Predicted_flow_Before'],marker='o',c='blue',label='Flow from level meas_before')
#        ax4.plot_date(field_meas_level_nozeros['Datetime'],field_meas_level_nozeros['Predicted_flow_After'],marker='o',c='black',label='Flow from level meas_after')
    
    ### Plot precip on inverted, secondary y axis
    ax4_2 = ax4.twinx()
    ax4_2.plot_date(rain.index, rain['Value'], marker='None',ls='steps-mid',color='b',label='Precip: '+raingauge_dict[site_name])
    
    ## Format/set limits
    ## full scale flow
    ax1.set_ylim(-3, WL['Level_in'].max() * 1.1)
    #ax2.set_ylim(-WL['offset_flow'].max() * 0.5, WL['offset_flow'].max() * 2.)
    ax3.set_ylim(0, rain['Value'].max() * 2.)
    ax4_2.set_ylim(0, rain['Value'].max() * 3.)
    ax3.invert_yaxis(), ax4_2.invert_yaxis()
    ## low flow
    ax4.set_ylim(-WL['Flow_compound_clipped'].max() * 0.45, WL['Flow_compound_clipped'].max() * 1.2)
    ## set x-axis to monitoring period
    ax1.set_xlim(start, end)
    ax1.grid(True)
    ax1.set_ylabel('Level (inches)',color='g')
    ax3.set_ylabel('Precip (inches)',color='teal')
    ax4.set_ylabel('Flow (gpm)',color='b')
    
    ax1.legend(fontsize=12,numpoints=1,ncol=1,loc='upper left')
    ax2.legend(fontsize=12,loc='lower left'), ax3.legend(fontsize=12,loc='lower right')
    ax4.legend(fontsize=12,numpoints=1,ncol=5,loc='lower left')
    
    ax4.xaxis.set_major_formatter(mpl.dates.DateFormatter('%A \n %m/%d/%y %H:%M'))
    
    fig.suptitle('Data processing for site: '+site_name,fontsize=16,fontweight='bold')
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    


#%% SAVE TO EXCEL

## SAVE EXCEL FILE WITH CALIBRATION DATA
    calibration_ExcelFile = pd.ExcelWriter(calibration_output_dir+site_name+'-calibration.xlsx')
    WL.to_excel(calibration_ExcelFile,'Level and Flow data')
    rain.to_excel(calibration_ExcelFile,'rain')
    field_meas_flow.to_excel(calibration_ExcelFile,'Flow calibration')
    field_meas_level.to_excel(calibration_ExcelFile,'Level calibration')
    
    offset_df = pd.DataFrame({'calculated_offset':calculated_offset,'overall_offset':overall_offset,'total_offset':tot_offset},index=['offsets']).to_excel(calibration_ExcelFile,'offsets')
    calibration_ExcelFile.save()
    
### FINALIZED FLOW OUTPUT
    Corr_flow = WL[['offset_flow','Flow_compound_weir','Flow_compound_clipped']].ix[start:]
    Corr_flow.columns = ['Flow (gpm)', 'Flow compound weir (gpm)', 'Flow compound weir stormflow clipped (gpm)']
    
    ## CAR-069 is a double outfall but only one side is measuring
    ## valid flow, the other side is leaking. Flow data from one side is
    ## doubled to provide a valid estimate of total flow
    if site_name == 'CAR-069':
        Corr_flow['Flow (gpm)'] = Corr_flow['Flow (gpm)'] * 2.
        Corr_flow['Flow compound weir (gpm)'] = Corr_flow['Flow compound weir (gpm)'] * 2.
        Corr_flow['Flow compound weir stormflow clipped (gpm)'] = Corr_flow['Flow compound weir stormflow clipped (gpm)'] * 2.
    
    Corr_flow.loc[:,('Year')] = Corr_flow.index.year
    Corr_flow.loc[:,('Month')] = Corr_flow.index.month
    Corr_flow.loc[:,('Day')] = Corr_flow.index.day
    Corr_flow.loc[:,('Hour')] = Corr_flow.index.hour
    Corr_flow.loc[:,('Minute')] = Corr_flow.index.minute
    Corr_flow.loc[:,('Weekday')] = Corr_flow.index.map(lambda x: calendar.day_name[x.weekday()])
    
    ## Kick out to Excel
    final_flow_ExcelFile = pd.ExcelWriter(hydrograph_fileoutput_dir+site_name+'-working draft.xlsx')
    
    max_row, rain_max_row = Excel_Plots(site_name, Corr_flow, rain_1D, final_flow_ExcelFile, start, end)
    
### Pivot TABLES

    ## Old style
    PivotTable_Sum = pd.pivot_table(Corr_flow,values='Flow compound weir stormflow clipped (gpm)', columns=['Month','Day','Weekday'], index=['Hour'], aggfunc=np.sum)  
    PivotTable_Sum.to_excel(final_flow_ExcelFile,site_name+'PivotTable-Sum')
    
    ## Seven day Average style
    Corr_flow['Flow compound weir stormflow clipped (gpm)'] = Corr_flow['Flow compound weir stormflow clipped (gpm)'].astype('float')
    PivotTable = pd.pivot_table(Corr_flow,values='Flow compound weir stormflow clipped (gpm)',columns=['Weekday'],index=['Hour'],aggfunc=np.mean)
    col_order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    PivotTable = PivotTable.reindex_axis(col_order,axis=1)
    
    PivotTable.to_excel(final_flow_ExcelFile,site_name+'PivotTable-Avg')
    
    ## Format Pivot Table 
    pivot = final_flow_ExcelFile.sheets[site_name+'PivotTable-Avg']
    
    ## Conditional formatting
    # Add a format. Yellow fill with RED text.
    redtxt = final_flow_ExcelFile.book.add_format({'bg_color': '#FFFF00',
                               'font_color': '#FF0000'})
    # Add a format. Yellow fill with black text.
    blacktxt = final_flow_ExcelFile.book.add_format({'bg_color': '#FFFF00',
                               'font_color': '#000000'})

    day_cols={'Monday':'B','Tuesday':'C','Wednesday':'D','Thursday':'E','Friday':'F','Saturday':'G','Sunday':'H'}
    col_order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    
    for index, letter in enumerate(string.ascii_uppercase[1:9]):
        ## Count cells over 25th percentile
        pivot.write_formula(25,index, '=SUMPRODUCT(--('+letter+'2:'+letter+'25>PERCENTILE($B$2:$H$25,0.85)))')
        
    
    ## Annotate
    pivot.write(25,0, 'Count>15% by day')
    pivot.write(26,3, 'Count>15% by day')
    
    for i, day in zip(np.arange(27,34,1),col_order):
        col = day_cols[day]
        print(i, day, col)
        pivot.write(i,0,day)
        pivot.write_formula(i,1,'=AVERAGE('+col+'2:'+col+'25)')
        pivot.write(i,2,'>Avg')
        pivot.write_formula(i,3,'=SUM('+col+'26)')
        
        ## Conditionally format each day
        pivot.conditional_format(col+'2:'+col+'25', {'type': 'cell','criteria': '>=','value':'$B$35','format': redtxt})
        pivot.conditional_format(col+'2:'+col+'25', {'type': 'cell','criteria': '>=','value':'$B$'+str(i+1),'format': blacktxt})
        
      
    pivot.write(34,0,'Top 15th%ile (excluding zeros)')
    pivot.write_formula(34,1,'=PERCENTILE(IF(B2:H25>0, B2:H25), 0.85)')
    pivot.write(34,2,'>15th%ile excl 0s')
    pivot.write(34,3,'(need to hit F2, then Ctrl+Shift+Enter to execute equation if you edit it)')
    
    pivot.write(35,0,'Top 15th%ile (including zeros)')
    pivot.write_formula(35,1,'=PERCENTILE(B2:H25,0.85)')
    pivot.write(35,2,'>15th%ile incl 0s')

### SAVE FINAL FILE
    final_flow_ExcelFile.save()


# Final Hydrograph    

    fig, ax1 = plt.subplots(1,1,figsize = (14,8))
    ## FLOW
    ax1.plot_date(Corr_flow.index, Corr_flow['Flow compound weir (gpm)'], marker='None', ls='-', c='grey',alpha=0.2,label='Stormflow, clipped, compound weir')
    ax1.plot_date(Corr_flow.index, Corr_flow['Flow compound weir stormflow clipped (gpm)'], marker='None', ls='-', c='b',label='Flow, compound weir')
    ## RAIN
    ax2 = ax1.twinx()
    ax2.plot_date(rain.index, rain['Value'], marker='None',ls='steps-mid',color='skyblue',label='Precip: '+raingauge_dict[site_name])
    ## FORMAT
    ax1.set_ylim(-Corr_flow['Flow compound weir stormflow clipped (gpm)'].max() * 0.25, Corr_flow['Flow compound weir stormflow clipped (gpm)'].max() * 2.)
    ax2.set_ylim(0, rain['Value'].max() * 3.)
    ax2.invert_yaxis()
    ## LEGEND
    ax1.legend(fontsize=12,loc='lower left'), ax2.legend(fontsize=12,loc='lower right')
    
    ax1.set_ylabel('Flow (gpm)'), ax2.set_ylabel('Precip (inches)')
    ax1.xaxis.set_major_formatter(mpl.dates.DateFormatter('%A \n %m/%d/%y %H:%M'))
    plt.xticks(rotation=90)
    
    ## set x-axis to monitoring period
    ax1.set_xlim(start, end)
    
    fig.suptitle('Working Draft Hydrograph for site: '+site_name,fontsize=16,fontweight='bold')
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)

    fig.savefig(hydrograph_figureoutput_dir+'Hydrographs/'+site_name+'-working hydrograph.png')
    plt.close()
    ## HEAT MAP Averaged by Weekday
    #
    #col_order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    #
    ### 
    #data = pd.pivot_table(Corr_flow,values='Flow (gpm) stormflow clipped',columns=['Weekday'],index=['Hour'],aggfunc=np.sum)
    #
    #data = data.reindex_axis(col_order,axis=1)
    #
    #data.median()
    #
    #fig, ax = plt.subplots(1,1,figsize=(10,8))
    #
    #cax = ax.pcolor(data,shading='interp')
    #
    #ax.set_ylabel('HOUR of DAY',fontsize=14,fontweight='bold')
    #ax.set_xlabel('DAY of WEEK',fontsize=14,fontweight='bold')
    #ax.set_ylim(0,24)
    #ax.invert_yaxis()
    #cbar = fig.colorbar(cax,orientation='vertical')
    #
    #
    #plt.yticks(np.arange(0.5,24.5,1.),data.index.values)
    #plt.xticks(np.arange(.5,7.5,1.), data.columns.values)
    #
    #fig.suptitle('Heatmap of flow (sum) for '+site_name,fontsize=14,fontweight='bold')
    #plt.tight_layout()
    #plt.subplots_adjust(top=0.94)
    #
    #fig.savefig(hydrograph_figureoutput_dir+'Heatmaps/by weekday/'+site_name+'-heatmap by weekday.png')
    
    
    
    #%% HEAT MAP NOT Averaged by Weekday
    
    #col_order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    
    data = pd.pivot_table(Corr_flow,values='Flow (gpm) stormflow clipped', columns=['Month','Day','Weekday'], index=['Hour'], aggfunc=np.sum)  
    #data = data.reindex_axis(col_order,axis=1)
    
    
    fig, ax = plt.subplots(1,1,figsize=(10,8))
    
    cax = ax.pcolor(data,shading='interp')
    
    ax.set_ylabel('HOUR of DAY',fontsize=14,fontweight='bold')
    ax.set_xlabel('DAY',fontsize=14,fontweight='bold')
    ax.set_ylim(0,24)
    ax.invert_yaxis()
    cbar = fig.colorbar(cax,orientation='vertical')
    
    
    plt.yticks(np.arange(0.5,24.5,1.),data.index.values)
    plt.xticks(np.arange(.5,len(data.columns)+0.5,1.), data.columns.values)
    
    fig.suptitle('Heatmap of flow (sum) for '+site_name,fontsize=14,fontweight='bold')
    plt.tight_layout()
    plt.subplots_adjust(top=0.94)
    plt.close()
    #fig.savefig(hydrograph_figureoutput_dir+'Heatmaps/'+site_name+'-heatmap.png')
    
    #%% CHECK FIELD FLOW MEASUREMENTS
    
    field_meas_level['Flow_meas_gpm'] = field_meas_flow['Flow_gpm_1']
    
    fig, ax = plt.subplots(1,1,figsize=(12,10))
    
    ax.plot([0,1000],[0,1000],ls='-',marker='None',color='grey',alpha=0.5,label='1:1')
    ax.plot(field_meas_level['Flow_meas_gpm'],field_meas_level['Predicted_flow_Before'],ls='None',marker='o',markersize=12,label='Flow')
    
    ax.set_xlabel('Measured Flow (gpm)',fontweight='bold',fontsize=16)
    ax.set_ylabel('Predicted flow from Measured Level (gpm)',fontweight='bold',fontsize=16)
    
    ax.set_xlim(0, 1.3 *field_meas_level['Predicted_flow_Before'].max())
    ax.set_ylim(0, 1.3 *field_meas_level['Predicted_flow_Before'].max())
    ax.legend(loc='upper left')
    
    fig.suptitle('Measured flow vs Flow from measured v-notch height',fontweight='bold',fontsize=20)
    ax.set_title(site_name,fontweight='bold',fontsize=18)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.close()
    
    #%% CHECK FIELD FLOW MEASUREMENTS against final flow
    
    field_meas_flow = field_meas_flow[field_meas_flow['Datetime'] > dt.datetime(2018,5,1)]
    final_flow_vals = pd.DataFrame(field_meas_flow[['Datetime','Flow_gpm_1']])
    final_flow_vals['offset_flow'] = field_meas_flow['Datetime'].apply(lambda x: WL.ix[x]['offset_flow'])
    final_flow_vals['difference_gpm'] = final_flow_vals['offset_flow'] - final_flow_vals['Flow_gpm_1']
    final_flow_vals['difference_%'] = (abs(final_flow_vals['offset_flow'] - final_flow_vals['Flow_gpm_1']) / final_flow_vals['Flow_gpm_1']) * 100.
    print(final_flow_vals)
    print() 
    print('Average difference between measured, and final processed flow values: '+"%.3f"%final_flow_vals['difference_gpm'].mean() +' gpm')
    print('Average difference between measured, and final processed flow values: '+"%.1f"%final_flow_vals['difference_%'].mean() +' %')
    
    
    fig, ax = plt.subplots(1,1,figsize=(12,10))
    
    ax.plot([0,1000],[0,1000],ls='-',marker='None',color='grey',alpha=0.5,label='1:1')
    ax.plot(final_flow_vals['Flow_gpm_1'],final_flow_vals['offset_flow'],ls='None',marker='o',markersize=12,label='Flow')
    
    ax.set_xlabel('Measured Flow (gpm)',fontweight='bold',fontsize=16)
    ax.set_ylabel('Flow from Processed Level (gpm)',fontweight='bold',fontsize=16)
    
    ax.set_xlim(0, 1.3 *final_flow_vals[['offset_flow','Flow_gpm_1']].max().max())
    ax.set_ylim(0, 1.3 *final_flow_vals[['offset_flow','Flow_gpm_1']].max().max())
    ax.legend(loc='upper left')
    
    fig.suptitle('Measured flow vs Flow from measured v-notch height',fontweight='bold',fontsize=20)
    ax.set_title(site_name,fontweight='bold',fontsize=18)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.close()







