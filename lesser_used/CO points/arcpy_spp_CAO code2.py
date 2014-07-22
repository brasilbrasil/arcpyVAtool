#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#if processing all files in a directory, code filters non-grid files by file name size, but filter could be changed
#remove previous results from arcgis workspace before re-running code as python sometimes cannot overwrite previous output. Alternatively, delete or move.  
#code needs table of values for raster constructed before running


#USER INPUT
datadir="C:/Users/lfortini/Data/FWS essential habitat/"
CCE_data_dir="C:/Users/lfortini/Data/SDM HI/"
save_results_to_table=1
#END USER INPUT

FWS_island_names=['BI', 'KA', 'KH', 'LA', 'MA', 'MO', 'NI', 'OA'] #no kahoolawe
JP_island_names=['Ha', 'Ka', 'Ke', 'La', 'Ma', 'Mo', 'Ni', 'Oa']

#START UNDERHOOD
resultsdir="%sresults/" %(datadir)
import os
import arcpy
import arcpy.sa
#import math
from time import time
from dbfpy import dbf #module for r/w dbf files available at http://dbfpy.sourceforge.net/
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
t0 = time()
mxd=arcpy.mapping.MapDocument("CURRENT")

def del_layer(layer_name):	
	for df in arcpy.mapping.ListDataFrames(mxd):
	    for lyr in arcpy.mapping.ListLayers(mxd, "", df):
		if lyr.name.lower() == layer_name:
		    arcpy.mapping.RemoveLayer(df, lyr)
	return
#WHICH SPECIES ARE THERE
dbfname="%sSH_all_islands_dissolved by spp and island.dbf" %(datadir)
db = dbf.Dbf(dbfname)

Spp_data=[]
Sp_data=['sp_name', 'Island', 'JP_code', 'CCE data', 'Point_data', 'n polygons', 'n polygons excluded', 'outlier points']
#Sp_data=['sp_name', 'area_CCE', 'area_FCE', 'area_dif', 'area_resist', 'area_refuge', 'area_migrate', 'FCE_distance', 'CCE_mean_elev', 'CCE_min_elev', 'CCE_max_elev', 'CCE_stdev_elev', 'CCE_mean_slope', 'CCE_stdev_slope', 'CCE_mean_aspect', 'CCE_stdev_aspect']
Spp_data.append(Sp_data)
for i in range(len(db)): #i=2 for debug

#for i in range(0, 10): #i=2 for debug
#db1=[1, 2, 3, 4, 5, 6, 7, 8, 9] #for debug
#db1=[2] #for debug
#for i in db1: #for debug
	#SELECT EACH INDIVIDUAL SPECIES FROM SHP
	expr='"FID" = %s' %(i)
	arcpy.SelectLayerByAttribute_management("SH_all_islands_dissolved by spp and island","", expr)
	sp=db[i]["SPECIES_NA"]
	sp = sp.replace(".", "") #get rid of punctuations to avoid filen renaming errors
	sp = sp.replace("-", " ") #get rid of punctuations to avoid filen renaming errors
	island=db[i]["ISLAND"]
	JP_sp_code=db[i]["JP_model_c"]
	jp_island_name=JP_island_names[FWS_island_names.index(island)]#deal with differences in island name between FWS and JP data
	
	#CREATE SEPARATE LAYER FOR THE SPECIES
	arcpy.CopyFeatures_management("SH_all_islands_dissolved by spp and island", 'sp_CH_data')
	
	#select species point data
	spp_pt_data="%sSp_point_data2.shp" %(datadir)
	
	if os.path.exists(spp_pt_data):
		point_filtered=1
		
		#REMOVE LARGE POLYGONS BASED ON POINT DATA
		arcpy.MultipartToSinglepart_management("sp_CH_data", "sp_CH_data_multi") #make each polygon a distinct feature
		n_original_polygons=arcpy.GetCount_management("sp_CH_data_multi")
		n_original_polygons=int(n_original_polygons[0])
		arcpy.CalculateAreas_stats("sp_CH_data_multi", "sp_CH_data_multi_w_area") #calc polygon areas
		#select only large polygons
		expr='"F_AREA" > 1000000' #select polygons greater than 1 sq km
		arcpy.SelectLayerByAttribute_management("sp_CH_data_multi_w_area","", expr)	
		arcpy.CopyFeatures_management("sp_CH_data_multi_w_area", "sp_CH_data_multi_w_area_large") #Save large polygons selected as separate layer
		arcpy.DeleteFeatures_management("sp_CH_data_multi_w_area") #temporarily deletes large polygons from species distribution map
		
		#determine which large polygons have points in them
		arcpy.SelectLayerByLocation_management("sp_CH_data_multi_w_area_large","INTERSECT", spp_pt_data,"","") 
		arcpy.CopyFeatures_management("sp_CH_data_multi_w_area_large", "sp_CH_data_multi_w_area_large_occupied")
		n_select_polygons=arcpy.GetCount_management("sp_CH_data_multi_w_area_large_occupied")
		n_select_polygons=int(n_select_polygons[0])
		n_select_polygons=n_original_polygons-n_select_polygons#add large occupied polygons back to species distribution map
		arcpy.Merge_management(["sp_CH_data_multi_w_area_large_occupied", "sp_CH_data_multi_w_area"],"sp_CH_data_multi_w_area_and_occupied_large")
	else:
		point_filtered=0
		n_original_polygons="NA"
		n_select_polygons="NA"
		arcpy.CopyFeatures_management("sp_CH_data", 'sp_CH_data_multi_w_area_and_occupied_large')
		
	#CLIP WITH ESSENTIAL HABITAT
	essential_habitat="%sPlant_essential_habitat_1998.shp" %(datadir)
	sp_CH_data_loc="%sIndividual_sp_CAO/temp_CH.shp" %(datadir)	
	arcpy.Clip_analysis("sp_CH_data_multi_w_area_and_occupied_large", essential_habitat, sp_CH_data_loc)

	#DETERMINE IF XY POINTS ARE OUTSIDE POLYGONS
	outlier_points=0
	point_status=""
	if os.path.exists(spp_pt_data):
		arcpy.CopyFeatures_management(spp_pt_data,"temp_pt_data")
		arcpy.SelectLayerByLocation_management('temp_pt_data',"INTERSECT", sp_CH_data_loc,"","")
		arcpy.SelectLayerByLocation_management('temp_pt_data',"INTERSECT", sp_CH_data_loc,"","SWITCH_SELECTION")
		outside_point_loc="%sIndividual_sp_CAO/temp_outside_points.shp" %(datadir)
		arcpy.CopyFeatures_management('temp_pt_data',outside_point_loc)
		dbfname2="%sdbf" %(outside_point_loc[:-3])
		db2 = dbf.Dbf(dbfname2)
		if len(db2)>0:
			outlier_points=1
			point_status="_pts_out"
		db2.close()
		arcpy.DeleteFeatures_management(outside_point_loc)
		
	#CLIP POLYGONS WITH CCE
	sp_CH_data='%sIndividual_sp_CAO/%s/%s_%s_CH.img' %(datadir, jp_island_name, JP_sp_code, sp)
	CCE_data="%sAnalysis%s/hs%s" %(CCE_data_dir, jp_island_name, JP_sp_code) 
	if os.path.exists(CCE_data): #must check if CCE data exist before clipping; #if JP code is 0, do not clip
		CCE_data_avail=1
		if point_filtered == 1:
			sp_CH_data='%sIndividual_sp_CAO/%s/%s_%s_CAO%s.img' %(datadir, jp_island_name, JP_sp_code, sp, point_status)
		else:
			sp_CH_data='%sIndividual_sp_CAO/%s/%s_%s_CAO_not_pt_filtered.img' %(datadir, jp_island_name, JP_sp_code, sp)
			
		CCE_temp=arcpy.sa.SetNull(CCE_data,1,"Value <101")
		#arcpy.Clip_analysis("sp_CH_data_multi_w_area_and_occupied_large_minus_CH", CCE_data, sp_CH_data) ####CLIP MUST BE FOR RASTER OVER POLYGON!!!
		extPolygonOut = arcpy.sa.ExtractByMask(CCE_temp, sp_CH_data_loc)
		extPolygonOut.save(sp_CH_data)
	else:
		CCE_data_avail=0
		if point_filtered == 1:
			sp_CH_data2_loc='%sIndividual_sp_CAO/%s/%s_CAO_noCCEclip%s.shp' %(datadir, jp_island_name, sp, point_status)
		else: #if no point data, name output accordingly
			sp_CH_data2_loc='%sIndividual_sp_CAO/%s/%s_CAO_noCCEclip_not_pt_filtered.shp' %(datadir, jp_island_name, sp)
		arcpy.CopyFeatures_management(sp_CH_data_loc,sp_CH_data2_loc)
		#jnk.save(sp_CH_data2_loc)
	Sp_data=[sp, jp_island_name, JP_sp_code, CCE_data_avail, point_filtered, n_original_polygons, n_select_polygons, outlier_points]
	Spp_data.append(Sp_data)
	
if save_results_to_table==1:
	import csv
	opath="%sall_spp_values.csv" %(datadir)
	if arcpy.Exists(opath): #delete previous version of output file if it exists
		os.remove(opath) 
	else:
		pass
	ofile = open(opath, 'wb')
	writer = csv.writer(ofile, dialect='excel')
	for i in range(len(Spp_data)):
		writer.writerow(Spp_data[i])
	ofile.close()

