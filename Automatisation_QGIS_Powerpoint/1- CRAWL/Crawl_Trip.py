import re
import time
import warnings
import pandas as pd
import concurrent.futures
import random

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor, as_completed

warnings.filterwarnings("ignore", category=DeprecationWarning) 

def loop(url_nom_chaine) :
    """
    Fonction prenant en argument une chaine de caractère composée
    de l'url de chaine Ctrip, par exemple "https://hotels.ctrip.com/brand/h1993/" 
    et du nom de la chaine associée à l'url, ici "Ilunion Hotels". Le tout 
    doit être séparé par un \t.

    A partir de l'url de la chaine, la fonction va se rendre sur l'url,
    recuperer pour chaque ville indiquée par Trip.com, le nombre d'hotels
    de la chaine dans la ville (1*) ainsi que l'url pour accéder aux hotels de la chaine dans la ville

    Une fois les urls des villes récupérés, on se rend sur chaque url de ville 
    et on récupère les urls des hôtels. Etant donné que Trip.com affiche un maximum
    de 30 hôtels par ville, si il ya >30 hotels sur un url, on completera en se basant sur 
    le total récupéré précédement (Cf 1*).

    Une fois les urls Ctrip des hôtels récupérés, on les transforme pour accéder au site
    miroir HKTRIP car plus stable pour obtenir les informations des hôtels et disponible en FR.
    On récupère ensuite les informations comme le nom, l'adresse, les chambres des hôtels ...
    que l'on sauvegarde sur un csv.

    Une fois que tous les urls d'une chaine ont été traités, on le note pour
    ne pas avoir à la relancer

    Arguments:
        url_nom_chaine: String : chaine de caractère composée
    de l'url de chaine Ctrip et de son nom. Par exemple : 
    "https://hotels.ctrip.com/brand/h1993/\tIlunion Hotels"
        
    Renvoit: Données sauvegardée sur un fichier csv
        Données de tous les hôtels de la chaine disponible sur CTRIP/HKTRIP
    """
    time.sleep(random.uniform(1,3))
    url_chaine = url_nom_chaine.split("\t")[0]
    nom_chaine = url_nom_chaine.split("\t")[1]
    #Driver
    chrome_options = Options()
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f"user-agent={userAgent}")
    path = r"DRIVER_PATH"
    #chrome_options.add_argument("--headless")
    chrome = webdriver.Chrome(executable_path = path, options = chrome_options)
    chrome.maximize_window()
    chrome.get(url_chaine)
    
    #Liste Hotels
    final_villes = []
    final_urls = []
    final_nb_hotel = []
    try :
        time.sleep(1)
        lecture_urls = chrome.find_element(By.CSS_SELECTOR,"div[class='tab_bd']")
        lecture_imbrique = lecture_urls.find_elements(By.TAG_NAME,"a")
        
        villes = []
        urls = []
        nb_hotel = []
        
        lecture_imbrique_urls = [url.get_attribute("href") for url in lecture_imbrique]
        lecture_imbrique_villes = [x.text for x in lecture_imbrique]
        lecture_imbrique_nb_hotels = []
        for x in lecture_imbrique : 
            try :
                lecture_imbrique_nb_hotels.append(re.search("(\d+)",x.text).group())
            except:
                lecture_imbrique_nb_hotels.append("")
        
        for i, ville in enumerate(lecture_imbrique_villes) :
            lecture_imbrique_villes[i] = lecture_imbrique_villes[i].replace(lecture_imbrique_nb_hotels[i],"")
        urls.extend(lecture_imbrique_urls)
        villes.extend(lecture_imbrique_villes)
        nb_hotel.extend(lecture_imbrique_nb_hotels)
        
        final_villes.extend(villes)
        final_urls.extend(urls)
        final_nb_hotel.extend(nb_hotel)
    except Exception as e :
        with open("Failed_chaines.txt","a",encoding ="utf-8") as failed:
            print(url_chaine+" =====> "+str(e),file = failed)
        
    #Ajout dans le CSV de verif Villes : Permet de savoir cb d'hotels manquent car Trip affiche max 30 hotels pour 1 ville
    sauvegardes_noms = [nom_chaine for url in final_urls]
    sauvegardes_urls = [url_chaine for url in final_urls]
    dic = {"url_chaine":sauvegardes_urls,"nom_chaine":sauvegardes_noms,"url_ville":final_urls,"nom_ville":final_villes,"nb_hotels":final_nb_hotel}
    df = pd.DataFrame.from_dict(dic)
    df.to_csv("Verif_Villes.csv", mode="a", encoding='utf_8_sig',index=False, header=False,sep = "\t")    

    #Url des Hotels
    lecture_urls = []
    Marques = []
    for i in range(len(dic["url_ville"])) :
        chrome.get(dic["url_ville"][i])
        time.sleep(1.5)

        temp = chrome.find_elements(By.CSS_SELECTOR,"div.list-card-title")
        urls = [url.find_element(By.TAG_NAME,"a").get_attribute("href")
                    for url in temp]
        marques = []
        for k in range(len(urls)) :
            marques.append(dic["url_ville"][i])
        lecture_urls.extend(urls)
        Marques.extend(marques)
    #Sauvegarder urls et marques dans un fichier pour savoir à quelle marque un hotel correspond
    temp_urls = [url.split("/")[-1].split(".")[0] for url in lecture_urls]
    Villes = [url for url in Marques]
    Marques = ["https://hotels.ctrip.com/brand/"+url.split("/")[-1]+"/" for url in Marques]
    dic = {"url_hotel":temp_urls,"marque_hotel":Marques,"ville_hotel":Villes}
    df = pd.DataFrame.from_dict(dic)
    df.to_csv("Verif_Marques.csv", mode="a", encoding='utf_8_sig',index=False, header=False,sep ="\t")    
    
    #Crawl des infos des hotels sur HK TRIP
    for url_ctrip in lecture_urls :
        try :
            id_hotel = re.search("(?<=https://hotels.ctrip.com/hotels/)(.+)(?=.html)",url_ctrip).group()
            url_hktrip = "https://fr.trip.com/hotels/hong+kong-hotel-detail-{}?locale=fr_fr".format(id_hotel)
            chrome.get(url_hktrip)
            time.sleep(2)

            #Popup
            try:
                pop_up = chrome.find_element(By.CSS_SELECTOR,"div[class='m-mask ']")
                chrome.execute_script("arguments[0].scrollIntoView();", pop_up)
                chrome.execute_script("arguments[0].click();",pop_up)
            except:
                pass

            #Nom
            try:
                lecture_nom = chrome.find_element(By.CSS_SELECTOR,"h1[class='detail-headline_name ']")
                nom = lecture_nom.text
                nom=' '.join(nom.replace('\n','').split())
            except:
                try :
                    lecture_nom = chrome.find_element(By.CSS_SELECTOR,"h1[class='detail-headline-v8_name hotelTag-title_h1']")
                    nom = lecture_nom.text
                    nom=' '.join(nom.replace('\n','').split())
                except:
                    try :
                        lecture_nom = chrome.find_element(By.CSS_SELECTOR,"h1[class='detail-headline-v8_name ']")
                        nom = lecture_nom.text
                        nom=' '.join(nom.replace('\n','').split())
                    except:
                        try:
                            lecture_nom = chrome.find_element(By.CSS_SELECTOR,"h1[class='detail-headline_name hotelTag-title_h1']")
                            nom = lecture_nom.text
                            nom=' '.join(nom.replace('\n','').split())
                        except:
                            nom =""

            #Adresse
            try :
                lecture_adrs = chrome.find_element(By.CSS_SELECTOR,"span[class='detail-headline_position_text']")
                adrs = lecture_adrs.text
                adrs=' '.join(adrs.replace('\n','').split())
            except:
                try :
                    lecture_adrs = chrome.find_element(By.CSS_SELECTOR,"span[class='detail-headline-v8_position_text']")
                    adrs = lecture_adrs.text
                    adrs=' '.join(adrs.replace('\n','').split())
                except :
                    adrs =""

            #Etoiles
            try :
                lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_diamond detail-headline_title_level']")
                etoiles = len(lecture_etoiles)
                if etoiles == 0:
                    lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_diamond detail-headline-v8_title_level']")
                    etoiles = len(lecture_etoiles)
                    if etoiles == 0:
                        lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_star detail-headline_title_level']")
                        etoiles = len(lecture_etoiles)
                        if etoiles == 0:
                            lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_star detail-headline-v8_title_level']")
                            etoiles = len(lecture_etoiles)
                            if etoiles == 0:
                                lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_circle detail-headline_title_level']")
                                etoiles = len(lecture_etoiles)
                                if etoiles == 0 :
                                    lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_circle detail-headline-v8_title_level']")
                                    etoiles = len(lecture_etoiles)
                                    if etoiles == 0 :
                                        etoiles =""
            except :
                etoiles =""
            
            #TYPE ETABLISSEMENT
            try :
                lecture_type = chrome.find_element(By.CSS_SELECTOR,"span[class='m-hotelTag_list_content']")
                type_ = lecture_type.text
                type_=' '.join(type_.replace('\n','').split())
            except:
                type_ =""

            #Note Clients
            try :
                lecture_note = chrome.find_element(By.CSS_SELECTOR,"b[class='detail-headreview_score_value']")
                note = lecture_note.get_attribute('innerHTML')
                note=' '.join(note.replace('\n','').split())
            except:
                try :
                    lecture_note = chrome.find_element(By.CSS_SELECTOR,"b[class='detail-headreview-v8_score_value']")
                    note = lecture_note.get_attribute('innerHTML')
                    note=' '.join(note.replace('\n','').split())
                except:
                    note =""

            #Nb Notes = 
            try:
                lecture_nb_notes = chrome.find_element(By.CSS_SELECTOR,"p[class='detail-headreview_all']")
                nb_notes = lecture_nb_notes.get_attribute("innerHTML").split(" évaluation")[0]
                nb_notes = ' '.join(nb_notes.replace('\n','').split())
            except:
                try :
                    lecture_nb_notes = chrome.find_element(By.CSS_SELECTOR,"span[class='detail-headreview-v8_all']")
                    nb_notes = lecture_nb_notes.get_attribute("innerHTML").split(" évaluation")[0]
                    nb_notes=' '.join(nb_notes.replace('\n','').split())
                except:
                    nb_notes =""

            # Chambres, OUVERTURE , RENOVATION
            try:
                lecture_infos = chrome.find_elements(By.CSS_SELECTOR,"ul[class='basicInfo clearfix']")
                chrome.execute_script("arguments[0].scrollIntoView();",lecture_infos[0])
                x = lecture_infos[0].text
                #Date ouverture
                regex_ouv = r'(?<=Ouvert depuis : )(\d+)'
                try :
                    date_ouverture = re.search(regex_ouv,x).group()
                except:
                    date_ouverture =""

                 #Renovation
                regex_renov = r'(?<=Rénové en : )(\d+)'
                try :
                    date_renovation = re.search(regex_renov,x).group()
                except :
                    date_renovation =""

                #Chambres
                regex_room = r'(?<=Nombre de chambres : )(\d+)'
                try :
                    rooms = re.search(regex_room,x).group()
                except:
                    rooms = ""
            except:
                date_ouverture =""
                date_renovation =""
                rooms =""

            #GPS
            time.sleep(0.1)
            for i in range(3,6) :
                try :
                    json = chrome.find_element(By.XPATH,"/html/body/script[{}]".format(i)).get_attribute('innerHTML')
                    gps = re.search(r'(?<="lat":)(.+)(?=,"poiList")',json).group()
                    gps = gps.replace("'","").replace('"',"").replace("lng:","")
                    lat = gps.split(",")[0]
                    lon = gps.split(",")[1]
                    break
                except:
                    continue
            try:
                result=(url_hktrip+'\t'+ str(nom)+ '\t'+ str(adrs)+ '\t'
                        +str(etoiles)+ '\t' +str(type_)+ '\t' +str(note)+ '\t' 
                        +str(nb_notes)+ '\t'+str(rooms)+ '\t'+str(date_ouverture)+ '\t' 
                        +str(date_renovation)+ '\t'+str(lat)+ '\t' +str(lon))
                with open('Parc_Trip_2023.csv','a',encoding='utf-8') as fhandle:
                    print(result,file=fhandle)
            except :
                exception=(url_hktrip+'\t'+ ""+ '\t'+ ""+ '\t'
                        +""+ '\t' +""+ '\t' +""+ '\t' 
                        +""+ '\t'+""+ '\t'+""+ '\t' 
                        +""+ '\t'+""+ '\t' +"")
                with open('Parc_Trip_2023.csv','a',encoding='utf-8') as fhandle:
                        print(exception,file=fhandle)
        except Exception as e :
            print(e)
            exception=(url_ctrip+'\t'+ ""+ '\t'+ ""+ '\t'
                        +""+ '\t' +""+ '\t' +""+ '\t' 
                        +""+ '\t'+""+ '\t'+""+ '\t' 
                        +""+ '\t'+""+ '\t' +"")
            with open('Parc_Trip_2023.csv','a',encoding='utf-8') as fhandle:
                    print(exception,file=fhandle)
    with open('completed.txt','a',encoding='utf-8') as fhandle:
                    print(url_chaine,file=fhandle)
    chrome.quit()

#Log
try :
    with open("completed.txt","r",encoding ="utf-8") as log:
        done_urls = log.readlines()
        done_urls = [url.replace("\n","") for url in done_urls]
except:
    done_urls = []
    
#Get brand urls and names
with open("Chaines_Ctrip_2023.txt","r", encoding ="utf-8") as file :
    chaines_urls = file.readlines()
chaines_urls = [url.replace("\n","") for url in chaines_urls[1:]]
chaines_urls = [url for url in chaines_urls if url.split("\t")[0] not in done_urls]

#Multithreading
def main() :
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
       	future_to_url = {executor.submit(loop, url_nom): url_nom for url_nom in chaines_urls}
        for future in tqdm(concurrent.futures.as_completed(future_to_url),total=len(future_to_url)):
       		url = future_to_url[future]
       		try:
       			data = future.result()
       		except Exception as exc:
       			with open('exception.txt',"a") as flog:
       				print('%r generated an exception: %s' % (url, exc),file=flog)
       		else:
       			with open('completed.txt',"a") as flog:
       				print(url,file=flog)
                     
if __name__ == "__main__":
    main()        