# -*- coding: utf-8 -*-
"""
Created on Fri May 19 12:11:47 2017

@author: alex.messina
"""
### BE SURE TO SET YOUR WORKING DIRECTORY TO:
## your github repository ie C:\Users\alex.messina\Documents\GitHub\SD_County_LowFlow\ ##
## to load modules set working directory to C:\Users\alex.messina\Documents\GitHub\SD_County_LowFlow\Python code\


import os

# Import Custom Modules
from Excel_Plots import Excel_Plots    
from OvertoppingFlows import *
from hover_points import *
import string
import textwrap

# Import Standard modules
import datetime as dt
import matplotlib as mpl
from matplotlib import pyplot as plt
import pandas as pd

import numpy as np
import calendar
from scipy import signal
## Image tools
import matplotlib.image as mpimg
from scipy import ndimage
from PIL import Image

## Set Pandas display options
pd.set_option('display.large_repr', 'truncate')
pd.set_option('display.width', 180)
pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 13)
plt.ion()


# Python program to find Excel column name from a  
# given column number 
  
def xl_columnrow(col,row=''):
    """ Convert given row and column number to an Excel-style cell name. """
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result)+str(row)
#xl_columnrow(93,2)


#%%

### UPDATE HERE #####
data_processing_date = '07_31_2019' #end date of data
prev_data_processing_date = '05_31_2019' ## Monthly deliverables ONLY
#####################

maindir = os.getcwd().replace('\\','/') +'/'
print 'Main directory is: '+maindir
## Input directories
raindir = maindir+'0 - Rain Data/'
calibrationdir = maindir+'0 - Field Data Sheets/'
leveldir = maindir+'1 - Level Data monthly submittals/'
ancillarydir = maindir + '0 - Ancillary files/'


## Previous deliverables
prev_deliv_dir = maindir+'2 - Flow output Excel files - working drafts/Data Output '+prev_data_processing_date+'/'

## Output directories
hydrograph_fileoutput_dir =   maindir+'2 - Flow output Excel files - working drafts/Data Output '+data_processing_date+'/'
hydrograph_figureoutput_dir = maindir+'3 - Flow output figures - working hydrographs/Data Output '+data_processing_date+'/'
calibration_output_dir =      maindir+'4 - Level calibration files and figures/Data Output '+data_processing_date+'/'


## Open HvF table
HvF = pd.read_csv(ancillarydir+'HvF-90degweir.csv',index_col='Level (in)')
## WEIR DIMENSIONS FOR OVERTOPPING FLOWS 
weir_dims = pd.read_excel(ancillarydir+'2019 Weir Dims.xlsx',sheetname='May 2019',index_col='Site', parse_cols='A:J')

## Dictionary of rain gauges for each site
## Data from  https://sandiego.onerain.com/rain.php
raingauge_dict = {'CAR-070':'San_Marcos', 'CAR-072':'San_Marcos','CAR-072B':'San_Marcos','CAR-072O':'San_Marcos','SDG-072':'Rancho_Bernardo', 'SDG-080':'Rancho_Bernardo', 'SDG-084':'Rancho_Bernardo','SDG-084J':'Rancho_Bernardo','SDG-085':'Rancho_Bernardo','SDG-085G':'Rancho_Bernardo','SDG-085M':'Rancho_Bernardo','SDR-036':'Flinn_Springs','SDR-041':'Los_Coches', 'SDR-064':'Cactus_County', 'SDR-097':'Los_Coches', 'SDR-098':'Los_Coches', 'SDR-1024':'Cactus_County','SDR-1031':'Los_Coches', 'SDR-127':'Flinn_Springs','SDR-127B':'Flinn_Springs','SDR-203A':'Los_Coches', 'SDR-204A':'Los_Coches','SDR-207':'Los_Coches', 'SDR-223':'Granite_Hills', 'SDR-228':'Cactus_County', 'SDR-568':'Granite_Hills', 'SDR-723':'Cactus_County', 'SDR-740':'Cactus_County', 'SDR-751':'Cactus_County', 'SDR-772':'Los_Coches', 'SDR-780':'Los_Coches', 'SDR-939':'Los_Coches', 'SLR-045':'Deer_Springs','SLR-045A':'Deer_Springs','SLR-045B':'Deer_Springs', 'SLR-095':'Deer_Springs','SWT-019':'Bonita', 'SWT-030':'Roads', 'SWT-055':'La_Mesa', 'SWT-055A':'La_Mesa'}

for k, v in sorted(zip(raingauge_dict.keys(),raingauge_dict.values())):
    print k, v
    
site_list = ['CAR-070',	'CAR-072',	'CAR-072B', 'CAR-072O',	'SDG-072',	'SDG-080',	'SDG-084', 'SDG-084J',	'SDG-085',	'SDG-085G',	'SDG-085M',	'SDR-036',	'SDR-041',	'SDR-064',	'SDR-097',	'SDR-098', 'SDR-1024', 'SDR-1031', 	'SDR-127',	'SDR-127B',	'SDR-203A',	'SDR-204A',	'SDR-207',	'SDR-223', 'SDR-228',	 'SDR-568', 'SDR-723', 'SDR-740', 'SDR-751', 'SDR-772', 'SDR-780', 'SDR-939', 'SLR-045', 'SLR-045A', 'SLR-045B',	'SLR-095',	'SWT-019',	'SWT-030',	'SWT-055',	'SWT-055A']

#site_list = ['CAR-072','SDG-072','SDG-084','SDG-085','SDR-036', 'SDR-041', 'SDR-064','SDR-098', 'SDR-127',  'SLR-045', 'SLR-095']


### OFFSET/ FIELD MEASUREMENTS
## Open spreadsheet
fds = pd.read_excel(calibrationdir+'Weir Calibration Field Form 2019 CURRENT '+data_processing_date+'.xlsx')

## Make a Datetime column (The TIMESTAMP column is when the form was submitted to Google, not the measurement)
fds['Datetime'] = pd.to_datetime(fds['Date'].astype('str') +' '+ fds['Time'].astype('str'))
## Round to 5Min
fds['Datetime'] = fds['Datetime'].apply(lambda x: dt.datetime(x.year, x.month, x.day, x.hour,5*(x.minute // 5)))
## Make Index line up with Excel row numbers for easy reference
fds.index+=2
fds['Line#'] = fds.index

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
    if fid not in site_list and fid != 'LAB_TEST':
        print(fid + ' NOT IN SITE LIST')       
fds.index = fds['SITE ID']

## UP to 2 level measurements
## cm to inches
fds['Level_above_V_cm'] = fds['Height above (or below) v-notch (cm)']
fds['Level_above_V_in'] = fds['Level_above_V_cm'] / 2.54

## UP to 3 flow measurements
## Flow in cfs: mL to cfs divided by seconds
fds['Flow_cfs_1'] = (fds['1. Flow Measurement, Volume in mL']/28316.8) / fds['1. Flow Measurement, Time in Seconds']
fds['Flow_cfs_2'] = (fds['2. Flow Measurement, Volume in mL']/28316.8) / fds['2. Flow Measurement, Time in Seconds']
fds['Flow_cfs_3'] = (fds['3. Flow Measurement, Volume in mL']/28316.8) / fds['3. Flow Measurement, Time in Seconds']
## To gpm
fds['Flow_gpm_1'] = fds['Flow_cfs_1'] * 448.83
fds['Flow_gpm_2'] = fds['Flow_cfs_2'] * 448.83
fds['Flow_gpm_3'] = fds['Flow_cfs_3'] * 448.83

## Drop any duplicate rows so it doesn't weight the average 
fds_len =  len(fds)
fds = fds.drop_duplicates(keep='first')
fds_len_no_dup = len(fds)
diff = fds_len - fds_len_no_dup
print ('')
print ('Dropped '+str(diff)+' duplicate rows')
print ('')

## TEST print
#fds[['Site','Datetime','Level_above_V_in_Before','Level_above_V_in_After','Flow_gpm_1','Flow_gpm_2','Flow_gpm_3']]


#%% START HERE - SITE NAME

## SITE NAME HERE #################


SITE_YOU_WANT_TO_PROCESS = 'SLR-095'


### UPDATE HERE #####
start, end = dt.datetime(2019,5,1,0,0), dt.datetime(2019,7,31,23,59)
#end = dt.datetime(2019,7,22,23,59)

# when you want to cut off calibration points
cal_start = start
#cal_start = dt.datetime(2019,5,12,0,0)
cal_end = dt.datetime(2019,5,31,23,59) 
#cal_end = dt.datetime(2019,6,6,23,59) 

## GET FILE WITH level data
files = [f for f in os.listdir(leveldir) if f.endswith('.xlsx') == True and SITE_YOU_WANT_TO_PROCESS == f.split(' ')[0]]  

if len(files) == 0:
    print 
    print 'No data file found in folder!'
    
for f in files: 
    #MaxFlow = HvF.loc[np.round(MaxLevel,2)]['Q (GPM)']
    print ('')
    print ('Filename: '+f)
    ## Read in the data
    site_name = f.split(' ')[0]     
    print ('Site name: '+site_name)
    print ('')
    ## Read in previous deliverable
    prev_deliv_filename = [d for d in os.listdir(prev_deliv_dir) if d.endswith('.xlsx') == True and SITE_YOU_WANT_TO_PROCESS == d.split('-working draft.xlsx')[0]][0]
    
    print 'Previous Deliverable file: ' + prev_deliv_dir + prev_deliv_filename
    print
    del_df = pd.read_excel(prev_deliv_dir+prev_deliv_filename, sheetname=site_name+'-flow',index_col=0,header=0,parse_cols='A:D')
    
    ## Level data
    WL = pd.read_excel(leveldir+f, skiprows= [0,1], index_col=0, header=0)
    WL = WL.rename(columns={'in Water Level':'Level_in_orig'})
    WL['idx'] = WL.index
    WL = WL.drop_duplicates(subset='idx')
    ## Some were set at 15Min intervals
    WL = WL.reindex(index=pd.date_range(start,end,freq='5Min')).interpolate(method='linear',limit=2)
    
# MANUAL DATA OFFSETS TO GET SERIES TO LINE 
#    offsets = pd.read_excel('C:/Users/alex.messina/Desktop/CountyWeirProcessing/Offsets and Clip times 05_31_2019_AM.xlsx',sheetname='Offsets',index_col=0,parse_cols='A:G')

    ## Open file of offsets
    offsets = pd.read_excel(hydrograph_fileoutput_dir+'Offsets and Clip times '+data_processing_date+'.xlsx',sheetname='Offsets',index_col=0,parse_cols='A:G')
    
    ## Get offsets for each site
    offsets_list_for_site = offsets[offsets.index  == site_name]
    
    ## Add column of zero for data offset
    WL['data_offset'] = 0.
    overall_offset, negative_level_as_zero_flow = np.nan, 'False'
    ## iterate over list manual data offsets
    
    ## THIS IS AS TUPLES SO THE TUPLE IS INDEXED BY NUMBER NOT STRING
    for offset in offsets_list_for_site.itertuples():
        print ('Manual offset from Excel sheet: ')
        print offset
        ## set overall offset
        overall_offset = offset.Overall_Offset_in
        negative_level_as_zero_flow = offset.Neg_Level_as_ZeroFlow ## assign for later use

        ## set data in bad_data indices to nan
        if pd.notnull(offset.Start)==True and pd.notnull(offset.End)==True:
            print ('Manual offset data: '+offset.Start.strftime('%m/%d/%y %H:%M')+' - '+offset.End.strftime('%m/%d/%y %H:%M')+' = '+str(offset.Offset_in)+ ' inches')
        ## add each offset value
            WL.loc[offset.Start:offset.End, ['data_offset']] = offset.Offset_in
        else:
            pass
        print ('')   
    ## Apply all offsets for unique shifts due to bad data or other issues
    WL['Level_in'] = WL['Level_in_orig'] + WL['data_offset']
      
    # FIELD CALIBRATIONS DATA OFFSETS
    field_meas_level = fds.loc[[site_name]][['Datetime','Level_above_V_in']]
    field_meas_flow = fds.loc[[site_name]][['Datetime','Flow_gpm_1','Flow_gpm_2','Flow_gpm_3']]
    
    ## Clip to just May Calibration dates
    field_meas_level_QC = field_meas_level[field_meas_level['Datetime']>dt.datetime(2019,5,31)]
    field_meas_level = field_meas_level[(field_meas_level['Datetime']>=cal_start) & (field_meas_level['Datetime']<=cal_end)]
    
    field_meas_flow_QC =  field_meas_flow[field_meas_flow['Datetime']>dt.datetime(2019,5,31)]
    field_meas_flow =  field_meas_flow[(field_meas_flow['Datetime']>=cal_start) & (field_meas_flow['Datetime']<=cal_end)]
    
    ##field_meas_level = field_meas_level[field_meas_level['Level_above_V_in']>=0.0]
    print ('Water Level Field Measurements: ')
    print (field_meas_level[['Datetime','Level_above_V_in']])
    print ('')

    ## Add PT level data to field measured level 
    for t in field_meas_level['Datetime'].values:
        t = pd.to_datetime(t)
        print ('Field measurement time:' + str(t))
        try:
            print 'Level data from Meter: '
            print WL.loc[t]['Level_in']
            field_meas_level.loc[field_meas_level['Datetime']==t, 'Level_in'] = WL.loc[t]['Level_in']
        except:
            try:
                ' Shifting calibration time back 5 miutes....'
                t = t - dt.timedelta(minutes=5)
                field_meas_level.loc[field_meas_level['Datetime']==t, 'Level_in'] = WL.loc[t]['Level_in']
            except:
                pass
    
    ## Add the flow that would be predicted from v-notch equation
    try: 
        field_meas_level.loc[:,'Predicted_flow'] =  [HvF.loc[np.round(x,2)]['Q (GPM)'] for x in field_meas_level['Level_above_V_in'].values]

    except KeyError:
        field_meas_level_nozeros = field_meas_level[field_meas_level['Level_above_V_in'] >=0.]
        field_meas_level_nozeros.loc[:,'Predicted_flow'] =  [HvF.loc[np.round(x,2)]['Q (GPM)'] for x in field_meas_level_nozeros['Level_above_V_in'].values]

    ## Calculate average offset from field data
    field_meas_level['calculated offset'] = field_meas_level['Level_above_V_in'] - field_meas_level['Level_in']
    
    ## Calculate total offset  
    calculated_offset = field_meas_level['calculated offset'].mean()
    
    ## If it has an Overall Offset in the Excel sheet then use it
    print ('')
    if pd.notnull(calculated_offset) == True and pd.isnull(overall_offset)== True:
        tot_offset =  calculated_offset
        print ('Calculated offset (mean)= '+"%.2f"%calculated_offset)
        print ('Total offset = '+"%.2f"%tot_offset)
        
    elif pd.notnull(calculated_offset)==False and pd.isnull(overall_offset)==False:
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
    
    
    offset_from_May = True
    
    if offset_from_May == True:
        offsets = pd.DataFrame.from_csv(maindir+'offsets_May2019.csv')
        tot_offset = offsets.loc[site_name]['total_offset_May']
        print ('')
        print ('Total offset calculated for the May 2019 deliverable: '+str(tot_offset))
        print ('...using total offset from May 2019 deliverable...')
        print ('')
        
#    tot_offset = -3.09055298818898 ## MANUAL OVERRIDE

    ###############################################
    ## Apply field calibration offset to PT data    
    WL['offset_corr_level'] =  WL['Level_in'] + tot_offset
    ## Save for later to plot negative flows to match up to calibrations
    WL['offset_level_w_neg'] = WL['offset_corr_level']
    
    ## Drop negative values or keep them as zeros
    if negative_level_as_zero_flow == 'True' or negative_level_as_zero_flow == True:
        print ('Negative Levels are 0 flow')
        WL['offset_corr_level'] = WL['offset_corr_level'].where(WL['offset_corr_level'] >= 0., 0.)
        
    elif negative_level_as_zero_flow == 'False' or negative_level_as_zero_flow == False:
        print ('Negative Levels are NaN (no data during downloading)')
        WL['offset_corr_level'] = WL['offset_corr_level'].where(WL['offset_corr_level']>= 0., np.nan)
    else:
        print ('Negative Levels NOT SET')
        WL['offset_corr_level'] = WL['offset_corr_level'].where(WL['offset_corr_level']>= 0., np.nan)
        
    ## Get rid of data dropouts
    WL['offset_corr_level'] = np.where(WL['Level_in'].isnull(),np.nan,WL['offset_corr_level'])
 
###  CALCULATE FLOW
    ## Look up to v-notch flow table and make Flow data from corrected level data
    try:    
        WL['offset_flow']  = WL['offset_corr_level'].apply(lambda x: HvF.loc[np.round(x,2)]['Q (GPM)'])    
        
    except KeyError:
        print
        print('KEY ERROR, level value not found!!')
        print
        WL['offset_corr_level'] =  WL['offset_corr_level'][WL['offset_corr_level'] <= 37.5]
        WL['offset_flow'] =  WL['offset_corr_level'].apply(lambda x: HvF.loc[np.round(x,2)]['Q (GPM)'])    
    
    ## Calculate flows when overtopping the weir
    WL['Flow_compound_weir'] = CTRSC_compound_weir(site_name, WL, weir_dims)#,  True, True)
    WL['Flow_compound_weir'] = WL['Flow_compound_weir'].astype('float').round(2)
    ## Get field measurements of flow
    print ('Flow Field Measurements: ')
    print (field_meas_flow)
    print ('')
    
# ADD PRECIP DATA 
    ## READ IN precip data    
    rainfile = [s for s in os.listdir(raindir+'Raw Data/') if raingauge_dict[site_name] in s][0]
    print ('')
    print ('Site: '+site_name+'  Precip file: '+rainfile)
    rain = pd.read_excel(raindir+'Raw Data/'+rainfile,index_col=0)
    rain = rain.rename(columns={'Value':'Precip_in'})
    rain.index.names = ['Datetime']
    rain.index = pd.to_datetime(rain.index)
    ## Resample to regular interval and fill non-data with zeros
    rain = rain.resample('15Min').sum()
    rain  = rain.fillna(0.)
    rain_1D = rain.resample('1D').sum()

# MANUAL CLIPS OF BAD DATA/STORMFLOW  
    clips = pd.read_excel(hydrograph_fileoutput_dir+'Offsets and Clip times '+data_processing_date+'.xlsx',sheetname='Clips',index_col=0,parse_cols='A:F')   
    # Local copy 'C:/Users/alex.messina/Desktop/CountyWeirProcessing/
#    clips = pd.read_excel('C:/Users/alex.messina/Desktop/CountyWeirProcessing/Offsets and Clip times '+data_processing_date+'.xlsx',sheetname='Clips',index_col=0,parse_cols='A:F')  
    
    clips_list_for_site = clips[clips.index  == site_name]

    ## Copy flow over to new column...
    WL['offset_flow_clipped'] = WL['offset_flow']
    WL['Flow_compound_clipped'] = WL['Flow_compound_weir']
    
    ## iterate over list of bad data and clip from 'offset_flow_clipped'....
    print ('Clipping data....')
    for clip in clips_list_for_site.iterrows():
        clip_start, clip_end = clip[1]['Start'], clip[1]['End']
        reason = clip[1]['Reason']
        if pd.isnull(clip_start)==False and pd.isnull(clip_end) == False:
            print ('Clipped: '+clip_start.strftime('%m/%d/%y %H:%M')+'-'+clip_end.strftime('%m/%d/%y %H:%M')+' Reason: '+reason)
            ## set data in storm_clip_data indices to nan
            WL.loc[clip_start:clip_end, ['offset_flow_clipped']] = np.nan
            WL.loc[clip_start:clip_end, ['Flow_compound_clipped']] = np.nan
        else:
            print ('No data to clip...')
            pass

#%% PLOT QC hydrograph
    fig, (ax1, ax2, ax4) = plt.subplots(3,1,figsize=(18,10),sharex=True)
    ## Plot full scale level data
    ## raw
    ax1.plot_date(WL.index, WL['Level_in_orig'], marker='None',ls='-',c='grey',alpha=0.25,label='Raw level')
    ##raw +overall offset
    ax1.plot_date(WL.index, WL['Level_in'], marker='None',ls='-',c='g',alpha=0.25,label='Raw level+overall offset')
    ## offset level with negatives for matching to negative calibrations
    ax1.plot_date(WL.index, WL['offset_level_w_neg'], marker='None',ls='-',c='grey',alpha=0.5,label='Raw level + tot_offset')
    ## Plot offset level
    ax1.plot_date(WL.index, WL['offset_corr_level'], marker='None',ls='-',c='orange',label='Offset Final Level ('+"%.2f"%tot_offset+' in.)')
    ## Plot field measurements
    ax1.plot_date(field_meas_level['Datetime'],field_meas_level['Level_above_V_in'],marker='s',c='b',label='Initial Calibration measurements')
    ax1.plot_date(field_meas_level_QC['Datetime'],field_meas_level_QC['Level_above_V_in'],marker='s',c='r',label='Follow-up QC measurements')
    ## Plot maximum v-notch height
    ax1.axhline(weir_dims.loc[site_name,'h2'],color='grey')
    ax1.axhline(weir_dims.loc[site_name,'h1'] + weir_dims.loc[site_name,'h2'],color='k')
    textstr = 'Weir crest height: '+str(weir_dims.loc[site_name,'h2'])+' inches'
    ax1.annotate(textstr, (mpl.dates.date2num(dt.datetime(2019,6,1)),weir_dims.loc[site_name,'h2']))
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
    for row in fds.loc[[site_name]][['Datetime','NOTES']].iterrows():
        note = '\n'.join(textwrap.wrap(row[1]['NOTES'], 16))
        ax2.annotate(note,xy=(pd.to_datetime(row[1]['Datetime']),WL['offset_flow'].mean()),rotation=90,verticalalignment='bottom')
        ax2.axvline(pd.to_datetime(row[1]['Datetime']),color='grey',alpha=0.5)

    ### Plot precip on inverted, secondary y axis
    ax3 = ax2.twinx()
    ax3.plot_date(rain.index, rain['Precip_in'], marker='None',ls='steps-mid',color='teal',label='Precip: '+raingauge_dict[site_name])
    
    ## Plot all flow data as greyed out bad data
    #ax4.plot_date(WL.index, WL['offset_flow'], marker='None',ls='-',c='red',alpha=0.5,label='Simple V flow')
    ## Plot compound weir flow data (including correct flow for overtopping flows)
    ax4.plot_date(WL.index, WL['Flow_compound_weir'], marker='None',ls='-',c='grey',alpha=0.5,label='Clipped flow data (storm/bad)')
    ## Plot corrected data (offset and clipped)
    ax4.plot_date(WL.index, WL['Flow_compound_clipped'], marker='None',ls='-',c='green',label='Corrected Flow, Compound, Clipped')
    
    ## Plot field measurements
    ax4.plot_date(field_meas_flow['Datetime'],field_meas_flow['Flow_gpm_1'],marker='o',c='r',label='Field meas. flow 1')
    ax4.plot_date(field_meas_flow['Datetime'],field_meas_flow['Flow_gpm_2'],marker='o',c='g',label='Field meas. flow 2')
    ax4.plot_date(field_meas_flow['Datetime'],field_meas_flow['Flow_gpm_3'],marker='o',c='darkorange',label='Field meas. flow 3')
    ## QC Measurements
    ax4.plot_date(field_meas_flow_QC['Datetime'],field_meas_flow_QC['Flow_gpm_1'],marker='o',c='b',label='Field meas. flow 1')
    ax4.plot_date(field_meas_flow_QC['Datetime'],field_meas_flow_QC['Flow_gpm_2'],marker='o',c='b',label='Field meas. flow 2')
    ax4.plot_date(field_meas_flow_QC['Datetime'],field_meas_flow_QC['Flow_gpm_3'],marker='o',c='b',label='Field meas. flow 3')
    
    ## Previous deliverable data
    #ax4.plot_date(del_df.index,del_df['Flow compound weir (gpm)'], marker='None',ls='-',c='b',label='Previous deliverable')
   
    ### Plot precip on inverted, secondary y axis
    ax4_2 = ax4.twinx()
    ax4_2.plot_date(rain.index, rain['Precip_in'], marker='None',ls='steps-mid',color='teal',label='Precip: '+raingauge_dict[site_name])
    
    ## Format/set limits
    ## full scale flow
    ax1.set_ylim(-3, WL['Level_in'].max() * 1.1)
    #ax2.set_ylim(-WL['offset_flow'].max() * 0.5, WL['offset_flow'].max() * 2.)
    ax3.set_ylim(0, rain['Precip_in'].max() * 2.)
    ax4_2.set_ylim(0, rain['Precip_in'].max() * 3.)
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


#%% CHECK FIELD LEVEL vs OFFSET LEVEL

meas_vals = field_meas_level.loc[[site_name]][['Datetime','Level_above_V_in']]
meas_vals['Offset Level Data (in)'] =  meas_vals['Datetime'].apply(lambda x: WL.loc[x]['offset_level_w_neg'])

meas_vals_QC = field_meas_level_QC.loc[[site_name]][['Datetime','Level_above_V_in']]
meas_vals_QC = meas_vals_QC[meas_vals_QC['Datetime']<end]
meas_vals_QC['Offset Level Data (in)'] =  meas_vals_QC['Datetime'].apply(lambda x: WL.loc[x]['offset_level_w_neg'])

###
fig, ax = plt.subplots(1,1,figsize=(12,10))

one_to_one = ax.plot([-10,1000],[-10,1000],ls='-',marker='None',color='grey',alpha=0.5,label='1:1')
one_to_one_plus = ax.plot([-10,1000],[-10.1,1000.1],ls='--',marker='None',color='grey',alpha=0.5,label='+0.1')
one_to_one = ax.plot([-10,1000],[-9.9,999.9],ls='--',marker='None',color='grey',alpha=0.5,label='-0.1')
points = ax.plot(meas_vals['Level_above_V_in'],meas_vals['Offset Level Data (in)'],ls='None',marker='o',c='b',markersize=12,label='Initial Calibration measurements')

QCpoints = ax.plot(meas_vals_QC['Level_above_V_in'],meas_vals_QC['Offset Level Data (in)'],ls='None',marker='o',c='r',markersize=12,label='Follow-up QC measurements', )
 
    
    
ax.set_xlabel('Measured Level (in)',fontweight='bold',fontsize=16)
ax.set_ylabel('Offset Level data (in)',fontweight='bold',fontsize=16)

max_level = meas_vals[[u'Level_above_V_in', u'Offset Level Data (in)']].max().max()
ax.set_xlim(0, 1.3 *max_level.max())
ax.set_ylim(0, 1.3 *max_level.max())

ax.legend(loc='upper left')

fig.suptitle('Measured level vs Offset Level',fontweight='bold',fontsize=20)
ax.set_title(site_name,fontweight='bold',fontsize=18)

plt.tight_layout()
plt.subplots_adjust(top=0.93)

hover_points(points, list(meas_vals['Datetime']), fig, ax)
hover_points(QCpoints, list(meas_vals_QC['Datetime']), fig, ax)

#%% CHECK PREDICTED FLOW FROM LEVEL vs FLOW MEASUREMENTS

field_meas = fds.loc[[site_name]][['Datetime','Level_above_V_in','Flow_gpm_1','Flow_gpm_2','Flow_gpm_3']]
field_meas['Predicted_flow'] = [HvF.loc[np.round(x,2)]['Q (GPM)'] for x in field_meas['Level_above_V_in'].values]


meas_vals = pd.DataFrame()
for col in ['Flow_gpm_1','Flow_gpm_2','Flow_gpm_3']:
    meas_vals = meas_vals.append(field_meas[['Datetime','Level_above_V_in','Predicted_flow',col]].rename(columns={col:'Flow_gpm'}))
    
meas_vals = meas_vals.dropna()
meas_vals_QC = meas_vals[meas_vals['Datetime']>dt.datetime(2019,5,31)]
meas_vals = meas_vals[meas_vals['Datetime']<dt.datetime(2019,5,31)]


###
fig, ax = plt.subplots(1,1,figsize=(12,10))

one_to_one = ax.plot([0,1000],[0,1000],ls='-',marker='None',color='grey',alpha=0.5,label='1:1')
points = ax.plot(meas_vals['Flow_gpm'],meas_vals['Predicted_flow'],ls='None',marker='o',markersize=12,label='Initial Calibration measurements',c='b')

QCpoints = ax.plot(meas_vals_QC['Flow_gpm'],meas_vals_QC['Predicted_flow'],ls='None',marker='o',markersize=12,label='Follow-up QC measurements',c='r')

ax.set_xlabel('Measured Flow (gpm)',fontweight='bold',fontsize=16)
ax.set_ylabel('Predicted flow from Measured Level (gpm)',fontweight='bold',fontsize=16)

ax.set_xlim(0, 1.3 *meas_vals['Predicted_flow'].max())
ax.set_ylim(0, 1.3 *meas_vals['Predicted_flow'].max())

ax.legend(loc='upper left')

fig.suptitle('Measured flow vs Flow from measured v-notch height',fontweight='bold',fontsize=20)
ax.set_title(site_name,fontweight='bold',fontsize=18)

plt.tight_layout()
plt.subplots_adjust(top=0.93)

hover_points(points, list(meas_vals['Datetime']), fig, ax)
hover_points(QCpoints, list(meas_vals_QC['Datetime']), fig, ax)

#%% CHECK FLOW MEASUREMENTS vs Final data

## Calibration measurements
field_meas = field_meas_flow[(field_meas_flow['Datetime']>=dt.datetime(2019,5,1)) & (field_meas_flow['Datetime']<=dt.datetime(2019,5,31))]
## Concatenate calibration flow values (Flow 1,2,3)
final_flow_vals = pd.DataFrame()
for col in ['Flow_gpm_1','Flow_gpm_2','Flow_gpm_3']:
    final_flow_vals = final_flow_vals.append(field_meas[['Datetime',col]].rename(columns={col:'Flow_gpm'}))
final_flow_vals = final_flow_vals[np.isfinite(final_flow_vals['Flow_gpm'])]
## Get flow data for the times of the calibration flow measurements
final_flow_vals['offset_flow'] = final_flow_vals['Datetime'].apply(lambda x: WL.loc[x]['offset_flow'])

## QC measurements  
field_meas_QC = fds.loc[[site_name]][['Datetime','Flow_gpm_1','Flow_gpm_2','Flow_gpm_3']]
field_meas_QC = field_meas_QC[field_meas_QC['Datetime']>=dt.datetime(2019,5,31)]   
## Concatenate calibration flow values (Flow 1,2,3)
final_flow_vals_QC = pd.DataFrame()
for col in ['Flow_gpm_1','Flow_gpm_2','Flow_gpm_3']:
    final_flow_vals_QC = final_flow_vals_QC.append(field_meas_QC[['Datetime',col]].rename(columns={col:'Flow_gpm'}))
final_flow_vals_QC = final_flow_vals_QC[np.isfinite(final_flow_vals_QC['Flow_gpm'])]

# Get flow data for the times of the QC flow measurements
final_flow_vals_QC = final_flow_vals_QC[(final_flow_vals_QC['Datetime']>=dt.datetime(2019,5,31))&(final_flow_vals_QC['Datetime']<=end)]
final_flow_vals_QC['offset_flow'] = final_flow_vals_QC['Datetime'].apply(lambda x: WL.loc[x]['offset_flow'])

## Calculate flow differences in gpm and %
final_flow_vals['difference_gpm'] = final_flow_vals['offset_flow'] - final_flow_vals['Flow_gpm']
final_flow_vals['difference_%'] = (abs(final_flow_vals['offset_flow'] - final_flow_vals['Flow_gpm']) / final_flow_vals['Flow_gpm']) * 100.

print final_flow_vals
print 
print 'Average difference between measured, and final processed flow values: '+"%.3f"%final_flow_vals['difference_gpm'].mean() +' gpm'
print 'Average difference between measured, and final processed flow values: '+"%.1f"%final_flow_vals['difference_%'].mean() +' %'


fig, ax = plt.subplots(1,1,figsize=(12,10))

one_to_one = ax.plot([0,1000],[0,1000],ls='-',marker='None',color='grey',alpha=0.5,label='1:1')
points = ax.plot(final_flow_vals['Flow_gpm'],final_flow_vals['offset_flow'],ls='None',marker='o',markersize=12,label='Initial Calibration measurements',c='b')
QCpoints = ax.plot(final_flow_vals_QC['Flow_gpm'],final_flow_vals_QC['offset_flow'],ls='None',marker='o',markersize=12,label='Follow-up QC measurements',c='r')

ax.set_xlabel('Measured Flow (gpm)',fontweight='bold',fontsize=16)
ax.set_ylabel('Flow data Output (gpm)',fontweight='bold',fontsize=16)

ax.set_xlim(0, 1.3 *final_flow_vals[['offset_flow','Flow_gpm']].max().max())
ax.set_ylim(0, 1.3 *final_flow_vals[['offset_flow','Flow_gpm']].max().max())
ax.legend(loc='upper left')

fig.suptitle('Measured flow vs Flow data output',fontweight='bold',fontsize=20)
ax.set_title(site_name,fontweight='bold',fontsize=18)


plt.tight_layout()
plt.subplots_adjust(top=0.93)


hover_points(points, list(final_flow_vals['Datetime']),fig, ax)
hover_points(QCpoints, list(final_flow_vals_QC['Datetime']),fig, ax)

#%% Compare to Ultrasonic
from xlrd import XLRDError

try:
    US = pd.read_excel(ancillarydir+'Alta May 2019 Flow Deliverable.xlsx', sheetname='MS4-'+site_name, index_col=0, header=0,parse_cols='B:D')
    
    US = US.append(pd.read_excel(ancillarydir+'Alta June 2019 Flow Deliverable.xlsx', sheetname='MS4-'+site_name, index_col=0, header=0,parse_cols='B:D'))
    
    US = US.append(pd.read_excel(ancillarydir+'Alta July 2019 Flow Deliverable.xlsx', sheetname='MS4-'+site_name, index_col=0, header=0,parse_cols='B:D'))
    
    
#    ns5min=5*60*1000000000   # 5 minutes in nanoseconds 
#    US.index = pd.to_datetime(((US.index.astype(np.int64) // ns5min + 1 ) * ns5min))
    
    US['idx'] = US.index
    US['idx'] =US['idx'].apply(lambda x: dt.datetime(x.year, x.month, x.day, x.hour,5*(x.minute // 5)))
    US = US.drop_duplicates(subset=['idx'])
    
    
    US.index = US['idx']
    
    US = US.reindex(pd.date_range(dt.datetime(2019,5,1,0,0),dt.datetime(2019,7,31,23,55),freq='5Min'))
    
    ## PLOT
    fig, (ax1, ax2) = plt.subplots(2,1,figsize=(18,10),sharex=True)
    ## Plot offset level
    ax1.plot_date(WL.index, WL['offset_corr_level'], marker='None',ls='-',c='green',label='Offset Final Level ('+"%.2f"%tot_offset+' in.)')
    ## Plot field measurements
    ax1.plot_date(field_meas_level['Datetime'],field_meas_level['Level_above_V_in'],marker='s',c='r',label='Level Cal')
    ax1.plot_date(field_meas_level_QC['Datetime'],field_meas_level_QC['Level_above_V_in'],marker='s',c='b',label='Level QC')
    ## Ultrasonic
    ax1.plot_date(US.index, US['Level (inches)'],marker='None',ls='-',c='orange',label='UltraSonic')
    ## Plot compound weir flow data (including correct flow for overtopping flows)
    ax2.plot_date(WL.index, WL['Flow_compound_weir'], marker='None',ls='-',c='grey',alpha=0.5,label='Weir (storm/bad)')
    ## Plot corrected data (offset and clipped)
    ax2.plot_date(WL.index, WL['Flow_compound_clipped'], marker='None',ls='-',c='green',label='Weir Flow')
    ## Plot field measurements
    ax2.plot_date(field_meas_flow['Datetime'],field_meas_flow['Flow_gpm_1'],marker='o',c='g',label='Field meas. flow 1')
    ax2.plot_date(field_meas_flow['Datetime'],field_meas_flow['Flow_gpm_2'],marker='o',c='g',label='Field meas. flow 2')
    ax2.plot_date(field_meas_flow['Datetime'],field_meas_flow['Flow_gpm_3'],marker='o',c='g',label='Field meas. flow 3')
    ## QC Measurements
    ax2.plot_date(field_meas_flow_QC['Datetime'],field_meas_flow_QC['Flow_gpm_1'],marker='o',c='b',label='Field meas. flow 1')
    ax2.plot_date(field_meas_flow_QC['Datetime'],field_meas_flow_QC['Flow_gpm_2'],marker='o',c='b',label='Field meas. flow 2')
    ax2.plot_date(field_meas_flow_QC['Datetime'],field_meas_flow_QC['Flow_gpm_3'],marker='o',c='b',label='Field meas. flow 3')
    ## Ultrasonic
    ax2.plot_date(US.index, US['Flow (gpm)'],marker='None',ls='-',c='orange',label='UltraSonic')
    
    for ax in fig.axes:
        ax.legend(loc='upper left')
    ax1.set_ylabel('Level (inches)',color='g')
    
    ax2.set_ylabel('Flow (gpm)',color='b')   
    
    ### Plot precip on inverted, secondary y axis
    ax1_2 = ax1.twinx()
    ax1_2.plot_date(rain.index, rain['Precip_in'], marker='None',ls='steps-mid',color='b',label='Precip: '+raingauge_dict[site_name])
    ax1_2.set_ylabel('Precip (inches)',color='teal')
    ax1_2.invert_yaxis()
    ax1_2.legend()
    ax2.xaxis.set_major_formatter(mpl.dates.DateFormatter('%A \n %m/%d/%y %H:%M'))
    
    fig.suptitle('Weir vs Ultrasonic for site: '+site_name,fontsize=16,fontweight='bold')
    plt.tight_layout()
    plt.subplots_adjust(top=0.95) 

except XLRDError:
    print
    print 'No Alta data found for site: ('+site_name+')'
    print 

#%% TEMP AND CONDUCTIVITY

fig, (ax1, ax2, ax3) = plt.subplots(3,1,sharex=True,figsize=(18,10))

## Temp
ax1.plot_date(WL.index, WL[u'°F Water Temperature'],marker='None',ls='-',c='blue',label='Water Temp')
ax1.plot_date(WL.index, WL[u'°F Logger Temperature'],marker='None',ls='-',c='tomato',label='Air Temp')

## Cond
cond_cals = fds[fds['SITE ID'] == site_name][['Datetime','Specific Conductivity (uS/cm)']].dropna()
WL[u'uS/cm EC'] = WL[u'mS/cm EC'] * 1000.
ax2.plot_date(WL.index, WL[u'uS/cm EC'],marker='None',ls='-',c='tomato',label='Cond (uS/cm)')
ax2.plot_date(cond_cals['Datetime'],cond_cals['Specific Conductivity (uS/cm)'],marker='o',ls='None',color='r',label='Manual measurements')

### Plot precip on inverted, secondary y axis
ax2_2 = ax2.twinx()
ax2_2.plot_date(rain.index, rain['Precip_in'], marker='None',ls='steps-mid',color='teal',label='Precip: '+raingauge_dict[site_name])

## Temp, Cond, Flow, precip

## Plot compound weir flow data (including correct flow for overtopping flows)
ax3.plot_date(WL.index, WL['Flow_compound_weir'], marker='None',ls='-',c='grey',alpha=0.5,label='Clipped flow data (storm/bad)')
## Plot corrected data (offset and clipped)
ax3.plot_date(WL.index, WL['Flow_compound_clipped'], marker='None',ls='-',c='green',label='Corrected Flow, Compound, Clipped')

## Cond
ax3_2 = ax3.twinx()
ax3_2.plot_date(WL.index, WL[u'uS/cm EC'],marker='None',ls='-',c='tomato',alpha=0.5,label='Cond (uS/cm)')


### Plot precip on inverted, secondary y axis
ax3_3 = ax3.twinx()
ax3_3.plot_date(rain.index, rain['Precip_in'], marker='None',ls='steps-mid',color='teal',label='Precip: '+raingauge_dict[site_name])

## scale
ax3.set_ylim(-WL['offset_flow'].max() * 0.1, WL['offset_flow'].max() * 1.1)
ax3_2.set_ylim(-WL[u'uS/cm EC'].max() * 0.75, WL[u'uS/cm EC'].max() * 1.1)
ax2_2.set_ylim(0, rain['Precip_in'].max() * 3.),ax3_3.set_ylim(0, rain['Precip_in'].max() * 3.)
ax2_2.invert_yaxis(), ax3_3.invert_yaxis()


ax1.set_xlim(start, end)
ax1.set_ylabel(u'Temperature °F ',color='k')
ax2.set_ylabel('Sp Conductivity (uS/cm)',color='k'), ax3_2.set_ylabel('Sp Conductivity (uS/cm)',color='k')
ax3.set_ylabel('Flow (gpm)',color='k')
ax3_3.set_ylabel('Precip (in)')
ax3_3.spines["right"].set_position(("axes", 1.1))

ax1.legend(fontsize=12,numpoints=1,ncol=1,loc='upper left')
ax2.legend(fontsize=12,loc='lower left')
ax3.legend(fontsize=12,numpoints=1,ncol=1,loc='lower right')

ax3.xaxis.set_major_formatter(mpl.dates.DateFormatter('%A \n %m/%d/%y %H:%M'))

fig.suptitle('Data processing for site: '+site_name,fontsize=16,fontweight='bold')
plt.tight_layout()
plt.subplots_adjust(top=0.95)

#%% HYDROGRAPH SEPARATION

alpha = 0.990

flow_df = WL[[u'Flow_compound_weir']]
## gap fill
flow_df = flow_df.fillna(flow_df.interpolate(method='linear')).fillna(flow_df.mode().loc[0].values[0])
#flow_df[''Flow_compound_weir'].plot(c='b')

## Function to add original flow peaks back into dataset
def peaks(original_flow, smoothed, peak_val=2):
    if abs(original_flow - smoothed) > peak_val:
        flow = original_flow
    else:
        flow = smoothed
    return flow

## Smoothing
flow_df['rolling'] = flow_df['Flow_compound_weir'].rolling(12,min_periods=3,center=True).mean()
#flow_df['rolling'].plot(c='g')
    
## Add peaks back into rolling data
flow_df['rolling+peaks']  = flow_df.apply(lambda x: peaks(x['Flow_compound_weir'],x['rolling']), axis=1)
#flow_df['rolling+peaks'].plot(c='r')

## Butter filter
b, a = signal.butter(3, 0.2, btype='lowpass', analog=False) ## 0.2 parameter selected by trial and error
flow_df['butter'] = signal.filtfilt(b, a, flow_df['rolling+peaks'])
#flow_df['butter'].plot(c='orange')
flow_df['butter+peaks']  = flow_df.apply(lambda x: peaks(x['Flow_compound_weir'],x['butter'], 1.), axis=1)


## CHoose a smoothed dataset to apply the DF to
flow_df['Flow compound weir (gpm) smooth'] = flow_df['butter+peaks']
## Set arbitrary index
flow_df = flow_df.reset_index()

## Baseflow df    
df = flow_df

## Define h_k1 (original flow data series
df['h_k1'] = df['Flow compound weir (gpm) smooth']

### BACKWARD FILTER
## Fill in first value for q_k-1
df.loc[0,'q_k-1'] = df.loc[0,'h_k1']
## q_k-1
for i in range(1,len(df)):
    # (0.925 * q_k-1) + (((1+0.925)/2) * (q_k - q_k-1))
    df.loc[i,'q_k-1'] = (alpha*df.loc[i-1,'q_k-1']) + (((1.+alpha)/2.) * (df.loc[i,'h_k1'] - df.loc[i-1,'h_k1']))

## Change negatives to 0's
df['q_k-1>0'] = df['q_k-1'].where(df['q_k-1']>0., 0.)
## b_k1
df['b_k1'] = df['h_k1'] - df['q_k-1>0']

## FORWARD FILTER
df['h_k2'] = df['h_k1'] - df['b_k1']
## Fill in first value for q_k+1
df.loc[df.index[-1],'q_k+1'] = 0.
##q_k+1
for i in range(df.index[-2],0,-1): ## iterate backwards
    # (0.925 * q_k+1) + (((1+0.925)/2) * (q_k - q_k-1))
    df.loc[i,'q_k+1'] = (alpha*df.loc[i+1,'q_k+1']) + (((1.+alpha)/2.) * (df.loc[i,'b_k1'] - df.loc[i+1,'b_k1']))
## change negatives to 0's
df['q_k+1>0'] = df['q_k+1'].where(df['q_k+1']>=0, 0.)
## b_k2
df['b_k2'] = df['b_k1'] - df['q_k+1>0']

## Rest values back to date
df = df.set_index(df['index'])
## Deliver
df[['h_k1','b_k1','b_k2']]

flowoutput = df[['Flow_compound_weir','Flow compound weir (gpm) smooth']]
flowoutput.loc[:,'Baseflow (gpm)'] = df['b_k2']
flowoutput.loc[:,'Quickflow (gpm)'] = df['Flow compound weir (gpm) smooth'] - df['b_k2']

## Put in original flow data and Mask where Nan values in orginal dataset
flowoutput.loc[:,'Flow_compound_weir'] = WL[[u'Flow_compound_weir']]
m = pd.notnull(flowoutput['Flow_compound_weir'])
flowoutput = flowoutput.where(m, np.nan)   

WL.loc[:,'Baseflow (gpm)'] = flowoutput['Baseflow (gpm)'].round(3)
WL.loc[:,'Quickflow (gpm)'] = flowoutput['Quickflow (gpm)'].round(3)

## Drop data for data dropouts
WL['Baseflow (gpm)'] = np.where(WL['Level_in'].isnull(),np.nan,WL['Baseflow (gpm)'])
WL['Quickflow (gpm)'] = np.where(WL['Level_in'].isnull(),np.nan,WL['Quickflow (gpm)'])

#%% BASEFLOW PLOT
## PLOT
#    fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(20,10),sharex=True)
fig, ax1 = plt.subplots(1,1)
fig.suptitle(site_name,fontsize=14, fontweight='bold')

## Flow
ax1.plot_date(WL.index, WL['Flow_compound_weir'],marker='None',ls='-',label='Orig. Flow Data (gpm)',c='grey')
ax1.plot_date(flowoutput.index, flowoutput['Flow compound weir (gpm) smooth'],marker='None',ls='-',label='Smoothed Flow Data (gpm)',c='b')
ax1.plot_date(WL.index, WL['Baseflow (gpm)'],marker='None',ls='-',label='Baseflow (digital filter='+str(alpha)+')',c='g')
ax1.set_ylabel('Flow (gpm)',fontweight='bold',fontsize=14)


#    ## Spec Conductivity and Water Temp
#    ax2.plot_date(WL.index, WL[u'mS/cm EC'],marker='None',ls='-',label='Sp Conductivity',c='orange')
#    ax2.set_ylabel('Spec. Conductivity (mS/cm)',fontweight='bold',fontsize=14)
#    ## Air temp and pressure
#    ax3.plot_date(WL.index, WL[u'kPa Reference Pressure'],marker='None',ls='-',label='Barometric Press.',c='teal')
#    ax3.set_ylabel('Pressure (kPa)',fontweight='bold',fontsize=14)
#
for ax in fig.axes:
    ax.legend(loc='upper left')
#    
#    ax2_2 = ax2.twinx()
#    ax2_2.plot_date(WL.index, WL[u'°F Water Temperature'],marker='None',ls='-',label='Water Temp(F)',c='b')
#    ax2_2.set_ylabel('Temp(F)',fontweight='bold',fontsize=14)
#    
#    ax3_2 = ax3.twinx()
#    ax3_2.plot_date(WL.index, WL[u'°F Logger Temperature'],marker='None',ls='-',label='Air Temp(F)',c='tomato')
#    ax3_2.set_ylabel('Temp(F)',fontweight='bold',fontsize=14)
#    
#    for ax in [ax2_2, ax3_2]:
#        ax.legend(loc='upper right')

#ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d-%Y %H:%M'))
ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H:%M'))
plt.tight_layout()
plt.subplots_adjust(top=0.95,hspace=0.05)


#%% SAVE TO EXCEL

## Get rid of all data for data dropouts
for col in WL.columns:
    #print col
    try:
        WL[col] = np.where(WL['Level_in'].isnull(),np.nan,WL[col])
    except:
        print 'skipped col: '+col
        pass

## SAVE EXCEL FILE WITH CALIBRATION DATA
calibration_ExcelFile = pd.ExcelWriter(calibration_output_dir+site_name+'-calibration.xlsx')
WL.to_excel(calibration_ExcelFile,'Level and Flow data')
rain.to_excel(calibration_ExcelFile,'rain')
field_meas_flow.to_excel(calibration_ExcelFile,'Flow calibration')
field_meas_level.to_excel(calibration_ExcelFile,'Level calibration')

offset_df = pd.DataFrame({'calculated_offset':calculated_offset,'overall_offset':overall_offset,'total_offset':tot_offset},index=['offsets']).to_excel(calibration_ExcelFile,'offsets')
calibration_ExcelFile.save()

### FINALIZED FLOW OUTPUT

## FLOW
Corr_flow = WL[['offset_flow','Flow_compound_weir', 'Flow_compound_clipped']].round(3)
Corr_flow.columns = ['Flow v-notch only (gpm)', 'Flow compound weir (gpm)', 'Flow compound weir stormflow clipped (gpm)']

## Add base/quickflow
Corr_flow[['Baseflow (gpm)','Quickflow (gpm)']] = WL[['Baseflow (gpm)','Quickflow (gpm)']]

## Add temp and conductivity to deliverable
Corr_flow[u'uS/cm EC'] = WL[u'uS/cm EC'].round(0)
Corr_flow[u'°F Water Temperature'] = WL[u'°F Water Temperature'].round(1)


## PIVOT TABLE STUFF
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

## Old style-SUM but ADDING the multiplication by 5min (gpm->gp5M)
PivotTable_Sum = pd.pivot_table(Corr_flow,values='Flow compound weir stormflow clipped (gpm)', columns=['Month','Day','Weekday'], index=['Hour'], aggfunc=np.sum).round(1) * 5. # *5 for 5Min interval data
PivotTable_Sum.to_excel(final_flow_ExcelFile,site_name+'PivotTable-Sum')
## Freeze Panes
final_flow_ExcelFile.sheets[site_name+'PivotTable-Sum'].freeze_panes(4, 1)
## Conditional Formatting
def rgb_hex(red,green,blue):
    return '#%02x%02x%02x' % (red, green, blue)
green, yellow, red = rgb_hex(99,190,123),rgb_hex(255,235,132),rgb_hex(248,105,107)

max_col_row = xl_columnrow(len(PivotTable_Sum.columns)+1,28) #24th hour is on row 28
final_flow_ExcelFile.sheets[site_name+'PivotTable-Sum'].conditional_format('B5:'+max_col_row, {'type': '3_color_scale','min_color': green,'mid_color':yellow,'max_color':red})
## Old style-AVG
PivotTable_Avg = pd.pivot_table(Corr_flow,values='Flow compound weir stormflow clipped (gpm)', columns=['Month','Day','Weekday'], index=['Hour'], aggfunc=np.mean).round(3)
PivotTable_Avg.to_excel(final_flow_ExcelFile,site_name+'PivotTable-Avg')
## Freeze Panes
final_flow_ExcelFile.sheets[site_name+'PivotTable-Avg'].freeze_panes(4, 1)
## Conditional Formatting
max_col_row = xl_columnrow(len(PivotTable_Sum.columns)+1,28)  #24th hour is on row 28
final_flow_ExcelFile.sheets[site_name+'PivotTable-Avg'].conditional_format('B5:'+max_col_row, {'type': '3_color_scale','min_color': green,'mid_color': yellow,'max_color': red})

## Seven day Average style
PivotTable = pd.pivot_table(Corr_flow,values='Flow compound weir stormflow clipped (gpm)',columns=['Weekday'],index=['Hour'],aggfunc=np.mean)
col_order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
PivotTable = PivotTable.reindex_axis(col_order,axis=1)

PivotTable.to_excel(final_flow_ExcelFile,site_name+'PivotTable-Avg7day')

## Format Pivot Table 
pivot = final_flow_ExcelFile.sheets[site_name+'PivotTable-Avg7day']

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
    print i, day, col        
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
## BASEFLOW
ax1.plot_date(Corr_flow.index,Corr_flow['Baseflow (gpm)'], marker='None', ls='-', c='grey',label='Baseflow')

## RAIN
ax2 = ax1.twinx()
ax2.plot_date(rain.index, rain['Precip_in'], marker='None',ls='steps-mid',color='skyblue',label='Precip: '+raingauge_dict[site_name])
## FORMAT
ax1.set_ylim(-Corr_flow['Flow compound weir stormflow clipped (gpm)'].max() * 0.25, Corr_flow['Flow compound weir stormflow clipped (gpm)'].max() * 2.)
ax2.set_ylim(0, rain['Precip_in'].max() * 3.)
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

#%%  VIEW PHOTOS


print 'Site for camera...'+site_name
## Downloading photos from Google Photos
pic_dir = 'C:/Users/alex.messina/Downloads/'
pic_folder = site_name + '/'

## Compile DF of datetimes and picture file names
print ' compiling datetimes and picture file names....'
pic_datetimes = pd.DataFrame()
for pic in [os.listdir(pic_dir+pic_folder)][0]:
    date_taken = Image.open(pic_dir+pic_folder + pic)._getexif()[36867]
    t = dt.datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
    pic_datetimes = pic_datetimes.append(pd.DataFrame({'Pic filename':pic,'Date Taken':t},index=[t]))
print 'datetimes and picture file names....DONE'   

#%% PHOTOS and DATA

# define your images to be plotted
#pics = [os.listdir(pic_dir+pic_folder)][0][5000:] ## You can limit photos here

## Select by date
pics = pic_datetimes[dt.datetime(2019,7,10):]['Pic filename']

# now the real code :) 
curr_pos = 0

def key_event(e):
    
    global curr_pos

    if e.key == "right":
        curr_pos = curr_pos + 1
    elif e.key == "left":
        curr_pos = curr_pos - 1
    else:
        return
    curr_pos = curr_pos % len(pics)
    print 'key event '+str(curr_pos)
  
    ## Select pic
    picture_file = pic_dir + pic_folder+ pics[curr_pos]
    print 'Pic file: '+pics[curr_pos]
    ## Extract datetime of pic and format datetime
    date_taken = Image.open(picture_file)._getexif()[36867]
    print 'Date taken: '+date_taken
    t = dt.datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
    t_round5 = dt.datetime(2019, t.month, t.day, t.hour,5*(t.minute // 5),0)
    ## Get flow and level data at time of pic
    flow_at_image = WL.ix[t_round5,'Flow_compound_weir']
    level_at_image = WL.ix[t_round5,'offset_level_w_neg']
    
    ## Image
    ax1.cla()
    ax1.set_title('SITE: '+site_name+' Datetime: '+t.strftime('%m/%d/%y %H:%M') +' Pic: '+pics[curr_pos])
    img=mpimg.imread(picture_file)
    # from now on you can use img as an image, but make sure you know what you are doing!
    if site_name == 'CAR-070' or site_name=='SDR-064':
        rot_img=ndimage.rotate(img,degrees)
        imgplot=ax1.imshow(rot_img)
        
    else:
        imgplot=ax1.imshow(img)
    plt.show()
    
    ## Plot flow data
    ax2.cla()
    ax2.plot_date(WL.index,WL['Flow_compound_weir'],marker='None',ls='-',c='b',label='Flow compound weir')
    ax2.plot_date(t_round5, flow_at_image,marker='o',ls='None',c='b',label='Flow at picture='+"%.3f"%flow_at_image)
    
    ## Plot Level data   
    ax2_2.cla()
    if level_at_image <0 or np.isnan(level_at_image):
        level_color = 'r'
    elif level_at_image == 0:
        level_color='k'
    elif level_at_image>0:
        level_color='g'
    ax2_2.plot_date(WL.index, WL['offset_level_w_neg'],marker='None',ls='-',c=level_color,label='Level (inches)')  
    ax2_2.plot_date(t_round5, level_at_image,marker='o',ls='None',c=level_color,label='Level at picture='+"%.2f"%level_at_image)
    ax2_2.set_ylim(-1, 6)
    ## Set plot limits
    ax2.set_xlim(t_round5 - dt.timedelta(hours=8), t_round5 + dt.timedelta(hours=8))
    ## Get flow data over a 24 hour surrounding period
    flow_over_interval = WL.ix[t_round5 - dt.timedelta(hours=8):t_round5 + dt.timedelta(hours=8),'Flow_compound_weir']
    ## y limits
    if flow_over_interval.min() == 0. and flow_over_interval.max() > 0.:
        ax2.set_ylim(-1.,flow_over_interval.max()*1.1)
    elif flow_over_interval.min() == 0. and flow_over_interval.max() == 0.:
            ax2.set_ylim(-3.,3.)
    else:
        ax2.set_ylim(flow_over_interval.min()*0.9,flow_over_interval.max()*1.1)
        
    ax2.xaxis.set_major_formatter(mpl.dates.DateFormatter('%A \n %m/%d/%y %H:%M'))

    ax2.set_ylabel('Flow (gpm)'), ax2_2.set_ylabel('Level (inches)')

    ## Legends, they're all around
    ax2.legend(loc='upper left')
    ax2_2.legend(loc='upper right')
        
    fig1.canvas.draw()
    return



fig1, (ax1,ax2) = plt.subplots(2,1,figsize=(16,11))

fig1.canvas.mpl_connect('key_press_event', key_event)


picture_file = pic_dir + pic_folder+ pics[curr_pos]
date_taken = Image.open(picture_file)._getexif()[36867]
t = dt.datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
t_round5 = dt.datetime(2019, t.month, t.day, t.hour,5*(t.minute // 5),0)
flow_at_image = WL.ix[t_round5,'Flow_compound_weir']
level_at_image = WL.ix[t_round5,'offset_level_w_neg']

## Image
#ax1 = fig1.axes[0]
ax1.set_title('SITE: '+site_name+' Datetime: '+t.strftime('%m/%d/%y %H:%M'))
img=mpimg.imread(picture_file)
# from now on you can use img as an image, but make sure you know what you are doing!
if site_name == 'CAR-070':
    degrees = -90
    rot_img=ndimage.rotate(img,degrees)
    imgplot=ax1.imshow(rot_img)
elif site_name=='SDR-064':
    degrees = 90
    rot_img=ndimage.rotate(img,degrees)
    imgplot=ax1.imshow(rot_img)    
    
else: 
    imgplot=ax1.imshow(img)
plt.show()

ax2 = fig1.axes[1]
ax2.plot_date(WL.index,WL['Flow_compound_weir'],marker='None',ls='-',c='b',label='Flow compound weir')
ax2.plot_date(t_round5, flow_at_image,marker='o',ls='None',c='b',label='Flow at picture='+"%.3f"%flow_at_image)


## Level
ax2_2 = ax2.twinx()
if level_at_image <0  or np.isnan(level_at_image):
        level_color = 'r'
elif level_at_image == 0:
    level_color='k'
elif level_at_image>0:
    level_color='g'
ax2_2.plot_date(WL.index, WL['offset_level_w_neg'],marker='None',ls='-',c=level_color,label='Level (inches)')
ax2_2.plot_date(t_round5, level_at_image,marker='o',ls='None',c=level_color,label='Level at picture='+"%.2f"%level_at_image)
ax2_2.set_ylim(-1, 6)

## Legends, they're all around
ax2.legend(loc='upper left')
ax2_2.legend(loc='upper right')

## Y labels
ax2.set_ylabel('Flow (gpm)'), ax2_2.set_ylabel('Level (inches)')


## x and y limits
ax2.set_xlim(t_round5 - dt.timedelta(hours=8), t_round5 + dt.timedelta(hours=8))
flow_over_interval = WL.ix[t_round5 - dt.timedelta(hours=8):t_round5 + dt.timedelta(hours=8),'Flow_compound_weir']
if flow_over_interval.min() == 0. and flow_over_interval.max() > 0.:
    ax2.set_ylim(-5.,flow_over_interval.max()*1.1)
elif flow_over_interval.min() == 0. and flow_over_interval.max() == 0.:
        ax2.set_ylim(-3.,3.)
else:
    ax2.set_ylim(flow_over_interval.min()*0.9,flow_over_interval.max()*1.1)
## X axis date format
ax2.xaxis.set_major_formatter(mpl.dates.DateFormatter('%A \n %m/%d/%y %H:%M'))


plt.tight_layout()