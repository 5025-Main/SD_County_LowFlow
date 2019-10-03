# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 17:30:12 2018

@author: alex.messina
"""
import os
import numpy as np
import pandas as pd
maindir = os.getcwd().replace('\\','/') +'/'
print 'Main directory is: '+maindir

## set directories
flowdata = maindir + '2 - Flow output Excel files - working drafts/Data Output 09_15_2019/'
outputdir = maindir+'Flow Summary/Compiled Flow and Totals 2019/'
pivotoutputdir = maindir+'Flow Summary/Compiled Totals 2019/'

## Data Summary for CTRSC
## N count, Total Flow, Total Non-storm Flow, Total Baseflow, Total Quickflow

def fill_w_median(data):

    clipped_col = [col for col in data.columns][0]
    ## ROLING MEDIANS
    ## Smooth data into 1HR rolling median
    data.loc[:,'1H roll_median'] = data[clipped_col].rolling(int(60./5.),center=True,min_periods=int(30./5.)).median()
    ## 24H rolling median - 24H = 1440 minutes
    data.loc[:,'24H roll_median'] = data['1H roll_median'].rolling(int(1440./5.),center=True,min_periods=int(720./5.)).median() 
    ## Weekly rolling median 1 Week = 10080 minutes
    data.loc[:,'Weekly roll_median'] = data['1H roll_median'].rolling(int(10080./5.),center=True,min_periods=int(5040./5.)).median()
    
    ## Fill with rolling median; priority: 24H rolling, Weekly rolling
    ## Get 24H rolling if available, else use Weekly rolling
    data.loc[:,'median for fill'] = data['24H roll_median'].where(np.isnan(data['24H roll_median'])==False, data['Weekly roll_median'])
    
    ## Fill na with rolling medians
    data.loc[:,clipped_col+' filled w median'] = data[clipped_col].fillna(data['median for fill'])
    
    data.loc[:,('Year')] = data.index.year
    data.loc[:,('Month')] = data.index.month
    return data
    
#%%

AllTotalFlows = pd.ExcelWriter(maindir+'Combined Flow Totals-All Sites.xlsx')
AllSites_df = pd.DataFrame()

for f in [d for d in os.listdir(flowdata) if d.endswith('xlsx')]:
    print f
    site = f.split('-working draft.xlsx')[0]
    print 'Site: '+site
    ## Open data
    df = pd.read_excel(flowdata+f,sheetname=site+'-stormflow clipped')
    ## Create output Excel File
    Flow_and_Totals = pd.ExcelWriter(outputdir + site+'-Flow and Totals.xlsx')
    Totals_pivot_tables = pd.ExcelWriter(pivotoutputdir + site+'-Totals.xlsx')
    
    ## Simple V-notch data #################################
    SimpleV = fill_w_median(df[['Flow v-notch only stormflow clipped (gpm)']])
    SimpleV_pivot = pd.pivot_table(SimpleV,values=['Flow v-notch only stormflow clipped (gpm)','Flow v-notch only stormflow clipped (gpm) filled w median'],index=['Year','Month'],aggfunc=[lambda x: len(x.dropna()),np.sum]).dropna()
    ## Rename gpm -> gal
    SimpleV_pivot = SimpleV_pivot.rename(columns={'<lambda>':'count','Flow v-notch only stormflow clipped (gpm)':'Flow v-notch only stormflow clipped (gal)','Flow v-notch only stormflow clipped (gpm) filled w median':'Flow v-notch only stormflow clipped (gal) filled w median'})
    ## Multiply gpm * 5Min = gal/5Min
    SimpleV_pivot['sum'] = SimpleV_pivot['sum'] * 5.
    
    ## CTRSC #################################
    CTRSC = fill_w_median(df[['Flow compound weir stormflow clipped (gpm)']])
    CTRSC_pivot = pd.pivot_table(CTRSC,values=['Flow compound weir stormflow clipped (gpm)','Flow compound weir stormflow clipped (gpm) filled w median'],index=['Year','Month'],aggfunc=[lambda x: len(x.dropna()),np.sum]).dropna()
    ## Rename gpm -> gal
    CTRSC_pivot = CTRSC_pivot.rename(columns={'<lambda>':'count','Flow (gpm) CTRSC':'Flow (gal) CTRSC','Flow compound weir stormflow clipped (gpm)':'Flow compound weir stormflow clipped (gal)','Flow compound weir stormflow clipped (gpm) filled w median':'Flow compound weir stormflow clipped (gal) filled w median'})
    ## Multiply gpm * 5Min = gal/5Min
    CTRSC_pivot['sum'] = CTRSC_pivot['sum'] * 5.
    
    ## BASEFLOW #################################
    Baseflow = fill_w_median(df[['Baseflow (gpm)']])
    Baseflow_pivot = pd.pivot_table(Baseflow,values=['Baseflow (gpm)','Baseflow (gpm) filled w median'],index=['Year','Month'],aggfunc=[lambda x: len(x.dropna()),np.sum]).dropna()
    ## Rename gpm -> gal
    Baseflow_pivot = Baseflow_pivot.rename(columns={'<lambda>':'count','Baseflow (gpm)':'Baseflow (gal)','Baseflow (gpm) filled w median':'Baseflow (gal) filled w median'})
    ## Multiply gpm * 5Min = gal/5Min
    Baseflow_pivot['sum'] = Baseflow_pivot['sum'] * 5.
    
    ## QUICKFLOW #################################
    Quickflow = fill_w_median(df[['Quickflow (gpm)']])
    Quickflow_pivot = pd.pivot_table(Quickflow,values=['Quickflow (gpm)','Quickflow (gpm) filled w median'],index=['Year','Month'],aggfunc=[lambda x: len(x.dropna()),np.sum]).dropna()
    ## Rename gpm -> gal
    Quickflow_pivot = Quickflow_pivot.rename(columns={'<lambda>':'count','Quickflow (gpm)':'Quickflow (gal)','Quickflow (gpm) filled w median':'Quickflow (gal) filled w median'})
    ## Multiply gpm * 5Min = gal/5Min
    Quickflow_pivot['sum'] = Quickflow_pivot['sum'] * 5.
    
    
    ## Save Level and Flow Data to Flow_and_Totals
    SimpleV.to_excel(Flow_and_Totals, site+'-Simple V Flow Data')
    CTRSC.to_excel(Flow_and_Totals, site+'-CTRSC Flow Data')
    Baseflow.to_excel(Flow_and_Totals, site+'-Baseflow Data')
    Quickflow.to_excel(Flow_and_Totals, site+'-Quickflow Data')
    
    ## Save Total Flow Pivot Table to Flow_and_Totals
    SimpleV_pivot.to_excel(Flow_and_Totals, site+'-Simple V Flow Totals')
    CTRSC_pivot.to_excel(Flow_and_Totals, site+'-CTRSC Flow Totals')
    ## Save 
    Flow_and_Totals.save()
    
  ## Combine Total Flow Pivot Tables onto one sheet
    ## Save Total Flow Pivot Table to Flow_and_Totals
    SimpleV_pivot.to_excel(Totals_pivot_tables,site+'-Simple V Flow Totals')
    CTRSC_pivot.to_excel(Totals_pivot_tables,site+'-CTRSC Flow Totals')
    Baseflow_pivot.to_excel(Totals_pivot_tables,site+'-Baseflow Totals')
    Quickflow_pivot.to_excel(Totals_pivot_tables,site+'-Quickflow Totals')
    
    ## Combine Total Flow Pivots onto one sheet
    Combined = SimpleV_pivot.join(CTRSC_pivot).join(Baseflow_pivot).join(Quickflow_pivot)
    Combined.to_excel(Totals_pivot_tables,site+'-Combined Flow Totals')
    ## Output Total Flow Pivot Tables
    Totals_pivot_tables.save()
    
    
    ## add site name to column for All Sites Pivot
    Combined['Site'] = site
    AllSites_df = pd.concat([AllSites_df,Combined])
    
AllSites_df.to_excel(AllTotalFlows,'AllSites-Combined Flow Totals')
AllTotalFlows.save()
    
#%%
#for f in os.listdir(maindir+'Totals/')[0:1]:   
#    print f
#    site = f.split('-FlowTotals.xlsx')[0]
#    print 'Site: '+site
#    
#    SimpleV_pivot = pd.read_excel(maindir+'Totals/'+f,sheetname= site + '-Simple V Flow Totals')
#    USBR_pivot = pd.read_excel(maindir+'Totals/'+f,sheetname= site + '-USBR Flow Totals')
#    CTRSC_pivot = pd.read_excel(maindir+'Totals/'+f,sheetname= site + '-CTRSC Flow Totals')
#

#%%

summary1 = pd.DataFrame(columns=['WMA','Year','Main/SpecialStudy','Mean Flow (gpm)','Mean Flow (gpd)','Total Flow (gal)'])
summary2 = pd.DataFrame(columns=['WMA','Mean Flow (gpm) Main Outfalls','Mean Flow (gpd) Main Outfalls','Total Flow (gal) Main Outfalls'])


summs = pd.DataFrame()

                 
for d in [f for f in os.listdir(flowdata) if f.endswith('.xlsx')]:                               
                                                                                                                       
    site = d.split('-working draft.xlsx')[0]
    print 'Site: '+site
    ## Open data
    df = pd.read_excel(flowdata+d,sheetname=site+'-stormflow clipped')
                       
    if site == 'HST01':
        WMA = 'SLR'
        main_special = 'MainOutfall'      
    else:
        WMA = site.split('-')[0]
    print 'WMA: ' + WMA
    try:
        if len(site.split('-')[1]) == 4:
            main_special = 'SpecialStudy'
        else:
            main_special = 'MainOutfall'
        print 'Outfall Type: ' + main_special
    except:
        pass
          
    ## Add year for pivot       
    df['Year'] = df.index.year
    ## Add Flow Volume for pivot
    df.loc[:,'Flow v-notch only stormflow clipped (gal)'] = df['Flow v-notch only stormflow clipped (gpm)'] * 5.
    df.loc[:,'Flow compound weir stormflow clipped (gal)'] = df['Flow compound weir stormflow clipped (gpm)'] * 5.
    
    ## Make pivot table of Total Flow
    tot_flow = pd.pivot_table(df,values=['Flow v-notch only stormflow clipped (gal)','Flow compound weir stormflow clipped (gal)'],index=['Year'],aggfunc=[lambda x: len(x.dropna()),np.sum])
    ## Rename lambda - >> count
    tot_flow = tot_flow.rename(columns={'<lambda>':'count'})
    
    ## Make pivot table of Mean flow
    
    mean_flow = pd.pivot_table(df,values=['Flow v-notch only stormflow clipped (gpm)','Flow compound weir stormflow clipped (gpm)'],index=['Year'],aggfunc=[lambda x: len(x.dropna()),np.max,np.mean,np.median,np.min])
    ## Rename lambda - >> count
    mean_flow = mean_flow.rename(columns={'<lambda>':'count'})
    
    sum1 = tot_flow.join(mean_flow)
    sum1['WMA'] = WMA
    sum1['Site'] = site
    sum1['MainOutfall/SpecialStudy'] = main_special
    
    print sum1

    summs = pd.concat([summs,sum1])
    
    

summs.to_csv(maindir+'Data Summary all sites allyears.csv')


