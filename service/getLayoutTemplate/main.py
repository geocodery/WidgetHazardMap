import sys
# ONLY USE IN GEOPROCESSIN SERVICE
sys.path.insert(0, r'D:\\aplicativos\\geoprocesos\\getLayoutTemplate')

import arcpy
import json
import os

arcpy.env.overwriteOutput = True

class GetTemplates(object):
    def __init__(self, folderTemplate):
        self.folder = folderTemplate

    def GetTemplatesInfo(self):
        arcpy.AddMessage(self.folder)
        templates = arcpy.GetLayoutTemplatesInfo_server(self.folder)
        j = json.dumps(templates[0])
        j2 = j.replace("activeDataFrameSize", "webMapFrameSize")
        j2 = j2.replace("\\\\n", "")
        j2 = j2.replace("\\\\", "")
        j2 = j2.replace("\\", "")
        j2 = j2.replace(" ", "")
        return j2

    def process(self):
        templates = self.GetTemplatesInfo()
        arcpy.SetParameterAsText(1, templates)

    def main(self):
        if self.folder in ("#", "0", 0, None, ""):
            pass
        else:
            self.process()