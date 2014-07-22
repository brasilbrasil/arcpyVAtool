#USER INPUT
search_term="response_zone"
rootdir=r"Y:/Py_code/results/all/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
val=2

#END USER INPUT
results_dir="Y:/Py_code/results/ensemble_zone_maps/secure/tol/"
CAO_data_dir=r"Y:/VA data/CAO/"
import os
import arcpy
import csv

from types import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"

csvname="%sspp_habitat_requirements.csv" %(CAO_data_dir)
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
spp_subgroup=column['Status.simplified'] #TEs

i=1
for root, dirs, files in os.walk(rootdir):
	for f in files:
		if search_term in f:
			if ("trim" in f)==False:
				if f[-4:]==".tif":
					sp_code=int(f[-8:-4])
					if int(sp_code)<1087:
						Sp_index=hab_sp_code.index(str(sp_code))
						sp_subgroup=spp_subgroup[Sp_index]
						if sp_subgroup=="Apparently Secure":
							print "found " + f
							out_name="%s%i_partial_ensemble.tif" %(results_dir,i)
							if arcpy.Exists(out_name):
								print str(i)+" already done"
							else:
								if i==1:
									jnk=arcpy.Raster(os.path.join(root, f))
									jnk=jnk==val
									jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
									ensemble=jnk
								else:
									past_ensemble_loc="%s%i_partial_ensemble.tif" %(results_dir,i-1)
									past_ensemble=arcpy.Raster(past_ensemble_loc)
									jnk=arcpy.Raster(os.path.join(root, f))
									jnk=jnk==val
									jnk=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)
									ensemble=jnk+past_ensemble						
								ensemble.save(out_name)
							i=i+1
	
	
