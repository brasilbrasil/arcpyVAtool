#USER INPUT
#this code will find all rasters in a folder and apply a projection from a file
#if you want to apply for only one type of raster, change the "All" value to the extension name desired
#prj_file=arcpy.Raster("Y:/PICCC_analysis/FB_analysis/model_results/biomod2finalmodel_P_PA_oldcode_less_PAs/output_rasters/Iiwi_BIN_baseline_ROC_ef.pmw.tif") #had to define datum on arcgis D_WGS_1984
datadir="Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/range maps archipelago reprojected/"
outputdir="Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/range maps archipelago reprojected 2bits/"

#projection="C:/Program Files (x86)/ArcGIS/Desktop10.0/Coordinate Systems/Geographic Coordinate Systems/North America/NAD 1983.prj"
#END USER INPUT
import os
import arcpy
from random import randrange
from types import *

if not os.path.exists(outputdir):
    os.mkdir(outputdir)
jnk=randrange(10000)
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
arcpy.env.compression = "LZW"
arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"

#WGS 1984 UTM Z4N projection code based on http://www.spatialreference.org/ref/epsg/32604/proj4js/
#prj_file=datadir+prj_file_name
rasterList = arcpy.ListRasters("*", "TIF")
f=rasterList[0]
for f in rasterList:
    print "starting %s" %(f)
    rastername=os.path.join(datadir, f)
    outrastername=os.path.join(outputdir, f)
    arcpy.CopyRaster_management(rastername, outrastername, "", "0", "0", "", "", "2_BIT", "", "")

    #arcpy.ProjectRaster_management(rastername, outrastername, arcpy.SpatialReference(32604), "NEAREST", "", "", "", "")
