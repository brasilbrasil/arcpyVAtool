wd="Y:/PICCC_data/VA data/Phase2/hab_data/"
#landscapeDataDir="Y:/PICCC_data/VA data/landscape/"
#buffer_dist=100
#must have final output as 1 edge, 2 core, null all else

#START UNDERHOOD
import os
import arcpy
import arcpy.sa
import sys
#from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/
from arcpy import env
from random import randrange


jnk=randrange(10000)
arcpy.env.overwriteOutput = True
arcpy.env.workspace = wd+"CAH_GISData_v1.gdb"
arcpy.env.compression = "LZW"
arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"

if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")

Roads_TigerLine_raster=arcpy.Raster("Roads_TigerLine_raster")
HI_dem=arcpy.Raster("hi_dem")
habqual_v3_4=arcpy.Raster("habqual_v3_4")
HIGAP_22Sep14=arcpy.Raster("HIGAP_22Sep14")
island=arcpy.sa.SetNull(habqual_v3_4,1,"Value < 1")
habqual_v3_4_ugly=arcpy.sa.SetNull(habqual_v3_4,1,"Value <> 1")
habqual_v3_4_bare=arcpy.sa.SetNull(habqual_v3_4,1,"Value <> 4")
habqual_v3_4_ugly=habqual_v3_4_ugly*island
habqual_v3_4_bare=habqual_v3_4_bare*island

raster_loc=wd+"Roads_TigerLine_raster.tif" #name of raster file to save output
arcpy.CopyRaster_management(Roads_TigerLine_raster, raster_loc, "", "0", "0", "", "", "1_BIT", "", "")

raster_loc=wd+"HI_dem.tif" #name of raster file to save output
arcpy.CopyRaster_management(HI_dem, raster_loc, "", "0", "0", "", "", "16_BIT_UNSIGNED", "", "")

raster_loc=wd+"habqual_v3_4.tif" #name of raster file to save output
arcpy.CopyRaster_management(habqual_v3_4, raster_loc, "", "0", "0", "", "", "4_BIT", "", "")

raster_loc=wd+"habqual_v3_4_ugly.tif" #name of raster file to save output
arcpy.CopyRaster_management(habqual_v3_4_ugly, raster_loc, "", "0", "0", "", "", "4_BIT", "", "")

raster_loc=wd+"habqual_v3_4_bare.tif" #name of raster file to save output
arcpy.CopyRaster_management(habqual_v3_4_bare, raster_loc, "", "0", "0", "", "", "4_BIT", "", "")

raster_loc=wd+"HIGAP_22Sep14.tif" #name of raster file to save output
arcpy.CopyRaster_management(HIGAP_22Sep14, raster_loc, "", "0", "0", "", "", "8_BIT_UNSIGNED", "", "")



arcpy.CheckInExtension("Spatial") # Check in the 3D Analyst extension so other users can


