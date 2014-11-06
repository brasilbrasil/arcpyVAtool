#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!

#USER INPUT
datadir=r"C:/Users/lfortini/Downloads/" #whichever is data dir, will have to have subfolders: la/DEM/ (where DEM based layers go), gaplandcover/ (where gaplandcov_hi is placed)

import arcpy
import arcpy.sa
from arcpy import env

arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
arcpy.env.compression = "LZW"

if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")
outras=arcpy.sa.SetNull("lafa_flow2.tif", "lafa_flow2.tif", "Value < 1")
loc_outras="young_lava_flow_map.tif"
arcpy.CopyRaster_management(outras, loc_outras, "", "0", "0", "", "", "2_BIT", "", "")

arcpy.CheckInExtension("Spatial")

