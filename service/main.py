import sys
sys.path.insert(0, r'D:\\aplicativos\\geoprocesos\\hazardmap')

from config import *
import arcpy
import os

arcpy.env.overwriteOutput = True

class HazarMap(object):
    def __init__(self, *args):
        self.este = args[0]
        self.norte = args[1]
        self.zona = args[2]
        self.radio = args[3]

    def function():
    	pass