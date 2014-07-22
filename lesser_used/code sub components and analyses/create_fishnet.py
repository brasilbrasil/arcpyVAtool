# import system module
import arcpy
import csv
from arcpy import env
import math

#USER INPUT
#del_terms=["protected_area.csv", "CO_points_w_zones", "tabulate_points_temp", "core_biome_", "fragmentation_", "GBU_", "intersect_", "Migrate_", "refuge", "simplified_", "ungfree_map", "temp_vals", "protected", "COR_CCE", "COR_FCE"]
del_term="response_zone_"
#rootdir=r"C:/Users/lfortini/toFWS/"
rootdir=r"Y:/Py_code/results/all/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
CAO_data_dir=r"C:/Users/lfortini/Data/VA data/CAO/"

#END USER INPUT
import os
import arcpy
from types import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
mxd=arcpy.mapping.MapDocument("CURRENT")
arcpy.env.compression = "LZW"

#SPECIES HABITAT REQUIREMENT LIST
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
spp_area=column['CCE_Area']

for root, dirs, files in os.walk(rootdir):
	for f in files:
		if f[-4:]==".shp":
			if del_term in f:
				if "trim" not in f:
					#os.unlink(os.path.join(root, f))
					print "found " + f + " in " + root
					sp_code=f[:-4]
					sp_code=sp_code[14:]
					
					# Set the origin of the fishnet
					originCoordinate = '413000 2074000'
					# Set the orientation
					yAxisCoordinate = '413000 2074100'
					#yAxisCoordinate = '1037.26 4155.81'
					
					# Enter 0 for width and height - these values will be calcualted by the tool
					sp_code_int=int(sp_code)
					Sp_index=hab_sp_code.index(str(sp_code_int))
					Sp_area=spp_area[Sp_index]
					spacing=str(int(round(math.sqrt(float(Sp_area)*1000000/(100)),0)))
					cellSizeWidth = spacing
					cellSizeHeight = spacing
					
					#outFeatureClass=root+"/"+sp_code +"_fishnet_"+spacing+"m.shp"
					outFeatureClass=root+"/"+sp_code +"_fishnet.shp"
					if arcpy.Exists(outFeatureClass)==False:
						print "saving as " + outFeatureClass
						
						# Number of rows and columns together with origin and opposite corner 
						# determine the size of each cell 
						numRows =  '0'
						numColumns = '0'
						
						oppositeCoorner = '#'
						# Create a point label feature class 
						labels = 'NO_LABELS'                                
						template= root+"/"+"response_zone_"+sp_code+".shp" ###RESPONSE ZONE SHP
						geometryType = 'POLYLINE'
						
						arcpy.CreateFishnet_management(outFeatureClass, originCoordinate, yAxisCoordinate, cellSizeWidth, cellSizeHeight, numRows, numColumns, oppositeCoorner, labels, template, geometryType)
					else:
						print "already calculated" + outFeatureClass