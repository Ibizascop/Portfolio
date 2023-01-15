import pandas as pd
import numpy as np
from osgeo import ogr
from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsProject , QgsDataSourceUri
from tqdm import tqdm

#function to remove every layer except those specified
def RemoveAllLayersExcept(*keep_layers):
    layers = QgsProject.instance().mapLayers().values()
    will_be_deleted = [l for l in layers if l not in keep_layers]
    for layer in will_be_deleted:
        QgsProject.instance().removeMapLayer(layer)

#function to create map for a specific year
def create_year_map(year) :
    """
    Fonction prenant en paramètre une valeur correspondant soit à une année 
    en tant que nombre ou autre, afin de notamment filtrer les gites
    ayant été labellisés au cours de cette anéne. Si la valeur n'est pas un nombre, 
    le filtre sera ignoré.
    
    Arguments:
        year : Integer : Une année
       
    Renvoit: Null
        Crée une Carte QGIS représentant la capacité d'accueil des gites
        labellisés au cours de l'année spécificiée par communes.
    """
    #Change CRS
    QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(3857))

    #Create a Group for Legend
    groupName=f"{year}"
    root = QgsProject.instance().layerTreeRoot()
    group = root.addGroup(groupName)

    #Load Openstreet Map
    tms = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0'
    osm_layer = QgsRasterLayer(tms,'OSM', 'wms')
    QgsProject.instance().addMapLayer(osm_layer)
    
    #Add OSM Layer to group for clean export (Every other layer after will be automatically added
    #In the group
    root = QgsProject.instance().layerTreeRoot()
    old_layer = root.findLayer(osm_layer.id())
    clone = old_layer.clone()
    group.insertChildNode(0, clone)
    root.removeChildNode(old_layer)

    #Load cities layer from local postgis database
    uri = QgsDataSourceUri()
    uri.setConnection("localhost", "5432", "postgis",username, password)
    uri.setDataSource("public", "communes_france", "geom")
    cities_layer = QgsVectorLayer(uri.uri(), f"{year}", "postgres")
    QgsProject.instance().addMapLayer(cities_layer)
    cities_layer.loadNamedStyle("style_communes.qml")
        
    #Load csv data with the gites, filter by date and group by INSEE code
    table = pd.read_csv("data_gites.csv",sep ="\t")
    table['DATE_LABEL'] = table['DATE_LABEL'].fillna(0).astype(np.int64)
    if type(year) == int
        table= table.loc[table["DATE_LABEL"]==year]
    table = table.groupby(["Code Insee Texte"],as_index=False)[["CAPACITE_PERSONNES"]].sum()
    table = table.reset_index(drop=True)
    clean_insee = lambda insee : "0"+insee if(len(insee) == 4) else insee
    table["clean_insee"] = table["Code Insee Texte"].apply(clean_insee)

    #Create temporary table
    flist = list(table.columns)
    vl = QgsVectorLayer("None", "gites", "memory")
    pr = vl.dataProvider()
    vl.startEditing()

    #Specify columns types
    types_col = [QVariant.String,QVariant.Int,QVariant.String]
    fieldlist = []
    for fieldname, type_col in zip(flist,types_col) :
        fieldlist.append(QgsField(fieldname,type_col))

    #Add dataframe Data to table
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

    #Join table to cities layer
    csvField='clean_insee'
    shpField='insee'
    joinObject=QgsVectorLayerJoinInfo()
    joinObject.setJoinFieldName(csvField)
    joinObject.setTargetFieldName(shpField)
    joinObject.setJoinLayerId(vl.id())
    joinObject.setUsingMemoryCache(True)
    joinObject.setJoinLayer(vl)
    cities_layer.addJoin(joinObject)
    cities_layer.triggerRepaint()

    #Collapse Legend for clean export
    nodes = root.children()
    for n in nodes:
        if isinstance(n, QgsLayerTreeGroup):
            if n.isExpanded() == True:
                n.setExpanded(False)
                print(f"Layer group '{n.name()}' now collapsed.")
                
    ###LAYOUT COMPOSING
    document = QDomDocument()
    project = QgsProject.instance()
    composition = QgsPrintLayout(project)

    layout = QgsLayout(project)
    layout.initializeDefaults()
    # read template content
    qpt_path = "mise_en_page_gites.qpt"
    layout_name = "mise_en_page_gites"
        
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
    exporter.exportToImage(".\Cartes\{}.png".format(year), QgsLayoutExporter.ImageExportSettings())

    #Remove layers and group legend
    RemoveAllLayersExcept()
    root.removeChildNode(group)

#Create all the Maps
years = list(pd.read_csv("data_gites.csv",sep ="\t")["DATE_LABEL"].unique())
years = [int(year) for year in years if not np.isnan(year)]
years.append("Total")
for year in tqdm(years) :
    create_year_map(year)
