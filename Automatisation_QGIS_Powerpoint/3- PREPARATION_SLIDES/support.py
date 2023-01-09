# -*- coding: utf-8 -*-



import pandas as pd
import traceback
import matplotlib.pyplot as plt

def import_data(file) :
    """
    Permet de lire les données d'un excel en tant que Pandas 
    
    Arguments:
        file: String : Chemin d'accès du fichier
        
    Renvoit: Dataframe
        Un Pandas Dataframe contenant les données du fichier excel spécifié
    """
    try :
        df = pd.read_excel(file)
        return df
    except FileNotFoundError:
        print("Cannot find the specified file")
    
def get_group_country(group_name,dataframe) :
    """
    Donne la nationalité d'un groupe/chaine
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        dataframe: Pandas Dataframe : Par construction la fonction ne marche qu'avec
        le fichier Parc_Trip_2022 comme argument
        
    Renvoit: String
        Le nationalité du groupe/chaine
    """
    try :
        country = dataframe["Nationalite EN"][dataframe["Groups"]==group_name]
        country = country.values[0]
        return country
    except:
        try :
            country = dataframe["Nationalite EN"][dataframe["Brands Final"]==group_name]
            country = country.values[0]
            return country
        except:
            print(traceback.format_exc())

def domestic_hotel(group_name,dataframe,global_group = True) :
    """
    Indique si le groupe/chaine donné possède ou non des chambres
    dans le pays de sa nationalité (colonne NATIONALITE EN dans le 
    fichier Parc_Trip_2022)
    
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
        dans le pays de sa nationalité, False sinon
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        country = get_group_country(group_name,dataframe).title()
        df_country = dataframe.loc[dataframe['Country'] == country]
        df_group_country = df_country.loc[df_country['{}'.format(column)] == group_name]
        if len(df_group_country) == 0 or df_group_country["Rooms 2022"].sum() == 0 :
            domestic_supply = False
        else:
            domestic_supply = True
        return domestic_supply
    except:
        print(traceback.format_exc())

def get_group_country_ranking(group_name,country,dataframe,segment = None,global_group = True):
    """
    Donne le classement (en nombre de chambres) d'un groupe/chaine
    au niveau national soit au global ou sur un segment spécifique
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        country: String : le nom du pays
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
        
    Renvoit: Integer, Integer
        Le classement en nombre de chambres du groupe/chaine
        dans le pays précisé et sur le segment donné
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        #Trier
        df_country = dataframe.loc[dataframe['Country'] == country]
        df_country = df_country.loc[df_country['Rooms 2022'] != 0]
        if segment != None :
            df_country = df_country.loc[df_country['Categorie Hotel'] == segment]
        groups_supply = df_country.groupby(["{}".format(column)],as_index=False)[["Hotels 2022","Rooms 2022"]].sum()
        groups_supply = groups_supply.sort_values(by='Rooms 2022', ascending=False, na_position='last')
        groups_supply = groups_supply.reset_index(drop=True)    
        #Get index of group
        index = groups_supply.index[groups_supply['{}'.format(column)]==group_name].values[0]+1
        return index
    except:
        print(traceback.format_exc())
    
def get_group_world_ranking(group_name,dataframe,global_group = True):
    """
    Donne le classement (en nombre de chambres) d'un groupe/chaine
    au niveau mondial
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
    
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
          
    Renvoit: Integer
        Le classement mondial en nombre de chambres du groupe/chaine
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        #Trier
        df = dataframe.loc[dataframe['Rooms 2022'] != 0]
        groups_supply = df.groupby(["{}".format(column)],as_index=False)[["Hotels 2022","Rooms 2022"]].sum()
        groups_supply = groups_supply.sort_values(by='Rooms 2022', ascending=False, na_position='last')
        groups_supply = groups_supply.reset_index(drop=True)    
        #Get index of group
        index = groups_supply.index[groups_supply['{}'.format(column)]==group_name].values[0]+1
        return index
    except:
        print(traceback.format_exc())

            
def get_select_group_country_supply(group_name,country,dataframe,global_group = True,segment = None) :
    """
    Donne le nombre d'hôtels et de chambres d'un groupe/chaine
    donné au niveau national soit au global ou sur un segment spécifique
    
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
        
    Renvoit: Integer, Integer
        Le nombre d'hôtels et nombre de chambres 
        du groupe/chaine dans le pays précisé et sur le segment donné
    """
    country = country.replace(" And "," and ")
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        df_country = dataframe.loc[dataframe['Country'] == country]
        df_group_country = df_country.loc[df_country['{}'.format(column)] == group_name]
        if segment != None :
            df_group_country = df_group_country.loc[df_group_country['Categorie Hotel'] == segment]
        group_hotels = df_group_country["Hotels 2022"].sum()
        group_rooms = df_group_country["Rooms 2022"].sum()
        return group_hotels, group_rooms
    except:
        print(traceback.format_exc()) 
            
def get_select_group_global_supply(group_name,dataframe,global_group = True) :
    """
    Donne le nombre d'hôtels et de chambres d'un groupe/chaine
    donné au niveau mondial
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
    
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
          
    Renvoit: Integer, Integer
        Le nombre d'hôtels et nombre de chambres dans le monde 
        du groupe/chaine
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        df = dataframe.loc[dataframe['{}'.format(column)] == group_name]

        group_hotels = df["Hotels 2022"].sum()
        group_rooms = df["Rooms 2022"].sum()
        return group_hotels, group_rooms
    except:
        print(traceback.format_exc())

            
def get_group_above_country(group_name,country,number,dataframe,global_group = True,segment = None) :
    """
    Indique le groupe/chaine classé n rangs au dessus (en fonction du nombre de chambres)
    d'un groupe/chaine donné au niveau d'un pays au global/sur un segment.
    Le nombre n est définit par l'argument "number" :
    Par exemple number = 1 => On cherche le groupe/chaine classé juste au dessus
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        country: String : le nom du pays
            
        number: Integer: Le nombre de rangs au dessus souhaité
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment
        
    Renvoit: String, Integer, Integer
        Le nom du groupe/chaine classé n rangs au dessus du
        groupe précisé au niveau du pays au global/sur un segment
        ,son nombre d'hôtels et son nombre de chambres
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        #Trier
        df_country = dataframe.loc[dataframe['Country'] == country]
        df_country = df_country.loc[df_country['Rooms 2022'] != 0]
        if segment != None :
            df_country = df_country.loc[df_country['Categorie Hotel'] == segment]
        groups_supply = df_country.groupby(["{}".format(column)],as_index=False)[["Hotels 2022","Rooms 2022"]].sum()
        groups_supply = groups_supply.sort_values(by='Rooms 2022', ascending=False, na_position='last')
        groups_supply = groups_supply.reset_index(drop=True)    
        #Get index of group
        index = groups_supply.index[groups_supply['{}'.format(column)]==group_name].values[0]
        try :
            group_above_name = groups_supply["{}".format(column)].iloc[index-number]
            group_above_hotels = groups_supply["Hotels 2022"].iloc[index-number]
            group_above_rooms = groups_supply["Rooms 2022"].iloc[index-number]
            
        except:
            group_above_name=group_above_hotels=group_above_rooms = None
        return group_above_name, group_above_hotels, group_above_rooms
        
    except:
        print(traceback.format_exc())

def get_group_above_global(group_name,number,dataframe,global_group = True) :
    """
    Indique le groupe/chaine classé n rangs au dessus (en fonction du nombre de chambres)
    d'un groupe/chaine donné au niveau mondial.
    Le nombre n est définit par l'argument "number" :
    Par exemple number = 1 => On cherche le groupe/chaine classé juste au dessus
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        number: Integer: Le nombre de rangs au dessus souhaité
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment
        
    Renvoit: String, Integer, Integer
        Le nom du groupe/chaine classé n rangs au dessus du
        groupe précisé au niveau mondial,son nombre d'hôtels et son nombre de chambres
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        #Trier
        df = dataframe.loc[dataframe['Rooms 2022'] != 0]
        groups_supply = df.groupby(["{}".format(column)],as_index=False)[["Hotels 2022","Rooms 2022"]].sum()
        groups_supply = groups_supply.sort_values(by='Rooms 2022', ascending=False, na_position='last')
        groups_supply = groups_supply.reset_index(drop=True)    
        #Get index of group
        index = groups_supply.index[groups_supply['{}'.format(column)]==group_name].values[0]
        try:
            group_above_name = groups_supply["{}".format(column)].iloc[index-number]
            group_above_hotels = groups_supply["Hotels 2022"].iloc[index-number]
            group_above_rooms = groups_supply["Rooms 2022"].iloc[index-number]
            
        except:
            group_above_name=group_above_hotels=group_above_rooms = None
        return group_above_name, group_above_hotels, group_above_rooms
        
    except:
        print(traceback.format_exc())

            
def get_group_below_country(group_name,country,number,dataframe,global_group = True,segment = None) :
    """
    Indique le groupe/chaine classé n rangs en dessous (en fonction du nombre de chambres)
    d'un groupe/chaine donné au niveau d'un pays au global/sur un segment.
    Le nombre n est définit par l'argument "number" :
    Par exemple number = 1 => On cherche le groupe/chaine classé juste en dessous
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        country: String : le nom du pays
            
        number: Integer: Le nombre de rangs en dessous souhaité
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment
        
    Renvoit: String, Integer, Integer
        Le nom du groupe/chaine classé n rangs en dessous du
        groupe précisé au niveau du pays au global/sur un segment
        ,son nombre d'hôtels et son nombre de chambres
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        #Trier
        df_country = dataframe.loc[dataframe['Country'] == country]
        df_country = df_country.loc[df_country['Rooms 2022'] != 0]
        if segment != None:
            df_country = df_country.loc[df_country['Categorie Hotel'] == segment]
        groups_supply = df_country.groupby(["{}".format(column)],as_index=False)[["Hotels 2022","Rooms 2022"]].sum()
        groups_supply = groups_supply.sort_values(by='Rooms 2022', ascending=False, na_position='last')
        groups_supply = groups_supply.reset_index(drop=True)    
        #Get index of group
        index = groups_supply.index[groups_supply['{}'.format(column)]==group_name].values[0]
        try :
            group_below_name = groups_supply["{}".format(column)].iloc[index+number]
            group_below_hotels = groups_supply["Hotels 2022"].iloc[index+number]
            group_below_rooms = groups_supply["Rooms 2022"].iloc[index+number]
            
        except:
            group_below_name=group_below_hotels=group_below_rooms = "..."
        return group_below_name, group_below_hotels, group_below_rooms
        
    except:
        print(traceback.format_exc())

def get_group_below_global(group_name,number,dataframe,global_group = True,segment = None):
    """
    Indique le groupe/chaine classé n rangs en dessous (en fonction du nombre de chambres)
    d'un groupe/chaine donné au niveau mondial.
    Le nombre n est définit par l'argument "number" :
    Par exemple number = 1 => On cherche le groupe/chaine classé juste en dessous
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        number: Integer: Le nombre de rangs en dessous souhaité
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment
        
    Renvoit: String, Integer, Integer
        Le nom du groupe/chaine classé n rangs en dessous du
        groupe précisé au niveau mondial,son nombre d'hôtels et son nombre de chambres
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        #Trier
        df = dataframe.loc[dataframe['Rooms 2022'] != 0]
        if segment != None:
            df = df.loc[df['Categorie Hotel'] == segment]
        groups_supply = df.groupby(["{}".format(column)],as_index=False)[["Hotels 2022","Rooms 2022"]].sum()
        groups_supply = groups_supply.sort_values(by='Rooms 2022', ascending=False, na_position='last')
        groups_supply = groups_supply.reset_index(drop=True)    
        #Get index of group
        index = groups_supply.index[groups_supply['{}'.format(column)]==group_name].values[0]
        try:
            group_below_name = groups_supply["{}".format(column)].iloc[index+number]
            group_below_hotels = groups_supply["Hotels 2022"].iloc[index+number]
            group_below_rooms = groups_supply["Rooms 2022"].iloc[index+number]
            
        except:
            group_below_name=group_below_hotels=group_below_rooms = None
        return group_below_name, group_below_hotels, group_below_rooms
        
    except:
        print(traceback.format_exc())

            
def country_number_one_group(country,dataframe,global_group = True,segment = None) :
    """
    Indique le groupe/chaine ayant le plus de chambres dans un pays donné
    au global ou sur un segment 
    
    Arguments:
        country: String : le nom du pays
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment
        
    Renvoit: String, Integer, Integer
        Le nom du groupe/chaine classé rang 1,son nombre d'hôtels et son nombre de chambres
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        df_country = dataframe.loc[dataframe['Country'] == country]
        if segment != None :
            df_country = df_country.loc[df_country['Categorie Hotel'] == segment]
        groups_supply = df_country.groupby(["{}".format(column)],as_index=False)[["Hotels 2022","Rooms 2022"]].sum()
        groups_supply = groups_supply.loc[groups_supply['Rooms 2022'] != 0]
        groups_supply = groups_supply.reset_index(drop=True)    
        index = groups_supply['Rooms 2022'].idxmax()
        leader_group = list(groups_supply["{}".format(column)])[index]
        leader_group_hotels = list(groups_supply["Hotels 2022"])[index]
        leader_group_rooms = list(groups_supply["Rooms 2022"])[index]
        return leader_group, leader_group_hotels, leader_group_rooms
    except:
        print(traceback.format_exc())

def country_number_groups(country,dataframe,segment= None,global_group = True) :
    """
    Indique le nombre de groupes/chaines ayant au moins 1 chambre
    dans un pays au global ou sur un segment
    
    Arguments:
        country: String : le nom du pays
        
        dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment
    
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
             
    Renvoit: Integer
        Nombre de groupes/chaines dans le pays
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        df_country = dataframe.loc[dataframe['Country'] == country]
        df_country = df_country.loc[df_country['Rooms 2022'] != 0]
        if segment != None : 
            df_country = df_country.loc[df_country['Categorie Hotel'] == segment]
        groups_supply = df_country.groupby(["{}".format(column)],as_index=False)[["Hotels 2022","Rooms 2022"]].sum()
        
        return len(groups_supply)
    except:
        print(traceback.format_exc())

def country_global_supply(country,dataframe) :
    """
    Donne le nombre de chambres global d'un pays selon 
    le fichier Chiffres_Globaux_2022.xlsx
    
    Arguments:
        country: String : le nom du pays
        
        brand_dataframe: Pandas Dataframe : Dataframe contenant les données
        des pays au global = Chiffres_Globaux_2022.xlsx
             
    Renvoit: Integer
        Nombre de chambres global d'un pays
    """
    country = country.replace(" And "," and ").replace(" Of "," of ")
    country_global_rooms = dataframe["Supply 2022"].loc[dataframe['Country Name'] == country].values[0]
    return country_global_rooms   
 
def country_branded_supply(country,dataframe) :
    """
    Donne le nombre de chambres de chaines d'un pays selon 
    le fichier Chiffres_Globaux_2022.xlsx
    
    Arguments:
        country: String : le nom du pays
        
        brand_dataframe: Pandas Dataframe : Dataframe contenant les données
        des pays au global = Chiffres_Globaux_2022.xlsx
             
    Renvoit: Integer
        Nombre de chambres de chaines d'un pays
    """
    country = country.replace(" And "," and ").replace(" Of "," of ")
    country_branded_rooms = dataframe["Branded Rooms 2022"].loc[dataframe['Country Name'] == country].values[0]
    return country_branded_rooms 


def global_supply_graph(group_name,country,brand_dataframe,global_dataframe,global_group = True) :
    """
    Crée un Camembert donnant l'offre de chaines d'un pays
    comparée à l'offre globale (avec les indep) du pays
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        country: String : le nom du pays
        
        brand_dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        brand_dataframe: Pandas Dataframe : Dataframe contenant les données
        des pays au global = Chiffres_Globaux_2022.xlsx
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
             
    Renvoit: Image PNG
        Image PNG du graphique sauvegardée dans le dossier GRAPHS
    """
    #DATA
    branded_supply =round(country_branded_supply(country,global_dataframe))
    global_supply = round(country_global_supply(country,global_dataframe))
    ind_supply = global_supply - branded_supply
    
    #Colors
    colors = ['#87B8FD','#FFC91C']
    
    #Labels
    values = ['{:,}'.format(branded_supply),""]
    textprops = {"fontsize":18}
    
    #Chart
    plt.pie([branded_supply,ind_supply],
            labels = values,
            colors = colors,
            textprops =textprops,
            wedgeprops={'edgecolor':'white', 'linewidth': 2}) 
    
    #Title
    if len(country) >= 10 :
        title_size = 17
    else :
        title_size = 22
    if country == "Bosnia and Herzegovina" :
        country_legend = "Bosnia"
    elif country =="United Republic of Tanzania" :
        country_legend = "Tanzania"
    elif country =="Myanmar/Burma" :
        country_legend = "Myanmar"
    else:
        country_legend =country
    plt.title('{} global supply'.format(country_legend),
              fontsize = title_size,
              color = "#0131B4",
              **{'fontname':'Avenir Next'})
    
    #Legend
    if len(group_name) >= 18 :
        position = (0.5, 0.12)
    else:
        position =(0.5, -0.02)
    leg = plt.legend(["Branded rooms"],loc='upper center', 
           bbox_to_anchor=position,
           fontsize=17,
           frameon=False)
    for text in leg.get_texts():
        text.set_color("#0131B4")

    
    #Save
    plt.savefig('.\GRAPHS\{}_global.png'.format(country),
                transparent = True)
    plt.close()
    plt.cla()
    plt.clf()
    
def branded_supply_graph(group_name,country,brand_dataframe,global_dataframe,global_group = True) :
    """
    Crée un Camembert donnant la part de marché de chaines 
    d'un groupe/chaine dans un pays 
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        country: String : le nom du pays
        
        brand_dataframe: Pandas Dataframe : Dataframe contenant les données
        des chaines = Parc_Trip_2022
        
        brand_dataframe: Pandas Dataframe : Dataframe contenant les données
        des pays au global = Chiffres_Globaux_2022.xlsx
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
             
    Renvoit: Image PNG
        Image PNG du graphique sauvegardée dans le dossier GRAPHS
    """
    country = country.title().replace(" And "," and ").replace(" Of "," of ")
    #DATA
    if global_group == True :
        group_hotels, group_rooms = get_select_group_country_supply(group_name,country,brand_dataframe,global_group = True)
    else:
        group_hotels, group_rooms = get_select_group_country_supply(group_name,country,brand_dataframe,global_group = False)

    branded_supply =round(country_branded_supply(country.title(),global_dataframe),1)
    group_market_share =round((group_rooms/branded_supply*100),1)
    
    #Colors
    colors = ['#87B8FD','#FFC91C']
    
    #Labels
    values = ['{}'.format(group_market_share)+"%",""]
    textprops = {"fontsize":18}
    
    #Chart
    plt.pie([group_market_share,100-group_market_share],
            labels = values,
            colors = colors,
            textprops =textprops,
            wedgeprops={'edgecolor':'white', 'linewidth': 2}) 
    
    #Title
    if len(country) >= 10 :
        title_size = 17
    else :
        title_size = 22
    if country == "Bosnia and Herzegovina" :
        country_legend = "Bosnia"
    elif country =="United Republic of Tanzania" :
        country_legend = "Tanzania"
    elif country =="Myanmar/Burma" :
        country_legend = "Myanmar"
    else:
        country_legend =country
    plt.title("{} branded hospitality share".format(country_legend.title()),
              fontsize = title_size,
              color = "#0131B4",
              **{'fontname':'Avenir Next'})
    
    #Legend
    if len(group_name) >= 40 :
        legend_size = 12.5
        cols = 1
        position = (0.5, 0.15)
    elif len(group_name) >= 18 :
        legend_size = 14
        cols = 1
        position = (0.5, 0.12)
    else:
        legend_size = 16
        cols = 2
        position = (0.5, -0.02)
    if global_group == True :
        leg = plt.legend(["{}".format(group_name),"Other groups"],loc='upper center', 
               bbox_to_anchor=position,
               fontsize=legend_size,
               frameon=False,
               ncol =cols)
    else :
        leg = plt.legend(["{}".format(group_name.split("-")[1]),"Other brands"],loc='upper center', 
               bbox_to_anchor=position,
               fontsize=legend_size,
               frameon=False,
               ncol =cols)
    for text in leg.get_texts():
        text.set_color("#0131B4")
    
    
    #Save
    plt.savefig('.\GRAPHS\{}_branded.png'.format(group_name),
                transparent = True)
    plt.close()
    plt.cla()
    plt.clf()

def fill_global_table(group_name,dataframe,global_group = True):
    """
    Crée un dictionnaire pour remplir le tableau du classement des chaines/groupes
    au niveau mondial
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        dataframe: Pandas Dataframe : Par construction la fonction ne marche qu'avec
        le fichier Parc_Trip_2022 comme argument
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
             
    Renvoit: Dictionnaire
        Dictionnaire contenant les données pour remplir le tableau powerpoint
        de classement mondial
    """
    if global_group == True :
        group_rank = get_group_world_ranking(group_name,dataframe,global_group = True)
        group_hotels, group_rooms = get_select_group_global_supply(group_name,dataframe,global_group = True)
    else :
        group_rank = get_group_world_ranking(group_name,dataframe,global_group = False)
        group_hotels, group_rooms = get_select_group_global_supply(group_name,dataframe, global_group = False)

    if group_rank != 1 :
        if global_group == True :
            above_group, above_hotels, above_rooms = get_group_above_global(group_name,1,dataframe, global_group= True)
            below_group, below_hotels, below_rooms = get_group_below_global(group_name,1,dataframe, global_group = True)
        else :
            above_group, above_hotels, above_rooms = get_group_above_global(group_name,1,dataframe, global_group= False)
            below_group, below_hotels, below_rooms = get_group_below_global(group_name,1,dataframe, global_group = False)
            
            above_group = above_group.split("-")[1]
            group_name = group_name.split("-")[1]
            try :
                below_group = below_group.split("-")[1]
            except:
                below_group = "..."
        
        dic = {"(1,0)" : group_rank-1,"(1,1)" : above_group,"(1,2)" : above_hotels,"(1,3)" : above_rooms,
               "(2,0)" : group_rank,"(2,1)" : group_name,"(2,2)" : group_hotels,"(2,3)" : group_rooms,
               "(3,0)" : group_rank+1,"(3,1)" : below_group,"(3,2)" : below_hotels,"(3,3)" : below_rooms  
               }
    else :
        if global_group == True :
            below_group_1, below_hotels_1, below_rooms_1 = get_group_below_global(group_name,1,dataframe,global_group = True)
            below_group_2, below_hotels_2, below_rooms_2 = get_group_below_global(group_name,2,dataframe,global_group = True)
        else :
            below_group_1, below_hotels_1, below_rooms_1 = get_group_below_global(group_name,1,dataframe,global_group = False)
            below_group_2, below_hotels_2, below_rooms_2 = get_group_below_global(group_name,2,dataframe,global_group = False)
            
            group_name = group_name.split("-")[1]
            below_group_1 = below_group_1.split("-")[1]
            below_group_2 = below_group_2.split("-")[1]
            
        dic = {"(1,0)" : group_rank,"(1,1)" : group_name,"(1,2)" : group_hotels,"(1,3)" : group_rooms,
               "(2,0)" : group_rank+1,"(2,1)" : below_group_1,"(2,2)" : below_hotels_1,"(2,3)" : below_rooms_1,
               "(3,0)" : group_rank+2,"(3,1)" : below_group_2,"(3,2)" : below_hotels_2,"(3,3)" : below_rooms_2  
               }
    return dic

def fill_country_table(group_name,country,dataframe,template,global_group = True):
    """
    Crée un dictionnaire pour remplir le tableau du classement des chaines/groupes
    dans un pays
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        country: String : le nom du pays
        
        dataframe: Pandas Dataframe : Par construction la fonction ne marche qu'avec
        le fichier Parc_Trip_2022 comme argument
        
        template: Integer : Le modèle de tableau a utilisé en fonction
        du classement du groupe/chaine dans le pays au global
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine.
             
    Renvoit: Dictionnaire
        Dictionnaire contenant les données pour remplir le tableau powerpoint
        de classement national au global
    """
    if global_group == True :
        group_rank = get_group_country_ranking(group_name,country,dataframe,global_group = True)
        group_hotels, group_rooms = get_select_group_country_supply(group_name,country,dataframe,global_group = True)
    else :
        group_rank = get_group_country_ranking(group_name,country,dataframe,global_group = False)
        group_hotels, group_rooms = get_select_group_country_supply(group_name,country,dataframe,global_group = False)
        
    if template == 2 :
        if global_group == True :
            below_group_1, below_hotels_1, below_rooms_1 = get_group_below_country(group_name,country,1,dataframe,global_group = True)
            below_group_2, below_hotels_2, below_rooms_2 = get_group_below_country(group_name,country,2,dataframe,global_group = True)
        else :
            below_group_1, below_hotels_1, below_rooms_1 = get_group_below_country(group_name,country,1,dataframe,global_group = False)
            below_group_2, below_hotels_2, below_rooms_2 = get_group_below_country(group_name,country,2,dataframe,global_group = False)
            
            group_name = group_name.split("-")[1]
            try :
                below_group_1 = below_group_1.split("-")[1]
            except:
                below_group_1 ="..."
            try :
                below_group_2 = below_group_2.split("-")[1]
            except:
                below_group_2 ="..."
        
        dic = {"(1,0)" : group_rank,"(1,1)" : group_name,"(1,2)" : group_hotels,"(1,3)" : group_rooms,
               "(2,0)" : group_rank+1,"(2,1)" : below_group_1,"(2,2)" : below_hotels_1,"(2,3)" : below_rooms_1,
               "(3,0)" : group_rank+2,"(3,1)" : below_group_2,"(3,2)" : below_hotels_2,"(3,3)" : below_rooms_2  
               }
    elif template == 3 :
        if global_group == True :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = True)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = True)
        else :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = False)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = False)
            
            first_group = first_group.split("-")[1]
            group_name = group_name.split("-")[1]
            try :
                below_group = below_group.split("-")[1]
            except:
                below_group = "..."
            
        dic = {"(1,0)" : 1,"(1,1)" : first_group,"(1,2)" : first_hotels,"(1,3)" : first_rooms,
               "(2,0)" : group_rank,"(2,1)" : group_name,"(2,2)" : group_hotels,"(2,3)" : group_rooms,
               "(3,0)" : group_rank+1,"(3,1)" : below_group,"(3,2)" : below_hotels,"(3,3)" : below_rooms  
               }
        
    elif template ==4 :
        if global_group == True :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = True)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = True)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = True)
        else :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = False)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = False)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = False)
            
            first_group = first_group.split("-")[1]
            above_group = above_group.split("-")[1]
            group_name = group_name.split("-")[1]
            try :
                below_group = below_group.split("-")[1]
            except:
                below_group = "..."
            
        dic = {"(1,0)" : 1,"(1,1)" : first_group,"(1,2)" : first_hotels,"(1,3)" : first_rooms,
               "(2,0)" : group_rank-1,"(2,1)" : above_group,"(2,2)" : above_hotels,"(2,3)" : above_rooms,
               "(3,0)" : group_rank,"(3,1)" : group_name,"(3,2)" : group_hotels,"(3,3)" : group_rooms,
               "(4,0)" : group_rank+1,"(4,1)" : below_group,"(4,2)" : below_hotels,"(4,3)" : below_rooms  
               }
        
    elif template ==5 :
        if global_group == True :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = True)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = True)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = True)
        else :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = False)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = False)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = False)
            
            first_group = first_group.split("-")[1]
            above_group = above_group.split("-")[1]
            group_name = group_name.split("-")[1]
            try :
                below_group = below_group.split("-")[1]
            except:
                below_group = "..."
            
        dic = {"(1,0)" : 1,"(1,1)" : first_group,"(1,2)" : first_hotels,"(1,3)" : first_rooms,
               "(2,0)" : "....",
               "(3,0)" : group_rank-1,"(3,1)" : above_group,"(3,2)" : above_hotels,"(3,3)" : above_rooms,
               "(4,0)" : group_rank,"(4,1)" : group_name,"(4,2)" : group_hotels,"(4,3)" : group_rooms,
               "(5,0)" : group_rank+1,"(5,1)" : below_group,"(5,2)" : below_hotels,"(5,3)" : below_rooms  
               }
        
    else :
        if global_group == True :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = True)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = True)
        else:
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = False)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = False)
            
            first_group = first_group.split("-")[1]
            above_group = above_group.split("-")[1]
            group_name = group_name.split("-")[1]
            
        dic = {"(1,0)" : 1,"(1,1)" : first_group,"(1,2)" : first_hotels,"(1,3)" : first_rooms,
               "(2,0)" : "....",
               "(3,0)" : group_rank-1,"(3,1)" : above_group,"(3,2)" : above_hotels,"(3,3)" : above_rooms,
               "(4,0)" : group_rank,"(4,1)" : group_name,"(4,2)" : group_hotels,"(4,3)" : group_rooms,
               "(5,0)" : "...."
               }

    return dic

def fill_country_table_by_segments(group_name,country,dataframe,template,hotels_segment,global_group = True):
    """
    Crée un dictionnaire pour remplir le tableau du classement des chaines
    par segment dans un pays
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        country: String : le nom du pays
        
        dataframe: Pandas Dataframe : Par construction la fonction ne marche qu'avec
        le fichier Parc_Trip_2022 comme argument
        
        template: Integer : Le modèle de tableau a utilisé en fonction
        du classement de la chaine dans le pays sur le segment
        
        hotels_segment: String: Indique le segment hôtelier considéré 
        
        global_group: Booleen True or False: Indique si l'on regarde un
        groupe ou une chaine. Pour cette fonction, ce sera toujours False.
             
    Renvoit: Dictionnaire
        Dictionnaire contenant les données pour remplir le tableau powerpoint
        de classement national sur un segment
    """
    if global_group == True :
        group_rank = get_group_country_ranking(group_name,country,dataframe,global_group = True,segment= hotels_segment)
        group_hotels, group_rooms = get_select_group_country_supply(group_name,country,dataframe,global_group = True,segment= hotels_segment)
    else :
        group_rank = get_group_country_ranking(group_name,country,dataframe,global_group = False,segment= hotels_segment)
        group_hotels, group_rooms = get_select_group_country_supply(group_name,country,dataframe,global_group = False,segment= hotels_segment)
        
    if template == 7 :
        if global_group == True :
            below_group_1, below_hotels_1, below_rooms_1 = get_group_below_country(group_name,country,1,dataframe,global_group = True,segment= hotels_segment)
            below_group_2, below_hotels_2, below_rooms_2 = get_group_below_country(group_name,country,2,dataframe,global_group = True,segment= hotels_segment)
        else :
            below_group_1, below_hotels_1, below_rooms_1 = get_group_below_country(group_name,country,1,dataframe,global_group = False,segment= hotels_segment)
            below_group_2, below_hotels_2, below_rooms_2 = get_group_below_country(group_name,country,2,dataframe,global_group = False,segment= hotels_segment)
            
            group_name = group_name.split("-")[1]
            try :
                below_group_1 = below_group_1.split("-")[1]
            except:
                below_group_1 ="..."
            try :
                below_group_2 = below_group_2.split("-")[1]
            except:
                below_group_2 ="..."
        
        dic = {"(1,0)" : group_rank,"(1,1)" : group_name,"(1,2)" : group_hotels,"(1,3)" : group_rooms,
               "(2,0)" : group_rank+1,"(2,1)" : below_group_1,"(2,2)" : below_hotels_1,"(2,3)" : below_rooms_1,
               "(3,0)" : group_rank+2,"(3,1)" : below_group_2,"(3,2)" : below_hotels_2,"(3,3)" : below_rooms_2  
               }
    elif template == 8 :
        if global_group == True :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = True,segment= hotels_segment)
            try :
                below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = True,segment= hotels_segment)
            except:
                below_group=below_hotels=below_rooms = "..."
        else :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = False,segment= hotels_segment)
            try:
                below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = False,segment= hotels_segment)
            except:
                below_group=below_hotels=below_rooms = "..."
                
            first_group = first_group.split("-")[1]
            group_name = group_name.split("-")[1]
            try :
                below_group = below_group.split("-")[1]
            except:
                below_group ="..."
            
        dic = {"(1,0)" : 1,"(1,1)" : first_group,"(1,2)" : first_hotels,"(1,3)" : first_rooms,
               "(2,0)" : group_rank,"(2,1)" : group_name,"(2,2)" : group_hotels,"(2,3)" : group_rooms,
               "(3,0)" : group_rank+1,"(3,1)" : below_group,"(3,2)" : below_hotels,"(3,3)" : below_rooms  
               }
        
    elif template ==9 :
        if global_group == True :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = True,segment= hotels_segment)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = True,segment= hotels_segment)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = True,segment= hotels_segment)
        else :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = False,segment= hotels_segment)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = False,segment= hotels_segment)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = False,segment= hotels_segment)
            
            first_group = first_group.split("-")[1]
            above_group = above_group.split("-")[1]
            group_name = group_name.split("-")[1]
            try :
                below_group = below_group.split("-")[1]
            except:
                below_group = "..."
            
        dic = {"(1,0)" : 1,"(1,1)" : first_group,"(1,2)" : first_hotels,"(1,3)" : first_rooms,
               "(2,0)" : group_rank-1,"(2,1)" : above_group,"(2,2)" : above_hotels,"(2,3)" : above_rooms,
               "(3,0)" : group_rank,"(3,1)" : group_name,"(3,2)" : group_hotels,"(3,3)" : group_rooms,
               "(4,0)" : group_rank+1,"(4,1)" : below_group,"(4,2)" : below_hotels,"(4,3)" : below_rooms  
               }
        
    elif template ==10 :
        if global_group == True :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = True,segment= hotels_segment)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = True,segment= hotels_segment)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = True,segment= hotels_segment)
        else :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = False,segment= hotels_segment)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = False,segment= hotels_segment)
            below_group, below_hotels, below_rooms = get_group_below_country(group_name,country,1,dataframe,global_group = False,segment= hotels_segment)
            
            first_group = first_group.split("-")[1]
            above_group = above_group.split("-")[1]
            group_name = group_name.split("-")[1]
            try :
                below_group = below_group.split("-")[1]
            except:
                below_group = "..."
            
        dic = {"(1,0)" : 1,"(1,1)" : first_group,"(1,2)" : first_hotels,"(1,3)" : first_rooms,
               "(2,0)" : "....",
               "(3,0)" : group_rank-1,"(3,1)" : above_group,"(3,2)" : above_hotels,"(3,3)" : above_rooms,
               "(4,0)" : group_rank,"(4,1)" : group_name,"(4,2)" : group_hotels,"(4,3)" : group_rooms,
               "(5,0)" : group_rank+1,"(5,1)" : below_group,"(5,2)" : below_hotels,"(5,3)" : below_rooms  
               }
        
    else :
        if global_group == True :
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = True,segment= hotels_segment)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = True,segment= hotels_segment)
        else:
            first_group, first_hotels, first_rooms = country_number_one_group(country,dataframe,global_group = False,segment= hotels_segment)
            above_group, above_hotels, above_rooms = get_group_above_country(group_name,country,1,dataframe,global_group = False,segment= hotels_segment)
            
            first_group = first_group.split("-")[1]
            above_group = above_group.split("-")[1]
            group_name = group_name.split("-")[1]
            
        dic = {"(1,0)" : 1,"(1,1)" : first_group,"(1,2)" : first_hotels,"(1,3)" : first_rooms,
               "(2,0)" : "....",
               "(3,0)" : group_rank-1,"(3,1)" : above_group,"(3,2)" : above_hotels,"(3,3)" : above_rooms,
               "(4,0)" : group_rank,"(4,1)" : group_name,"(4,2)" : group_hotels,"(4,3)" : group_rooms,
               "(5,0)" : "...."
               }

    return dic

def is_country_last(group_name,country,dataframe,global_group = True,segment = None) :
    """
    Indique si un groupe\chaine est classé dernier dans un pays au global
    ou sur un segment
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        country: String : le nom du pays
        
        dataframe: Pandas Dataframe : Par construction la fonction ne marche qu'avec
        le fichier Parc_Trip_2022 comme argument
        
        global_group: Booleen True ou False : Indique si l'on regarde un
        groupe ou une chaine
        
        segment: String ou None: Indique le segment hôtelier considéré ou None
        si pas de segment    
        
    Renvoit: Booleen
        True ou False si le groupe/chaine est dernier ou non
    """
    if global_group == True :
        rank = get_group_country_ranking(group_name,country,dataframe,segment,global_group = True)
        number_groups = country_number_groups(country,dataframe,segment,global_group = True)
    else :
        rank = get_group_country_ranking(group_name,country,dataframe,segment,global_group = False)
        number_groups = country_number_groups(country,dataframe,segment,global_group = False)
    if rank == number_groups :
        return True 
    else:
        return False
    
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
    df = df.loc[df['Rooms 2022'] != 0]
    liste_brands = list(df["Brands Final"].unique())
    return liste_brands

def new_country_to_use(group_name,dataframe,global_group = True) :
    """
    Definit le nouveau pays de référence à utiliser si 
    un groupe/chaine n'a pas d'hotels dans le pays de sa nationalite
    
    Arguments:
        group_name: String: Le nom d'un groupe ou d'une chaine issu 
        de la colonne "Groups" ou "Brands Final" du fichier Parc_Trip_2022
        Par exemple : "ACCOR" ou "ACCOR-IBIS"
        
        dataframe: Pandas Dataframe : Par construction la fonction ne marche qu'avec
        le fichier Parc_Trip_2022 comme argument
        
        global_group: Booleen True ou False : Indique si l'on regarde un
        groupe ou une chaine
        
    Renvoit: String
        Le pays dans lequel le groupe/chaine a le plus de chambres
    """
    if global_group == True :
        column = "Groups"
    else:
        column = "Brands Final"
    try :
        df = dataframe.loc[dataframe['{}'.format(column)] == group_name]
        df = df.loc[df['Rooms 2022'] != 0]
        df = df.sort_values(by='Rooms 2022', ascending=False, na_position='last')
        new_country = list(df["Country"])[0]
        return new_country
    except:
        print(traceback.format_exc())

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
