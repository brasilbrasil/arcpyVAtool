##this code is not finished trying to do it by shapefile means
#USER INPUT
search_term="CCE"
rootdir=r"Y:/VA data/CEs500m/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)
by_veg_type=True

#END USER INPUT
results_dir="Y:/PICCC_analysis/plant_landscape_va_results/ensemble_zone_maps/non_coastal_vuln_quantile_maps/"
spp_info_dir="Y:/PICCC_analysis/plant_landscape_va_results/redone_w_eff_CE/results/"
#spp_info_dir=r"Y:/PICCC_data/VA data/CAO/"
import os
import arcpy
import csv

from types import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"

###update file!!!
csvname="%sunknwnfacs_eqwgts_priors_thirddispersion_all_combined_corrected.csv" %(spp_info_dir)
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
indicator_val=column['rd_quantile'] #TEs
dominant_val=column['dominant_cover'] #TEs
cover1_val=column['cover1'] #TEs

if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")

rasterList = arcpy.ListRasters("*", "tif")
quants=[10, 20, 30, 40, 50]
quant=quants[0]

for quant in quants:
	i=1
	past_sp=0
	f=rasterList[0]
	for f in rasterList:
		if search_term in f:
			sp_code=int(f[-13:-9])
			if int(sp_code)<=1085:
				Sp_index=hab_sp_code.index(str(sp_code))
				sp_subgroup=indicator_val[Sp_index]
				print Sp_index
				print sp_subgroup
				print "indicator score for species " + str(sp_code) + " is " + sp_subgroup
				sp_subgroup=int(sp_subgroup)
				if sp_subgroup<=quant:
					out_name="%squant%i_%i_map_sp%i.tif" %(results_dir,quant,i,sp_code)
					if arcpy.Exists(out_name):
						print "raster " + str(i)+" species "+str(sp_code)+" already done"
					else:
						if i==1:
							jnk=arcpy.Raster(os.path.join(rootdir, f))
							#jnk=jnk>0
							jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
							ensemble=jnk
						else:
							past_ensemble_loc="%squant%i_%i_map_sp%i.tif" %(results_dir,quant,i-1,past_sp)
							past_ensemble=arcpy.Raster(past_ensemble_loc)
							jnk=arcpy.Raster(os.path.join(rootdir, f))
							#jnk=jnk>0
							jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
							ensemble=jnk+past_ensemble
						arcpy.CopyRaster_management(ensemble,out_name,"","","","","","32_BIT_UNSIGNED")
						#ensemble.save(out_name)
					i=i+1
					past_sp=sp_code
				else:
					print "species " + str(sp_code) + " not in quantile"

arcpy.CheckInExtension("Spatial")
