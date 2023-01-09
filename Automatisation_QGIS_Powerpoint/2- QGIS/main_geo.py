import pandas as pd
import support_geo as sp
from tqdm import tqdm

from osgeo import ogr
from qgis.utils import iface

def create_map(group_name) :
    """
    Fonction prenant en argument le nom d'un groupe hôtellier/d'une chaine d'un groupe
    et créant une carte PNG via QGIS. La carte donne les informations
    suivantes :
        - Pour tous les pays du monde : le nombre de chambres d'hôtels global
        fin 2022, (Source : Différents organismes statistiques) via la couleur 
        des polygones des pays

        - Pour le groupe/chaine, via les centroides : Le % représenté
        par chaque pays dans l'offre global du groupe/chaine est indiqué
        par la taille des points.

        - Pour le groupe/chaine, via les centroides : La part de marché 
        (au global si groupe, sur le segment si chaine) dans les différents pays
        est représenté par la couleur des points

    Arguments:
        group_name: String: Le nom d'un groupe issu 
        de la colonne "Groups" du fichier Parc_Trip_2022.xlsx
        Par exemple : "ACCOR" 
        
    Renvoit: PNG
        Renvoit une carte QGIS sous format PNG avec le nom du groupe stockée
        dans le dossier 2-QGIS\CARTES
    """
    df = pd.read_excel("..\DATA\PARC_TRIP_2022.xlsx")
    #For Group and each brand
    liste_brands = sp.list_brands(group_name,df)
    if len(liste_brands) == 1 :
        limit = 1
    else :
        limit = len(liste_brands) + 1
    for map_number in range(0,limit) :
        #Group or Brand
        if map_number != 0 : 
            global_group = False
            group_name = liste_brands[map_number-1]
            segment = sp.get_segment(group_name,df)
        else :
            global_group = True
            segment = None
        try : 
            #Load global supply gpkg
            gpkg = ".\GEO\pays_final_geo.gpkg"
            global_layer = sp.add_gpkg_layer(gpkg,"pays_final_geo","global_layer")
            global_layer.loadNamedStyle(".\STYLES\global rooms.qml")
            global_layer.triggerRepaint()

            #Load dots GPKG
            gpkg = ".\GEO\\bulles_geo.gpkg"
            bulles_layer = sp.add_gpkg_layer(gpkg,"bulles_geo","bulles_layer")
            bulles_layer.loadNamedStyle(".\STYLES\\bulles.qml")

            #Load df and prepare it for joint
            table = sp.prepare_group_data(group_name,df,global_group,segment)

            #ADD GROUPED DATAFRAME AS TABLE
            #Create temporary table
            flist = list(table.columns)
            vl = QgsVectorLayer("None", "group_table", "memory")
            pr = vl.dataProvider()
            vl.startEditing()

            #Specify columns types
            types_col = [QVariant.String,QVariant.String,QVariant.Int,QVariant.Int,
                        QVariant.Int,QVariant.Int,QVariant.Int,QVariant.Int,
                        QVariant.Int,QVariant.Int,QVariant.Int,QVariant.Int,
                        QVariant.Int,QVariant.Int,QVariant.String,QVariant.Double,QVariant.Double]
            fieldlist = []
            for fieldname, type_col in zip(flist,types_col) :
                fieldlist.append(QgsField(fieldname,type_col))

            #Add Data to table
            pr.addAttributes(fieldlist)
            vl.updateFields()
            for i in table.index.to_list():
                fet = QgsFeature()
                newrow = table[flist].iloc[i].tolist()
                newrow = [c.item() if hasattr(c, 'item') else c for c in newrow]
                fet.setAttributes(newrow)
                pr.addFeatures([ fet ])
            vl.commitChanges()
            #Add table to project
            QgsProject.instance().addMapLayer(vl)

            #Joindre table au centroide
            csvField='Country'
            shpField='NAME_ENGL'
            joinObject=QgsVectorLayerJoinInfo()
            joinObject.setJoinFieldName(csvField)
            joinObject.setTargetFieldName(shpField)
            joinObject.setJoinLayerId(vl.id())
            joinObject.setUsingMemoryCache(True)
            joinObject.setJoinLayer(vl)
            bulles_layer.addJoin(joinObject)
            bulles_layer.triggerRepaint()

            ###LAYOUT COMPOSING
            document = QDomDocument()
            project = QgsProject.instance()
            composition = QgsPrintLayout(project)

            layout = QgsLayout(project)
            layout.initializeDefaults()
            # read template content
            if sp.has_europe_supply(group_name,df,global_group) :
                qpt_path = ".\MISES EN PAGE\mise_en_page_europe.qpt"
                layout_name = "Main-europe"
            elif sp.has_asia_supply(group_name,df,global_group) :
                qpt_path = ".\MISES EN PAGE\mise_en_page_asie.qpt"
                layout_name = "Main-asia"
            else :
                qpt_path = ".\MISES EN PAGE\mise_en_page.qpt"
                layout_name = "Main"
                
            template_file = open(qpt_path)
            template_content = template_file.read()
            template_file.close()
            document.setContent(template_content)
            items, ok = layout.loadFromTemplate(document, QgsReadWriteContext(), False)

            # load layout from template and add to Layout Manager
            
            composition.loadFromTemplate(document, QgsReadWriteContext())
            project.layoutManager().addLayout(composition)
            layout = project.layoutManager().layoutByName(layout_name)


            exporter = QgsLayoutExporter(layout)
            exporter.exportToImage(".\CARTES\{}.png".format(group_name), QgsLayoutExporter.ImageExportSettings())
            
            #qgs.exitQgis()
            with open("done.txt","a") as file :
                print(group_name, file=file)
            sp.RemoveAllLayersExcept()
        except Exception as e:
            with open("exception.txt","a") as file :
                print(e, file = file)
            sp.RemoveAllLayersExcept()

#Lancer toutes les cartes pas encore faites
try :
    with open("done.txt","r") as flog :
        done_groups = flog.readlines()
        done_groups = [name.replace("\n","") for name in done_groups]
except:
    done_groups = []
    
groups = list(pd.read_excel("..\DATA\PARC_TRIP_2022.xlsx")["Groups"].unique())
groups = [group for group in groups if group not in done_groups]

for group_name in tqdm(groups) :
    create_map(group_name)
