import json
import urllib.request as urlreq
import urllib.parse
import http.client

class searcher:
    def __init__(self,item,api):
        self.item=item
        self.conn = http.client.HTTPConnection('api.positionstack.com')
        self.api = api

        params = urllib.parse.urlencode({
            'access_key': self.api,
            'query': self.item,
            'limit': 1
            })
        self.conn.request('GET', '/v1/forward?{}'.format(params))
        res = self.conn.getresponse()
        self.data = res.read()
        self.data = json.loads(self.data.decode('utf-8'))

class parser:
    def __init__(self,data):
        self.data=data
        self.number=None
        self.route=None
        self.neighbourhood=None
        self.administrative_area=None
        self.region=None
        self.region_code=None
        self.country=None
        self.country_code=None
        self.postal_code=None
        self.latitude=None
        self.longitude=None
        self.label=None
        self.ue=None

        try:
            self.number= self.data['data'][0]['number']
        except:
            self.number=""

        try:
            self.route= self.data['data'][0]['street']
        except:
            self.route=""

        try:
            self.neighbourhood= self.data['data'][0]['neighbourhood']
        except:
            self.neighbourhood=""

        try:
            self.administrative_area= self.data['data'][0]['administrative_area']
        except:
            self.administrative_area=""
        
        try:
            self.region= self.data['data'][0]['region']
        except:
            self.region=""

        try:
            self.region_code= self.data['data'][0]['region_code']
        except:
            self.region_code=""

        try:
            self.country= self.data['data'][0]['country']
        except:
            self.country=""
        
        try:
            self.country_code= self.data['data'][0]['country_code']
        except:
            self.country_code=""

        try:
            self.postal_code= self.data['data'][0]['postal_code']
        except:
            self.postal_code=""
        
        try:
            self.latitude= self.data['data'][0]['latitude']
        except:
            self.latitude=""
        
        try:
            self.label= self.data['data'][0]['label']
        except:
            self.label=""
        
        UE_L=['ALLEMAGNE','AUTRICHE','BELGIQUE','BULGARIE','CHYPRE','DANEMARK','ESPAGNE','ESTONIE','FINLANDE','FRANCE','GRÈCE','HONGRIE','IRLANDE','ITALIE','LETTONIE','LITUANIE','LUXEMBOURG','MALTE','PAYS-BAS','POLOGNE','PORTUGAL','TCHÉQUIE','ROUMANIE','ROYAUME-UNI','SLOVAQUIE','SLOVÉNIE','SUÈDE']
        try:
            if self.country in UE_L:
                self.ue='UE'
            else:
                self.ue='NON UE'
        except:
            self.ue=''
