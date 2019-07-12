# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 14:31:39 2017

@author: alex.messina
"""
#%%
def Excel_Plots(site_name, Corr_flow, rain_1D, final_flow_ExcelFile,hydro_start,hydro_end):
    import numpy as np
    workbook = final_flow_ExcelFile.book
    ## Work sheets
    # Flow data
    sheet_name  =site_name+'-flow'
    print(sheet_name)
    Corr_flow.to_excel(final_flow_ExcelFile,sheet_name)
    # Rain Data
    rain_1D.to_excel(final_flow_ExcelFile,'Rain')
    # Field Calibration data
    #field_meas_flow_stage.round(2).to_excel(final_flow_ExcelFile,'Field Calibrations')
    
    ## Format columns
    for sheet in [sheet_name,'Rain']:#,'Field Calibrations']:
        final_flow_ExcelFile.sheets[sheet].set_column('A:Z',18)
    #final_flow_site.sheets['Field Calibrations'].set_column('C:F',24)
    
    ## Date format column for Date Axis
    date_format = workbook.add_format({'num_format': 'mm/dd/yyyy HH:MM'})
    #final_flow_ExcelFile.sheets[sheet_name].write_column('A2',Corr_flow.index,date_format)
    final_flow_ExcelFile.sheets['Rain'].write_column('A2',rain_1D.index,date_format)
    #final_flow_ExcelFile.sheets['Field Calibrations'].write_column('A2',field_meas_flow_stage['Datetime'], date_format)
   
#######################################
    ### FULL SCALE HYDROGRAPH WITH STORMS
    chartsheet_full = workbook.add_chartsheet('Hydrograph(full)') 
    chart_full = workbook.add_chart({'type':'scatter'})

    max_row = str(len(Corr_flow) + 1)
    print('Max Row: '+max_row)
    rain_max_row = str(len(rain_1D) + 1)
    print('Rain Max Row: '+rain_max_row)
    ## Flow series
    chart_full.add_series({'categories':"='"+sheet_name+"'!$A2:$A"+max_row,'values':"='"+sheet_name+"'!$C2:$C"+max_row,'marker':{'type':'none'},'line':{'color':'gray','width':0.5},'name':'Stormflow/Erroneous'})
    ## Clipped Flow series
    chart_full.add_series({'categories':"='"+sheet_name+"'!$A2:$A"+max_row,'values':"='"+sheet_name+"'!$D2:$D"+max_row,'marker':{'type':'none'},'line':{'color':'blue'},'name':'Flow'})
    ## Rain
    chart_full.add_series({'categories':'=Rain!$A2:$A'+rain_max_row,'values':'=Rain!$B2:$B'+rain_max_row,'line':{'none':True},'y2_axis': 1,'name':'Rain (in.)','marker':{'type':'none'},'y_error_bars':{'type':'custom','plus_values':'none','minus_values':'=Rain!$B2:$B'+rain_max_row,'end_style':0,'line':{'color':'#7bf2ec','width':1}}})
    
    ## Field Measurements
    #chart_full.add_series({'categories':'=Field Calibrations!$B2:$B'+max_row,'values':'=Field Calibrations!$C2:$C'+max_row, 'line':{'none':True},'marker':{'type':'diamond','border':{'color':'black'},'fill':{'color':'black'},'size':8},'name':'Field Calibration (gpm)'})
    
    # Configure the chart axes.
    xmin, xmax = hydro_start,hydro_end
    chart_full.set_x_axis({'position_axis':'on_tick','min':xmin,'max':xmax,'num_font':{'rotation':90},'num_format':'mm/dd/yyyy'})
    
    ymin, ymax = -5, Corr_flow['Flow (gpm)'].max() * 1.5
    chart_full.set_y_axis({'name': 'Flow (gpm)','min':ymin,'max':ymax,'major_gridlines': {'visible':False},'num_font':{'color':'blue'}, 'crossing': ymin})
    
    rain_max = rain_1D.max()*1.5
    chart_full.set_y2_axis({'name':'Rainfall (inches)','min':0.0,'max':np.round(rain_max.values,1)[0],'reverse':True})
    chart_full.set_x2_axis({'min':xmin,'max':xmax})
    
    ## Chart Title
    chart_full.set_title({'name':'Hydrograph for MS4 site '+site_name})
    ## Chart Size
    chart_full.set_style(1)
    chart_full.set_size({'width': 1080, 'height': 360})
    chart_full.set_plotarea({'layout':{'x':0.1,'y':0.15,'width':0.85,'height':0.7},'border':{'color': 'black', 'width': 1}})

    # LEGEND
    chart_full.set_legend({'position': 'top'})
    # Insert the chart into the worksheet.
    chartsheet_full.set_chart(chart_full)
    chartsheet_full.set_tab_color('#4286f4')
    
####################################################################################
   
    # RESCALE Y-axis to LOW FLOWS and put in other chartsheet
    chartsheet_low = workbook.add_chartsheet('Hydrograph(low)')
    chart_low = workbook.add_chart({'type':'scatter'})
    
    ## Flow series
    chart_low.add_series({'categories':"='"+sheet_name+"'!$A2:$A"+max_row,'values':"='"+sheet_name+"'!$C2:$C"+max_row,'marker':{'type':'none'},'line':{'color':'gray','width':0.5},'name':'Stormflow/Erroneous'})
    ## Clipped Flow series
    chart_low.add_series({'categories':"='"+sheet_name+"'!$A2:$A"+max_row,'values':"='"+sheet_name+"'!$D2:$D"+max_row,'marker':{'type':'none'},'line':{'color':'blue'},'name':'Flow'})
    ## Rain
    chart_low.add_series({'categories':'=Rain!$A2:$A'+rain_max_row,'values':'=Rain!$B2:$B'+rain_max_row,'line':{'none':True},'y2_axis': 1,'name':'Rain (in.)','marker':{'type':'none'},'y_error_bars':{'type':'custom','plus_values':'none','minus_values':'=Rain!$B2:$B'+rain_max_row,'end_style':0,'line':{'color':'#7bf2ec','width':1}}})
    
    ## Field Measurements
    #chart_low.add_series({'categories':'=Field Calibrations!$B2:$B'+max_row,'values':'=Field Calibrations!$C2:$C'+max_row, 'line':{'none':True},'marker':{'type':'diamond','border':{'color':'black'},'fill':{'color':'black'},'size':8},'name':'Field Calibration (gpm)'})
    
    # Configure the chart axes.
    #xmin, xmax = dt.date(2017,5,1), dt.date(2017,6,1)
    chart_low.set_x_axis({'position_axis':'on_tick','min':xmin,'max':xmax,'num_font':{'rotation':90},'num_format':'mm/dd/yyyy'})
    
    ymin, ymax = -5, Corr_flow['Flow compound weir stormflow clipped (gpm)'].max() * 1.1
    chart_low.set_y_axis({'name': 'Flow (gpm)','min':ymin,'max':ymax,'major_gridlines': {'visible':False},'num_font':{'color':'blue'}, 'crossing':ymin})
    
    rain_max = rain_1D.max()*1.5
    chart_low.set_y2_axis({'name':'Rainfall (inches)','min':0.0,'max':np.round(rain_max.values,1)[0],'reverse':True})
    chart_low.set_x2_axis({'min':xmin,'max':xmax})
    
    ## Chart Title
    chart_low.set_title({'name':'Hydrograph for MS4 site '+site_name})
    ## Chart Size
    chart_low.set_style(1)
    chart_low.set_size({'width': 1080, 'height': 360})
    chart_low.set_plotarea({'layout':{'x':0.1,'y':0.15,'width':0.85,'height':0.7},'border':{'color': 'black', 'width': 1}})
    # LEGEND
    chart_low.set_legend({'position': 'top'})
    # Insert the chart into the worksheet.
    chartsheet_low.set_chart(chart_low)
    chartsheet_low.set_tab_color('#4286f4')
    return max_row, rain_max_row
