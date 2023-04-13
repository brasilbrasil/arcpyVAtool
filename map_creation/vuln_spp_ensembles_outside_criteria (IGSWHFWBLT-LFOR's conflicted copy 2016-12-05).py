##this code is not finished trying to do it by shapefile means
#USER INPUT
search_term="CCE" #FCE or CCE
rootdir=r"Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/range maps archipelago reprojected 2bits/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)
results_dir="Y:/PICCC_analysis/plant_landscape_va_results/ensemble_zone_maps_P2/"
spp_info_dir="Y:/PICCC_analysis/plant_landscape_va_results/ensemble_zone_maps_P2/phase2_map_info/"
csvname="%sall_merged_data.csv" %(spp_info_dir)
column_name='DDA1B__Vulnerability_mask'
#DDA1B__Winkout_mask	SDrcp45__Winkout_mask	SDrcp85__Winkout_mask
#DDA1B__Vulnerability_mask	SDrcp45__Vulnerability_mask	SDrcp85__Vulnerability_mask
#DDA1B__CE_no_overlap_mask	SDrcp45__CE_no_overlap_mask	SDrcp85__CE_no_overlap_mask
#NC_winkout	NC_NO	NC_NEx_winkout	NC_Nex_NO OA_NC_Nex_End OA_NC_Nex_notSec
proj_name=""
#the two parameters below are unlikely to change
indicator_val=1 #what is the value in column that indicates species should be included? must be number
#out_str=proj_name+"_"+column_name+"_"+search_term #name of raster
out_str=column_name+"_"+search_term #name of raster
#END USER INPUT


import os
import arcpy
import csv
from random import randrange
from types import *

jnk=randrange(10000)
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"
arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"

###sp info file processing
f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
reader = csv.reader(f)
headers = reader.next()
column = {}
for h in headers:
	column[h] = []
for row in reader:
	for h, v in zip(headers, row):
		column[h].append(v)
hab_sp_code=column['VAID'] #changed in sheet sp_code to sp_code_1 because there were multiple columns with the same name
indicator_col=column[column_name]


if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")

rasterList = arcpy.ListRasters("*", "tif")

i=1
past_sp=0
f=rasterList[6]
for f in rasterList:
	if search_term in f:
		sp_code=int(f[-8:-4]) #-13:-9
		if int(sp_code)<=1085:
			if str(sp_code) in hab_sp_code: #to exclude few sp with no info on spreadsheet (VA analysis did not work, or CE is corrupt)
	   			Sp_index=hab_sp_code.index(str(sp_code))
				sp_subgroup=indicator_col[Sp_index]
				print Sp_index
				print sp_subgroup
				print "indicator score for species " + str(sp_code) + " is " + sp_subgroup
				sp_subgroup=int(sp_subgroup)
				if sp_subgroup==indicator_val:
					out_name="%s%s_%i_sp%i.tif" %(results_dir,out_str,i,sp_code)
					if arcpy.Exists(out_name):
						print "raster " + str(i)+" species "+str(sp_code)+" already done"
					else:
						if i==1:
							jnk=arcpy.Raster(os.path.join(rootdir, f))
							#jnk=jnk>0
							jnk0=arcpy.sa.IsNull(jnk)
							jnk=arcpy.sa.Con(jnk0,0,1)
							ensemble=jnk
						else:
							past_ensemble_loc="%s%s_%i_sp%i.tif" %(results_dir,out_str,i-1,past_sp)
							past_ensemble=arcpy.Raster(past_ensemble_loc)
							jnk=arcpy.Raster(os.path.join(rootdir, f))
							jnk0=arcpy.sa.IsNull(jnk)
							jnk=arcpy.sa.Con(jnk0,0,1)
							ensemble=jnk+past_ensemble
						arcpy.CopyRaster_management(ensemble,out_name,"","","","","","32_BIT_UNSIGNED")
						#ensemble.save(out_name)
					i=i+1
					past_sp=sp_code
				else:
					print "species " + str(sp_code) + " not in quantile"

arcpy.CheckInExtension("Spatial")
