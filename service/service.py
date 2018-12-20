import sys
#sys.path.insert(0, r'F://x_hcastro//geocatmin//geoprocesos_py//geocatminMapasCatastrales//scripts')
sys.path.insert(0, r'D:\\aplicativos\\geoprocesos\\hazardmap')

import main

if __name__ == '__main__':
	try:		
		este = arcpy.GetParameterAsText(0)			# Agregar parametros
		norte = arcpy.GetParameterAsText(1)			# Agregar parametros
		zona = arcpy.GetParameterAsText(2)			# Agregar parametros
		radio = arcpy.GetParameterAsText(3)			# Agregar parametros
		arcpy.AddMessage('ejecuta')
		
		poo = main.HazarMap()						# Agregar parametros
		poo.main()									# Agregar parametros
		
	except Exception as e:
		arcpy.AddMessage('Error')
		arcpy.AddError('//n//t%s//n' % e.message)
		