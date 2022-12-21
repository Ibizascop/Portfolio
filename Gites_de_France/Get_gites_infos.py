import os
import time
import re
import random
import concurrent.futures
import warnings
import datetime
import pandas as pd
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium.webdriver.chrome.service import Service

from tqdm.notebook import tqdm

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor, as_completed

def loop(url) :
    #Driver
    try :
        chrome_options = Options()
        ua = UserAgent()
        userAgent = ua.random
        chrome_options.add_argument(f'user-agent={userAgent}')
        path = r"C:\Cours\Python\chromedriver_win32\chromedriver.exe"
        chrome_options.add_argument("--headless")
        chrome = webdriver.Chrome(executable_path= path ,options=chrome_options)
        chrome.maximize_window()
    except:
        ua = UserAgent()
        userAgent = ua.random
        chrome_options.add_argument(f'user-agent={userAgent}')
        path = r"C:\Users\w.grasina\OneDrive - Adelphon\Bureau\TRAVAUX\Crawls\chromedriver.exe"
        chrome_options.add_argument("--headless")
        chrome = webdriver.Chrome(executable_path= path ,options=chrome_options)
        chrome.maximize_window()
    try :
        url_gite = url.split("\t")[1]
        chrome.get(url_gite)
        time.sleep(1)
        #Popup
        try :
            btn = chrome.find_element(By.XPATH,'//*[@id="onetrust-accept-btn-handler"]')
            chrome.execute_script("arguments[0].scrollIntoView();", btn)
            chrome.execute_script("arguments[0].click();",btn)
            time.sleep(0.5)
        except:
            pass
        
        lecture_nom = chrome.find_element(By.CSS_SELECTOR,"h1[class='g2f-accommodationHeader-title']") 
        try :
            nom = lecture_nom.text
        except :
            nom=""

        lecture_code = chrome.find_element(By.CSS_SELECTOR,"p[class='g2f-accommodationHeader-detail']")
        try :
            code = lecture_code.find_element(By.TAG_NAME,"span").text
            code = code.split("Ref : ")[1]
        except:
            code =""

        try :
            lecture_type = chrome.find_element(By.CSS_SELECTOR,"a[class='g2f-breadcrumb-link']")
            type_ = lecture_type.text
            type_ = type_.split("Location ")[1].split(" ")[0]
        except:
            try :
                lecture_type = chrome.find_element(By.CSS_SELECTOR,"h3[class='g2f-accommodationHeader-type']")
                type_ = lecture_type.text
                type_ = type_.split(" - ")[0]
            except:
                type_ = ""
        #2. Avec la description du nom, cherche un nom
        lecture_adrs = chrome.find_element(By.CSS_SELECTOR,"p[class='g2f-accommodationHeader-detail']") 
        try :
            adrs = lecture_adrs.text
            ville = adrs.split("| à ")[1].split("- ")[0]
            ville=' '.join(ville.replace('\n',' ').split())
            dep = adrs.split("| à ")[1].split("- ")[1]
            dep=' '.join(dep.replace('\n',' ').split())
        except :
            ville=""
            dep =""


        #3. Avec la description des adresses, cherche une adresse
        try :
            #Gites
            lecture_etoiles = chrome.find_element(By.CSS_SELECTOR,"ul[class='g2f-levelEpis--big gite g2f-levelEpis']") 
            lecture_etoiles = lecture_etoiles.find_elements(By.TAG_NAME,"li")
            etoiles = len(lecture_etoiles)
        except :
            try :
                #Chambres hotes
                lecture_etoiles = chrome.find_element(By.CSS_SELECTOR,"ul[class='g2f-levelEpis--big chambre g2f-levelEpis']") 
                lecture_etoiles = lecture_etoiles.find_elements(By.TAG_NAME,"li")
                etoiles = len(lecture_etoiles)
            except :
                try :
                    #Camping
                    lecture_etoiles = chrome.find_element(By.CSS_SELECTOR,"ul[class='g2f-levelEpis--big camping g2f-levelEpis']") 
                    lecture_etoiles = lecture_etoiles.find_elements(By.TAG_NAME,"li")
                    etoiles = len(lecture_etoiles)
                except :
                    try :
                        #City Break
                        lecture_etoiles = chrome.find_element(By.CSS_SELECTOR,"div[class='g2f-cartouche g2f-cartouche-citybreak']") 
                        etoiles = lecture_etoiles.text
                    except :
                        etoiles=""


        #4. Avec la description des étoiles, cherche les icônes qui répresentent les étoiles
        try :
            lecture_rooms = chrome.find_element(By.CSS_SELECTOR,"li[class='room']") 
            lecture_rooms = lecture_rooms.find_element(By.CSS_SELECTOR,"span[class='capacity-value']")
            rooms = lecture_rooms.text
        except :
            rooms=""
        try:
            lecture_capa= chrome.find_element(By.CSS_SELECTOR,"li[class='people']") 
            lecture_capa = lecture_capa.find_element(By.CSS_SELECTOR,"span[class='capacity-value']")
            capa = lecture_capa.text
        except :
            capa=""

        try:
            lecture_surface= chrome.find_element(By.CSS_SELECTOR,"li[class='surface']") 
            lecture_surface = lecture_surface.find_element(By.CSS_SELECTOR,"span[class='capacity-value']")
            surface = lecture_surface.text
        except :
            surface=""
        try :
            lecture_carte= chrome.find_element(By.CSS_SELECTOR,"div[id='map-accommodation']") 
            try :
                lat = lecture_carte.get_attribute("data-lat")
            except :
                lat=""
            try :
                long = lecture_carte.get_attribute("data-lng")
            except :
                long=""
        except:
            lat =""
            long=""

        try:
            lecture_prix = chrome.find_element(By.CSS_SELECTOR,"strong[class='g2f-accommodationSticky-price--datesPrice g2f--tt-3']")
            prix = lecture_prix.text.replace(" €","").replace(",",".")
        except:
            prix=''

        try :
            lecture_date = chrome.find_element(By.CSS_SELECTOR,"div[class='g2f-contactCard-profil u-display--flex']")
            date = re.search("(\d+)",lecture_date.text).group()
        except:
            date = ""
        #5. Avec la description des chambres, cherche les icônes qui répresentent les chambres

        #6. ESSAIE (try) d'afficher sous format texte, l'url, le premier nom trouvé, la premier adresse trouvée, 
        # le nombre d'icônes correspondants aux étoiles, le premier match des chiffres qui précedent le mot "habitaciones".
        # SI CELA N'EST PAS POSSIBLE (except), affiche que les urls, et met des vides dans les autres colonnes.
        try:
            result=(url_gite+'\t'+ str(code)+'\t'+ str(type_)+'\t'+ str(nom)+ '\t'+ str(ville)+ '\t'+ str(dep)
                    + '\t' +str(etoiles)+'\t'+ str(rooms)+ '\t'+ str(surface)+ '\t'+ str(capa)
                    + '\t' +str(lat)+ '\t' +str(long)+ '\t' +str(date))
            with open('Gites_de_France.csv','a',encoding ="utf-8") as fhandle:
                print(result,file=fhandle)
        except :
            exception=(url_gite+'\t'+ ""+'\t'+ ""+'\t'+ ""+ '\t'+ ""+ '\t'+ ""+ '\t' +""
                    +'\t'+ ""+ '\t'+ ""+ '\t'+ ""+ '\t' +""+ '\t' +""+ '\t' +"")
            with open('Gites_de_France.csv','a',encoding = "utf-8") as fhandle:
                    print(exception,filea=fhandle)  

            chrome.quit()
    except:
        chrome.quit()

#Get regions urls

with open(r"urls.txt","r") as liste_urls :
    gites_urls = liste_urls.readlines()
    gites_urls = [url.replace("\n","") for url in gites_urls]
gites_urls = gites_urls[1:]

try :
    with open("completed.txt") as log :
        done_urls = log.readlines()
        done_urls = [url.replace("\n","").replace(" page is completed","").replace("'","").replace("\\t","\t")
                    for url in done_urls]
except:
    done_urls = []
gites_urls = [url for url in gites_urls if url not in done_urls] 

#with open('Gites_de_France.csv','w',encoding ="utf-8") as fhandle:
    #print('url\tcode\ttype\tnom\tadrs\tDépartement\tetoiles\trooms\tsurface-(m²)\tpersonnes\tlat\tlong\tdate',file=fhandle)
    
#Multithreading
def main() :
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
       	future_to_url = {executor.submit(loop, url): url for url in gites_urls}
       	for future in tqdm(concurrent.futures.as_completed(future_to_url),total=len(future_to_url)):
       		url = future_to_url[future]
       		try:
       			data = future.result()
       		except Exception as exc:
       			with open('exception.txt',"a") as flog:
       				print('%r generated an exception: %s' % (url, exc),file=flog)
       		else:
       			with open('completed.txt',"a") as flog:
       				print('%r page is completed' % url,file=flog)
                     
if __name__ == "__main__":
    main()    