#Import modules
from bs4 import BeautifulSoup as soup
import time
import os
from tqdm.notebook import tqdm
import concurrent.futures
import requests
import re
import json
import pandas as pd
import datetime
import calendar
from tools_pointage.support import support as sp
from random import randint
from customsearch_tools import customsearch as cs
import jellyfish
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def flag(s1,s2):
    try:
        if jellyfish.jaro_winkler_similarity(s1.upper(),s2.upper()) > 0.5:
            return "OK"
        else:
            return "CHECK"
    except:
        return "NaN"


def pointer(x):
    date = datetime.datetime.utcnow()
    tsx = str(calendar.timegm(date.utctimetuple()))
    namefile='hotels'+'16_fast'+'.csv'
    fhandle=open(namefile,'w', encoding="utf-8")
    headers = ("Hotel Name"+"\t"+'stars'+'\t'+"Capacities" + '\t' + "webname" + '\t' + "address" +'\t'+"url\t"+"check\n")
    fhandle.write(headers)
    fhandle.close()
    lines = open(x, 'r').readlines()
    lines = [x.strip().replace('\n','') for x in lines]
    for url in tqdm(lines) :
        time.sleep(0.5)
        scrape_hotel_info(url)
    
    newname = 'hotels16_fast'+str(tsx)+'.csv'
    df_mapping = pd.DataFrame({'order':lines,})
    sort_mapping = df_mapping.reset_index().set_index('order')
    df = pd.read_csv('hotels16_fast.csv', sep = '\t')
    df['order'] = df['Hotel Name'].map(sort_mapping['index'])
    df.sort_values('order')
    del df['order']
    df.to_csv(newname, sep='\t', index=False)


def scrape_hotel_info(x):
    y='hotels'+'16_fast'+'.csv'
    time.sleep(random.randint(20,50)/10)
    x=x.strip().replace('"','')
    cosito=cs.duck_duck_go_search(x)
    try:
        cosito.request()
    except Exception as e:
        pass

    #1st attempt hotels.com

    #print('checking hotels.com...')
    try:
        url=cosito.hotels
    except:
        url=''

    try:
        try:
            chrome_options = Options()
            path = r"C:\Users\ibiza\Desktop\TRAVAUX\chromedriver_win32\chromedriver.exe"
            chrome_options.add_argument("--headless")
            chrome = webdriver.Chrome(executable_path= path ,options=chrome_options)
            chrome.maximize_window()
            chrome.get(url)
            
            try:
                lecture_chambres = chrome.find_element(By.CSS_SELECTOR,"div[class='uitk-spacing uitk-spacing-margin-blockend-four']")
                chambres = re.search(r'(\d+)',lecture_chambres.text).group()
            except:
                chambres = ''

            try:
                lecture_etoiles=chrome.find_elements(By.CSS_SELECTOR,"svg[class='uitk-icon uitk-rating-icon uitk-icon-xsmall']")
                stars = len(lecture_etoiles)
            except:
                stars=''

            try:
                lecture_name = chrome.find_element(By.CSS_SELECTOR,"h1[class='uitk-heading uitk-heading-3']")
                vname = lecture_name.text
                vname=' '.join(vname.replace('\n','').split())
            except:
                vname = ""

            try:
                lecture_adrs = chrome.find_element(By.CSS_SELECTOR,"div[data-stid='content-hotel-address']")
                adrs = lecture_adrs.text
                adrs=' '.join(adrs.replace('\n','').split())
            except:
                adrs = ""
            chrome.quit()
        except:
            vname=""
            stars=''
            chambres=''
            adrs=''
            chrome.quit()
        #Check if hotels.com returned valid information

        if flag(x,vname)=='OK':

            check = 'OK'
            varlist=[str(x).replace('\t',''),str(stars).replace('\t',''),str(chambres).replace('\t',''),str(vname).replace('\t',''),str(adrs).replace('\t',''),str(url).replace('\t',''), check]
            to_append=varlist
            s = pd.DataFrame(to_append).T
            s.to_csv(y, mode='a', header=False,sep='\t',index=False)
            #time.sleep(1)
            #pbar.update(1)

        else:
            #Second attempt
            #print('checking tripadvisor...')
            #Getting url
            try:
                url=cosito.tripadvisor
            except:
                url=''
            try:
                chrome_options = Options()
                path = r"C:\Users\ibiza\Desktop\TRAVAUX\chromedriver_win32\chromedriver.exe"
                chrome_options.add_argument("--headless")
                chrome = webdriver.Chrome(executable_path= path ,options=chrome_options)
                chrome.maximize_window()
                chrome.get(url)

                try:
                    stars_tripadvisor = chrome.find_element(By.CSS_SELECTOR,"svg[class='UctUV d H0 hzzSG']")
                    stars_tripadvisor = stars_tripadvisor.get_attribute("aria-label")
                    stars = stars_tripadvisor.split(" ")[0]
                except:
                    stars=''
                try:
                    capacity_tripadvisor = chrome.find_elements(By.CSS_SELECTOR,'div[class="IhqAp Ci"]')
                    chambres = capacity_tripadvisor[-1].text
                except:
                    chambres=''
                try:
                    name_tripadvisor=chrome.find_element(By.CSS_SELECTOR,"h1[id='HEADING']")
                    vname = name_tripadvisor.text
                    vname=' '.join(vname.replace('\n','').split())
                except:
                    vname=''
                try:
                    adrs_tripadvisor = chrome.find_element(By.XPATH,'//*[@id="component_34"]/div/div[1]/div[3]/div[1]/div[2]/span[2]/span')
                    adrs = adrs_tripadvisor.text
                    adrs=' '.join(adrs.replace('\n','').split())
                except:
                    adrs=""
                chrome.quit()
            except Exception as ex:
                print(x, 'could not be completed','because of',ex)
                vname=""
                stars=''
                chambres=''
                adrs=''
                chrome.quit()
            #Check if tripadvisor returned valid information

            if flag(x,vname)=='OK':

                check = 'OK'
                varlist=[str(x).replace('\t',''),str(stars).replace('\t',''),str(chambres).replace('\t',''),str(vname).replace('\t',''),str(adrs).replace('\t',''),str(url).replace('\t',''),check]
                to_append=varlist
                s = pd.DataFrame(to_append).T
                s.to_csv(y, mode='a', header=False,sep='\t',index=False)
                #time.sleep(1)
                #pbar.update(1)

            else:
                try:
                    url=cosito.trip
                    if "hotels.ctrip.com/hotels/" in url :
                        id_hotel = re.search("(?<=https://hotels.ctrip.com/hotels/)(.+)(?=.html)",url).group()
                        url = "https://fr.trip.com/hotels/hong+kong-hotel-detail-{}?locale=fr_fr".format(id_hotel)
                except:
                    url=''
                try:
                    #Driver
                    chrome_options = Options()
                    path = r"C:\Users\ibiza\Desktop\TRAVAUX\chromedriver_win32\chromedriver.exe"
                    chrome_options.add_argument("--headless")
                    chrome = webdriver.Chrome(executable_path= path ,options=chrome_options)
                    chrome.maximize_window()
                    chrome.get(url)

                    #Nom
                    try:
                        lecture_nom = chrome.find_element(By.CSS_SELECTOR,"h1[class='detail-headline_name ']")
                        vname = lecture_nom.text
                        vname=' '.join(vname.replace('\n','').split())
                    except:
                        try :
                            lecture_nom = chrome.find_element(By.CSS_SELECTOR,"h1[class='detail-headline-v8_name hotelTag-title_h1']")
                            vname = lecture_nom.text
                            vname=' '.join(vname.replace('\n','').split())
                        except:
                            try :
                                lecture_nom = chrome.find_element(By.CSS_SELECTOR,"h1[class='detail-headline-v8_name ']")
                                vname = lecture_nom.text
                                vname=' '.join(vname.replace('\n','').split())
                            except:
                                try:
                                    lecture_nom = chrome.find_element(By.CSS_SELECTOR,"h1[class='detail-headline_name hotelTag-title_h1']")
                                    vname = lecture_nom.text
                                    vname=' '.join(vname.replace('\n','').split())
                                except:
                                    vname =""
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
                        stars = len(lecture_etoiles)
                        if stars == 0:
                            lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_diamond detail-headline-v8_title_level']")
                            stars = len(lecture_etoiles)
                            if stars == 0:
                                lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_star detail-headline_title_level']")
                                stars = len(lecture_etoiles)
                                if stars == 0:
                                    lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_star detail-headline-v8_title_level']")
                                    stars = len(lecture_etoiles)
                                    if stars == 0:
                                        lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_circle detail-headline_title_level']")
                                        stars = len(lecture_etoiles)
                                        if stars == 0 :
                                            lecture_etoiles = chrome.find_elements(By.CSS_SELECTOR,"i[class='u-icon u-icon-ic_new_circle detail-headline-v8_title_level']")
                                            stars = len(lecture_etoiles)
                                            if stars == 0 :
                                                stars =""
                    except :
                        stars =""
                    # Chambres
                    try:
                        lecture_infos = chrome.find_elements(By.CSS_SELECTOR,"ul[class='basicInfo clearfix']")
                        chrome.execute_script("arguments[0].scrollIntoView();",lecture_infos[0])
                        x = lecture_infos[0].text
                        regex_room = r'(?<=Nombre de chambres : )(\d+)'
                        chambres = re.search(regex_room,x).group()
                    except:
                        chambres = ""

                    chrome.quit()
                except Exception as ex:
                    print(x, 'could not be completed','because of',ex)
                    vname=""
                    stars=''
                    chambres=''
                    adrs=''
                    chrome.quit()
            
                check = 'CHECK'
                varlist=[str(x).replace('\t',''),str(stars).replace('\t',''),str(chambres).replace('\t',''),str(vname).replace('\t',''),str(adrs).replace('\t',''),str(url).replace('\t',''),check]
                to_append=varlist
                s = pd.DataFrame(to_append).T
                s.to_csv(y, mode='a', header=False,sep='\t',index=False)
                #time.sleep(1)
                #pbar.update(1)

    except Exception as ex:
        stars=''
        chambres=''
        vname=''
        adrs=''
        url=''
        print(x, 'could not be completed','because of',ex)
        varlist=[x,stars,chambres,vname,adrs,url]
        to_append=varlist
        s = pd.DataFrame(to_append).T
        s.to_csv(y, mode='a', header=False,sep='\t',index=False)
        #time.sleep(1)
        #pbar.update(1)
