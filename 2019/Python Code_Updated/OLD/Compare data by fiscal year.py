import os
from pandas import *
from datetime import datetime
import pandas as pd
import numpy as np

StartTime=datetime.now()

All_years_dir = '//sdg1-fs1/SDShare/Projects-South/Environmental - Schaedler/5025-17-4034 2017 County Weir Monitoring/Post Deployment Assessment/AllYears Data/hydrograph w Rolling Median/'
###update with new deliverable
source_dir_2018 = '//sdg1-fs1/SDShare/Projects-South/Environmental - Schaedler/5025-18-4055 COSD TO 55 Low Flow Data Mngmt/DATA/Data Deliverables/Hydrographs Hydro Data and Pivot Tables 7-27-2018/'
dest_folder = 'P:/Projects-South/Environmental - Schaedler/5025-18-4055 COSD TO 55 Low Flow Data Mngmt/DATA/Data Deliverables/Comparison Files/'
output_filename = dest_folder+"data_compilation_OLD SITES.xlsx"
deliverable_filename = dest_folder+"Monthly Averages and Sums_OLD SITES.xlsx"
writer = pd.ExcelWriter(output_filename)
deliverable = pd.ExcelWriter(deliverable_filename)

###SET VARIABLES FOR COLUMNS AND OUTPUT DATAFRAME AND DATA FREQUENCY
columns = ['Flow (gpm)', 'Flow (gpm) stormflow clipped', 'Flow (gpm) filled w mean', 'Flow (gpm) filled w median', '24H roll_median', 'flow over 24H median', 'Weekly roll_median', 'flow over Weekly median']  
final_table = pd.DataFrame(index = [])
data_frequency_min = 5.

for f in os.listdir(All_years_dir):
    sitename = f.replace("-AllYears-hydrograph.xlsx", "")
    print(sitename)
    output_panda = pd.DataFrame(index = [])
    
##GET ALL FLOW WORKSHEETS IN EACH SITE FILE AND APPEND INTO SINGLE DATAFRAME
    final_sheet_list=[]
    workbook = pd.ExcelFile(All_years_dir+f)
    for sheet in workbook.sheet_names:
        if "flow" in sheet:
            final_sheet_list.append(sheet)
        else:
            pass    
    for sheet in final_sheet_list:
        working_sheet = read_excel(All_years_dir+f, sheetname=sheet, index_col=0)
        output_panda = output_panda.append(working_sheet)
    print(sitename, "previous years of data compiled.")

#CurrentSites = os.listdir(source_dir_2018)
#OldSites = os.listdir(All_years_dir)
#for site in CurrentSites:
#    ind = 0
#    CurrentSites.remove(site)
#    CurrentSites.insert(ind, site.replace("-working draft.xlsx", ""))
#    ind+=1
#    CurrentSites.sort()
#print(CurrentSites)    
#for site in OldSites:
#    ind = 0
#    OldSites.remove(site)
#    OldSites.insert(ind, site.replace("-AllYears-hydrograph.xlsx", ""))
#    ind+=1
#    OldSites.sort()  
#print(OldSites)
#Only2018Sites = (set(CurrentSites)-set(OldSites))
#Only2018Sites.sort()
#print(Only2018Sites)
#
#for f in Only2018Sites:
#    sitename = f
#    print(sitename)
#    output_panda = pd.DataFrame(index = [])

###TRY TO APPEND 2018 DATA AND CALC STATS FOR THE 2018 DATA
    try:    
        file_2018 = source_dir_2018 + sitename + "-working draft.xlsx"
        panda_2018 = read_excel(file_2018 , sheetname = sitename+"-flow", index_col=0)
        panda_2018 = panda_2018.drop(["Day","Hour", "Minute", "Weekday", "Month", "Year"], axis=1)
    
## ROLLING MEDIANS from Alex's FDC for assessment_data script to calculate the stats for 2018 deliverable data
        ## Smooth data into 1HR rolling median
        panda_2018['1H roll_median'] = panda_2018['Flow (gpm) stormflow clipped'].rolling(int(60./data_frequency_min),center=True,min_periods=int(30./data_frequency_min)).median()
        ## 24H rolling median - 24H = 1440 minutes
        panda_2018['24H roll_median'] = panda_2018['1H roll_median'].rolling(int(1440./data_frequency_min),center=True,min_periods=int(720./data_frequency_min)).median() 
        ## Weekly rolling median 1 Week = 10080 minutes
        panda_2018['Weekly roll_median'] = panda_2018['1H roll_median'].rolling(int(10080./data_frequency_min),center=True,min_periods=int(5040./data_frequency_min)).median() 
        
## FILL MISSING DATA
        median_flow, mean_flow = panda_2018['Flow (gpm) stormflow clipped'].median(), panda_2018['Flow (gpm) stormflow clipped'].mean()
        median_flow, mean_flow = np.round(median_flow, 3), np.round(mean_flow,3)
        ## Fill with just seaonal mean
        panda_2018['Flow (gpm) filled w mean'] = panda_2018['Flow (gpm) stormflow clipped'].fillna(mean_flow)
        ## Fill with rolling median; priority: 24H rolling, Weekly rolling, seasonal median
        ## Get 24H rolling if available, else use Weekly rolling
        panda_2018['median for fill'] = panda_2018['24H roll_median'].where(np.isnan(panda_2018['24H roll_median'])==False, panda_2018['Weekly roll_median'])
        ## Fill na with rolling medians
        panda_2018['Flow (gpm) filled w median'] = panda_2018['Flow (gpm) stormflow clipped'].where(np.isnan(panda_2018['Flow (gpm) stormflow clipped'])==False,  panda_2018['median for fill'] )
        ## Fill remaining na's with seasonal median
        panda_2018['Flow (gpm) filled w median'] = panda_2018['Flow (gpm) filled w median'].fillna(median_flow)
        panda_2018 = panda_2018.reindex_axis(columns, axis=1)     
        output_panda = output_panda.append(panda_2018)
        print(sitename, "2018 data compiled.")
    except FileNotFoundError:
        print("No 2018 Data exists for this site. Continuing with script.")
        



###CALC COLUMNS FOR MONTH AND YEAR AND TOTAL FLOW FOR EACH FLOW COLUMN (all flow, storm clipped, mean-filled, median-filled)
    months = output_panda.index.strftime('%b')
    years = output_panda.index.strftime('%Y')
    output_panda['Site'] = pd.Series(sitename, index=output_panda.index)
    output_panda['Month'] = pd.Series(months, index=output_panda.index)
    output_panda['Year'] = pd.Series(years, index=output_panda.index)
    output_panda['Total Flow (gal)'] = output_panda.apply(lambda row: row['Flow (gpm)'] * 5, axis=1)
    output_panda['Total Flow stormflow clipped (gal)'] = output_panda.apply(lambda row: row['Flow (gpm) stormflow clipped'] * 5, axis=1)
    output_panda['Total Flow filled w mean (gal)'] = output_panda.apply(lambda row: row['Flow (gpm) filled w mean'] * 5, axis=1)
    output_panda['Total Flow filled w median (gal)'] = output_panda.apply(lambda row: row['Flow (gpm) filled w median'] * 5, axis=1)
    print("Extra columns for pivot tables calculated and added to the dataset for", sitename)
    
###pivot table for each site
    table  = pivot_table(output_panda, values=['Flow (gpm)', 'Flow (gpm) stormflow clipped', 'Flow (gpm) filled w mean', 'Flow (gpm) filled w median', 'Total Flow (gal)','Total Flow stormflow clipped (gal)', 'Total Flow filled w mean (gal)','Total Flow filled w median (gal)'], 
                         index=['Site','Year', 'Month'], 
                         aggfunc={'Flow (gpm)':[np.mean, 'count'],
                                  'Flow (gpm) stormflow clipped':[np.mean, 'count'],
                                  'Flow (gpm) filled w mean':[np.mean, 'count'],
                                  'Flow (gpm) filled w median':[np.mean, 'count'],
                                  'Total Flow (gal)':np.sum,
                                  'Total Flow stormflow clipped (gal)':np.sum,
                                  'Total Flow filled w mean (gal)':np.sum,
                                  'Total Flow filled w median (gal)':np.sum})
    print(table)
    final_table = final_table.append(table)
    output_panda.to_excel(writer,sitename)

final_table.to_excel(deliverable,"Monthly Averages and Sums")
writer.save()
deliverable.save()
print("This program took ", str(datetime.now()-StartTime), " to complete.")






    