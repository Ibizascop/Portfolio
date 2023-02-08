#Imports
import pyodbc
import pandas as pd
import os
import glob
import numpy as np
from tqdm.notebook import tqdm
import glob2
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import locale
import random
import urllib
import sqlalchemy as sa
import re
import warnings
from datetime import datetime
# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port

params = urllib.parse.quote_plus("DRIVER=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.8.so.1.1;"
                                 "SERVER=SERVER"
                                 "DATABASE=DATABASE;"
                                 "UID=USERNAME;"
                                 "PWD=PASSWORD!")

engine = sa.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

#Set language to French for dates
locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

#Ignore setting with copy error
pd.options.mode.chained_assignment = None

#Upload files to DATABASE
print('\n\n')

def split_dataframe(df, chunk_size = 100):
    chunks = list()
    num_chunks = len(df) // chunk_size + 1
    for i in range(num_chunks):
        chunks.append(df[i*chunk_size:(i+1)*chunk_size])
    return chunks


def etl_pipe_bulk(file):
    df = pd.read_csv(file, sep = '\t')
    if len(df)>0:
        #Enlever erreur date commentaire
        for i in range(len(df)) :
            if "choix" in str(df.iloc[i]["Dates_commentaires"]) :
                df["Dates_commentaires"][i] = "1 janvier 1970"
        #Correction types des colonnes
        df['Notes'] = df['Notes'].astype(str)
        df['Notes'] = df['Notes'].str.replace(',', '.').astype(float)
        df['Durées_sejours'] = df['Durées_sejours'].astype(float)
        df['Dates_commentaires'] =  pd.to_datetime(df.Dates_commentaires,format ="%d %B %Y")

        #Enlever lignes vides
        rows_to_remove = []
        for i in range(len(df)) :
                if df.iloc[i].isnull().sum() >= 10 :
                    #print("Removing row {}".format(i))
                    rows_to_remove.append(i)
        df = df.drop(rows_to_remove)

        #Cohérence noms de colonnes avec SQL
        df=df.rename(columns={"Urls": "URL", "Hotels": "HOTEL", "Notes":"NOTE", "Types_chambres":"TYPE_ROOMS",
                              "Durées_sejours":"DUREE_SEJOUR", "Mois_sejours": "MOIS_SEJOUR",
                              "Annees_sejours":"ANNEE_SEJOUR", "Types_voyageurs":"TYPE_VOYAGEUR",
                              "Nationalites":"NATIONALITE", "Dates_commentaires": "DATE_COMMENTAIRE",
                              "Titres_commentaires":"TITRE_COMMENTAIRE", "Commentaires": "COMMENTAIRE"})

        #Diviser le dataframe
        lista_df = split_dataframe(df)

        for x in lista_df:
            tries=0
            while tries<=4:
                try:
                    params = urllib.parse.quote_plus("DRIVER=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.8.so.1.1;"
                                 "SERVER=SERVER"
                                 "DATABASE=DATABASE;"
                                 "UID=USERNAME;"
                                 "PWD=PASSWORD!")

                    engine = sa.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
                    x.to_sql('booking_avis_IDF', con=engine, if_exists='append', index=False, method='multi')
                    break
                except Exception as e:
                    print(e)
                    time.sleep(2)
                    tries=+1

                    if tries==4:
                        now = datetime.now()
                        timestamp = datetime.timestamp(now)
                        timestamp = str(int(timestamp))
                        filename = '/datadrive/missed/missed_'+timestamp+'.csv'
                        x.to_csv(filename, sep = '\t', index=False)
                        break
         #Log
        with open('logio.txt','a') as flog:
            length = str(len(df))
            message = 'Processing df ' + file + ' of length: '+length
            print(message, file = flog)
    else :
        with open('logio.txt','a') as flog:
            message = 'Empty df ' + file
            print(message, file = flog)

#Check if hotel was already done
try :
    with open('logio.txt','r') as flog:
        done_files = flog.readlines()
        flog.close()
    done_files = [re.search("./To_Export/16.+csv",file).group() for file in done_files ]
except :
    done_files = []
files= glob2.glob('./To_Export/16*.csv')
for file in tqdm(files):
    if file not in done_files :
        try :
            #print(file)
            etl_pipe_bulk(file)
        except Exception as e:
            with open('exception.txt','a') as flog:
                print(file+" generated an exception "+e, file = flog)


#Get final results as CSV
#Server Parameters
params = urllib.parse.quote_plus("DRIVER=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.8.so.1.1;"
                                 "SERVER=SERVER"
                                 "DATABASE=DATABASE;"
                                 "UID=USERNAME;"
                                 "PWD=PASSWORD!")
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
engine = sa.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

liste_years = [2018,2019,2020,2021]
for year in tqdm(liste_years) :
    try :
        query= '''
        with raw_data as (SELECT URL , HOTEL, NOTE, TYPE_ROOMS, DUREE_SEJOUR, ANNEE_SEJOUR, TYPE_VOYAGEUR, NATIONALITE,
        DATE_COMMENTAIRE, TITRE_COMMENTAIRE, COMMENTAIRE, b.TYPE_, b.ADDRESSE_,
        coalesce(ANNEE_SEJOUR, year(DATE_COMMENTAIRE)) as YEAR_,

        case when CHARINDEX(' 75001 ', b.ADDRESSE_)>0 then '1er'
        when CHARINDEX(' 75002 ', b.ADDRESSE_)>0 then '2ème'
        when CHARINDEX(' 75003 ', b.ADDRESSE_)>0 then '3ème'
        when CHARINDEX(' 75004 ', b.ADDRESSE_)>0 then '4ème'
        when CHARINDEX(' 75005 ', b.ADDRESSE_)>0 then '5ème'
        when CHARINDEX(' 75006 ', b.ADDRESSE_)>0 then '6ème'
        when CHARINDEX(' 75007 ', b.ADDRESSE_)>0 then '7ème'
        when CHARINDEX(' 75008 ', b.ADDRESSE_)>0 then '8ème'
        when CHARINDEX(' 75009 ', b.ADDRESSE_)>0 then '9ème'
        when CHARINDEX(' 75010 ', b.ADDRESSE_)>0 then '10ème'
        when CHARINDEX(' 75011 ', b.ADDRESSE_)>0 then '11ème'
        when CHARINDEX(' 75012 ', b.ADDRESSE_)>0 then '12ème'
        when CHARINDEX(' 75013 ', b.ADDRESSE_)>0 then '13ème'
        when CHARINDEX(' 75014 ', b.ADDRESSE_)>0 then '14ème'
        when CHARINDEX(' 75015 ', b.ADDRESSE_)>0 then '15ème'
        when CHARINDEX(' 75016 ', b.ADDRESSE_)>0 then '16ème'
        when CHARINDEX(' 75017 ', b.ADDRESSE_)>0 then '17ème'
        when CHARINDEX(' 75018 ', b.ADDRESSE_)>0 then '18ème'
        when CHARINDEX(' 75019 ', b.ADDRESSE_)>0 then '19ème'
        when CHARINDEX(' 75020 ', b.ADDRESSE_)>0 then '20ème'
        when CHARINDEX(', 92', b.ADDRESSE_)>0 then 'Hauts-de-Seine'
        when CHARINDEX(', 93', b.ADDRESSE_)>0 then 'Seine-Saint-Denis'
        when CHARINDEX(', 94', b.ADDRESSE_)>0 then 'Val-de-Marne'
        when CHARINDEX(', 95', b.ADDRESSE_)>0 then 'Val dOISE'
        when CHARINDEX(', 77', b.ADDRESSE_)>0 then 'Seine-et-Marne'
        when CHARINDEX(', 91', b.ADDRESSE_)>0 then 'Essonne'
        when CHARINDEX(', 78', b.ADDRESSE_)>0 then 'Yvelines'
        END as ARRONDISSEMENT,
        ROW_NUMBER() over(partition by URL , HOTEL, NOTE, TYPE_ROOMS, DUREE_SEJOUR, ANNEE_SEJOUR, TYPE_VOYAGEUR, NATIONALITE,
        DATE_COMMENTAIRE, TITRE_COMMENTAIRE, COMMENTAIRE order by URL , HOTEL, NOTE, TYPE_ROOMS, DUREE_SEJOUR, ANNEE_SEJOUR, TYPE_VOYAGEUR, NATIONALITE,
        DATE_COMMENTAIRE, TITRE_COMMENTAIRE, COMMENTAIRE) as row_num
        FROM dbo.booking_avis_IDF a LEFT JOIN dbo.Booking2021 b
        ON (a.URL = b.URL_)
        )

        select *  from raw_data
        where row_num =1 and YEAR_ = {}'''.format(year)

        #result = pd.read_sql(query,cnxn)
        cursor.execute(query)
        tables = cursor.fetchall()
        df=pd.DataFrame(result)
        df.to_excel("Booking_Avis_{}.xlsx".format(year),sheet_name='Avis')

    except Exception as e :
        print(e)
