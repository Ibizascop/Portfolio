# Automatisation_QGIS_Powerpoint
Une presentation d'un projet de crawl de données, d'automatisation QGIS et Powerpoint
que j'ai réalisé via Python. 

Les principaux outils utilisés sont les suivants :
- Python avec notamment les packages suivant :
    - Pandas pour le traitement des données
    - Selenium pour le crawl de données 
    - PyGIS pour automatiser la création des cartes
    - Pptxpour automatiser la création des slides Powerpoint
- QGIS

Le but de ce projet est de crawler les données sur les hôtels de chaines listés 
sur le site CTRIP ("https://hotels.ctrip.com/brand/"). Pour estimer les nombres 
de chambres globaux (chaines + indépendants) des différents pays, des recherches 
sur les offices statistiques ont été réalisées
- Dossier 1- CRAWL

Une fois ces données récupéres, on les consolide par chaines groupes et pays pour
produire des cartes QGIS sur l'offre des groupes/chaines à travers le monde
- Dossier 2- QGIS

On termine ensuite par réaliser une pipeline de traitement de données pour 
produire automatiquement des slides powerpoints et des pdf synthétisant 
des classements de groupes/chaines par pays, par segments hôteliers
- Dossier 3- PREPARATION_SLIDES



Les dossiers restant sont des annexes :
- Dossier EXTRAITS_DATA : Extraits des données CTRIP consolidées et des 
données globales pour quelques pays

- Dossier EXTRAITS_PDF_FINAUX : Extraits des pdf finaux pour le groupe
MARRIOTT INTERNATIONAL et la chaine PEPPERS de ACCOR.

