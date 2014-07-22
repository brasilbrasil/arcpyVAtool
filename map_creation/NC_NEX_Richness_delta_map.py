##this code is not finished trying to do it by shapefile means
#USER INPUT
results_dir="Y:/PICCC_analysis/plant_landscape_va_results/ensemble_zone_maps/NC_Nex_vuln_quantile_maps/"
import os
import arcpy
from types import *
from random import randrange

jnk=randrange(10000)
arcpy.env.overwriteOutput = True
arcpy.env.workspace = results_dir
arcpy.env.compression = "LZW"
arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"

out_str='NC_Nex' #NC_winkout	NC_NO	NC_NEx_winkout	NC_Nex_NO OA_NC_Nex_End OA_NC_Nex_notSec
i=990
sp_code=1085
out_name="%s%s_%i_sp%i.tif" %(results_dir,out_str,i,sp_code)
CCE_ensemble=arcpy.Raster(out_name)


out_str='NC_Nex_wFCE' #NC_winkout	NC_NO	NC_NEx_winkout	NC_Nex_NO OA_NC_Nex_End OA_NC_Nex_notSec
i=955
sp_code=1085
out_name="%s%s_%i_sp%i.tif" %(results_dir,out_str,i,sp_code)
FCE_ensemble=arcpy.Raster(out_name)

if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")

richness_delta=FCE_ensemble-CCE_ensemble
out_name="Modelled_richness_delta.tif"
arcpy.CopyRaster_management(richness_delta,out_name,"","","","","","16_BIT_SIGNED")


richness_delta=(float(FCE_ensemble)-float(CCE_ensemble))/float(CCE_ensemble)
out_name="Modelled_richness_relative_delta.tif"
arcpy.CopyRaster_management(richness_delta,out_name,"","","","","","32_BIT_FLOAT")

arcpy.CheckInExtension("Spatial")
