# Restaurants_Tripadvisor
Un project d'extraction de données sur le site Tripadvisor.
Les données ont ensuite été exportées sur une base MongoDB
Des Query pour produire des indicateurs et graphs ont ensuite été réalisés.

Un dashboard interactif hosté sur MongoDB Cloud est acessible via le lien suivant :
https://charts.mongodb.com/charts-project-0-jingm/public/dashboards/63a709e1-b99d-4ea0-8f53-82b42c905aa3

Les principaux outils utilisés sont les suivants :
- Python avec notamment les packages suivant :
    - Pandas pour le traitement des données
    - Selenium pour le crawl de données 
    - PyMongo pour intéragir avec une base de donnée MongoDB
- MongoDB

Le but de ce projet est de crawler les données sur les restaurants en France 
listés sur le site Tripadvisor ("https://www.tripadvisor.com/Restaurants-g187070-France.html"). 
Les données de plus de 160k restaurants ont été récupérées. 
- Notebooks 1- Crawl Urls Restos et 2- Crawl Infos Restos

Une fois ces données récupéres, on les met en forme et on les 
envoie sur une basae de donnée MongoDB
- Notebook 3- Export Mongo

On termine ensuite par réaliser des pipelines de traitement de données pour 
produire des indicateurs sur le marché de la restauration en France,
comme on pourrait être amené à faire pour une mission client.
- Notebook 4- Requetes Mongo
