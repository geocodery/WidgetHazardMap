import sys, os
# ONLY USE IN GEOPROCESSING SERVICE

# Ruta del servicio
sys.path.insert(0, r'D:\\aplicativos\\geoprocesos\\exportWebMapTask')

import main

if __name__ == "__main__":
    Web_Map_as_JSON  = arcpy.GetParameterAsText(0)  # JSON DEL ESTADO ACTUAL DEL MAPA WEB
    Format           = arcpy.GetParameterAsText(1)  # DEFINIR ENTRE PNG, PDF, etc.
    Layout_Template  = arcpy.GetParameterAsText(2)  # DEFINIR COMO OPCIONAL Y DEJAR EN BLANCO

    poo = main.HazardMap(Web_Map_as_JSON, Format, Layout_Template)
    poo.main()


