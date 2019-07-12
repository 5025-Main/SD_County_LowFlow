# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 12:30:18 2016

@author: alex.messina
"""

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


import time

from BeautifulSoup import BeautifulSoup

import numpy as np
import pandas as pd
import requests

import datetime as dt


#maindir = 'P:/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/Data Processing/'


SITE_IDs = {'Bonita':11,'Bonsall':	118,'Cactus County Park':	74,'Couser Canyon':	117,'Deer Springs':	104,'El Camino del Norte':	32,'Flinn Springs County Park':	61,'La Mesa':	16,'Lake Hodges':	29,'Los Coches':	62,'Rainbow County Park':	121,'Rancho Bernardo':	28,'Roads Div I':	15,'San Marcos CRS':	105}

## TEST ONE
#SITE_IDs = {'Bonita':11}


SITE_SERIAL_dict = {'Bonita':'dbbd1242-4f9f-43f9-90b9-8b3ad8eeb0c4','Bonsall':	'e6f79336-c471-44b4-ae9f-440dc5021b92','Cactus County Park':	'1e235bf7-3b36-46a5-9202-d5969a3d7f98', 'Couser Canyon':	'cbe65d01-2763-4743-995c-b8d0753eeae7','Deer Springs':	'2a03361b-b8e7-430b-ad6f-aa897a765439','El Camino del Norte':	'730fd8d6-b24f-485a-b869-642a59b9dd72','Flinn Springs County Park':	'b73e2e89-144a-46f3-83ef-3e3ca268a8d6','Granite Hills':'ac0f8008-2fae-4df7-a376-22ebf92e1ff0','La Mesa':	'e9d397f8-de38-429f-a324-9d339a38547a','Lake Hodges':'65212cff-f993-44a7-befb-fbd331cd5d1c','Los Coches':	'e186e452-ddd5-4119-a34c-efdc00b35221','Rainbow County Park':	'081af52d-e96d-495b-adb3-fe4df7151e72','Rancho Bernardo':	'a1c6e51f-7f47-4b67-82c0-71f319062885','Roads Div I':	'91047666-b9ea-48a7-bb25-f3d0b974a428','San Marcos CRS':	'5476904e-d351-44ec-80e5-80ea107b65e8','Valley Center':'bfbccfe2-79fd-42c8-9b8f-7b19eeaa06bd'}

######### UPDATE HERE ###################
start_date, end_date = '2019-04-31', dt.date.today().strftime('%Y-%m-%d')
## DOWNLOAD Bonsall manually, for some reason it gets wrong data

daterange = pd.date_range('20190430',dt.datetime.now(),freq='D')


for SITE in sorted(SITE_IDs.keys()):
    SITE_ID = str(SITE_IDs[SITE])
    SITE_SERIAL = SITE_SERIAL_dict[SITE]
    print "SITE : " +str(SITE)+' ID: '+str(SITE_ID) 
#    print SITE+' - '+str(SITE_ID)+' - '+SITE_SERIAL_dict[SITE]
    site_df = pd.DataFrame()
    try:

        url = 'https://sandiego.onerain.com/sensor.php?site_id='+SITE_ID+'&device_id=1&device=86001905-29ee-4eff-bc28-5c9a2746e686'
        
        
        s = requests.get(url).content
        
        soup = BeautifulSoup(s)
        
        try:
            Site_Name = soup.title.text.split('[')[1].split('(')[0]
        except:
            Site_Name = SITE
        
        
        
        if len(Site_Name) > 0:
            print
            print 'Grabbing data for SiteID: '+SITE_ID+'... Site Name: '+Site_Name
            print '...from date range: '+str(daterange[0])+' to '+str(daterange[-1])
            try:
                ##enter web address of data
                #start_date = str(month.year)+'-'+str(month.month)+'-'+'01'
                #end_date = str(month.year)+'-'+str(month.month)+'-'+str(month.day)
                #start_date, end_date = str(date),str(date+ dt.timedelta(days=1))
                

                device_id = str(1)
                if SITE == 'Bonita':
                    device_id = str(3)
                print 'Device ID: '+device_id
                url = 'https://sandiego.onerain.com/sensor.php?time_zone=US%2FPacific&site_id='+SITE_ID+'&site='+SITE_SERIAL+'&device_id='+device_id+'&device=e1f42d5d-1cb7-4732-ac46-acf743c10d3c&data_start='+start_date+'+00%3A00%3A00&data_end='+end_date+'+23%3A59%3A59&bin=900&range=Custom+Range&legend=true&thresholds=true&refresh=off&show_raw=true&show_quality=true'
                s = requests.get(url).content
                soup = BeautifulSoup(s)
                
                if len(soup.findAll('h1')) > 0:
                    if 'Rain Increment' in soup.findAll('h1')[0].text:        
                        print 'Rain Increment in Title...'
                        #print url
                        ## Get data from website
                        ## Open up browser
                        driver = webdriver.Chrome()
                        driver.get(url)
                        
                        ## Save report
                        print 'saving report...'
                        #time.sleep(10)
                        ## Click on save button
                        print 'clicking save as...'
                        
                        print 'Find element...'
                        element_xpath = driver.find_element_by_xpath('//*[@id="dropdown-button-action-download"]/i')                        
                        
                        print 'scroll into view'
                        driver.execute_script("arguments[0].scrollIntoView();", element_xpath)
                        
                        print 'wait for button'
                        WebDriverWait(driver,15).until(expected_conditions.visibility_of_element_located((By.XPATH, '//*[@id="dropdown-button-action-download"]')))
                        
                        print 'find button'
                        driver.find_element_by_xpath('//*[@id="dropdown-button-action-download"]').click()

                        ## Click on 'Excel'
                        print '...clicking Save Excel...'
                        WebDriverWait(driver, 15).until(expected_conditions.visibility_of_element_located((By.XPATH, '//*[@id="dropdown-menu-action-download"]/li[2]/a')))
                        driver.find_element_by_xpath('//*[@id="dropdown-menu-action-download"]/li[2]/a').click()
                        
                        time.sleep(3)
    
                        print '...saved...'
                        print '...closing browser...'
                        driver.quit()
                        time.sleep(3)
                        print '...browser closed.'
                        print 
                        print
                    
                   
            except Exception as e:
                print (e)
                pass

    except:
        raise
        
        
        
        
#%% Plot rain data


raindir = maindir+'0 - Rain Data/'
raw_rain_files = raindir+'Raw Data/'
daily_rain_files = raindir+'Daily/'

## Data from  https://sandiego.onerain.com/rain.php

#for one site
#site_name = 'SLR-152'
#raingauge_dict = {'CAR-015':'El_Camino','CAR-059':'El_Camino',  'CAR-069':'San_Marcos', 'CAR-070':'San_Marcos', 'CAR-072':'San_Marcos','CAR-072O':'San_Marcos', 'HST01':'Rainbow', 'SDG-077':'Rancho_Bernardo', 'SDG-072':'Rancho_Bernardo', 'SDG-080':'Rancho_Bernardo', 'SDG-074':'Rancho_Bernardo', 'SDG-084':'Rancho_Bernardo','SDG-085':'Rancho_Bernardo','SDG-085M':'Rancho_Bernardo', 'SDG-080':'Rancho_Bernardo','SDG-115':'Lake_Hodges','SDG-115B':'Lake_Hodges', 'SDR-036':'Flinn_Springs', 'SDR-036J':'Flinn_Springs', 'SDR-041':'Los_Coches', 'SDR-064':'Cactus_County', 'SDR-097':'Los_Coches', 'SDR-098':'Los_Coches', 'SDR-127':'Flinn_Springs','SDR-127B':'Flinn_Springs', 'SDR-207':'Los_Coches','SDR-203A':'Los_Coches','SDR-204A':'Los_Coches','SDR-207G':'Los_Coches','SDR-207L':'Los_Coches','SDR-207M':'Los_Coches','SDR-554':'Los_Coches','SDR-607':'Los_Coches', 'SDR-228':'Cactus_County', 'SDR-754':'Los_Coches', 'SLR-041':'Couser', 'SLR-045':'Deer_Springs', 'SLR-095':'Deer_Springs', 'SLR-150':'Bonsall', 'SLR-152':'Couser', 'SLR-152A':'Couser', 'SLR-152H':'Couser', 'SLR-155':'Couser', 'SLR-155F':'Couser', 'SWT-019':'Bonita', 'SWT-023':'Bonita', 'SWT-030':'Roads', 'SWT-055':'La_Mesa', 'SWT-055A':'La_Mesa','SWT-235':'Roads'}
#rainfiles = [s for s in os.listdir(raindir) if raingauge_dict[site_name] in s]

#for one gauge
#gauge_name = 'La_Mesa'
#rainfiles = [s for s in os.listdir(raindir) if gauge_name in s]

#for all gauges
rainfiles = [s for s in os.listdir(raw_rain_files) if s.endswith('.xls')]

fig, ax = plt.subplots(1,1,figsize=(12,8))

for rainfile in rainfiles:
    print ('')
    print 'Precip file: '+rainfile
    rain = pd.read_excel(raw_rain_files+rainfile)
    rain.index = pd.to_datetime(rain['Reading'])
    ## Resample to regular interval and fill non-data with zeros
    rain = rain.resample('15Min').sum()
    rain  = rain.fillna(0.)
    rain_1D = rain.resample('1D').sum()

    ax.plot_date(rain_1D.index, rain_1D['Value'],ls='steps-pre',marker='None',label=rainfile.split('_')[1:2])
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%d'))
    
    rain_1D.to_csv(daily_rain_files+'Daily-'+rainfile.replace('.xls','.csv'))

ax.legend()


