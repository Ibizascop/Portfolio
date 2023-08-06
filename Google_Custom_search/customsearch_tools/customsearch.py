import json
import requests
import warnings
from duckduckgo_search import DDGS
from itertools import islice
from urllib.parse import quote

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class duck_duck_go_search:
    def __init__(self,query):
        self.query = query
        self.tripadvisor=None
        self.hotels=None
        self.trip =None
    def request(self):
        self.urls=DDGS().text(self.query, backend="lite")
        global links
        links=[]

        for item in self.urls:
            links.append(item['href'])
        temp_tripadvisor=[x for x in links if 'tripadvisor' in x]
        temp_hotel=[x for x in links if 'hotels.com/' in x]
        temp_trip=[x for x in links if 'hk.trip.com' in x or "hotels.ctrip.com/hotels/" in x
                  or "trip.com/hotels/" in x]


        try:
            tripadvisor_url=temp_tripadvisor[0]
        except:
            tripadvisor_url=""
        try:
            hotel_url=temp_hotel[0]
        except:
            hotel_url=""
        try:
            trip_url=temp_trip[0]
        except:
            trip_url=""
            
        self.tripadvisor=tripadvisor_url
        self.hotels=hotel_url
        self.trip=trip_url
        self.links = links

class custom_search:
    def __init__(self,query):
        self.query = query
        self.url='https://customsearch.googleapis.com/customsearch/v1?cx=06d9ec2333cc2f87f&q='+quote(self.query)+'&key="INSERT API KEY'
        self.tripadvisor=None
        self.hotels=None
    def request(self):
        global page
        global links
        links=[]
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36", 'referer':'https://www.google.com/' }
        http_proxy  = "ADD PROXY"
        https_proxy = "ADD PROXY"
        ftp_proxy   = "ADD PROXY"

        proxyDict = {
                      "http"  : http_proxy,
                      "https" : https_proxy,
                      "ftp"   : ftp_proxy
                    }
        #add proxies if necessary

        page=requests.get(self.url,verify=False,headers=headers)
        csjson=json.loads(page.text)
        for item in csjson['items']:
            links.append(item['link'])
        temp_trip=[x for x in links if 'tripadvisor.fr' in x]
        temp_hotel=[x for x in links if 'fr.hotels.com' in x]


        try:
            trip_url=temp_trip[0]
        except:
            trip_url=""
        try:
            hotel_url=temp_hotel[0]
        except:
            hotel_url=""
            
        self.tripadvisor=trip_url
        self.hotels=hotel_url
        #return links
