# -*- coding: utf-8 -*-
"""
Created on Mon May 18 15:13:35 2020

@author: alex.messina
"""

import mysql.connector
from datetime import datetime
import pandas as pd


db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Mactec101',
        database = 'testdatabase' #added after created in lines below
        )
        
mycursor = db.cursor()

## Create database
#mycursor.execute("CREATE DATABASE testdatabase")

## Create table and define columns
#mycursor.execute("CREATE TABLE Test (site varchar(50) NOT NULL, created datetime NOT NULL, status ENUM('flowing', 'ponded', 'obstructed', 'dry'), id int PRIMARY KEY NOT NULL AUTO_INCREMENT)")

## Alter data type
mycursor.execute("ALTER TABLE Test MODIFY site VARCHAR(12) NOT NULL")

## Add column
mycursor.execute("ALTER TABLE Test ADD Level_in FLOAT NOT NULL")

db.commit()

## Insert an entry
#mycursor.execute("INSERT INTO Test (site, created, status) VALUES (%s, %s, %s)", ("CAR-007",datetime.now(), 'ponded'))
#db.commit()
#%%
selection = '*'
table_name = 'Test'
site_name = 'CAR-007'
sql_query =  "SELECT %s FROM %s WHERE site= '%s' " % (selection, table_name, site_name) #'%s' needed extra quotes
mycursor.execute(sql_query)

for x in mycursor:
    print x
    
#%%

## MySQL table into a Pandas dataframe
df = pd.read_sql_query(sql_query,db)
print df



#%%

## Describe tables in a database
db_tables = pd.read_sql_query('SHOW TABLES FROM testdatabase', db)

for table_name in db_tables['Tables_in_testdatabase']:
    print 'Table Name: ' + table_name
    output = pd.read_sql_query('SHOW FIELDS FROM {}'.format(table_name), db)
    print output
    print '\n'
    ## Doesn't seem to show the data type or key correclty. can see in Workbench though


























