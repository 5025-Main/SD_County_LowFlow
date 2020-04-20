# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 10:58:22 2019

@author: alex.messina
"""
#%%
# Import Standard modules
import datetime as dt
import matplotlib as mpl
from matplotlib import pyplot as plt
import pandas as pd
import os
import numpy as np
import calendar
from scipy import signal

import seaborn as sns

## Set Pandas display options
pd.set_option('display.large_repr', 'truncate')
pd.set_option('display.width', 180)
pd.set_option('display.max_rows', 30)
pd.set_option('display.max_columns', 13)
plt.ion()

### UPDATE HERE #####
data_processing_date = '05_31_2019' #end date of data

## Input directories
maindir = 'P:/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/'
localdir = 'C:/Users/alex.messina/Desktop/CountyWeirProcessing/'

## 
#leveldir = maindir+'1 - Level Data monthly submittals/Data processing '+data_processing_date+'/'
leveldir = localdir+'1 - Level Data monthly submittals/Data processing '+data_processing_date+'/'

## Loop through deliverable folder
deliverable_dir = maindir + 'Data Deliverables/Monthly Flow Data Deliverable/' + 'May/' ### UPDATE HERE

## Output directories
output_dir = localdir + '5 - Temp Cond and Baseflow/'

## GET FILE 
SITE_YOU_WANT_TO_PROCESS = 'CAR-070'
files = [f for f in os.listdir(deliverable_dir) if f.endswith('.xlsx') == True and SITE_YOU_WANT_TO_PROCESS == f.split('-working draft.xlsx')[0]]  

for f in files:
    print f
    site_name = f.split('-working draft.xlsx')[0]
    print site_name
    print
    print 'Deliverable file: ' + deliverable_dir+f
    del_df = pd.read_excel(deliverable_dir+f, sheetname=site_name+'-flow',index_col=0,header=0,parse_cols='A:D')
    
    
    ## Add temp and conductivity to deliverables
    site_file = [f for f in os.listdir(leveldir) if f.endswith('.xlsx') == True and site_name == f.split(' ')[0]]  
    print 'Original data file: ' + site_file[0]

    if len(site_file)==1:
        print
        temp_cond_df = pd.read_excel(leveldir+site_file[0], skiprows= [0,1], index_col=0, header=0)[[u'mS/cm EC', u'°F Water Temperature', u'°F Logger Temperature', u'kPa Reference Pressure']]
    else:
        print 'No original data file found'
    
    ## Add columns to deliverable
    del_df[[u'mS/cm EC', u'°F Water Temperature', u'°F Logger Temperature', u'kPa Reference Pressure']] = temp_cond_df[[u'mS/cm EC', u'°F Water Temperature', u'°F Logger Temperature', u'kPa Reference Pressure']]



#%% BASEFLOW Separation

    alpha = 0.990

    flow_df = del_df[[u'Flow compound weir (gpm)']]
    ## gap fill
    flow_df = flow_df.fillna(flow_df.interpolate(method='linear')).fillna(flow_df.mode().ix[0].values[0])
    #flow_df['Flow compound weir (gpm)'].plot(c='b')
    
    ## Function to add original flow peaks back into dataset
    def peaks(original_flow, smoothed, peak_val=2):
        if abs(original_flow - smoothed) > peak_val:
            flow = original_flow
        else:
            flow = smoothed
        return flow
    
    ## Smoothing
    flow_df['rolling'] = flow_df['Flow compound weir (gpm)'].rolling(12,min_periods=3,center=True).mean()
    #flow_df['rolling'].plot(c='g')
        
    ## Add peaks back into rolling data
    flow_df['rolling+peaks']  = flow_df.apply(lambda x: peaks(x['Flow compound weir (gpm)'],x['rolling']), axis=1)
    #flow_df['rolling+peaks'].plot(c='r')

    ## Butter filter
    b, a = signal.butter(3, 0.2, btype='lowpass', analog=False) ## 0.2 parameter selected by trial and error
    flow_df['butter'] = signal.filtfilt(b, a, flow_df['rolling+peaks'])
    #flow_df['butter'].plot(c='orange')
    flow_df['butter+peaks']  = flow_df.apply(lambda x: peaks(x['Flow compound weir (gpm)'],x['butter'], 1.), axis=1)


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
    
    flowoutput = df[['Flow compound weir (gpm)','Flow compound weir (gpm) smooth']]
    flowoutput.loc[:,'Baseflow (gpm)'] = df['b_k2']
    flowoutput.loc[:,'Peakflow (gpm)'] = df['Flow compound weir (gpm) smooth'] - df['b_k2']
    
    ## Put in original flow data and Mask where Nan values in orginal dataset
    flowoutput.loc[:,'Flow compound weir (gpm)'] = del_df[[u'Flow compound weir (gpm)']]
    m = pd.notnull(flowoutput['Flow compound weir (gpm)'])
    flowoutput = flowoutput.where(m, np.nan)        
   
    #flowoutput[['Flow compound weir (gpm)','Flow compound weir (gpm) smooth','Baseflow (gpm)','Peakflow (gpm)']].to_csv(outputdir+site+'_'+year+'-flow separated.csv')
    
    ## PLOT
#    fig, ax = plt.subplots(1,1,figsize=(12,6))
#    ax.set_title(site_name,fontsize=14, fontweight='bold')
#    ax.plot_date(flowoutput.index, flowoutput['Flow compound weir (gpm)'],marker='None',ls='-',label='Orig. Flow Data (gpm)',c='grey')
#    ax.plot_date(flowoutput.index, flowoutput['Flow compound weir (gpm) smooth'],marker='None',ls='-',label='Smoothed Flow Data (gpm)',c='b')
#    #ax.plot_date(df.index, df['b_k1'],marker='None',ls='-',label='b_k1 (1st diff)',c='r')
#    ax.plot_date(flowoutput.index, flowoutput['Baseflow (gpm)'],marker='None',ls='-',label='Baseflow (digital filter='+str(alpha)+')',c='g')
#    #ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d-%Y %H:%M'))
#    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H:%M'))
#    ax.legend()
#    ax.set_ylabel('Flow (gpm)',fontweight='bold',fontsize=16)
#    plt.tight_layout()
    
#%%
    del_df[[u'Flow compound weir (gpm) smooth', u'Baseflow (gpm)', u'Peakflow (gpm)']] = flowoutput[[u'Flow compound weir (gpm) smooth', u'Baseflow (gpm)', u'Peakflow (gpm)']]
    
    #del_df.round(3).to_excel(output_dir + site_name + ' - flow w Cond Temp and baseflow.xlsx')
    
#%%  
    ## PLOT
    fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(20,10),sharex=True)
    fig.suptitle(site_name,fontsize=14, fontweight='bold')
    
    ## Flow
    ax1.plot_date(del_df.index, del_df['Flow compound weir (gpm)'],marker='None',ls='-',label='Orig. Flow Data (gpm)',c='grey')
    ax1.plot_date(del_df.index, del_df['Flow compound weir (gpm) smooth'],marker='None',ls='-',label='Smoothed Flow Data (gpm)',c='b')
    ax1.plot_date(del_df.index, del_df['Baseflow (gpm)'],marker='None',ls='-',label='Baseflow (digital filter='+str(alpha)+')',c='g')
    ax1.set_ylabel('Flow (gpm)',fontweight='bold',fontsize=14)
    ## Spec Conductivity and Water Temp
    ax2.plot_date(del_df.index, del_df[u'mS/cm EC'],marker='None',ls='-',label='Sp Conductivity',c='orange')
    ax2.set_ylabel('Spec. Conductivity (mS/cm)',fontweight='bold',fontsize=14)
    ## Air temp and pressure
    ax3.plot_date(del_df.index, del_df[u'kPa Reference Pressure'],marker='None',ls='-',label='Barometric Press.',c='teal')
    ax3.set_ylabel('Pressure (kPa)',fontweight='bold',fontsize=14)
    
    for ax in fig.axes:
        ax.legend(loc='upper left')
    
    
    ax2_2 = ax2.twinx()
    ax2_2.plot_date(del_df.index, del_df[u'°F Water Temperature'],marker='None',ls='-',label='Water Temp(F)',c='b')
    ax2_2.set_ylabel('Temp(F)',fontweight='bold',fontsize=14)
    
    ax3_2 = ax3.twinx()
    ax3_2.plot_date(del_df.index, del_df[u'°F Logger Temperature'],marker='None',ls='-',label='Air Temp(F)',c='tomato')
    ax3_2.set_ylabel('Temp(F)',fontweight='bold',fontsize=14)
    
    for ax in [ax2_2, ax3_2]:
        ax.legend(loc='upper right')
    
    
    #ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d-%Y %H:%M'))
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H:%M'))
    plt.tight_layout()
    plt.subplots_adjust(top=0.95,hspace=0.05)
    
    
    
#%%


    
    
