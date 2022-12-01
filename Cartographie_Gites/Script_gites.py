from osgeo import ogr
from qgis.utils import iface

#1 = Changer le Crs en 3857 
QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(3857))

#2 = Charger le shapefile des communes (sur le serverur MKG)
url_communes = r"\\symbiose.mkg.local\Docu-Share\MKG Consulting\3. Etudes Sectorielles\29 - QGIS\Cartes\Shapefiles Generaux\Communes France\communes-20220101.shp"
Communes = iface.addVectorLayer(url_communes,"Communes","ogr")
    
#3 = Charger le fichier txt avec les coordones des gites
absolute_path_to_csv_file = r"C:/Users/w.grasina/OneDrive - Adelphon/Bureau/TRAVAUX/Crawls/CRAWLS DIVERS/GITES DE FRANCE/GPS_Gites.txt"
encoding = "UTF-8"
delimiter =r"\t"
decimal = "."
crs = "epsg:4326"
x = "LONG"
y = "LAT"
uri_gites = "file:///{}?encoding={}&delimiter={}&decimalPoint={}&crs={}&xField={}&yField={}".format(absolute_path_to_csv_file,encoding,delimiter,decimal,crs,x,y)
#Transformer en points
Gites = QgsVectorLayer(uri_gites, "Gites", "delimitedtext")

#Verification du resultat
if not Gites.isValid():
    print ("Layer not loaded")

#Ajouter les points
QgsProject.instance().addMapLayer(Gites)
#Creer un Index spatial pour acceler les traitements
Gites.dataProvider().createSpatialIndex()

#4= Joindre les communes aux gites , cree un excel à l'emplacement souhaité
processing.runAndLoadResults("qgis:joinattributesbylocation",{
                        "INPUT":Gites, 
                        "JOIN":Communes,
                        "PREDICATE":[5],#5 = pour chercher dans quel polygone le point se situe
                        "SUMMARY":0,
                        "KEEP":1,
                        "OUTPUT":r"C:\Users\w.grasina\OneDrive - Adelphon\Bureau\TRAVAUX\Crawls\CRAWLS DIVERS\GITES DE FRANCE\Resultats_Script_Gites.xlsx"})