# -*- coding: utf-8 -*-
"""
Created on Wed Aug 08 14:36:38 2018

@author: alex.messina
"""
#%%
from matplotlib import pyplot as plt

def get_weir_dims(site_name,weir_dims):
    vnotch_in= weir_dims.ix[site_name][['h2']].values
    width_in = weir_dims.ix[site_name][['b2']].values + weir_dims.ix[site_name][['c1']].values + weir_dims.ix[site_name][['c2']].values
    vnotch_ft, width_ft = vnotch_in/12., width_in/12.
    print() 
    print('Site: '+site_name)
    print('V-notch height: '+str(vnotch_in)+' in. Width: '+str(width_in) +' in.')
    print('V-notch height: '+"%.2f"%vnotch_ft+' ft. Width: '+"%.2f"%width_ft +' ft.')
    return vnotch_ft, width_ft

def USBR_compound_weir(site_name,data,weir_dims,plot_timeseries=False,plot_scatter=False):
    import numpy as np
    vnotch_ft, width_ft = get_weir_dims(site_name,weir_dims)
    df = data[['Level_in','offset_flow_clipped']]
    df.columns = ['Level (inches)','Flow (gpm) stormflow clipped']
    df['Level (ft)'] = df['Level (inches)'] / 12.
    ## just values for V-notch? like 0 to height of V or the whole water column?
    #df['Height above v-notch'] = df['Level (inches)'][df['Level (inches)'] <= 0]
    df['Height above horizontal crest (ft)'] = df['Level (ft)'] - vnotch_ft
    df['Height above horizontal crest (ft)'] = df['Height above horizontal crest (ft)'].where(df['Height above horizontal crest (ft)'] > 0., np.nan)
    ## Calculate discharge for compound weir (https://www.openchannelflow.com/blog/compound-weirs)
    L = width_ft - (2. * vnotch_ft)
    print(' L = '+"%.2f"%L)
    df['Flow (cfs) compound'] = (3.9*(df['Level (ft)']**1.72)) -1.5 + (3.3 * L * (df['Height above horizontal crest (ft)']**1.5))
    df['Flow (gpm) compound'] = df['Flow (cfs) compound'] * 448.8325660485
    ## Add the flow from the compound weir equation where it is higher than the standard v-notch equation
    df['Flow (gpm) combined'] = df['Flow (gpm) stormflow clipped'].where((df['Flow (gpm) compound'] < df['Flow (gpm) stormflow clipped']) | (np.isnan(df['Flow (gpm) compound'])==True), df['Flow (gpm) compound'])

    if plot_timeseries == True:
        fig, (level,flow) = plt.subplots(2,1,sharex=True,figsize=(12,6))
        level.plot_date(df.index,df['Level (ft)'],ls='-',marker='.',label='Level ft',c='b')
        level.plot_date(df.index,df['Height above horizontal crest (ft)'] + vnotch_ft,ls='-',marker='.',label='Height above horizontal crest (ft)',c='r')
        level.axhline(vnotch_ft,c='r')
        level.set_ylabel('Level (feet)',fontweight='bold')
        
        flow.plot_date(df.index,df['Flow (gpm) stormflow clipped'],ls='-',marker='.',label='Flow just V',c='b')
        flow.plot_date(df.index,df['Flow (gpm) compound'],ls='-',marker='.',label='Flow compound',c='g')
        flow.plot_date(df.index,df['Flow (gpm) combined'],ls='-',marker='.',label='Flow combined',c='r')
        flow.set_ylabel('Flow (gpm)',fontweight='bold')
        
        level.legend(), flow.legend()
        plt.tight_layout()
        
        
    if plot_scatter == True:
        fig, ax = plt.subplots(1,1,figsize=(10,10))
        ax.plot(df['Level (inches)'], df['Flow (gpm) compound'],ls='None',marker='.',c='r',label='Compound weir equation')
        ax.plot(df['Level (inches)'], df['Flow (gpm) stormflow clipped'],ls='None',marker='.',c='b',label='V-notch equation')
        ax.set_xlabel('Level (inches)',fontweight='bold'), ax.set_ylabel('Flow (gpm)',fontweight='bold')
        ax.legend(loc='upper left')
        plt.tight_layout()

    return df['Flow (gpm) combined'] 

#USBR_compound_weir(site_name, WL, True, True)
#%%
def CTRSC_compound_weir(site_name,WL,weir_dims,plot_timeseries=False,plot_scatter=False):
    import numpy as np
    import math
    ## Get weir dims from sheet
    vnotch_in= weir_dims.ix[site_name][['h2']].values
    b2 = weir_dims.ix[site_name][['b2']].values
    b1 = weir_dims.ix[site_name][['b1 (left)']].values + weir_dims.ix[site_name][['b1 right (if different)']].values
    c1 = weir_dims.ix[site_name][['c1']].values
    c2 = weir_dims.ix[site_name][['c2']].values
    h1 = weir_dims.ix[site_name][['h1']].values
        
    vnotch_cm, width_cm, c1_cm, c2_cm, h1_cm = vnotch_in * 2.54, (b1+b2) * 2.54, c1*2.54, c2*2.54, h1*2.54 
    vnotch_m, width_m, c1_m, c2_m, h1_m = vnotch_in * 0.0254, (b1+b2) * 0.0254, c1*0.0254, c2*0.0254, h1*0.0254
    ## Calculate weir geometry for equation
    b2_cm = b2 * 2.54
    b1_cm = b1 * 2.54
    b1_m, b2_m = b1_cm/100, b2_cm/100
    ## Constants
    Ctd, Crd = 0.579,	0.590
    
    ## Get Level data
    df = WL[['offset_corr_level','offset_flow']]
    df.columns = ['Level (inches)','Flow (gpm)']
    df['Level (inches)'] = df['Level (inches)'].where(df['Level (inches)'] >= 0., np.nan)
    
    ## Format equation inputs
    df['h2(m)'] = df['Level (inches)'] * 0.0254 ## Height above V
    df['h2_eff(m)'] =  df['h2(m)'] + 0.0008 ## Effective head
    df['h1(m)'] = df['h2(m)'] - vnotch_m ## Height above Horizontal crest
    df['h1_eff(m)'] = df['h1(m)']  + 0.0008 ## Effective head
    
    
    ## Calculate discharge for compound weir - Discussion of “Design and Calibration of a Compound Sharp-Crested Weir” by J. Martínez, J. Reca, M. T. Morillas, and J. G. López,”, 2005
    df['Flow (m3/s) compound'] =     ((8./15.) * Ctd * ((2.*9.81)**0.5) * (np.tan(np.radians(90.)/2.)) * (df['h2_eff(m)']**2.5 - df['h1_eff(m)']**2.5))    +     ((2./3.) * Crd * ((2.*9.81)**0.5) * (2 * b1_m) * (df['h1(m)']**1.5))
    ## change from m3/s to gpm
    df['Flow (gpm) compound'] = df['Flow (m3/s) compound'] * 15850.372483753
    
    ## Add the flow from the compound weir equation where it is higher than the standard v-notch equation
    df['Flow (gpm) combined'] = df['Flow (gpm) compound'].where((df['Flow (gpm) compound'] > df['Flow (gpm)']), df['Flow (gpm)'])

    ## PLOTTING
    if plot_timeseries == True:
        fig, (level,flow) = plt.subplots(2,1,sharex=True,figsize=(12,6))
        ## PLOT LEVEL
        ## Plot total Water Level Height
        level.plot_date(df.index,df['h2(m)'] * 100. /2.54,ls='-',marker='.',label='Level inches',c='b')
        ## Plot overtopping Water Level 
        level.plot_date(df.index,(df['h1(m)'] + vnotch_m)* 100. /2.54,ls='-',marker='.',label='Height above horizontal crest (in)',c='r')
        ## Add line at vnotch height
        level.axhline(vnotch_in,c='r')
        level.set_ylabel('Level (inches)',fontweight='bold')
        
        ## PLOT FLOW
        flow.plot_date(df.index,df['Flow (gpm) combined'],ls='-',marker='.',label='Flow combined',c='r')
        flow.plot_date(df.index,df['Flow (gpm)'],ls='-',marker='.',label='Flow just V',c='b')
#        flow.plot_date(df.index,df['Flow (gpm) compound'],ls='-',marker='.',label='Flow compound',c='g')
        flow.set_ylabel('Flow (gpm)',fontweight='bold')
        
        ## fmt
        level.legend(), flow.legend()
        plt.tight_layout()
        
        
    if plot_scatter == True:
        fig, ax = plt.subplots(1,1,figsize=(10,10))
        ax.plot(df['Level (inches)'], df['Flow (gpm) compound'],ls='None',marker='.',c='r',label='Compound weir equation')
        ax.plot(df['Level (inches)'], df['Flow (gpm)'],ls='None',marker='.',c='b',label='V-notch equation')
        ax.set_xlabel('Level (inches)',fontweight='bold'), ax.set_ylabel('Flow (gpm)',fontweight='bold')
        ax.legend(loc='upper left')
        plt.tight_layout()

    return df['Flow (gpm) combined']
    
#CTRSC_compound_weir('CAR-059',WL,weir_dims,plot_timeseries=True,plot_scatter=True)    
    
    
    
    
    
    
    
    
    
    
    
    
