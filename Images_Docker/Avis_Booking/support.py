#Changement test pour tutoriel
#Test de modification
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as soup
import time
import requests
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
from IPython.display import Image
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import glob
import csv
from xlsxwriter.workbook import Workbook
import pandas as pd
from IPython.display import display
import re
from urllib.parse import quote
import random
import gzip
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

current_path=os.getcwd()

'''
# List of user agents (for req2)
for x in sys.path:
    try:
        with gzip.open(x+'/pointage/user_agents.txt.gz','rb') as f:
            user_agents=f.readlines()
            break
    except:
        pass
user_agents=[x.decode('utf-8').strip() for x in user_agents]
'''


#Define proxies

http_proxy  = "ADD PROXY"
https_proxy = "ADD PROXY"
ftp_proxy   = "ADD PROXY"

proxyDict = {
              "http"  : http_proxy,
              "https" : https_proxy,
              "ftp"   : ftp_proxy
            }

#Define requests function
def req_simple(x):
    global page
    page=requests.get(x)


#Define requests function
def req(x):
    global page
    page=requests.get(x,proxies=proxyDict,verify=False)

#Define requests function
def req2(x):
    global page
    default_user='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    try:
        user_agent=random.choice(user_agents)
    except:
        user_agent=default_user
    headers = {'User-Agent': user_agent}
    page=requests.get(x,proxies=proxyDict,verify=False,headers=headers)





def help():

    print( '''
open_session() : Ouvre une nouvelle séance de chrome avec une nouvelle adresse IP

close_session() : Fermer la session avant de reouvrir une nouvelle avec une nouvelle adresse IP (économise des ressources)

change(x) : Aller sur le site x avec une séance ouvert de chrome. Ex: change('https://www.google.com/') pour aller à Google.

data(): Lire le code html tel comme il est présenté dans le navigateur virtuel.

scroll(): Aller à la fin de la page.

screnshoot(x): Sauvegarder une capture d'écran du navigateur avec l'image x. Ex: screenshot('test.png')

screen(): Sauvegarder une capture d'écran du navigateur sous le nom 'browser.png'

scrape(x,y): Trouver tous les éléments avec les identifiants html x et y. Ex: identifiant= h2 class="mb0" -> x='h2' ; y={'class':'mb0'}. Le data scrape s'effectue quand la fonction .now() est appellée.

printext(x): Imprimer le texte trouvé sur la console

geturls(x): Capturer les urls dans le récipient html specifié par scrape dans une liste appellée urls.

printhtml(x): Imprimer le code html de tous les récipients qui s'allignent avec la définition donnée par scrape.

connect_ctrip(): Permet de se connecter et d'activer le slider sur Ctrip. Si le captcha apparait, il faut fermer et relancer le navigateur
            ''')


def image(x):
    Image(filename=x)

def open_session_firefox(headless=True):
    global browser
    PROXY="ADD PROXY"
    webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
    "httpProxy": PROXY,
    "sslProxy": PROXY,
    "proxyType": "MANUAL",
    }
    options = FirefoxOptions()
    options.add_argument('--proxy-server=%s' % PROXY)
    if headless == True :
    	options.add_argument("--headless")
    options.add_argument("--window-size=1024x5000")
    #options.add_argument('start-maximized')
    profile = webdriver.FirefoxProfile()
    #profile.add_extension(current_path+"/disable_webrtc-1.0.23-an+fx.xpi")
    #profile.add_extension(current_path+"/adblock_for_firefox-4.24.1-fx.xpi")
    #profile.add_extension(current_path+"/image_block-5.0-fx.xpi")
    #profile.add_extension(current_path+"/ublock_origin-1.31.0-an+fx.xpi")
    profile.DEFAULT_PREFERENCES['frozen']["media.peerconnection.enabled" ] = False
    profile.set_preference("media.peerconnection.enabled", False)
    #profile.set_preference("permissions.default.image", 2)
    profile.update_preferences()
    browser = webdriver.Firefox(profile,options=options)
    #browser.install_addon(current_path+"/disable_webrtc-1.0.23-an+fx.xpi", temporary=True)
    #browser.install_addon(current_path+"/image_block-5.0-fx.xpi", temporary=True)
    #browser.install_addon(current_path+"/ublock_origin-1.31.0-an+fx.xpi", temporary=True)


def screenshot(x):
    browser.save_screenshot(x)

def screen():
	browser.save_screenshot('browser.png')

def close_session():
    browser.close()

def data():
	global content
	content=browser.page_source
	global sopa
	sopa=soup(content,'html.parser')

def scroll():
	height=0
	height2=1
	while height!=height2:
		height= browser.execute_script("return $(document).height()")
		browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)
		height2 = browser.execute_script("return $(document).height()")
	browser.save_screenshot("endscroll.png")

def change(x):
	browser.get(x)


http_proxy2  = "ADD PROXY"
https_proxy2 = "ADD PROXY"
ftp_proxy2   = "ADD PROXY"

proxyDict2 = {
              "http2"  : http_proxy2,
              "https2" : https_proxy2,
              "ftp2"   : ftp_proxy2
            }


class google_search_site:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.url='https://www.bing.com/search?q='+quote(self.x)+quote(' ')+quote(self.y)
    def request(self):
        global page
        global google_url
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36", 'referer':'https://www.google.com/' }
        http_proxy  = "ADD PROXY"
        https_proxy = "ADD PROXY"
        ftp_proxy   = "ADD PROXY"

        proxyDict = {
                      "http"  : http_proxy,
                      "https" : https_proxy,
                      "ftp"   : ftp_proxy
                    }


        page=requests.get(self.url,proxies=proxyDict,verify=False,headers=headers)
        description=scrape_light('li',{'class':'b_algo'})
        lecture=description.now()
        tempurls=[]
        for link in lecture:
            try:
                tempurls.append(link.h2.a['href'])
            except:
                pass
        final_url=[x for x in tempurls if '//fr' in x]
        try:
            google_url=final_url[0]
        except:
            google_url=""
        return google_url


class google_search_site_trip:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.url='https://www.bing.com/search?q='+quote(self.x)+quote(' ')+quote(self.y)
    def request(self):
        global page
        global google_url
        headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36", 'referer':'https://www.google.com/' }
        http_proxy  = "ADD PROXY"
        https_proxy = "ADD PROXY"
        ftp_proxy   = "ADD PROXY"

        proxyDict = {
                      "http"  : http_proxy,
                      "https" : https_proxy,
                      "ftp"   : ftp_proxy
                    }


        page=requests.get(self.url,proxies=proxyDict,verify=False,headers=headers)
        description=scrape_light('li',{'class':'b_algo'})
        lecture=description.now()
        tempurls=[]
        for link in lecture:
            try:
                tempurls.append(link.h2.a['href'])
            except:
                pass
        final_url=[x for x in tempurls if 'tripadvisor.fr' in x]
        try:
            google_url=final_url[0]
        except:
            google_url=""
        return google_url


class scrape:
    def __init__(self,x,y=None):
        self.x = x
        self.y = y if y is not None else x
    def now(self):
        content=browser.page_source
        sopa=soup(content,'html.parser')
        if self.x==self.y:
            return sopa.findAll(self.x)
        else:
            return sopa.findAll(self.x,self.y)
    def find(self,z):
        treasure=re.compile(z)
        tempfind=[]
        content=browser.page_source
        sopa=soup(content,'html.parser')
        if self.x==self.y:
            nugget=sopa.findAll(self.x)
        else:
            nugget=sopa.findAll(self.x,self.y)
        for a in nugget:
            findings=treasure.findall(a.text)
            tempfind.append(findings)
        return tempfind

class scrape_light:
    def __init__(self,x,y=None):
        self.x = x
        self.y = y if y is not None else x
    def now(self):
        content=page.text
        sopa=soup(content,'html.parser')
        if self.x==self.y:
            return sopa.findAll(self.x)
        else:
            return sopa.findAll(self.x,self.y)
    def find(self,z):
        treasure=re.compile(z)
        tempfind=[]
        content=page.text
        sopa=soup(content,'html.parser')
        if self.x==self.y:
            nugget=sopa.findAll(self.x)
        else:
            nugget=sopa.findAll(self.x,self.y)
        for a in nugget:
            tempfind=treasure.findall(a.text)
            if len(tempfind)==0:
                tempfind.append("")
            #tempfind.append(findings)
        return tempfind

def printext(x):
    for a in x:
        print(a.text.strip())


def geturls(x):
    global urls
    urls=[]
    for a in x:
        try:
            urls.append(a['href'])
        except:
            pass

def alterurls(x,y):
    return list(map(lambda z: y+z,x))

def printhtml(x):
    for a in x:
        print(a)

def excelfy():
    for csvfile in glob.glob(os.path.join('.', '*.csv')):
        df=pd.read_csv(csvfile, sep='\t')
        excelfile=csvfile[:-4] + '.xlsx'
        df.to_excel(excelfile, index = False)
        display(df)

def excelfy_specific(x):
    df=pd.read_csv(x,sep='\t')
    excelfile=x[:-4] + '.xlsx'
    df.to_excel(excelfile, index = False)
    display(df)

def reste_a_pointer(x,y,z):
    if x[-4:]=='.csv':
        df=pd.read_csv(x, sep='\t')
        filtered_df = df[df[z].isnull()]
        filtered_df=filtered_df[~filtered_df[y].isnull()]
        noms = filtered_df[y].tolist()
        with open(x[:-4]+'_a_pointer.txt','w') as f:
            for nom in noms:
                print(str(nom).strip(),file=f)
                print(nom)
    if x[-5:]=='.xlsx':
        df=pd.read_excel(x)
        filtered_df = df[df[z].isnull()]
        filtered_df=filtered_df[~filtered_df[y].isnull()]
        noms = filtered_df[y].tolist()
        with open(x[:-4]+'_a_pointer.txt','w') as f:
            for nom in noms:
                print(str(nom).strip(),file=f)
                print(nom)
                
def connect_ctrip(Id = "ADD CTRIP ID", mdp =  "ADD CTRIP PASSWORK") : 
    #Function to use when Ctrip redirect to a connection page
    #If needed custom id and password can be passed
    try:
        #Selecting text boxes where ID and pwd need to be written
        Id_area = browser.find_element_by_id('nloginname')
        Password_area = browser.find_element_by_id('npwd')
        
        #If slider is in default state (Not slided)
        if  browser.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[1]/div[1]/dl[3]/dd/div[1]/div[4]/span").text =="请按住滑块，拖动到最右" :
            #Inputting ID and PWD
            Id_area.send_keys(Id)
            Password_area.send_keys(mdp)
            
            #Sliding
            print("Attempting to slide")
            time.sleep(2)
            button = browser.find_element_by_class_name("cpt-drop-btn")
            
            #Getting the number of pixel the button need to be slid
            slider_length = browser.find_element_by_xpath('//*[@id="sliderddnormal"]').size["width"]
            button_length = button.size["width"]
            distance_to_slide = int(slider_length) - int(button_length)
            
            #Sliding
            action = ActionChains(browser)
            action.click_and_hold(button).perform()
            action.reset_actions
            action.move_by_offset(distance_to_slide,0).perform()
            time.sleep(1.5)
            
            #Check if button was slid
            if browser.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[1]/div[1]/dl[3]/dd/div[1]/div[3]/div/span").text =="校验成功，通过！" :
                print("Succes")
                pass
            
            #Click on button to connect
            connection_btn =  browser.find_element_by_xpath('//*[@id="nsubmit"]')
            browser.execute_script("arguments[0].scrollIntoView();", connection_btn)
            connection_btn.click()
        
        #If no slider or already done, just connect
        else :
            Id_area.send_keys("ADD CTRIP ID")
            Password_area.send_keys("ADD CTRIP PASSWORD")
    
            connection_btn =  browser.find_element_by_xpath('//*[@id="nsubmit"]')
            browser.execute_script("arguments[0].scrollIntoView();", connection_btn)
            connection_btn.click()
    #If can't connect, notably cause of Captcha, recommended to close and reopen browser
    except:
        print("Could not connect")