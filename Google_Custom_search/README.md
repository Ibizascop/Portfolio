# Google_Custom_search
Une presentation d'un projet utilisant l'API de recherche google afin
de créer un outil de pointage permettant de chercher sur Hotel.com
et Tripadvisor les informations des hôtels lorsque celles-ci ne 
sont pas disponible sur le site de l'hôtel. Une API de géocodage 
est aussi utilisée afin d'obtenir les coordonées GPS et l'emplacement
des hôtels.

Les principaux outils utilisés sont les suivants :
- Python avec notamment les packages suivant :
    - Requests et l'API customsearch de Google
    - Json pour le formatage des résultats Google

Dossier 1- CUSTOMSEARCH_TOOLS-MAIN

Dans ce dossier on trouve les fichiers :
- customsearch.py : Script contenant le code pour effectuer une recherche
    google sur un nom d'hôtel et récupérer les liens tripadvisor et Hotel.com
    associés
- geocode.py : Script contenant le code pour effectuer une geolocalisation
    google sur un nom d'hôtel et récupérer les informations sur la rue, ville,
    pays, GPS ...


Dossier 2- TOOLS_POINTAGE-MAIN

Dans ce dossier on trouve les dossiers :
- supply_updater : Dossier contenant les fichiers :
    - fusion.py  : Script permettant de fusionner les informations 
        obtenues directement sur le site de l'hôtel avec les informations 
        obtenues via recherche google sur dans un CSV/EXCEL
    - hotels.py  : Script faisant appel au script customsearch.py pour 
        requeter les informations des hôtels lorsque nécessaire

- support : Dossier contenant les fichiers :
    - support.py  : Script contenant diverses fonctions permettant
        de crawler des données sur Internet.
