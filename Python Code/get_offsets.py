# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 16:20:20 2019

@author: alex.messina
"""

ddir = 'P:/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/Data Processing/4 - Level calibration files and figures/Data Output 05_31_2019/'

offsets_df = pd.DataFrame()

for f in os.listdir(ddir):
    print
    print f
    
    site_name = f.split('-calibration.xlsx')[0]
    print site_name

    offsets = pd.read_excel(ddir+f,sheetname='offsets')
    offsets.index = [site_name]
    
    offsets_df = offsets_df.append(offsets)
