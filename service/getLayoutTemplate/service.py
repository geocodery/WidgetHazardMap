import sys
# ONLY USE IN GEOPROCESSING SERVICE

# Ruta del servicio
sys.path.insert(0, r'D:\\aplicativos\\geoprocesos\\getLayoutTemplate')
import main

if __name__ == "__main__":
    folderTemplate = arcpy.GetParameterAsText(0)
    poo = main.GetTemplates(folderTemplate)
    poo.main()
    # mxds = arcpy.GetLayoutTemplatesInfo_server(folderTemplate)
    # arcpy.SetParameterAsText(1, mxds)
