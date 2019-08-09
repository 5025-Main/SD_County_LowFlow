# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 16:20:20 2019

@author: alex.messina
"""

ddir = 'P:/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/Data Processing/4 - Level calibration files and figures/Data Output 05_31_2019/'

ddir = 'C:/Users/alex.messina/Documents/GitHub/SD_County_LowFlow/4 - Level calibration files and figures/Data Output 06_30_2019/'

offsets_df = pd.DataFrame()

for f in os.listdir(ddir):
    print
    print f
    
    site_name = f.split('-calibration.xlsx')[0]
    print site_name

    offsets = pd.read_excel(ddir+f,sheetname='offsets')
    offsets.index = [site_name]
    
    offsets_df = offsets_df.append(offsets)

#%%

datadir = 'C:/Users/alex.messina/Documents/GitHub/SD_County_LowFlow/2 - Flow output Excel files - working drafts/'
maydir = datadir+'Data Output 05_31_2019/'
junedir = datadir+'Data Output 06_30_2019/'

site_to_process = 'SDR-207'

#for f in [d for d in os.listdir(maydir) if d==site_to_process+'-working draft.xlsx']:
    
for f in [d for d in os.listdir(maydir) if d.endswith('working draft.xlsx')][-3:]:
    print f
    df_may = pd.read_excel(maydir + f,index_col=0)
    df_june = pd.read_excel(junedir + f)
    fig, ax = plt.subplots(1,1)
    
    ax.set_title(f)
    ax.plot_date(df_june.index,df_june['Flow (gpm)'],marker='None',ls='-',c='r',label='June')
    ax.plot_date(df_may.index,df_may['Flow (gpm)'],marker='None',ls='-',c='b',label='May')
    ax.legend()
    ax.set_xlim(df_may.index[0],df_may.index[-1])
    ax.set_ylim(0,df_may['Flow (gpm)'].max())
    
    diff = df_may['Flow (gpm)'] - df_june[df_may.index[0]:df_may.index[-1]]['Flow (gpm)']
    if diff.sum() != 0:
        print 'Difference! ' + f
        print diff.sum()
    
    
    

