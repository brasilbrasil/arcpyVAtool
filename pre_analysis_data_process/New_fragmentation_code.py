wd="Y:/PICCC_data/VA data/Phase2/hab_data/"
landscapeDataDir="Y:/PICCC_data/VA data/Phase2/hab_data/"
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
#arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
#arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"

if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")

roads_raster=arcpy.Raster(wd+"Roads_TigerLine_raster.tif")
habqual_raster=arcpy.Raster(wd+"habqual_v3_4.tif")
goodqual_raster=arcpy.sa.Con(habqual_raster,1,0,"Value=3")
notgoodqual_raster=arcpy.sa.Con(habqual_raster,1,0, "Value<3")
notgoodqual_raster=arcpy.sa.SetNull(notgoodqual_raster,1,"Value=0")

roads_raster_buffer= arcpy.sa.EucDistance(roads_raster, 100, "","")
roads_raster_buffer=arcpy.sa.Con(arcpy.sa.IsNull(roads_raster_buffer),101,roads_raster_buffer)
roads_raster_buffer=arcpy.sa.Int(roads_raster_buffer) #must convert to integerr to use conditional statement
roads_raster_buffer=arcpy.CalculateStatistics_management(roads_raster_buffer)
roads_raster_buffer_core=arcpy.sa.Con(roads_raster_buffer,1,0,"Value>100")

notgoodqual_raster_buffer=arcpy.sa.EucDistance(notgoodqual_raster, 100, "","")
notgoodqual_raster_buffer=arcpy.sa.Con(arcpy.sa.IsNull(notgoodqual_raster_buffer),101,notgoodqual_raster_buffer)
notgoodqual_raster_buffer=arcpy.sa.Int(notgoodqual_raster_buffer) #must convert to integerr to use conditional statement
notgoodqual_raster_buffer=arcpy.CalculateStatistics_management(notgoodqual_raster_buffer)
notgoodqual_raster_buffer_core=arcpy.sa.Con(notgoodqual_raster_buffer,1,0,"Value>100")

#island=arcpy.sa.Con(habqual_raster,1,0,"Value>0")
jnk=arcpy.sa.SetNull(goodqual_raster, 1, "Value=0")
frag_map=jnk*notgoodqual_raster_buffer_core*roads_raster_buffer_core
frag_map=arcpy.sa.Con(frag_map,2,1,"Value=1")
arcpy.CheckInExtension("Spatial") # Check in the 3D Analyst extension so other users can access it

file_loc=r"fragmentation_map.tif"
#CCE_full.save(loc_simple_CCE)
arcpy.CopyRaster_management(frag_map, file_loc, "", "0", "0", "", "", "2_BIT", "", "")
