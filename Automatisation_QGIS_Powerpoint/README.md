<img width="1055" alt="Capture d’écran 2023-01-16 121150" src="https://user-images.githubusercontent.com/72470212/212664943-3fde81f4-0333-49e5-b55a-665ca430fad3.png">
# Automatisation_QGIS_Powerpoint
Une presentation d'un projet de crawl de données, d'automatisation QGIS et Powerpoint
que j'ai réalisé via Python. Pour avoir un apercu du résultat final, vous trouverez 2
examples de PDF dans le dossier EXTRAITS_PDFS_FINAUX

Les principaux outils utilisés sont les suivants :
- Python avec notamment les packages suivant :
    - Pandas pour le traitement des données
    - Selenium pour le crawl de données 
    - PyGIS pour automatiser la création des cartes
    - Pptx pour automatiser la création des slides Powerpoint
- QGIS

Le but de ce projet est de crawler les données sur les hôtels de chaines listés 
sur le site CTRIP ("https://hotels.ctrip.com/brand/"). Les données de plus de 133k
hotels, 2k groupes et 3k chaines d'hotels ont été récupérées. Pour estimer les nombres 
de chambres globaux (chaines + indépendants) des différents pays, des recherches 
sur les offices statistiques ont été réalisées
- Dossier 1- CRAWL

Une fois ces données récupéres, on les consolide par chaines groupes et pays pour
produire des cartes QGIS sur l'offre des groupes/chaines à travers le monde
- Dossier 2- QGIS

On termine ensuite par réaliser une pipeline de traitement de données pour 
produire automatiquement des slides powerpoints à partir d'un template
et des pdf synthétisant des classements de groupes/chaines par pays et
par segments hôteliers
- Dossier 3- PREPARATION_SLIDES



Les dossiers restant sont des annexes :
- Dossier EXTRAITS_DATA : Extraits des données CTRIP consolidées et des 
données globales pour quelques pays

- Dossier EXTRAITS_PDF_FINAUX : Extraits des pdf finaux pour le groupe
MARRIOTT INTERNATIONAL et la chaine PEPPERS de ACCOR.

