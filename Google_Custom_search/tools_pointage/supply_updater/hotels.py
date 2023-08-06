#Import modules
from bs4 import BeautifulSoup as soup
import time
import os
from tqdm.notebook import tqdm
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import concurrent.futures
import requests
import re
import json
import pandas as pd
import datetime
import calendar
import glob
from tools_pointage.support import support as sp
from random import randint
from customsearch_tools import customsearch as cs
import jellyfish
import urllib
import random


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
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(scrape_hotel_info, url): url for url in lines}
        for future in tqdm(concurrent.futures.as_completed(future_to_url),total=len(lines)):
            time.sleep(1.5)
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                with open('exception.txt',"a") as flog:
                    print('%r generated an exception: %s' % (url, exc),file=flog)
            else:
                with open('completed.txt',"a") as flog:
                    print('%r page is completed' % url,file=flog)
    
    newname = 'hotels16_fast'+tsx+'.csv'
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
            sp.req2(url)

            webpage=sp.page.text
            toy_soup2 = soup(webpage, "html.parser")
            gold=toy_soup2.findAll("span")
            
            try:
                lecture_chambres = toy_soup2.find("div",{"class":"uitk-spacing uitk-spacing-margin-blockend-four"})
                chambres = re.search(r'(\d+)',lecture_chambres.get_text()).group()
            except:
                chambres = ''

            lecture_etoiles=toy_soup2.findAll("svg",{"class":"uitk-icon uitk-rating-icon uitk-icon-xsmall"})
            try:
                stars = len(lecture_etoiles)
            except:
                stars=''

            lecture_name = toy_soup2.find("h1",{"class":"uitk-heading uitk-heading-3"})
            try:
                vname = lecture_name.get_text()
            except:
                vname = ""

            lecture_adrs = toy_soup2.find("div",{"itemprop":"address"})
            try:
                adrs = lecture_adrs.get_text().replace('\ue98d','')
            except:
                adrs = ""

        except:
            vname=""
            stars=''
            chambres=''
            adrs=''

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
                sp.req2(url)
                webpage=sp.page.text
                tripadvisor_soup = sp.soup(webpage, "html.parser")
                stars_tripadvisor=tripadvisor_soup.findAll('svg',{'class':'TkRkB d H0'})
                capacity_tripadvisor=tripadvisor_soup.findAll('div',{'id':'ABOUT_TAB'})
                name_tripadvisor=tripadvisor_soup.findAll('h1',{'id':'HEADING'})
                adrs_tripadvisor=tripadvisor_soup.findAll('span',{'class':'ceIOZ yYjkv'})

                try:
                    stars=str(stars_tripadvisor[0]['title']).replace(' sur 5\xa0bulles','')
                except:
                    stars=''
                try:
                    chambres=str(capacity_tripadvisor)
                    roomsy=re.compile('NOMBRE DE CHAMBRES<\/div><div class="cJdpk Ci">(\d+)')
                    chambres=roomsy.findall(chambres)[0]
                except:
                    chambres=''
                try:
                    vname=name_tripadvisor[0].text
                except:
                    vname=''
                try:
                    adrs=adrs_tripadvisor[0].text
                except:
                    adrs=""
            except Exception as ex:
                print(x, 'could not be completed','because of',ex)
                vname=""
                stars=''
                chambres=''
                adrs=''
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
                    sp.req2(url)
                    webpage=sp.page.text
                    trip_soup = sp.soup(webpage, "html.parser")
                    stars_trip=trip_soup.findAll('i',{'class':'u-icon u-icon-ic_new_diamond detail-headline_title_level'})
                    capacity_trip=trip_soup.findAll('ul',{'class':'basicInfo clearfix'})
                    name_trip=trip_soup.findAll('h1',{'class':'detail-headline_name '})
                    adrs_trip=trip_soup.findAll('span',{'class':'detail-headline_position_text'})

                    try:
                        stars=str(len(stars_trip))
                    except:
                        stars=''
                    try:
                        chambres=capacity_trip[0].text
                        roomsy=re.compile('(?<=Nombre de chambres : )(\d+)')
                        chambres=roomsy.findall(chambres)[0]
                    except:
                        chambres=''
                    try:
                        vname=name_trip[0].text
                        vname=' '.join(vname.replace('\n','').split())
                    except:
                        vname=''
                    try:
                        adrs=adrs_trip[0].text
                        adrs=' '.join(adrs.replace('\n','').split())
                    except:
                        adrs=""
                except Exception as ex:
                    print(x, 'could not be completed','because of',ex)
                    vname=""
                    stars=''
                    chambres=''
                    adrs=''
            
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
