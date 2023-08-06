from tools_pointage.support import support as sp
from tools_pointage.supply_updater import hotels as ho
from customsearch_tools import geocode as gc
import os
import glob
import time
from tqdm.notebook import tqdm
import numpy as np
import pandas as pd
import jellyfish
import json

class branding():
    """
    Classe permettant d'attribuer le nom d'une chaine d'hôtel à un 
    hotel (ligne d'un csv) si le nom de la chaine est contenu dans
    le nom de l'hôtel
    
    Arguments:
        x : String : Nom de l'hôtel
        x : String : Nom de la chaine
        
    Renvoit: Null
        Permet de flagger les hôtels par enseigne
    """
    def __init__(self,x,y):
        self.candidates=x
        self.name=y
        self.brand=None
        for z in self.candidates:
            if z.lower() in self.name.lower():
                self.brand=z

def flag(s1,s2):
    """
    Fonction permettant de verifier la similarité entre
    le nom originel d l'hôtel et le nom trouvé sur internet pour
    fusionner les informations
    
    Arguments:
        s1 : String : Nom originel (sur le site de la chaine) de l'hôtel
        s2 : String : Nom de l'hôtel trouvé sur internet via google
        
    Renvoit: Integer ou "NaN"
        Si la similarité est assez élevée, renvoit 1, 0 sinon
    """
    try:
        if jellyfish.jaro_winkler_similarity(s1,s2) > 0.7:
            return 1
        else:
            return 0
    except:
        return "NaN"

def fusion(filename, brands, api,mode=0, fill_blank=False, force_fill=0, force_country=''):
    """
    Fonction permettant de fusionner les données du csv obtenu
    via crawl du site avec les donnée du csv obtenu via le pointage 
    automatique avec google pour completer les informations des hôtels manquants.
    La fusion se fait sur la base du nom de l'hôtel
    
    Arguments:
        filename : String : Nom à donner au fichier de sortie
        brands : List : Liste de nom de chaines d'hôtels à flagger via le nom des hôtels
        mode : Integer 0 ou 1 : Si le csv originel ne contient que les noms des hôtels utiliser 1
        fill_blank : Boolean : A utiliser si on veut remplir automatiquement les données manquantes
        force_fill : Integer : Nombre de chambres a utiliser pour les hotels ou l'info n'est pas disponible
        force_country : String : Nom du Pays a utiliser par defaut si la geolocalisation n'a pas fonctionné
        
        
    Renvoit: Fichiers CSV et EXCEL contenant les données fusionnées 
    """

    if mode==0:
        result = glob.glob('*.csv')
        temp_result=[x for x in result if 'hotels16' not in x and 'final_' not in x]
        main_csv=temp_result[0]
        temp_result=[x for x in result if 'hotels16' in x]
        alter_csv=temp_result[0]
        main_pandas=sp.pd.read_csv(main_csv,sep='\t',encoding='utf-8')
        alter_pandas=sp.pd.read_csv(alter_csv,sep='\t',encoding='utf-8')
        alter_pandas=alter_pandas.rename(columns={'Hotel Name':'nom'})
        main_pandas['nom'] = main_pandas['nom'].astype(str)
        alter_pandas['nom'] = alter_pandas['nom'].astype(str)
        main_pandas['nom']= main_pandas['nom'].str.strip()
        alter_pandas['nom']= alter_pandas['nom'].str.strip()
        final_pandas=main_pandas.merge(alter_pandas, on='nom',how='left')
        final_pandas.capacité.fillna(final_pandas.Capacities, inplace=True)
        final_pandas.etoiles.fillna(final_pandas.stars, inplace=True)


        del final_pandas['Capacities']
        del final_pandas['stars']
        final_pandas=final_pandas.rename(columns={'url_x':'url_original'})
        final_pandas=final_pandas.rename(columns={'webname':'external_name'})
        final_pandas=final_pandas.rename(columns={'address':'external_adresse'})
        final_pandas=final_pandas.rename(columns={'url_y':'external_url'})
        final_pandas['adress'].fillna(final_pandas['external_adresse'],inplace=True)
        final_pandas['adress'] = final_pandas['adress'].astype(str)
        #final_pandas['adress'] = final_pandas['adress'].astype(str)

        brand_pandas=final_pandas['nom']
        brand_pandas=brand_pandas.to_frame()
        brand_pandas['BRAND'] = brand_pandas.apply(lambda x: branding(brands,x['nom']).brand, axis=1)

        final_pandas=final_pandas.merge(brand_pandas, on='nom',how='left')

        geo_pandas=final_pandas['adress']
        geo_pandas=geo_pandas.to_frame()
        geo_pandas = geo_pandas[geo_pandas.adress.notnull()]
        geo_pandas = geo_pandas[geo_pandas['adress']!='nan']

        factors=[]
        number=len(geo_pandas.index)
        for whole_number in range(1, number + 1):
            if number % whole_number == 0:
                factors.append(whole_number)

        filtered=[x for x in factors if (number/x)<=10]
        chunk=min(filtered)
        geo_list = np.vsplit(geo_pandas, chunk)
        print('Fetching location data...')
        for a_data in tqdm(geo_list):
            time.sleep(1)
            a_data['data'] = a_data.apply(lambda x: gc.searcher(x['adress'],api).data, axis=1)
        geo_pandas=pd.concat(geo_list,ignore_index=True)



        geo_pandas['street_number'] = geo_pandas.apply(lambda x: gc.parser(x['data']).number, axis=1)
        geo_pandas['route'] = geo_pandas.apply(lambda x: gc.parser(x['data']).route, axis=1)
        geo_pandas['neighborhood'] = geo_pandas.apply(lambda x: gc.parser(x['data']).neighbourhood, axis=1)
        geo_pandas['locality'] = geo_pandas.apply(lambda x: gc.parser(x['data']).administrative_area, axis=1)
        geo_pandas['aa2'] = geo_pandas.apply(lambda x: gc.parser(x['data']).region, axis=1)
        geo_pandas['aa1'] = geo_pandas.apply(lambda x: gc.parser(x['data']).region_code, axis=1)
        geo_pandas['country'] = geo_pandas.apply(lambda x: gc.parser(x['data']).country, axis=1)
        geo_pandas['country_code'] = geo_pandas.apply(lambda x: gc.parser(x['data']).country_code, axis=1)
        geo_pandas['code_postal'] = geo_pandas.apply(lambda x: gc.parser(x['data']).postal_code, axis=1)
        geo_pandas['lat'] = geo_pandas.apply(lambda x: gc.parser(x['data']).latitude, axis=1)
        geo_pandas['lng'] = geo_pandas.apply(lambda x: gc.parser(x['data']).longitude, axis=1)
        geo_pandas['formatted_address'] = geo_pandas.apply(lambda x: gc.parser(x['data']).label, axis=1)
        geo_pandas['UE'] = geo_pandas.apply(lambda x: gc.parser(x['data']).ue, axis=1)
        del geo_pandas['data']

        final_pandas2=final_pandas.merge(geo_pandas, on='adress',how='left')
        final_pandas2=final_pandas2.drop_duplicates('url_original')
        final_pandas2=final_pandas2.reset_index(drop=True)
        #final_pandas2['flag_pointage'] = final_pandas2.apply(lambda x: flag(x['nom'], x['external_name']) , axis=1 )

        def fillbrand(x):
            if x is None:
                return 'NO BRAND'
            else:
                return x

        final_pandas2['BRAND'] = final_pandas2.apply(lambda x: fillbrand(x['BRAND']), axis = 1)

        def fillcountry(x):
            if x=='' or x=='NaN':
                return 'COUNTRY NOT FOUND'
            else:
                return x
        final_pandas2['country'] = final_pandas2.apply(lambda x: fillcountry(x['country']), axis = 1)
        if force_country=='':
            final_pandas2['country'].fillna("COUNTRY NOT FOUND", inplace=True)
        else:
            final_pandas2['country'].fillna(force_country, inplace=True)
        final_pandas2['UE'].fillna("NA", inplace=True)


        filenamexlsx='final_'+filename+'.xlsx'
        filenamecsv='final_'+filename+'.csv'

        final_pandas2.reset_index(drop=True)

        if fill_blank == True:
            if force_fill>0:
                final_pandas2['fill_na'] = np.where(final_pandas['capacité'].notna(), 0, 1)
                final_pandas2['capacité'].fillna(force_fill, inplace=True)
                final_pandas2['capacité']=final_pandas2['capacité'].apply(np.floor)

            else:

                final_pandas2['fill_na'] = np.where(final_pandas['capacité'].notna(), 0, 1)
                final_pandas2['capacité'].fillna((final_pandas2['capacité'].mean()), inplace=True)
                final_pandas2['capacité']=final_pandas2['capacité'].apply(np.floor)

        writer = pd.ExcelWriter(filenamexlsx)

        table = pd.pivot_table(final_pandas2, values=['capacité'], index=['BRAND'], columns=['UE','country'],
                    aggfunc=[np.count_nonzero, np.sum], fill_value=0, margins = True )

        table.to_excel(writer,sheet_name='Summary')

        final_pandas2.to_excel(writer, na_rep='', index=False, sheet_name='DATA')
        final_pandas2.to_csv(filenamecsv, sep='\t',na_rep='', index=False)
        writer.save()


    if mode==1:
        result = glob.glob('*.csv')
        #temp_result=[x for x in result if 'hotels16' not in x and 'final_' not in x]
        #main_csv=temp_result[0]
        temp_result=[x for x in result if 'hotels16' in x]
        alter_csv=temp_result[0]
        #main_pandas=sp.pd.read_csv(main_csv,sep='\t',encoding='utf-8')
        alter_pandas=sp.pd.read_csv(alter_csv,sep='\t',encoding='utf-8')
        alter_pandas=alter_pandas.rename(columns={'Hotel Name':'nom'})
        #main_pandas['nom'] = main_pandas['nom'].astype(str)
        alter_pandas['nom'] = alter_pandas['nom'].astype(str)
        #main_pandas['nom']= main_pandas['nom'].str.strip()
        alter_pandas['nom']= alter_pandas['nom'].str.strip()
        final_pandas=alter_pandas.drop_duplicates('nom')
        #final_pandas.capacité.fillna(final_pandas.Capacities, inplace=True)
        #final_pandas.etoiles.fillna(final_pandas.stars, inplace=True)


        #del final_pandas['Capacities']
        #del final_pandas['stars']

        #final_pandas=final_pandas.rename(columns={'url_x':'url_original'})
        final_pandas=final_pandas.rename(columns={'Capacities':'capacité'})
        final_pandas=final_pandas.rename(columns={'webname':'external_name'})
        final_pandas=final_pandas.rename(columns={'webname':'external_name'})
        final_pandas=final_pandas.rename(columns={'address':'external_adresse'})
        final_pandas=final_pandas.rename(columns={'url':'external_url'})
        #final_pandas['adress'].fillna(final_pandas['external_adresse'],inplace=True)
        final_pandas['external_adresse'] = final_pandas['external_adresse'].astype(str)
        #final_pandas['adress'] = final_pandas['adress'].astype(str)

        brand_pandas=final_pandas['nom']
        brand_pandas=brand_pandas.to_frame()
        brand_pandas['BRAND'] = brand_pandas.apply(lambda x: branding(brands,x['nom']).brand, axis=1)

        final_pandas=final_pandas.merge(brand_pandas, on='nom',how='left')

        geo_pandas=final_pandas['external_adresse']
        geo_pandas=geo_pandas.to_frame()
        geo_pandas = geo_pandas[geo_pandas.external_adresse.notnull()]
        geo_pandas = geo_pandas[geo_pandas['external_adresse']!='nan']


        factors=[]
        number=len(geo_pandas.index)
        for whole_number in range(1, number + 1):
            if number % whole_number == 0:
                factors.append(whole_number)

        filtered=[x for x in factors if (number/x)<=10]
        chunk=min(filtered)
        geo_list = np.vsplit(geo_pandas, chunk)
        print('Fetching location data...')
        for a_data in tqdm(geo_list):
            time.sleep(1)
            a_data['data'] = a_data.apply(lambda x: gc.searcher(x['external_adresse'],api).data, axis=1)
        geo_pandas=pd.concat(geo_list,ignore_index=True)



        geo_pandas['street_number'] = geo_pandas.apply(lambda x: gc.parser(x['data']).number, axis=1)
        geo_pandas['route'] = geo_pandas.apply(lambda x: gc.parser(x['data']).route, axis=1)
        geo_pandas['neighborhood'] = geo_pandas.apply(lambda x: gc.parser(x['data']).neighbourhood, axis=1)
        geo_pandas['locality'] = geo_pandas.apply(lambda x: gc.parser(x['data']).administrative_area, axis=1)
        geo_pandas['aa2'] = geo_pandas.apply(lambda x: gc.parser(x['data']).region, axis=1)
        geo_pandas['aa1'] = geo_pandas.apply(lambda x: gc.parser(x['data']).region_code, axis=1)
        geo_pandas['country'] = geo_pandas.apply(lambda x: gc.parser(x['data']).country, axis=1)
        geo_pandas['country_code'] = geo_pandas.apply(lambda x: gc.parser(x['data']).country_code, axis=1)
        geo_pandas['code_postal'] = geo_pandas.apply(lambda x: gc.parser(x['data']).postal_code, axis=1)
        geo_pandas['lat'] = geo_pandas.apply(lambda x: gc.parser(x['data']).latitude, axis=1)
        geo_pandas['lng'] = geo_pandas.apply(lambda x: gc.parser(x['data']).longitude, axis=1)
        geo_pandas['formatted_address'] = geo_pandas.apply(lambda x: gc.parser(x['data']).label, axis=1)
        geo_pandas['UE'] = geo_pandas.apply(lambda x: gc.parser(x['data']).ue, axis=1)
        del geo_pandas['data']

        final_pandas2=final_pandas.merge(geo_pandas, on='external_adresse',how='left')
        final_pandas2=final_pandas2.drop_duplicates('nom')
        final_pandas2=final_pandas2.reset_index(drop=True)
        #final_pandas2['flag_pointage'] = final_pandas2.apply(lambda x: flag(x['nom'], x['external_name']) , axis=1 )



        def fillbrand(x):
            if x is None:
                return 'NO BRAND'
            else:
                return x

        final_pandas2['BRAND'] = final_pandas2.apply(lambda x: fillbrand(x['BRAND']), axis = 1)

        def fillcountry(x):
            if x=='' or x=='NaN':
                return 'COUNTRY NOT FOUND'
            else:
                return x
        final_pandas2['country'] = final_pandas2.apply(lambda x: fillcountry(x['country']), axis = 1)
        if force_country=='':
            final_pandas2['country'].fillna("COUNTRY NOT FOUND", inplace=True)
        else:
            final_pandas2['country'].fillna(force_country, inplace=True)
        final_pandas2['UE'].fillna("NA", inplace=True)

        filenamexlsx='final_'+filename+'.xlsx'
        filenamecsv='final_'+filename+'.csv'

        writer = pd.ExcelWriter(filenamexlsx)

        final_pandas2.reset_index(drop=True)

        if fill_blank == True:
            if force_fill>0:
                final_pandas2['fill_na'] = np.where(final_pandas['capacité'].notna(), 0, 1)
                final_pandas2['capacité'].fillna(force_fill, inplace=True)
                final_pandas2['capacité']=final_pandas2['capacité'].apply(np.floor)

            else:

                final_pandas2['fill_na'] = np.where(final_pandas['capacité'].notna(), 0, 1)
                final_pandas2['capacité'].fillna((final_pandas2['capacité'].mean()), inplace=True)
                final_pandas2['capacité']=final_pandas2['capacité'].apply(np.floor)

        writer = pd.ExcelWriter(filenamexlsx)

        table = pd.pivot_table(final_pandas2, values=['capacité'], index=['BRAND'], columns=['UE','country'],
                    aggfunc=[np.count_nonzero, np.sum], fill_value=0, margins = True )

        table.to_excel(writer,sheet_name='Summary')

        final_pandas2.to_excel(writer, na_rep='', index=False, sheet_name='DATA')
        final_pandas2.to_csv(filenamecsv, sep='\t',na_rep='', index=False)
        writer.save()
