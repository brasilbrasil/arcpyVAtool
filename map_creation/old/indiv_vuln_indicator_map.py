##this code is not finished trying to do it by shapefile means
#USER INPUT
search_term="CCE"
rootdir=r"Y:/VA data/CEs500m/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
val=2

#END USER INPUT
results_dir="Y:/Py_code/results/ensemble_zone_maps/avg_map/"
CAO_data_dir=r"Y:/VA data/CAO/"
import os
import arcpy
import csv

from types import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"

csvname="%svulnerability_ensemble_maps_aux_data.csv" %(CAO_data_dir)
f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
reader = csv.reader(f)
headers = reader.next()
column = {}
for h in headers:
	column[h] = []
for row in reader:
	for h, v in zip(headers, row):
		column[h].append(v)
hab_sp_code=column['sp_code']
indicator_val=column['vuln'] #TEs
##add vulnerability score!
if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")
i=1
rasterList = arcpy.ListRasters("*", "tif")
f = rasterList[0]
for f in rasterList:
	if search_term in f:
		sp_code=int(f[-13:-9])
		if int(sp_code)<1087:
			Sp_index=hab_sp_code.index(str(sp_code))
			sp_subgroup=indicator_val[Sp_index]
			print "indicator score for species " + str(sp_code) + " is " + sp_subgroup
			sp_subgroup=float(sp_subgroup)
			if sp_subgroup>=0:
				out_name="%s%s_vuln.tif" %(results_dir,f[:-4])
				if arcpy.Exists(out_name):
					print "raster " + str(i)+" species "+str(sp_code)+" already done"
				else:
					jnk=arcpy.Raster(os.path.join(rootdir, f))
					jnk=jnk*sp_subgroup
					arcpy.CopyRaster_management(jnk,out_name,"","","0","","","32_BIT_UNSIGNED")

	
arcpy.CheckInExtension("Spatial")
