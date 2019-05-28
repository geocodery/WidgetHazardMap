import sys
# ONLY USE IN GEOPROCESSIN SERVICE
sys.path.insert(0, r'D:\\aplicaciones\\geoproceso\\exportWebMapTask')
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *
import json
import arcpy
import os
import uuid
import time

arcpy.env.overwriteOutput = True

pathTemplates = r'C:\plantillas\plantillas_dgar'
pathGeoproceso = r'D:\aplicaciones\geoproceso\exportWebMapTask'

class exportWebMapTask(object):
    def __init__(self, Web_Map_as_JSON, Format, Layout_Template):
        self.wmj         = Web_Map_as_JSON
        self.format      = Format
        self.lyttemplate = Layout_Template
        self.scratch     = arcpy.env.scratchGDB
        self.pathzonas   = os.path.join(pathGeoproceso, r'HM_Hazard.gdb\GPO_ZonasUTM')
        self.lineLyr     = os.path.join(pathGeoproceso, r'lyr\LYR_HM_LineMovMasa.lyr')

    def acondicionaJson(self, dicc):
        # arcpy.AddMessage(dicc)
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

        array = arcpy.Array([arcpy.Point(e["xmax"], e["ymax"]),
        arcpy.Point(e["xmax"], e["ymin"]),
        arcpy.Point(e["xmin"], e["ymin"]),
        arcpy.Point(e["xmin"], e["ymax"])
        ])
        self.polygon = arcpy.Polygon(array, arcpy.SpatialReference(102100))

        return outputJson

    def extractTitleMap(self):
        if self.wmj not in ("", "#"):
            dicc = json.loads(self.wmj)
            self.wmj = self.acondicionaJson(dicc)
        else:
            dicc = {"msg": "true"}
        self.maptitle = dicc["layoutOptions"]['titleText'] if dicc.has_key("layoutOptions") else "ArcGIS Web Map"
        # arcpy.AddMessage(self.maptitle)

    def extractZone(self):
        point = arcpy.Point(self.xy[0], self.xy[1])
        pt = arcpy.PointGeometry(point, arcpy.SpatialReference(102100))
        zonas = arcpy.MakeFeatureLayer_management(self.pathzonas, "zonas")
        zonaSelect = arcpy.SelectLayerByLocation_management("zonas", 'INTERSECT', pt, '#', 'NEW_SELECTION', 'NOT_INVERT')
        zona = [x[0] for x in arcpy.da.SearchCursor(zonaSelect, ["Zona"])][0]
        return zona

    def extractTipoPeligro(self):
        arcpy.AddMessage([x.name for x in arcpy.mapping.ListLayers(self.mxd, "Poligonos", self.df)])
        peligros = arcpy.mapping.ListLayers(self.mxd, "Poligonos", self.df)[0]
        peligrosSelect = arcpy.SelectLayerByLocation_management(peligros, 'INTERSECT', self.polygon, '#', 'NEW_SELECTION', '#')
        peligro = [int(x[0]) for x in arcpy.da.SearchCursor(peligros, ["TIPO"])]
        arcpy.AddMessage(peligro)
        return peligro

    def changeGridZone(self, zone):
        if zone == u'Z-17':
            self.df.spatialReference = arcpy.SpatialReference(32717)
        elif zone == u'Z-18':
            self.df.spatialReference = arcpy.SpatialReference(32718)
        elif zone == u'Z-19':
            self.df.spatialReference = arcpy.SpatialReference(32719)
        arcpy.RefreshActiveView()

    def updateScale(self, df, lyrLeyenda):  
        # df.extent = lyrLeyenda.getSelectedExtent()
        newExtent = df.extent
        newExtent.XMin, newExtent.YMin = -0.025, -0.0245
        newExtent.XMax, newExtent.YMax = 0.036, 0.007
        df.extent = newExtent
        # df.scale = df.scale*1.2
        arcpy.RefreshActiveView()

    def selectTipoPeligro(self, listTipo):
        df = arcpy.mapping.ListDataFrames(self.mxd, "Leyenda")[0]
        ptLeyenda = arcpy.mapping.ListLayers(self.mxd, "GPT_HM_Leyenda")[0]
        arcpy.DeleteRows_management(ptLeyenda)
        xini = 0
        yini = 0
        rowx = 0
        rowy = 0
        cursor = arcpy.da.InsertCursor(ptLeyenda, ["SHAPE@X", "SHAPE@Y", "TIPO"])
        for i in range(len(listTipo)):
            cursor.insertRow([xini + rowx, yini + rowy, listTipo[i]])
            if len(listTipo) > 1:
                rowy = rowy - 0.004
                if i == 7:
                    rowy = 0
                    rowx = 0.032
        del cursor
        arcpy.RefreshActiveView()

        self.updateScale(df, ptLeyenda)

    def selectTemplate(self):
        # zona = self.extractZone()

        if self.lyttemplate == '#' or not self.lyttemplate:
            self.lyttemplate = 'A4-Horizontal'

        if self.format == "#" or not self.format:
            self.format = "PDF"

        arcpy.AddMessage(os.path.join(pathTemplates, '{}.mxd'.format(self.lyttemplate)))

        template_mxd = os.path.join(pathTemplates, '{}.mxd'.format(self.lyttemplate))
        proyecto = arcpy.mapping.ConvertWebMapToMapDocument(self.wmj, template_mxd)
        self.mxd = proyecto.mapDocument
        self.df = arcpy.mapping.ListDataFrames(self.mxd)[2]
        arcpy.AddMessage(self.df.name)

        # peligro = self.extractTipoPeligro()
        # peligro = list(set(peligro))

        # self.selectTipoPeligro(peligro)
        # self.changeGridZone(zona)

        # update_layer = arcpy.mapping.ListLayers(self.mxd, 'SimbologiaPeligros_9341', self.df)
        # update_layer = update_layer[0]
        # source_layer = arcpy.mapping.Layer(self.lineLyr)
        # arcpy.mapping.UpdateLayer(self.df, update_layer, source_layer, symbology_only = True)

        # try:
        #     self.removeLayers()
        # except Exception as e:
        #     pass

    def saveCopyMxd(self, name):
        copia = os.path.join(pathGeoproceso, 'Map{}.mxd'.format(name))
        self.mxd.saveACopy(copia)

    def removeLayers(self):
        listlayers = [x for x in arcpy.mapping.ListLayers(self.mxd)]
        if len(listlayers) > 0:
            for x in listlayers:
                if x.name[:13] == "graphicsLayer":
                    arcpy.mapping.RemoveLayer(self.df, x)
                if x.name.lower() in ["simbologiapeligros", "simbologiapeligros - gpt_hm_movmasa", "simbologiapeligros - gpl_hm_movmasa", "simbologiapeligros - gpo_hm_movmasa"]:
                    arcpy.mapping.RemoveLayer(self.df, x)
        arcpy.RefreshActiveView()

    def exportMap(self):
        namepdf = str(uuid.uuid4())
        if self.format == "PDF":
            salida = os.path.join(arcpy.env.scratchFolder, 'Map{}.pdf'.format(namepdf))
            arcpy.mapping.ExportToPDF(self.mxd, salida, "PAGE_LAYOUT")
        else:
            salida = os.path.join(arcpy.env.scratchFolder, 'Map{}.png'.format(namepdf))
            arcpy.mapping.ExportToPNG(self.mxd,  salida, "PAGE_LAYOUT", resolution=200)
        # self.saveCopyMxd(namepdf)
        return salida

    # ***************************************************************************

    def main(self):
        self.extractTitleMap()
        self.selectTemplate()
        Output_File = self.exportMap()
        arcpy.SetParameterAsText(3, Output_File)