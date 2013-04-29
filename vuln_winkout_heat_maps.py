##this code is not finished trying to do it by shapefile means
#USER INPUT
search_term="CCE"
rootdir=r"Y:/VA data/CEs/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 

#END USER INPUT
results_dir="Y:/Py_code/results/ensemble_zone_maps/avg_map/vuln_quantile_heat_maps/"
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
indicator_val=column['winkout_overlap'] #TEs

if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")

rasterList = arcpy.ListRasters("*", "tif")
quants=[-1, 0]
labels=["winkout","no_overlap"]
quant =quants[0]
for quant in quants:
	i=1
	past_sp=0
	label=labels[quants.index(quant)]
	for f in rasterList:
		if search_term in f:
			sp_code=int(f[-8:-4])
			if int(sp_code)<=1085:
				Sp_index=hab_sp_code.index(str(sp_code))
				sp_subgroup=indicator_val[Sp_index]
				print "indicator score for species " + str(sp_code) + " is " + sp_subgroup
				sp_subgroup=int(sp_subgroup)
				if sp_subgroup<=quant:
					out_name="%squant%s_%i_map_sp%i.tif" %(results_dir,label,i,sp_code)
					if arcpy.Exists(out_name):
						print "raster " + str(i)+" species "+str(sp_code)+" already done"
					else:
						print " will save as " + out_name
						if i==1:
							jnk=arcpy.Raster(os.path.join(rootdir, f))
							#jnk=jnk>0
							print "loaded raster"
							jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
							print "added zeros"
							ensemble=jnk
						else:
							past_ensemble_loc="%squant%s_%i_map_sp%i.tif" %(results_dir,label,i-1,past_sp)
							past_ensemble=arcpy.Raster(past_ensemble_loc)
							print "loaded past raster"
							jnk=arcpy.Raster(os.path.join(rootdir, f))
							print "loaded raster"
							#jnk=jnk>0
							jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
							print "added zeros"
							ensemble=jnk+past_ensemble
							print "added rasters"
						arcpy.CopyRaster_management(ensemble,out_name,"","","","","","32_BIT_UNSIGNED")
						#ensemble.save(out_name)
					i=i+1
					past_sp=sp_code
				else:
					print "species " + str(sp_code) + " not in quantile"
	
arcpy.CheckInExtension("Spatial")
