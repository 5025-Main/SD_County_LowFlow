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
    Corr_flow_w_storms = Corr_flow.drop(['Flow compound weir stormflow clipped (gpm)'],axis=1)
    Corr_flow_clipped = Corr_flow.drop(['Flow compound weir (gpm)'],axis=1)
    
    # Flow data - with stormflow/all data
    sheet_name_w_storms  =site_name+'-all flow'
    print(sheet_name_w_storms)
    Corr_flow_w_storms.to_excel(final_flow_ExcelFile,sheet_name_w_storms)
    
    # Flow data - stormflow clipped
    sheet_name_clipped  =site_name+'-stormflow clipped'
    print(sheet_name_clipped)
    ## make all data for storm periods nans
    for col in Corr_flow_clipped.columns:
        try:
            Corr_flow_clipped[col] = np.where(Corr_flow_clipped['Flow compound weir stormflow clipped (gpm)'].isnull(),np.nan,Corr_flow_clipped[col])
        except:
            print 'skipped col: '+col
            pass
    ## rename the v-notch flow column
    Corr_flow_clipped = Corr_flow_clipped.rename(columns={'Flow v-notch only (gpm)':'Flow v-notch only stormflow clipped (gpm)'})
    Corr_flow_clipped.to_excel(final_flow_ExcelFile,sheet_name_clipped)
    
    # Rain Data
    rain_1D.to_excel(final_flow_ExcelFile,'Rain')
    # Field Calibration data
    #field_meas_flow_stage.round(2).to_excel(final_flow_ExcelFile,'Field Calibrations')
    
    ## Format columns
    for sheet in [sheet_name_w_storms,sheet_name_clipped,'Rain']:#,'Field Calibrations']:
        final_flow_ExcelFile.sheets[sheet].set_column('A:Z',26)
    final_flow_ExcelFile.sheets[sheet_name_clipped].set_column('B:C',38)
    
    #final_flow_site.sheets['Field Calibrations'].set_column('C:F',24)
    
    ## Date format column for Date Axis
    date_format = workbook.add_format({'num_format': 'mm/dd/yyyy HH:MM'})
    #final_flow_ExcelFile.sheets[sheet_name].write_column('A2',Corr_flow.index,date_format)
    final_flow_ExcelFile.sheets['Rain'].write_column('A2',rain_1D.index,date_format)
    #final_flow_ExcelFile.sheets['Field Calibrations'].write_column('A2',field_meas_flow_stage['Datetime'], date_format)
   
#######################################
    ### FULL SCALE HYDROGRAPH WITH STORMS
    chartsheet_full = workbook.add_chartsheet('Hydrograph(w storms)') 
    chart_full = workbook.add_chart({'type':'scatter'})

    max_row = str(len(Corr_flow_w_storms) + 1)
    print('Max Row: '+max_row)
    rain_max_row = str(len(rain_1D) + 1)
    print('Rain Max Row: '+rain_max_row)
    ## Flow series
    chart_full.add_series({'categories':"='"+sheet_name_w_storms+"'!$A2:$A"+max_row,'values':"='"+sheet_name_w_storms+"'!$B2:$B"+max_row,'marker':{'type':'none'},'line':{'color':'red'},'name':'Stormflow/Erroneous'})
    ## Clipped Flow series
    chart_full.add_series({'categories':"='"+sheet_name_clipped+"'!$A2:$A"+max_row,'values':"='"+sheet_name_clipped+"'!$B2:$B"+max_row,'marker':{'type':'none'},'line':{'color':'blue'},'name':'Flow'})
    ## Rain
    chart_full.add_series({'categories':'=Rain!$A2:$A'+rain_max_row,'values':'=Rain!$B2:$B'+rain_max_row,'line':{'none':True},'y2_axis': 1,'name':'Rain (in.)','marker':{'type':'none'},'y_error_bars':{'type':'custom','plus_values':'none','minus_values':'=Rain!$B2:$B'+rain_max_row,'end_style':0,'line':{'color':'#7bf2ec','width':1}}})
    
    ## Field Measurements
    #chart_full.add_series({'categories':'=Field Calibrations!$B2:$B'+max_row,'values':'=Field Calibrations!$C2:$C'+max_row, 'line':{'none':True},'marker':{'type':'diamond','border':{'color':'black'},'fill':{'color':'black'},'size':8},'name':'Field Calibration (gpm)'})
    
    # Configure the chart axes.
    xmin, xmax = hydro_start,hydro_end
    chart_full.set_x_axis({'position_axis':'on_tick','min':xmin,'max':xmax,'num_font':{'rotation':90},'num_format':'mm/dd/yyyy'})
    
    ymin, ymax = -5, Corr_flow_w_storms['Flow compound weir (gpm)'].max() * 1.5
    chart_full.set_y_axis({'name': 'Flow (gpm)','min':ymin,'max':ymax,'major_gridlines': {'visible':False},'num_font':{'color':'blue'}, 'crossing': ymin})
    
    rain_max = rain_1D.max()*1.5
    chart_full.set_y2_axis({'name':'Rainfall (inches)','min':0.0,'max':np.round(rain_max.values,1)[0],'reverse':True})
    chart_full.set_x2_axis({'min':xmin,'max':xmax})
    
    ## Chart Title
    chart_full.set_title({'name':'Hydrograph for MS4 site '+site_name})
    ## Chart Size
    chart_full.set_style(1)
    chart_full.set_size({'width': 1200, 'height': 320})
    chart_full.set_plotarea({'layout':{'x':0.1,'y':0.15,'width':0.8,'height':0.7},'border':{'color': 'black', 'width': 1}})

    # LEGEND
    chart_full.set_legend({'position': 'top'})
    # Insert the chart into the worksheet.
    chartsheet_full.set_chart(chart_full)
    chartsheet_full.set_tab_color('#4286f4')
    
####################################################################################
   
    # RESCALE Y-axis to LOW FLOWS and put in other chartsheet
    chartsheet_low = workbook.add_chartsheet('Hydrograph(stormflow clipped)')
    chart_low = workbook.add_chart({'type':'scatter'})
    
    ## Flow series
    chart_low.add_series({'categories':"='"+sheet_name_w_storms+"'!$A2:$A"+max_row,'values':"='"+sheet_name_w_storms+"'!$B2:$B"+max_row,'marker':{'type':'none'},'line':{'color':'gray','width':0.5},'name':'Stormflow/Erroneous'})
    ## Clipped Flow series
    chart_low.add_series({'categories':"='"+sheet_name_clipped+"'!$A2:$A"+max_row,'values':"='"+sheet_name_clipped+"'!$B2:$B"+max_row,'marker':{'type':'none'},'line':{'color':'blue'},'name':'Flow'})
    ## Rain
    chart_low.add_series({'categories':'=Rain!$A2:$A'+rain_max_row,'values':'=Rain!$B2:$B'+rain_max_row,'line':{'none':True},'y2_axis': 1,'name':'Rain (in.)','marker':{'type':'none'},'y_error_bars':{'type':'custom','plus_values':'none','minus_values':'=Rain!$B2:$B'+rain_max_row,'end_style':0,'line':{'color':'#7bf2ec','width':1}}})
    
    ## Field Measurements
    #chart_low.add_series({'categories':'=Field Calibrations!$B2:$B'+max_row,'values':'=Field Calibrations!$C2:$C'+max_row, 'line':{'none':True},'marker':{'type':'diamond','border':{'color':'black'},'fill':{'color':'black'},'size':8},'name':'Field Calibration (gpm)'})
    
    # Configure the chart axes.
    #xmin, xmax = dt.date(2017,5,1), dt.date(2017,6,1)
    chart_low.set_x_axis({'position_axis':'on_tick','min':xmin,'max':xmax,'num_font':{'rotation':90},'num_format':'mm/dd/yyyy'})
    
    ymin, ymax = -1, Corr_flow_clipped['Flow compound weir stormflow clipped (gpm)'].max() * 1.1
    chart_low.set_y_axis({'name': 'Flow (gpm)','min':ymin,'max':ymax,'major_gridlines': {'visible':False},'num_font':{'color':'blue'}, 'crossing':ymin})
    
    rain_max = rain_1D.max()*1.5
    chart_low.set_y2_axis({'name':'Rainfall (inches)','min':0.0,'max':np.round(rain_max.values,1)[0],'reverse':True})
    chart_low.set_x2_axis({'min':xmin,'max':xmax})
    
    ## Chart Title
    chart_low.set_title({'name':'Hydrograph for MS4 site '+site_name})
    ## Chart Size
    chart_low.set_style(1)
    chart_low.set_size({'width': 1200, 'height': 320})
    chart_low.set_plotarea({'layout':{'x':0.1,'y':0.15,'width':0.8,'height':0.7},'border':{'color': 'black', 'width': 1}})
    # LEGEND
    chart_low.set_legend({'position': 'top'})
    # Insert the chart into the worksheet.
    chartsheet_low.set_chart(chart_low)
    chartsheet_low.set_tab_color('#4286f4')
    
####################################################################################

    temp_cond_sheet = workbook.add_worksheet('Temp and Conductivity')
    temp_cond_sheet.set_zoom(80)
    
    ########## TEMPERATURE
    temp_chart = workbook.add_chart({'type':'scatter'})
    temp_cond_sheet.insert_chart('A1',temp_chart)
    ## Flow series
    temp_chart.add_series({'categories':"='"+sheet_name_w_storms+"'!$A2:$A"+max_row,'values':"='"+sheet_name_w_storms+"'!$B2:$B"+max_row,'marker':{'type':'none'},'line':{'color':'gray','width':0.5},'name':'Stormflow/Erroneous'})
    ## Clipped Flow series
    temp_chart.add_series({'categories':"='"+sheet_name_clipped+"'!$A2:$A"+max_row,'values':"='"+sheet_name_clipped+"'!$B2:$B"+max_row,'marker':{'type':'none'},'line':{'color':'blue'},'name':'Flow'})
    ## Temp series
    temp_chart.add_series({'categories':"='"+sheet_name_w_storms+"'!$A2:$A"+max_row,'values':"='"+sheet_name_w_storms+"'!$G2:$G"+max_row,'marker':{'type':'none'},'line':{'color':'red'},'name':'Water Temp. (F)','y2_axis': 1,})
    
    ## Format chart
    temp_chart.set_x_axis({'position_axis':'on_tick','min':xmin,'max':xmax,'num_font':{'size':8,'rotation':90},'num_format':'mm/dd/yyyy'})
    # Flow
    ymin, ymax = -1, Corr_flow_clipped['Flow compound weir stormflow clipped (gpm)'].max() * 1.1
    temp_chart.set_y_axis({'name': 'Flow (gpm)','min':ymin,'max':ymax,'major_gridlines': {'visible':False},'num_font':{'color':'blue'}, 'crossing':ymin})
    # Temp
    temp_min, temp_max = Corr_flow_w_storms[u'°F Water Temperature'].min()*0.9, Corr_flow_w_storms[u'°F Water Temperature'].max()*1.1
    temp_chart.set_y2_axis({'name':'Water Temperature (F)','min':temp_min,'max':temp_max})
    temp_chart.set_x2_axis({'min':xmin,'max':xmax})
    
    
    ## Chart Size
    temp_chart.set_style(1)
    temp_chart.set_size({'width': 1200, 'height': 360})
    temp_chart.set_plotarea({'layout':{'x':0.1,'y':0.15,'width':0.8,'height':0.7},'border':{'color': 'black', 'width': 1}})
    ## Chart Title
    temp_chart.set_title({'name':'Hydrograph and Water Temp for MS4 site '+site_name})
    # LEGEND
    temp_chart.set_legend({'position': 'top'})
    
    
    ########### CONDUCTIVITY
    cond_chart = workbook.add_chart({'type':'scatter'})
    temp_cond_sheet.insert_chart('A19',cond_chart)
    ## Flow series
    cond_chart.add_series({'categories':"='"+sheet_name_w_storms+"'!$A2:$A"+max_row,'values':"='"+sheet_name_w_storms+"'!$B2:$B"+max_row,'marker':{'type':'none'},'line':{'color':'gray','width':0.5},'name':'Stormflow/Erroneous'})
    ## Clipped Flow series
    cond_chart.add_series({'categories':"='"+sheet_name_clipped+"'!$A2:$A"+max_row,'values':"='"+sheet_name_clipped+"'!$B2:$B"+max_row,'marker':{'type':'none'},'line':{'color':'blue'},'name':'Flow'})
    ## cond series
    cond_chart.add_series({'categories':"='"+sheet_name_w_storms+"'!$A2:$A"+max_row,'values':"='"+sheet_name_w_storms+"'!$F2:$F"+max_row,'marker':{'type':'none'},'line':{'color':'orange'},'name':'Sp. Conductivity (uS/cm)','y2_axis': 1,})
    
    ## Format chart
    cond_chart.set_x_axis({'position_axis':'on_tick','min':xmin,'max':xmax,'num_font':{'size':8,'rotation':90},'num_format':'mm/dd/yyyy'})
    # Flow
    ymin, ymax = -1, Corr_flow_clipped['Flow compound weir stormflow clipped (gpm)'].max() * 1.1
    cond_chart.set_y_axis({'name': 'Flow (gpm)','min':ymin,'max':ymax,'major_gridlines': {'visible':False},'num_font':{'color':'blue'}, 'crossing':ymin})
    # Conductivity
    cond_min, cond_max = Corr_flow_w_storms[u'uS/cm EC'].min()*0.9, Corr_flow_w_storms[u'uS/cm EC'].max()*1.1
    cond_chart.set_y2_axis({'name':'Sp. Conductivity (uS/cm)','min':cond_min,'max':cond_max})
    cond_chart.set_x2_axis({'min':xmin,'max':xmax})
    
    
    ## Chart Size
    #cond_chart.set_style(1)
    cond_chart.set_size({'width': 1200, 'height': 360})
    cond_chart.set_plotarea({'layout':{'x':0.1,'y':0.15,'width':0.8,'height':0.7},'border':{'color': 'black', 'width': 1}})
    ## Chart Title
    cond_chart.set_title({'name':'Hydrograph and Conductivity for MS4 site '+site_name})
    # LEGEND
    cond_chart.set_legend({'position': 'top'})
    return max_row, rain_max_row

