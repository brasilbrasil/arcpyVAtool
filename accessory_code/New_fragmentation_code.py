wd="Y:/PICCC_data/VA data/landscape/fragmentation/"
landscapeDataDir="Y:/PICCC_data/VA data/landscape/"
buffer_dist=100
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
arcpy.env.workspace = wd
arcpy.env.compression = "LZW"
arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"

if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")

roads_raster=arcpy.Raster(wd+"road.tif")
habqual_raster=arcpy.Raster(landscapeDataDir+"habqual_simple.tif")
goodqual_raster=arcpy.sa.SetNull(habqual_raster,1,"Value!=3")
roads_raster_buffer= arcpy.sa.EucDistance(roads_raster_buffer, 100, "","")
roads_raster_buffer=arcpy.sa.SetNull(roads_raster_buffer,1,"Value>100")
