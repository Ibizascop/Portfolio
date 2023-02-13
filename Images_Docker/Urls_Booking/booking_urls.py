# -*- coding: utf-8 -*-

# Import modules
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures
import requests
import pandas as pd
import re
import random
import traceback
import time
import os.path
from os import path
import support as sp
from tqdm import tqdm
from random import randint
import datetime
import glob
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psutil
from selenium.common.exceptions import WebDriverException

#Ignore SSL certificate errors
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

#Prepare txt file
timestamp=int(time.time())
filename = "booking_flag_url"+str(timestamp)+".txt"
filename2 = "booking_done_url"+str(timestamp)+".txt"
filename3= "booking_scraped_url"+str(timestamp)+".txt"
filename4="logs"+str(timestamp)+".txt"
filename5="cleanlogs"+str(timestamp)+".txt"

now = datetime.datetime.now()
fhandle = open(filename,"w", encoding="utf-8")
#Print timestamp file 1
print (now.strftime("%Y-%m-%d %H:%M:%S"),file=fhandle)
fhandle.close()
fhandle2 = open(filename2,"w", encoding="utf-8")
#Print timestamp file 2
print (now.strftime("%Y-%m-%d %H:%M:%S"),file=fhandle2)
fhandle2.close()
fhandle3 = open(filename3,"w", encoding="utf-8")
print (now.strftime("%Y-%m-%d %H:%M:%S"),file=fhandle3)
fhandle3.close()
fhandle4 = open(filename4,"w", encoding="utf-8")
print (now.strftime("%Y-%m-%d %H:%M:%S"),file=fhandle4)
fhandle4.close()
fhandle5 = open(filename5,"w", encoding="utf-8")
print (now.strftime("%Y-%m-%d %H:%M:%S"),file=fhandle5)
fhandle5.close()

#Import selection
with open('master_city_url_selection.txt') as fselection:
    url_a_city=fselection.readlines()
url_a_city=list(map(lambda x: x.strip(),url_a_city))

#Generate consolited log file
read_files_logs = glob.glob("cleanlogs1*")
with open("consolidatedlog.txt", "w") as outfile:
    for f in read_files_logs:
        with open(f, "r") as infile:
            outfile.write(infile.read())
            
#Import logs
flogname='consolidatedlog.txt'
with open(flogname) as flogdone:
	done_urls=flogdone.readlines()
done_urls = list(map(lambda x : x.replace("'",""),done_urls))   
done_urls=list(map(lambda x: x.strip(),done_urls))
done_urls=list(map(lambda x: x.replace('\\n',''),done_urls))
done_urls=list(filter(lambda x: 'page is completed' in x, done_urls))
done_urls=list(map(lambda x: x.replace('page is completed',''),done_urls))
done_urls=list(map(lambda x: x.strip(),done_urls))
url_a_city=list(set(url_a_city)-set(done_urls))
url_a_city=sorted(url_a_city)

#Define subfunction
def urlfetch():
    object_=sp.scrape('a',{'class':'e13098a59f'})
    object_=object_.now()
    for a in object_:
        urlhotel= a['href'].strip()
        try:
            urlhotel= urlhotel.split("?")[0]
        except:
            pass
        with open(filename2,'a') as f2:
            f2.write(urlhotel)
            f2.write('\n')
            
# Define main function
def searchcityurl(x):
    try :
        for counter in range(5):
            try:
                time.sleep(2)
                sp.open_session_firefox()
                time.sleep(2)
                sp.change(x)
                time.sleep(2)
                break
            except:
                time.sleep(2)
                sp.browser.quit()
                time.sleep(2)
                '''
                PROCNAME = "geckodriver"
                for proc in psutil.process_iter():
                     if proc.name() == PROCNAME:
                          proc.kill()'''
        #Handle Popup
        time.sleep(1)
        c=sp.browser.find_elements(By.ID,'onetrust-reject-all-handler')
        try:
            c[0].click()
            time.sleep(1)
        except:
            pass
        
        #Search hotels and accomodations
        time.sleep(1)
        a=sp.browser.find_elements(By.CLASS_NAME,'sb-searchbox__button ')
        sp.browser.execute_script("arguments[0].scrollIntoView();", a[0])
        a[0].click()
        time.sleep(1)
        
        #Second Popup
        try:
            c=sp.browser.find_elements(By.ID,'onetrust-accept-all-handler')
            c[0].click()
            time.sleep(1)
        except:
            pass
        
        #Get Number of accomodations in city
        time.sleep(1)
        element_=sp.scrape('h1',{'class':'e1f827110f d3a14d00da'})
        element_=element_.now()
        if len(element_)>0:
            element_=element_[0].text
            element_=element_.replace(' ','').strip()
            try:
                element_=element_.replace('\xa0','').replace(' ','').strip()
            except:
                pass
            element_c=re.findall(r"(\d+)",element_)
            element_c_seuil=int(element_c[0])
        elif len(element_)==0:
            element_=sp.scrape('div',{'class':'d8f77e681c'})
            element_=element_.now()
            element_=element_[0].text
            element_=element_.replace(' ','').strip()
            try:
                element_=element_.replace('\xa0','').replace(' ','').strip()
            except:
                pass
            element_c=re.findall(r"(\d+)Ã©tablissementstrouvÃ©s",element_)
            element_c_seuil=int(element_c[0])
        with open(filename4,"a") as flog:
            print(element_c_seuil," etablissements sur l'url: ",x)
            print(element_c_seuil," etablissements sur l'url: ",x,file=flog)
        
        #Bouton pour naviguer entre les pages
            xpath_page_suivante = '//*[@id="search_results_table"]/div[2]/div/div/div/div[6]/div[2]/nav/div/div[3]/button'
        #1er cas oÃ¹ le nombre d'Ã©tablissement <1000
        if element_c_seuil<=1000:
            with open(filename4,"a") as flog:
                print('Fetching : ',x,file=flog)
            with open(filename3,'a') as f3:
                f3.write(x)
                f3.write('\n')
                
            #1Ã¨re page
            urlfetch()
            time.sleep(1)
            description=sp.scrape('li',{'class':'f32a99c8d1'})
            lecture=description.now()
            
            #Pages suivantes
            if len(lecture)>0:
                max_pages=[]
                for page in lecture:
                    try :
                        max_pages.append(int(re.findall(r'(\d+)',page.text)[0]))
                    except:
                        pass
                    max_page=max(max_pages)
                if max_page>1:
                    for counter_refresh in range(5):
                        try:
                            element = WebDriverWait(sp.browser, 4).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                        except:
                            try:
                                sp.browser.refresh()
                                time.sleep(3)
                                element = WebDriverWait(sp.browser, 4).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                            except:
                                continue
                    try:
                        time.sleep(3)
                        click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                        sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                        sp.browser.execute_script("arguments[0].click();",click_element)
                        time.sleep(2)
                    except:
                        sp.browser.refresh()
                        time.sleep(3)
                        click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                        sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                        sp.browser.execute_script("arguments[0].click();",click_element)
                        time.sleep(2)
                    #Boucle sur les pages suivantes
                    while True:
                        try:
                            url_0=str(sp.browser.current_url)
                            urlfetch()
                            time.sleep(1)
                            timeout = time.time() + 45
                            try:
                                element = WebDriverWait(sp.browser, 4).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                            except:
                                try:
                                    sp.browser.refresh()
                                    element = WebDriverWait(sp.browser, 4).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                except:
                                    break
                            try:
                                time.sleep(3)
                                click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                sp.browser.execute_script("arguments[0].click();",click_element)
                                time.sleep(2)
                            except:
                                sp.browser.refresh()
                                time.sleep(3)
                                click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                sp.browser.execute_script("arguments[0].click();",click_element)
                                time.sleep(2)
                            url_1=str(sp.browser.current_url)
                        except:
                            urlfetch()
                            if len(sp.browser.find_elements(By.XPATH,xpath_page_suivante))>0:
                                raise Exception("Failed at pressing next-page button-Timeout")
                                break
                            else:
                                raise Exception("Failed at pressing next-page button-Button not present...Check for completion")
                                break

                        if url_0==url_1:
                            break

        elif element_c_seuil>1000:
            sp.data()
            listetoiles = []
            try :  
                e1=sp.scrape('div',{'data-filters-item':"class:class=1"})
                se1 = e1.now()[0]
                de1={'label':se1.find("div",{"class":"a1b3f50dcd b2fe1a41c3 a1f3ecff04 db7f07f643 d1764ea78b"}).text.strip(),'count':int(se1.find("span",{"class":"d8eab2cf7f a414c2b280"}).text.strip()),'id':'//input[@name="class=1"]'}
                listetoiles.append(de1)
            except:
                pass
            try :
                e2=sp.scrape('div',{'data-filters-item':"class:class=2"})
                se2 = e2.now()[0]
                de2={'label':se2.find("div",{"class":"a1b3f50dcd b2fe1a41c3 a1f3ecff04 db7f07f643 d1764ea78b"}).text.strip(),'count':int(se2.find("span",{"class":"d8eab2cf7f a414c2b280"}).text.strip()),'id':'//input[@name="class=2"]'}
                listetoiles.append(de2)
            except:
                pass
            try:
                e3=sp.scrape('div',{'data-filters-item':"class:class=3"})
                se3 = e3.now()[0]
                de3={'label':se3.find("div",{"class":"a1b3f50dcd b2fe1a41c3 a1f3ecff04 db7f07f643 d1764ea78b"}).text.strip(),'count':int(se3.find("span",{"class":"d8eab2cf7f a414c2b280"}).text.strip()),'id':'//input[@name="class=3"]'}
                listetoiles.append(de3)
            except:
                pass
            try:
                e4=sp.scrape('div',{'data-filters-item':"class:class=4"})
                se4 = e4.now()[0]
                de4={'label':se4.find("div",{"class":"a1b3f50dcd b2fe1a41c3 a1f3ecff04 db7f07f643 d1764ea78b"}).text.strip(),'count':int(se4.find("span",{"class":"d8eab2cf7f a414c2b280"}).text.strip()),'id':'//input[@name="class=4"]'}
                listetoiles.append(de4)
            except:
                pass
            try:
                e5=sp.scrape('div',{'data-filters-item':"class:class=5"})
                se5 = e5.now()[0]
                de5={'label':se5.find("div",{"class":"a1b3f50dcd b2fe1a41c3 a1f3ecff04 db7f07f643 d1764ea78b"}).text.strip(),'count':int(se5.find("span",{"class":"d8eab2cf7f a414c2b280"}).text.strip()),'id':'//input[@name="class=5"]'}
                listetoiles.append(de5)
            except:
                pass
            try:
                e0=sp.scrape('div',{'data-filters-item':"class:class=0"}) 
                se0 = e0.now()[0]
                de0={'label':se0.find("div",{"class":"a1b3f50dcd b2fe1a41c3 a1f3ecff04 db7f07f643 d1764ea78b"}).text.strip(),'count':int(se0.find("span",{"class":"d8eab2cf7f a414c2b280"}).text.strip()),'id':'//input[@name="class=0"]'}
                listetoiles.append(de0)
            except:
                pass
            base1=sp.browser.current_url
            for z in listetoiles:
                sp.change(base1)
                try :
                    time.sleep(2)
                    sp.data()
                    elem = sp.browser.find_element(By.XPATH,z['id'])
                    sp.browser.execute_script("arguments[0].scrollIntoView();", elem)
                    sp.browser.execute_script("arguments[0].click();", elem)
                    time.sleep(2)
                    if z['count']<=1000:
                        with open(filename4,"a") as flog:
                            options=z['label']
                            print('Fetching : ',x,'with more than 1000 results',options, file=flog)
                        with open(filename3,'a') as f3:
                            f3.write(x)
                            f3.write('\n')
                        urlfetch()
                        time.sleep(1)
                        try:
                            element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                        except:
                            try:
                                sp.browser.refresh()
                                element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                            except:
                                continue
                        try:
                            time.sleep(2)
                            click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                            sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                            sp.browser.execute_script("arguments[0].click();",click_element)
                            time.sleep(2)
                        except:
                            print(traceback.format_exc())
                            browser.refresh()
                            time.sleep(2)
                            click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                            sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                            sp.browser.execute_script("arguments[0].click();",click_element)
                            time.sleep(2)
                        while True:
                            try:
                                url_0=str(sp.browser.current_url)
                                urlfetch()
                                time.sleep(1)
                                timeout = time.time() + 45
                                try:
                                    element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                except:
                                    try:
                                        sp.browser.refresh()
                                        element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                    except:
                                        continue
                                try:
                                    time.sleep(2)
                                    click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                    sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                    sp.browser.execute_script("arguments[0].click();",click_element)
                                    time.sleep(2)
                                except:
                                    browser.refresh()
                                    time.sleep(2)
                                    click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                    sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                    sp.browser.execute_script("arguments[0].click();",click_element)
                                    time.sleep(2)
                                #time.sleep(4)
                                url_1=str(sp.browser.current_url)
                            except:
                                urlfetch()
                                if len(sp.browser.find_elements(By.XPATH,xpath_page_suivante))>0:
                                    raise Exception("Failed at pressing next-page button-Timeout")
                                    break
                                else:
                                    raise Exception("Failed at pressing next-page button-Button not present...Check for completion")
                                    break
                            if url_0==url_1:
                                break
                    if z['count']>1000:
                        sp.data()
                        base2=sp.browser.current_url
                        #Liste deroulantes
                        btns = sp.browser.find_elements_by_css_selector('button[class="fc63351294 a168c6f285 d65b7d20ae a25b1d9e47"]')
                        for btn in btns :
                            try :
                                sp.browser.execute_script("arguments[0].scrollIntoView();", btn)
                                sp.browser.execute_script("arguments[0].click();", btn)
                            except:
                                pass
                        types= sp.browser.find_elements_by_css_selector('div[data-filters-item*="ht_id:ht_id="]')
                        types = [x for x in types if len(x.text) > 0 ]
                        typesh=[]
                        for type_ in types:
                            xpath_type ='//input[@name="{}"]'.format(type_.get_attribute("data-filters-item").split(":")[1])
                            case={'label':type_.text.strip().split("\n")[0],'count':int(type_.text.strip().split("\n")[1]),'id':xpath_type}
                            typesh.append(case)
                        for type_ in typesh:
                            sp.change(base2)
                            time.sleep(2)
                            try :
                                elem_type = sp.browser.find_element(By.XPATH,type_['id'])
                                sp.browser.execute_script("arguments[0].scrollIntoView();", elem_type)
                                sp.browser.execute_script("arguments[0].click();", elem_type)
                                time.sleep(2)
                                if type_['count']<=1000:
                                    with open(filename4,"a") as flog:
                                        options=z['label']+'//'+type_['label']
                                        print('Fetching : ',x,options, file=flog)
                                    with open(filename3,'a') as f3:
                                        f3.write(x)
                                        f3.write('\n')
                                    urlfetch()
                                    time.sleep(1)
                                    try:
                                        element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                    except:
                                        try:
                                            sp.browser.refresh()
                                            element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                        except:
                                            continue
                                    try:
                                        time.sleep(2)
                                        click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                        sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                        sp.browser.execute_script("arguments[0].click();", click_element)
                                        time.sleep(2)
                                    except:
                                        browser.refresh()
                                        time.sleep(2)
                                        click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                        sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                        sp.browser.execute_script("arguments[0].click();", click_element)
                                        time.sleep(2)
                                    while True:
                                        try:
                                            url_0=str(sp.browser.current_url)
                                            urlfetch()
                                            time.sleep(1)
                                            timeout = time.time() + 45
                                            try:
                                                element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                            except:
                                                try:
                                                    sp.browser.refresh()
                                                    element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                                except:
                                                    continue
                                            try:
                                                time.sleep(2)
                                                click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                                sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                                sp.browser.execute_script("arguments[0].click();",click_element)
                                                time.sleep(2)
                                            except:
                                                print(traceback.format_exc())
                                                sp.browser.refresh()
                                                time.sleep(2)
                                                click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                                sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                                sp.browser.execute_script("arguments[0].click();",click_element)
                                                time.sleep(2)
                                            url_1=str(sp.browser.current_url)
                                        except:
                                            urlfetch()
                                            if len(sp.browser.find_elements(By.XPATH,xpath_page_suivante))>0:
                                                raise Exception("Failed at pressing next-page button-Timeout")
                                                break
                                            else:
                                                raise Exception("Failed at pressing next-page button-Button not present...Check for completion")
                                                break
                                        if url_0==url_1:
                                            break
                                if type_['count']>1000:
                                    sp.data()
                                    base3=sp.browser.current_url
                                    #Liste deroulantes
                                    btns = sp.browser.find_elements_by_css_selector('button[class="fc63351294 a168c6f285 d65b7d20ae a25b1d9e47"]')
                                    for btn in btns :
                                        try :
                                            sp.browser.execute_script("arguments[0].scrollIntoView();", btn)
                                            sp.browser.execute_script("arguments[0].click();", btn)
                                        except:
                                            pass

                                    locations= sp.browser.find_elements_by_css_selector('div[data-filters-item*="di:di="]')
                                    locations = [x for x in locations if len(x.text) > 0 ]
                                    time.sleep(1)
                                    districts=[]
                                    for loc in locations:
                                        xpath_district ='//input[@name="{}"]'.format(loc.get_attribute("data-filters-item").split(":")[1])
                                        case2={'label':loc.text.strip().split("\n")[0],'count':int(loc.text.strip().split("\n")[1]),'id':xpath_district}
                                        districts.append(case2)
                                    for district in districts:
                                        #print(base3)
                                        sp.change(base3)
                                        time.sleep(2)
                                        try :
                                            elem_district = sp.browser.find_element(By.XPATH,district['id'])
                                            sp.browser.execute_script("arguments[0].scrollIntoView();", elem_district)
                                            sp.browser.execute_script("arguments[0].click();", elem_district)
                                            time.sleep(2)
                                            if district['count']<=1000:
                                                try:
                                                    with open(filename4,"a") as flog:
                                                        options=z['label']+'//'+type_['label']+'//'+district['label']
                                                        print('Fetching : ',x,options, file=flog)
                                                    with open(filename3,'a') as f3:
                                                        f3.write(x)
                                                        f3.write('\n')
                                                    urlfetch()
                                                    time.sleep(1)
                                                    try:
                                                        element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                                    except:
                                                        try:
                                                            sp.browser.refresh()
                                                            element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                                        except:
                                                            continue
                                                    try:
                                                        time.sleep(2)
                                                        click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                                        sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                                        sp.browser.execute_script("arguments[0].click();",click_element)
                                                        time.sleep(2)
                                                    except:
                                                        print(traceback.format_exc())
                                                        sp.browser.refresh()
                                                        time.sleep(2)
                                                        click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                                        sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                                        sp.browser.execute_script("arguments[0].click();",click_element)
                                                        time.sleep(2)
                                                    while True:
                                                        try:
                                                            url_0=str(sp.browser.current_url)
                                                            urlfetch()
                                                            time.sleep(1)
                                                            timeout = time.time() + 45
                                                            try:
                                                                element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                                            except:
                                                                try:
                                                                    sp.browser.refresh()
                                                                    element = WebDriverWait(sp.browser, 20).until(EC.presence_of_element_located((By.XPATH,xpath_page_suivante)))
                                                                except:
                                                                    continue
                                                            try:
                                                                time.sleep(2)
                                                                click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                                                sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                                                sp.browser.execute_script("arguments[0].click();",click_element)
                                                                time.sleep(2)
                                                            except:
                                                                sp.browser.refresh()
                                                                time.sleep(2)
                                                                click_element=sp.browser.find_element(By.XPATH,xpath_page_suivante)
                                                                sp.browser.execute_script("arguments[0].scrollIntoView();", click_element)
                                                                sp.browser.execute_script("arguments[0].click();",click_element)
                                                                time.sleep(2)
                                                            url_1=str(sp.browser.current_url)
                                                        except:
                                                            urlfetch()
                                                            if len(sp.browser.find_elements(By.XPATH,xpath_page_suivante))>0:
                                                                raise Exception("Failed at pressing next-page button-Timeout")
                                                                break
                                                            else:
                                                                raise Exception("Failed at pressing next-page button-Button not present...Check for completion")
                                                                break
                                                        if url_0==url_1:
                                                            break
                                                except:
                                                    options=z['label']+'//'+type_['label']+'//'+district['label']
                                                    print('Problem with',x,'options:',options)
                                                    continue
                                            if district['count']>1000:
                                                with open(filename4,"a") as flog:
                                                    options=z['label']+'//'+type_['label']+'//'+district['label']
                                                    print('More than 1000 : ',x,options, file=flog)
                                                with open(filename3,'a') as f3:
                                                    f3.write(x)
                                                    f3.write('\n')
                                                continue
                                        except:
                                            pass
                            except:
                                pass
                except :
                    pass
        sp.browser.quit()
        
    except Exception as e:
        sp.browser.quit()
        with open(filename4,"a") as flog:
            print('Did not complete:',x,traceback.format_exc(),file=flog)
            
print('\n','Fetching individual urls...','\n')
with open(filename4,"a") as flog:
    print('\n','Fetching individual urls...','\n',file=flog)

with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
    future_to_url = {executor.submit(searchcityurl, url): url for url in url_a_city}
    for future in tqdm(concurrent.futures.as_completed(future_to_url),total=len(future_to_url)):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            with open(filename4,"a") as flog:
                print('%r generated an exception: %s' % (url, traceback.format_exc()),file=flog)
        else:
            with open(filename5,"a") as flog:
                print('%r page is completed' % url,file=flog)
