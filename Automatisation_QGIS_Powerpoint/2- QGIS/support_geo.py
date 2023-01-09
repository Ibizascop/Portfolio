from osgeo import ogr
from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsProject
import pandas as pd

#Function to load geopackage
def add_gpkg_layer(gpkg, layer,name) :
    """
    Fonction pour importer et ajouter à qgis les geopackage 
    des pays du monde et des centroides des pays

    Arguments:
        gpk: String : Chemin d'accès du géopackage à ouvrir.
                    Par exemple : ".\GEO\pays_final_geo.gpkg"
        layer: String : Nom de la couche à charger dans le geopackage

        name: String : Nom à donner à la variable du geopackage une fois
        importé sur qgis
        
    Renvoit: Un objet VectorLayer QGIS contenant les données de la couche
    du geopackage et ayant le nom "name"
    """ 
    layers = [l.GetName() for l in ogr.Open(gpkg)]
    if layer in layers :
        #x = QgsVectorLayer(gpkg +"|layername=" + layer, 'ogr')
        #QgsProject.instance().addMapLayer(x)
        x = iface.addVectorLayer(gpkg,name,"ogr")
    else :
        print('Error: there is no layer named "{}" in {}!'.format(layer, gpkg))
        x = None
    return x
    
def country_supply(country,dataframe,segment = None) :
    """
    Donne le nombre d'hôtels et de chambres de chaines d'un pays
     au global ou sur un segment spécifique
    
    Arguments:
        country: String : le nom du pays
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment
        
    Renvoit: Integer
        Le nombre de chambres 
        du pays précisé et sur le segment donné
    """
    try :
        df_country = dataframe.loc[dataframe['Country'] == country]
        if segment != None :
            df_country = df_country.loc[df_country['Categorie Hotel'] == segment]
        country_rooms = df_country["Rooms 2022"].sum()
        return country_rooms
    except Exception as e:
        print(e)

def has_europe_supply(group_name,dataframe,global_group =True) :
    """
    Indique si le groupe/chaine donné possède ou non des chambres
    dans un pays en Europe justifiant d'ajouter une petite carte de zoom
    sur la zone.
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
        
    Renvoit: Booleen : True ou False
        Renvoit True si le groupe/chaine possède au moins 1 chambre
        dans un pays pour lequel on effectue un zoom sur la carte
    """
    if global_group == True :
        column = "Groups"
    else :
        column = "Brands Final"
    df_group_countries = dataframe.loc[dataframe['{}'.format(column)] == group_name]
    df_group_countries = df_group_countries.loc[df_group_countries["ZOOM EUROPE"]=="YES"]
    europe_rooms = df_group_countries["Rooms 2022"].sum()
    if europe_rooms > 0 :
        return True
    else :
        return False
        
def has_asia_supply(group_name,dataframe,global_group =True) :
    """
    Indique si le groupe/chaine donné possède ou non des chambres
    dans un pays en Asie justifiant d'ajouter une petite carte de zoom
    sur la zone.
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
        
    Renvoit: Booleen : True ou False
        Renvoit True si le groupe/chaine possède au moins 1 chambre
        dans un pays pour lequel on effectue un zoom sur la carte
    """
    if global_group == True :
        column = "Groups"
    else :
        column = "Brands Final"
    df_group_countries = dataframe.loc[dataframe['{}'.format(column)] == group_name]
    df_group_countries = df_group_countries.loc[df_group_countries["ZOOM ASIE"]=="YES"]
    asia_rooms = df_group_countries["Rooms 2022"].sum()
    if asia_rooms > 0 :
        return True
    else :
        return False
            
def prepare_group_data(group_name,dataframe,global_group = True,segment = None) :
    """
    Crée et renvoit un dataframe donnant pour un groupe/chaine donné
    (au global ou sur un segment spécifique), pour l'ensemble des pays
    dans lesquels le groupe/chaine est présent, les informations suivantes :
        - Nombre de chambres du groupe/chaine dans le pays
        - Part représentée par le pays dans l'offre mondiale du groupe/chaine
        - Part de marché du groupe/chaine dans le pays

    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        country: String : le nom du pays
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment
        
    Renvoit: DataFrame
        Dataframe contenant pour chaque pays dans lesquels le groupe/chaine
        est présent, le nombre de chambres, la part de marché et le %
        représenté par le pays dans l'offre globale du groupe
    """
    if global_group == True :
        column = "Groups"
    else :
        column = "Brands Final"
    df_group_countries = dataframe.loc[dataframe['{}'.format(column)] == group_name]
    df_group_countries = df_group_countries.loc[df_group_countries["Rooms 2022"] != 0]
    df_group_countries = df_group_countries.groupby(["Country"],as_index = False).sum()
    #Calculer PDM par pays
    df_group_countries["Market_Share"] = ""
    for i,pays in enumerate(list(df_group_countries["Country"].unique())) :
        country_branded_supply = country_supply(pays,dataframe,segment)
        try :
            group_supply = df_group_countries["Rooms 2022"].loc[df_group_countries['Country'] == pays].values[0]
            try :
                df_group_countries['Market_Share'].iloc[i] = group_supply/country_branded_supply
            except Exception as e:
                df_group_countries['Market_Share'].iloc[i] = 0
        except Exception as e :
            print(pays)
            print(e)
            
    #Calculer % groupe par pays
    df_group_countries['% GROUP'] = ""
    rooms_to_use = []
    for i,pays in enumerate(list(df_group_countries["Country"].unique())) :
        rooms_to_use.append(df_group_countries["Rooms 2022"].loc[df_group_countries['Country'] == pays].values[0])
    for i,pays in enumerate(list(df_group_countries["Country"].unique())) :
        df_group_countries['% GROUP'].iloc[i] = rooms_to_use[i]/sum(rooms_to_use)
    return df_group_countries
    
def RemoveAllLayersExcept(*keep_layers):
    """
    Fonction pour enlever toutes les couches qgis sauf celles 
    indiquées en arguments

    Arguments:
        keep_layers: liste : liste de VectorLayers a conserver sur QGIS
    
    Renvoit: Null
        Retire de QGIS toutes les couches actuellement présentes
        sauf celles passées en argument
    """ 
    layers = QgsProject.instance().mapLayers().values()
    will_be_deleted = [l for l in layers if l not in keep_layers]
    for layer in will_be_deleted:
        QgsProject.instance().removeMapLayer(layer)
        
def list_brands(group_name,dataframe) :
    """
    Liste l'ensemble des chaines avec au moins 1 chambre d'un groupe
    
    Arguments:
        group_name: String: Le nom d'un groupe issu 
        de la colonne "Groups" du fichier Parc_Trip_2022
        Par exemple : "ACCOR"
        
        dataframe: Pandas Dataframe : Par construction la fonction ne marche qu'avec
        le fichier Parc_Trip_2022 comme argument
        
    Renvoit: List
        Une liste contenant l'ensemble des chaines du groupe
    """
    df = dataframe.loc[dataframe['Groups'] == group_name]
    liste_brands = list(df["Brands Final"].unique())
    return liste_brands

def get_segment(brand_name,dataframe) :
    """
    Donne le segment hôtelier d'une chaine
    
    Arguments:
        brand_name: String: Le nom d'une chaine issu 
        de la colonne "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR-IBIS"
        
        dataframe: Pandas Dataframe : Par construction la fonction ne marche qu'avec
        le fichier Parc_Trip_2022 comme argument
    Renvoit: String
    
        Le positionnement hôtelier de la chaine : SUPER-ECO,ECO,
        MDG,HDG ou LUX
    """
    df = dataframe.loc[dataframe['Brands Final'] == brand_name]
    segment = df["Categorie Hotel"].values[0]
    return segment