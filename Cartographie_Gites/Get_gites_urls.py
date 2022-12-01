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

def loop(region) :
    #Driver
    chrome_options = Options()
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')
    path = r"C:\Cours\Python\chromedriver_win32\chromedriver.exe"
    chrome_options.add_argument("--headless")
    chrome = webdriver.Chrome(executable_path= path ,options=chrome_options)
    chrome.maximize_window()
    try :
        chrome.get(region)
        time.sleep(1)
        #Popup
        try :
            btn = chrome.find_element(By.XPATH,'//*[@id="onetrust-accept-btn-handler"]')
            chrome.execute_script("arguments[0].scrollIntoView();", btn)
            chrome.execute_script("arguments[0].click();",btn)
            time.sleep(0.5)
        except:
            pass
            
        #Dernière page
        last_page = chrome.find_element(By.CSS_SELECTOR,"li[class='pager__item pager__item--last']")
        num_last_page = int(last_page.find_element(By.TAG_NAME,"a").get_attribute("href").split("page=")[1])

        #1ere page
        urls = chrome.find_elements(By.CSS_SELECTOR,"a[class='g2f-accommodationTile-link']")
        urls = [url.get_attribute("href") for url in urls]
        for url in urls :
            with open("urls.txt","a",encoding ="utf-8") as file:
                print(region+"\t"+url,file=file)
        #Autres pages
        for page in range(1,num_last_page+1) :
            chrome.get(region+"&page={}".format(page))
            time.sleep(1)
            urls = chrome.find_elements(By.CSS_SELECTOR,"a[class='g2f-accommodationTile-link']")
            urls = [url.get_attribute("href") for url in urls]
            for url in urls :
                with open("urls.txt","a",encoding ="utf-8") as file:
                    print(region+"\t"+url,file = file)
        chrome.quit()
    except:
        chrome.quit()

#Get regions urls
with open("urls.txt","w",encoding ="utf-8") as file:
    print("Region\tUrl",file=file)
    
with open(r"Regions.txt","r") as liste_regions :
    regions = liste_regions.readlines()
    regions = [url.replace("\n","") for url in regions]
                
#Multithreading
def main() :
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
       	future_to_url = {executor.submit(loop, url): url for url in regions}
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