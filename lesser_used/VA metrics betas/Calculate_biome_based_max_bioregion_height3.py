#USER INPUT
datadir=r"C:/Users/lfortini/Data/VA data/landscape/fragmentation/" #whichever is data dir, will have to have subfolders: la/DEM/ (where DEM based layers go), gaplandcover/ (where gaplandcov_hi is placed)
landscape_dir=r"C:/Users/lfortini/Data/VA data/landscape/" #whichever is data dir, will have to have subfolders: la/DEM/ (where DEM based layers go), gaplandcover/ (where gaplandcov_hi is placed)

#END USER INPUT

#START UNDERHOOD
import os
import arcpy
import arcpy.sa
import math
import csv
import arcgisscripting
from types import *
import time
from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/
import numpy
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
mxd=arcpy.mapping.MapDocument("CURRENT")

Bioregions_loc="%sbioregions.shp" %(landscape_dir)
arcpy.CopyFeatures_management(Bioregions_loc, "bioregions")
all_dem=landscape_dir+"all/DEM/all_dem.tif"
all_dem=arcpy.Raster(all_dem)

rasterList = arcpy.ListRasters("*", "tif")

Spp_data=[]
Sp_data=['biome_combo', 'FCE_max_elev_E_Ma', 'FCE_max_elev_E_Mo', 'FCE_max_elev_Hualalai', 'FCE_max_elev_Ko', 'FCE_max_elev_Kau', 'FCE_max_elev_Ka', 'FCE_max_elev_Kilauea', 'FCE_max_elev_Kohala',
	'FCE_max_elev_Kona', 'FCE_max_elev_Koolau', 'FCE_max_elev_La', 'FCE_max_elev_Maunakea', 'FCE_max_elev_NE_Maunaloa', 'FCE_max_elev_Ni', 'FCE_max_elev_NW_Maunaloa', 'FCE_max_elev_Waianae',
	'FCE_max_elev_W_Ma', 'FCE_max_elev_W_Mo']
Spp_data.append(Sp_data)

for raster in rasterList:
	Sp_data=[]
	orig_file_nm=raster.encode('ascii','replace')
	biome_combo="b"+ orig_file_nm[-12:-9]
	Sp_data.append(biome_combo)
	orig_file_nm=arcpy.Raster(orig_file_nm)
	biome_filter=orig_file_nm>0
	biome_filter=arcpy.sa.SetNull(biome_filter,1,"Value <1")
	print 'biome filter %s complete' %(biome_combo)
	biome_dem=biome_filter*all_dem
	print 'biome filter %s applied to dem' %(biome_combo)
	#loc_min_elev_FCE_table=r"%smax_elev/elev_biome_combo_%s.dbf" %(datadir,biome_combo)
	
	#INPUTS FOR ZONAL QUANTILE ROUTINE
	field_name="VOLCANO"
	zone_shape="bioregions"
	inraster=biome_dem
	Q_threshold=0.95
	
	expr=""" "%s" = 'NA' """ %(field_name)#
	arcpy.SelectLayerByAttribute_management (zone_shape, "CLEAR_SELECTION", expr)
	rows = arcpy.SearchCursor(zone_shape, "", "",field_name) #"RASTERVALU = 2"
	vals=[]
	for row in rows:
	    if type(row)== NoneType:
		freq=0
	    else:
		freq=row.getValue(field_name)
	    vals.append(freq)
	    #row = rows.next()
	
	for val in vals:
	    expr=""" "%s" = '%s' """ %(field_name, val)
	    arcpy.SelectLayerByAttribute_management (zone_shape, "NEW_SELECTION", expr)
	    temp_loc=datadir+"max_elev/temp_zone.tif"
	    
	    arcpy.Clip_management(inraster, "#", temp_loc,zone_shape, "0", "ClippingGeometry")
	    myArray = arcpy.RasterToNumPyArray(temp_loc)
	    myArray=myArray[myArray>0] ##GET RID OF 0 ELEV
	    #del temp_loc
	    if len(myArray)>0:
		    temp_hist=numpy.histogram(myArray,1000)
		    temp_cum_dist=temp_hist[0]
		    temp_elev_bins=temp_hist[1]
		    temp_cum_dist=numpy.cumsum(temp_cum_dist)
		    max_temp_cum_dist=temp_cum_dist[len(temp_cum_dist)-1]
		    max_temp_cum_dist=max_temp_cum_dist*Q_threshold
		    temp_index=temp_cum_dist<max_temp_cum_dist
		    temp_max_elev=temp_elev_bins[temp_index]
		    try: 
			temp_max_elev=max(temp_max_elev)
		    except ValueError:
			temp_max_elev=0
	    else:
		    temp_max_elev=0
	    #temp_max_elev=0
	    Sp_data.append(temp_max_elev)
	
	expr=""" "%s" = 'NA' """ %(field_name)#
	arcpy.SelectLayerByAttribute_management (zone_shape, "CLEAR_SELECTION", expr)
	Spp_data.append(Sp_data)

Spp_data=zip(*Spp_data) #transpose

opath=r"%smax_elev/all_biome_values_test.csv" %(datadir)
if arcpy.Exists(opath): #delete previous version of output file if it exists
	os.remove(opath) 
else:
	pass
ofile = open(opath, 'wb')
writer = csv.writer(ofile, dialect='excel')
for i in range(len(Spp_data)):
	writer.writerow(Spp_data[i])
ofile.close()