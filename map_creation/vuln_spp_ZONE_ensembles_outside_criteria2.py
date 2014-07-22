#USER INPUT
search_term="response_zone"
rootdir=r"Y:/PICCC_analysis/plant_landscape_va_results/redone_w_eff_CE/results/all" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)
zone_val=2 #1,2,3
spp_info_dir=r"Y:/PICCC_analysis/plant_landscape_va_results/redone_w_eff_CE/results/" #where is spreadsheet
csvname="%stmp_ensemble_criteria5_highVuln.csv" %(spp_info_dir)
column_name='NC_Nex_wFCE' #'OA_NC_Nex_End', 'OA_NC_Nex_notSec'
indicator_val="1" #what is the value in column that indicates species should be included? must be number
out_str=column_name #name of raster

#END USER INPUT
results_dir="Y:/PICCC_analysis/plant_landscape_va_results/ensemble_zone_maps/NC_Nex_vuln_quantile_maps/"
import os
import arcpy
import csv
from types import *
from random import randrange

jnk=randrange(10000)
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"
arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"
if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")

f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
reader = csv.reader(f)
headers = reader.next()
column = {}
for h in headers:
	column[h] = []
for row in reader:
	for h, v in zip(headers, row):
		column[h].append(v)

hab_sp_code=column['sp_code_1']
spp_subgroup=column[column_name] #TEs

i=1
for root, dirs, files in os.walk(rootdir):
	for f in files:
		if search_term in f:
			if ("trim" in f)==False:
			 if ("_eff_" in f)==False:
				if f[-4:]==".tif":
					sp_code=int(f[-8:-4])
					if int(sp_code)<1087:
						if str(sp_code) in hab_sp_code: #to exclude few sp with no info on spreadsheet (VA analysis did not work, or CE is corrupt)
							Sp_index=hab_sp_code.index(str(sp_code))
    						sp_subgroup=str(spp_subgroup[Sp_index])
    						if sp_subgroup==indicator_val:
    							print "found " + f
    							out_name="%s%i_%s_zone%s_partial_ensemble.tif" %(results_dir,i,out_str, zone_val)
    							if arcpy.Exists(out_name):
    								print str(i)+" already done"
    							else:
    								if i==1:
    									jnk=arcpy.Raster(os.path.join(root, f))
    									jnk=jnk==zone_val
    									jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
    									ensemble=jnk
    								else:
    									past_ensemble_loc="%s%i_%s_zone%s_partial_ensemble.tif" %(results_dir,i-1,out_str, zone_val)
    									past_ensemble=arcpy.Raster(past_ensemble_loc)
    									jnk=arcpy.Raster(os.path.join(root, f))
    									jnk=jnk==zone_val
    									jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
    									ensemble=jnk+past_ensemble
    								ensemble.save(out_name)
    							i=i+1

arcpy.CheckInExtension("Spatial")
