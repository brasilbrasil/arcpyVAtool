##this code is not finished trying to do it by shapefile means
#USER INPUT
search_term="CCE"
#rootdir=r"C:/Users/lfortini/code/polygon_project - Copy/data/CEs/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
#rootdir=r"Y:/VA data/CEs500m/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
rootdir="Y:/Py_code/results/ensemble_zone_maps/avg_map/vuln_CCE_500m/"
val=2

#END USER INPUT
results_dir="Y:/Py_code/results/ensemble_zone_maps/avg_map/"
import os
import arcpy
import csv

from types import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"


####add vulnerability score!
if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")
i=1
rasterList = arcpy.ListRasters("*", "tif")
f = rasterList[0]
for f in rasterList:
	if search_term in f:
		sp_code=int(f[-18:-14]) #f[-8:-4]
		if int(sp_code)<1087:
			print "summing species " + str(sp_code)
			#print "found " + f
			out_name="%scount_%i_partial_ensemble_done_sp_%i.tif" %(results_dir,i,sp_code)
			if arcpy.Exists(out_name):
				print "raster " + str(i)+" species "+str(sp_code)+" already done"
			else:
				if i==1:
					jnk=arcpy.Raster(os.path.join(rootdir, f))
					jnk=jnk>0
					jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
					ensemble=jnk
				else:
					past_ensemble_loc="%scount_%i_partial_ensemble_done_sp_%i.tif" %(results_dir,i-1,sp_code-1)
					past_ensemble=arcpy.Raster(past_ensemble_loc)
					jnk=arcpy.Raster(os.path.join(rootdir, f))
					jnk=jnk>0
					jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
					ensemble=jnk+past_ensemble						
				arcpy.CopyRaster_management(ensemble,out_name,"","","","","","32_BIT_UNSIGNED")
				#ensemble.save(out_name)
			i=i+1

arcpy.CheckInExtension("Spatial")	
