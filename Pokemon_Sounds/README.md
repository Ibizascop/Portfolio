# Pokemon_Sounds
Dans les jeux Pokemon, les pokémons sont regroupés dans ce que l'on appelle des "groupes d'oeufs". Ces groupes déterminent quels pokemons peuvent se reproduire entre eux et sont par conséquent similaire à la notion de "genre animal". Par exemple, le lion et le tigre font parti du même genre et peuve ainsi donner naissance à des hybrides.

Le but de ce projet est d'essayer de construire un modèle de prediction de l'appartenance ou non d'un pokémon aux différents groupes d'oeufs (CLASSIFICATION MULTILABEL)

Les principaux outils et méthodes utilisés sont les suivants :
- Python avec notamment les packages suivant :
    - Librosa pour le traitement des données audio
    - Tsfresh pour l'extraction de features de séries temporelles
    - Selenium pour le Crawl de données
    - Numpy pour le traitement des series temporelles
- R avec notamment les librairis suivantes :
    - dtwclust pour la classification non supervisée de séries temporelles
    - caret pour la création d'un modèle RandomForest
    - utiml pour la création d'un modèle RandomForest Multilabel : Prédire 
    plus d'un label à la fois

Déroulement :

1) Récupérer les données nécessaires via un crawl :
    - Fichier = 1- Crawl

2) Transformer les fichiers mp3 en séries temporelles csv :
    - Fichier = 2- CSV & PLOTS

3) Calculer une matrice de distance entre les différentes séries temporelles via 
   la métrique SBD (SHAPE BASED DISTANCE) et clusteriser les séries :
    - Fichier = 3- SBD CLUSTERING

4) Analyse des clusters et extraction des centroides via l'algorithme KSHAPE
   la métrique SBD (SHAPE BASED DISTANCE) et clusteriser les séries :
    - Fichier = 4- Analyse_cluster

5) Extraction de features des series via tsfresh pour le modèle de prédiction
    - Fichier = 5- Extraction_de_features

6) Construction d'un modèle de prédiction 
    - Fichier = 6- Random_forest_on_features

Taux de précision autour des 60%. Pistes d'amélioration sur la prise en compte de 
l'inclusion/exclusion mutuelle de certains labels. Par exemple, le groupe
"Insectoide" n'est jamais accompagné du groupe "Terrestre"

