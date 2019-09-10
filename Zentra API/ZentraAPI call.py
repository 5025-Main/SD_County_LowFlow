# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:51:41 2019

@author: alex.messina
"""
import pandas as pd
import datetime as dt
import pytz
from pytz import timezone
import json
import urllib2

#%%
def zentra_json_parser(json_obj):
    results_df = pd.DataFrame()
    for row in json_obj['device']['timeseries'][0]['configuration']['values']:
    
        utc_time = dt.datetime.utcfromtimestamp(row[0]).replace(tzinfo=timezone('UTC'))
        loc_time = utc_time.astimezone(timezone('US/Pacific')).replace(tzinfo=None)
        
        meas_df = pd.DataFrame(row[3])
        meas_df.index =   meas_df['units'].str.strip(' ')+' '+meas_df['description']
        meas_df = meas_df.T
        
        results_df = results_df.append(pd.DataFrame(dict(meas_df.ix['value']),index=[loc_time]))
    
    return results_df

def getDeviceReadings(site_name,start_time_loc):
    device_dict = {
        'CAR-070':('06-02245','89211-11784'),
        'CAR-072':('06-02294','27595-95125'),
        'CAR-072B':('06-02127','63599-01736'),
        'CAR-072O':('06-02246','70870-65036'),
        'SDG-084J':('06-02225','86271-24221')
        }
    
    
    user = "alex.messina@woodplc.com"
    user_password = "Mactec101"
    
    device_serial_number = device_dict[site_name][0]
    device_password = device_dict[site_name][1]
    ip = "zentracloud.com"
    
    token =  '1a45a3456373971b5d1120ab9a9953e731f13402'
    
    start_time_utc = start_time_loc.astimezone(timezone('UTC'))
    start_time  = int((start_time_utc-dt.datetime(1970,1,1,0,0,tzinfo=timezone('UTC'))).total_seconds())
    
    url = 'https://' + ip + '/api/v1/readings'+ '?' + "sn=" + device_serial_number+ '&' + "start_time=" + '%s'%start_time
    
    request = urllib2.Request(url)
    request.add_header('Authorization','token %s' % token)
    request.add_header('Content-Type','application/json')
    
    
    response = urllib2.urlopen(request)
    readings_str = response.read()
    readings_json = json.loads(readings_str)
    # Readings are now contained in the 'readings_json' Python dictionary
    
    # Examples of accessing data
    #print json.dumps(readings_json, sort_keys=True, indent=4)
    #print "get_readings_ver: ", json.dumps(readings_json['get_readings_ver'])
    #print "created: ", json.dumps(readings_json['created'])
    #print "device: ", json.dumps(readings_json['device'])
    #print "device_info: ", json.dumps(readings_json['device']['device_info'])

    df = zentra_json_parser(readings_json)
    df['in Water Level'].plot()
    
    return df[['in Water Level',u'°F Water Temperature',u'mS/cm EC',u' Sensor Metadata']]


if __name__ == "__main__":
    
    ##
    site = 'SDG-084J'
    
    start_time_loc = dt.datetime(2019,8,1,0,0)
    
    ## Format for UTC
    mytz = timezone('US/Pacific')
    start_time_loc = mytz.normalize(mytz.localize(start_time_loc,is_dst=True))

    df = getDeviceReadings(site, start_time_loc)
    
    df.to_csv(site+'.csv',encoding='utf-8')


#%%
