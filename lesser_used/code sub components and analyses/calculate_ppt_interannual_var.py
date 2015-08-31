import os
import arcpy
import arcpy.sa
import math
import shutil
import arcgisscripting
from types import *
import time
import traceback
import sys
#from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/
from arcpy import env

wd="Y:/PICCC_data/climate_data/rainfall_hindcast/Month_Rasters_State_mm/Annual/"
arcpy.env.overwriteOutput = True
arcpy.env.workspace = wd
arcpy.env.compression = "LZW"
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")

annual_rasters=arcpy.ListRasters("stann_*")



arcpy.CheckInExtension("Spatial") # Check in the 3D Analyst extension so other users can access it

