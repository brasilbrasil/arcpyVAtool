##this code is not finished trying to do it by shapefile means
#USER INPUT
rootdir=r"Y:/PICCC_data/VA data/CEs/"
results_dir=r"Y:/PICCC_data/VA data/CEs_250m/"
overwrite=False
#END USER INPUT


import os
import arcpy
from random import randrange
from types import *
import time
jnk=randrange(10000)
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"
#arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
#arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"
arcpy.env.scratchWorkspace = "D:/temp/arcgis/"

if not os.path.exists(results_dir):
    os.mkdir(results_dir)

if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")

rasterList = arcpy.ListRasters("*", "tif")


cell_factor=250/30
#rasterList=rasterList[0:2]
t1 = time.time()

f=rasterList[1]
for f in rasterList:
    out_name=results_dir+f
    if arcpy.Exists(out_name) and overwrite==False:
		print "raster " + out_name+" already done"
    else:
        print " doing raster " + out_name
        #maskedRaster = arcpy.sa.SetNull(mask_layer, f, "Value = 100")
        outRas=arcpy.sa.Aggregate(f, cell_factor, "MAXIMUM", "TRUNCATE", "DATA")
        arcpy.CopyRaster_management(outRas,out_name,"","","","","","2_BIT")

t2 = time.time()
print len(rasterList),"elements","for loop time",(t2-t1),"s"

arcpy.CheckInExtension("Spatial")
