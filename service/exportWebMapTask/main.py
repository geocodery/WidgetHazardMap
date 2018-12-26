import sys
# ONLY USE IN GEOPROCESSIN SERVICE
sys.path.insert(0, r'D:\\aplicativos\\geoprocesos\\exportWebMapTask')
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *
import json
import arcpy
import os
import uuid
import time

arcpy.env.overwriteOutput = True

# directorio = r'D:\RYali\TDR3\3Product')
directorio = r'C:\plantillas_dgar'

class exportWebMapTask(object):
    def __init__(self, Web_Map_as_JSON, Format, Layout_Template):
        self.wmj         = Web_Map_as_JSON
        self.format      = Format
        self.lyttemplate = Layout_Template
        self.scratch     = arcpy.env.scratchGDB

    def acondicionaJson(self, dicc):
        arcpy.AddMessage(dicc)
        for x in dicc["operationalLayers"]:
            if x.has_key("featureCollection"):
                if x["featureCollection"].has_key("layers"):
                    for m in x["featureCollection"]["layers"]:
                        if m.has_key("featureSet"):
                            if m["featureSet"].has_key("features"):
                                for n in m["featureSet"]["features"]:
                                    if n.has_key("symbol"):
                                        symbol = "symbol" if n["symbol"].has_key("color") else ""
                                        outline_tmp = n["symbol"]["outline"] if n["symbol"].has_key("outline") else {
                                            "msg": "msg"}
                                        outline = "outline" if outline_tmp.has_key("color") else ""
                                        info = [symbol, outline]
                                        for x in info:
                                            if x == "symbol":
                                                n["symbol"]["color"] = ["220", "220", "220", "255"]
                                            elif x == "outline":
                                                n["symbol"]["outline"]["color"] = ["220", "220", "220", "255"]
        outputJson = json.dumps(dicc)
        e = dicc["mapOptions"]["extent"]
        self.xy = [(e["xmax"] + e["xmin"])/2, (e["ymax"] + e["ymin"])/2]
        return outputJson

    def extractTitleMap(self):
        if self.wmj not in ("", "#"):
            dicc = json.loads(self.wmj)
            self.wmj = self.acondicionaJson(dicc)
        else:
            dicc = {"msg": "true"}
        self.maptitle = dicc["layoutOptions"]['titleText'] if dicc.has_key("layoutOptions") else "ArcGIS Web Map"
        arcpy.AddMessage(self.maptitle)

    def seleccionarPlantilla(self):
        if self.lyttemplate == '#' or not self.lyttemplate:
            self.lyttemplate = 'A4-Horizontal'

        if self.format == "#" or not self.format:
            self.format = "PDF"

        template_mxd = os.path.join(directorio, '{}.mxd'.format(self.lyttemplate))
        proyecto = arcpy.mapping.ConvertWebMapToMapDocument(self.wmj, template_mxd)
        self.mxd = proyecto.mapDocument
        self.df = arcpy.mapping.ListDataFrames(self.mxd)[2]
        # refLayer = [x.name.lower() for x in arcpy.mapping.ListLayers(self.mxd, "", self.df)][0]
        # # refLayer = "simbologiapeligros - gpo_hm_movmasa"

        update_layer = arcpy.mapping.ListLayers(self.mxd, 'Peligros - lineas', self.df)[0]
        source_layer = arcpy.mapping.Layer(r'D:\aplicativos\geoprocesos\exportWebMapTask\lyr\LYR_HM_LineMovMasa.lyr')
        arcpy.mapping.UpdateLayer(self.df, update_layer, source_layer, symbology_only = True)

        try:
            self.removerLayers()
        except Exception as e:
            pass
        # try:
        #     self.removeFromLegend()
        # except Exception as e:
        #     raise e

    def almacenarCopiaMXD(self, name):
        copia = os.path.join("D:\\aplicativos\\geoprocesos\\exportWebMapTask", 'Map{}.mxd'.format(name))
        self.mxd.saveACopy(copia)

    def ordenarLayers(self, capaAmover, capaSobrecualmover):
        for lyr in arcpy.mapping.ListLayers(self.mxd, "", self.df):
            if lyr.name.lower() == capaAmover:
                moveLayer = lyr
            if lyr.name.lower() == capaSobrecualmover:
                refLayer = lyr
        if refLayer:
            arcpy.mapping.MoveLayer(self.df, refLayer, moveLayer, "BEFORE")
            arcpy.RefreshActiveView()

    def removerLayers(self):
        listlayers = [x for x in arcpy.mapping.ListLayers(self.mxd)]
        if len(listlayers) > 0:
            for x in listlayers:
                if x.name[:13] == "graphicsLayer":
                    arcpy.mapping.RemoveLayer(self.df, x)
                if x.name.lower() in ["simbologiapeligros", "simbologiapeligros - gpt_hm_movmasa", "simbologiapeligros - gpl_hm_movmasa", "simbologiapeligros - gpo_hm_movmasa"]:
                    arcpy.mapping.RemoveLayer(self.df, x)
        arcpy.RefreshActiveView()

    def removeFromLegend(self):
        legend = arcpy.mapping.ListLayoutElements(self.mxd, "LEGEND_ELEMENT")[0]
        for lyr in legend.listLegendItemLayers():
            # if lyr.name.lower() in ["puntos", "lineas", "poligonos", "simbologiapeligros - gpo_hm_movmasa", "peligros - puntos", "peligros - lineas", "peligros - poligonos"]:
            if lyr.name.lower() in ["peligros - puntos", "peligros - lineas", "peligros - poligonos"]:
                legend.removeItem(lyr)
        arcpy.RefreshActiveView()

        # for lyr in legend.listLegendItemLayers():
        #     if lyr.name == "SimbologiaPeligros - GPO_HM_MovMasa":
        #         legend.removeItem(lyr)
        # arcpy.RefreshActiveView()

    def updateNames(self):
        distpath = os.path.join(CONN, 'DATA_GIS.GPO_DEP_DISTRITO')
        dist = arcpy.MakeFeatureLayer_management(distpath, "dist")

        puntoTemp = os.path.join(self.scratch, "pt")
        if arcpy.Exists(puntoTemp):
            pt = arcpy.MakeFeatureLayer_management(puntoTemp, "pt")
        else:
            pt = arcpy.CreateFeatureclass_management(self.scratch, "pt", "POINT", "#", "DISABLED", "DISABLED", arcpy.SpatialReference(4326))
        with arcpy.da.InsertCursor(pt, ["SHAPE@X", "SHAPE@Y"]) as cursor:
            cursor.InsertRow(self.xy)
        sel = arcpy.SelectLayerByLocation_management(dist, "INTERSECT", pt, "#", "NEW_SELECTION", "NOT_INVERT")
        ubic = [x for x in arcpy.da.SearchCursor(sel, ["NM_DIST", "NM_PROV", "NM_DEPA"])]

        ElementoTexto1 = arcpy.mapping.ListLayoutElements(self.mxd, "TEXT_ELEMENT", "UBICACION")[0]
        location = u'Evaluacion tecnica a Pitucona \n(Distrito de {}, provincia {}, \nregion {})'.format(ubic[0], ubic[1], ubic[2])
        ElementoTexto1.text = location
        

    def exportarMapa(self):
        namepdf = str(uuid.uuid4())
        if self.format == "PDF":
            salida = os.path.join(arcpy.env.scratchFolder, 'Map{}.pdf'.format(namepdf))
            arcpy.mapping.ExportToPDF(self.mxd, salida, "PAGE_LAYOUT")
        else:
            salida = os.path.join(arcpy.env.scratchFolder, 'Map{}.png'.format(namepdf))
            arcpy.mapping.ExportToPNG(self.mxd,  salida, "PAGE_LAYOUT", resolution=200)
        self.almacenarCopiaMXD(namepdf)
        return salida

    # ***************************************************************************

    def main(self):
        self.extractTitleMap()
        self.seleccionarPlantilla()
        Output_File = self.exportarMapa()
        arcpy.SetParameterAsText(3, Output_File)
