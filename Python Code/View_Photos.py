# -*- coding: utf-8 -*-
"""
Created on Wed Aug 07 09:03:56 2019

@author: alex.messina
"""
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os
from PIL import Image
import datetime as dt

### CHOO CHOO CHOOse your site
site = 'SDR-127'

flow_dir = 'C:/Users/alex.messina/Documents/GitHub/SD_County_LowFlow/2 - Flow output Excel files - working drafts/Data Output 07_25_2019/'
flow_filename = [f for f in os.listdir(flow_dir) if f.split('-working draft.xlsx')[0]==site][0]
flow_df = pd.read_excel(flow_dir+flow_filename,sheetname=site+'-flow')
level_dir = 'C:/Users/alex.messina/Documents/GitHub/SD_County_LowFlow/4 - Level calibration files and figures/Data Output 07_25_2019/'
level_filename= [f for f in os.listdir(level_dir) if f.split('-calibration.xlsx')[0]==site][0]
level_df = pd.read_excel(level_dir+level_filename,sheetname=site+'Level and Flow data')

pic_dir = 'C:/Users/alex.messina/Downloads/'
pic_folder = site + '/'


#%%

# define your images to be plotted
pics = [os.listdir(pic_dir+pic_folder)][0][950:] ## You can limit photos here

# now the real code :) 
curr_pos = 0

def key_event(e):
    global curr_pos

    if e.key == "right":
        curr_pos = curr_pos + 1
    elif e.key == "left":
        curr_pos = curr_pos - 1
    else:
        return
    curr_pos = curr_pos % len(pics)
    print 'key event '+str(curr_pos)
  
    ## Select pic
    picture_file = pic_dir + pic_folder+ pics[curr_pos]
    print 'Pic file: '+pics[curr_pos]
    ## Extract datetime of pic and format datetime
    date_taken = Image.open(picture_file)._getexif()[36867]
    print 'Date taken: '+date_taken
    t = dt.datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
    t_round5 = dt.datetime(2019, t.month, t.day, t.hour,5*(t.minute // 5),0)
    ## Get flow data at time of pic
    flow_at_image = flow_df.ix[t_round5,'Flow compound weir (gpm)']
    
    ## Image
    ax1.cla()
    ax1.set_title('SITE: '+site+' Datetime: '+t.strftime('%m/%d/%y %H:%M') +' Pic: '+pics[curr_pos])
    img=mpimg.imread(picture_file)
    # from now on you can use img as an image, but make sure you know what you are doing!
    imgplot=ax1.imshow(img)
    plt.show()
    
    ## Plot flow data
    ax2.cla()
    ax2.plot_date(flow_df.index,flow_df['Flow compound weir (gpm)'],marker='None',ls='-',c='b',label='Flow compound weir (gpm)')
    ax2.plot_date(t_round5, flow_at_image,marker='o',ls='None',c='r')
    
    ## Set plot limits
    ax2.set_xlim(t_round5 - dt.timedelta(hours=8), t_round5 + dt.timedelta(hours=8))
    ## Get flow data over a 24 hour surrounding period
    flow_over_interval = flow_df.ix[t_round5 - dt.timedelta(hours=8):t_round5 + dt.timedelta(hours=8),'Flow compound weir (gpm)']
    ## y limits
    if flow_over_interval.min() == 0. and flow_over_interval.max() > 0.:
        ax2.set_ylim(-5.,flow_over_interval.max()*1.1)
    elif flow_over_interval.min() == 0. and flow_over_interval.max() == 0.:
            ax2.set_ylim(-5.,5.)
    else:
        ax2.set_ylim(flow_over_interval.min()*0.9,flow_over_interval.max()*1.1)
        
    ax2.xaxis.set_major_formatter(mpl.dates.DateFormatter('%A \n %m/%d/%y %H:%M'))
    fig.canvas.draw()
    print 'done'
    
    return



fig = plt.figure(1,figsize=(16,11))
fig.canvas.mpl_connect('key_press_event', key_event)


picture_file = pic_dir + pic_folder+ pics[curr_pos]
date_taken = Image.open(picture_file)._getexif()[36867]
t = dt.datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
t_round5 = dt.datetime(2019, t.month, t.day, t.hour,5*(t.minute // 5),0)
flow_at_image = flow_df.ix[t_round5,'Flow compound weir (gpm)']

## Image
ax1 = plt.subplot(211)
ax1.set_title('SITE: '+site+' Datetime: '+t.strftime('%m/%d/%y %H:%M'))
img=mpimg.imread(picture_file)
# from now on you can use img as an image, but make sure you know what you are doing!
imgplot=plt.imshow(img)
plt.show()

ax2 = plt.subplot(212)
ax2.plot_date(flow_df.index,flow_df['Flow compound weir (gpm)'],marker='None',ls='-',c='b',label='Flow compound weir (gpm)')
ax2.plot_date(t_round5, flow_at_image,marker='o',ls='None')

ax2.set_xlim(t_round5 - dt.timedelta(hours=8), t_round5 + dt.timedelta(hours=8))
flow_over_interval = flow_df.ix[t_round5 - dt.timedelta(hours=8):t_round5 + dt.timedelta(hours=8),'Flow compound weir (gpm)']
if flow_over_interval.min() == 0. and flow_over_interval.max() > 0.:
    ax2.set_ylim(-5.,flow_over_interval.max()*1.1)
elif flow_over_interval.min() == 0. and flow_over_interval.max() == 0.:
        ax2.set_ylim(-5.,5.)
else:
    ax2.set_ylim(flow_over_interval.min()*0.9,flow_over_interval.max()*1.1)
ax2.xaxis.set_major_formatter(mpl.dates.DateFormatter('%A \n %m/%d/%y %H:%M'))

ax2_2 = ax2.twinx()
ax2


plt.tight_layout()









#%%












