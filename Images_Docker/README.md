# Images_Docker
Une presentation d'un projet de création d'images docker
permettant de réaliser des crawls sur le site Booking.com.

Les principaux outils utilisés sont les suivants :
- Python avec notamment les packages suivant :
    - Requests et Selenium pour le crawl de données
    - Pyodbc pour envoyer les données sur une base SQL
- Scripting Bash notamment Docker
- SQL 

- Dossier 1- AVIS_BOOKING

Dans ce dossier on trouve les fichiers :
    - booking_avis.py : Script contenant le code pour effectuer un crawl des avis
    booking sur la page d'un hôtel
    - SQL.py : Script pour envoyer les avis récupérés sur une base SQL


- Dossier 2- INFO_BOOKING

Dans ce dossier on trouve les fichiers :
    - booking.py : Script contenant le code pour effectuer un crawl des informations
    booking sur la page d'un hôtel

- Dossier 2- URLS_BOOKING

Dans ce dossier on trouve les fichiers :
    - booking_urls.py : Script contenant le code pour effectuer un crawl des urls
    des établissements sur la page d'une destination booking