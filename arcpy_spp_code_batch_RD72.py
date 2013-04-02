#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#must have open document with hillshade background image

#USER INPUT
island="all" #la ha all
landscape_factor_dir=r"Y:/VA data/landscape/" #whichever is data dir, will have to have subfolders: la/DEM/ (where DEM based layers go), gaplandcover/ (where gaplandcov_hi is placed)
CAO_data_dir=r"Y:/VA data/CAO/"
highest_slr_impact=3 #max elev of slr impacts (this avoids SLR impact calc for high elev species)
#f = open("C:/Users/lfortini/Data/0_model_config_sp_to_run.txt", "r")
#sub_spp_CE_folder= f.read() 
#ce_data_dir=r"C:/Users/lfortini/Data/VA data/CEs/%s/" %(sub_spp_CE_folder)
ce_data_dir=r"Y:/VA data/CEs/"
max_search_dist_for_transition_zone= 5000 #in m
use_bio_region_filter=0
subset_of_CEs=[0,1084] #[0,1084] leave empty [] for no subset, if subset: [300,400]
import_cce_list=False
use_effective_CE_mask=True
use_zonal_stats=1
all_files_in_directory=1 #1 to do batch processing of all files in a directory, 0 if want to specify which species below
reverse_spp_order=False
keep_intermediary_output=0 #enter 1 for debug reasons, will a lot of intermediary analyses outputs for inspection
send_email_error_message=1
overwrite=0
sp_envelope_gap=0 #this will avoid the computationally intensive mapping of the transition zone if value is 0

#what pieces to run?
pre_process_envelopes=False
calculate_veg_type_areas=False
calc_cce_total_area=False
calc_fce_total_area=False
calc_cce_fce_dif=False
map_tol_zone=False
map_mrf_zone=False
map_mig_zone_pt1=False
calc_dist_fce_to_CCE=False
calc_mean_elev_cce=False
calc_mean_elev_fce=False

##response zone metrics
create_rep_zones=False
calc_resp_zone_area=False
calc_zone_slr_area=False
calc_zone_lava_flow_area=False #missing
calc_zone_hab_qual=False
calc_eff_hab_qual_nonpioneer=True
calc_eff_hab_qual_pioneer=False
chose_eff_hab_qual=False
#create_eff_resp_zones=False
#calc_eff_resp_zone_area=False
calc_hab_qual=False
calc_good_hab=False #always off
calc_fragmentation=False
calc_dist_to_top_of_island=False
calc_protected_area=False 
calc_ung_free_area=False
calc_slope_metrics=False
calc_zone_aspect_mean=False
calc_zone_cos_aspect=False
calc_zone_sin_aspect=False
calc_zone_aspect_std=False
calc_ppt_gradient=False 
calc_zone_invasibility=False

#START UNDERHOOD
#f = open("C:/Users/lfortini/Data/0_model_config_data_dir.txt", "r")
#rootdir= f.read() 
#rootdir=r"Y:/Py_code/redone_w_eff_CE/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
rootdir=r"Y:/Py_code/redone_w_eff_CE/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
resultsdir0=r"%sresults/%s/" %(rootdir, island)
datadir=ce_data_dir

import os
import arcpy
import arcpy.sa
import math
import csv
import shutil
import numpy
import arcgisscripting
from types import *
import time
import traceback
import sys
from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/
import fnmatch
from arcpy import env
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
arcpy.env.compression = "LZW"
deg2rad = math.pi / 180.0
rad2deg = 180.0 / math.pi 
t0 = time.time()
#mxd=arcpy.mapping.MapDocument("CURRENT")
kio=keep_intermediary_output

def get_num_attributes(raster, value):
	jnk = arcpy.GetRasterProperties_management(raster, value)
	jnk= jnk.getOutput(0) 	
	jnk=float(jnk)
	return jnk
def get_zone_stats(zone_index, db, stat):
	output=[0, 0, 0]
	for z in range(len(zone_index)):
		rec=db[z][stat]
		output[zone_index[z]]=rec
	return output

def save_temp_csv_data(temp_data, opath):
	#opath=r"%sDBFs/%s_%s.csv" %(resultsdir, Sp_index, name)
	ofile = open(opath, 'wb')
	writer = csv.writer(ofile, dialect='excel')
	writer.writerow(temp_data)
	ofile.close()
	return

def load_temp_csv_float_data(opath):
	f = open(opath, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
	reader = csv.reader(f)
	jnk= reader.next()
	jnk[:]=[float(x) for x in jnk]
	return jnk

def load_temp_csv_data(opath):
	f = open(opath, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
	reader = csv.reader(f)
	jnk= reader.next()
	return jnk

def alt_zonal_stats(zone_raster, var_raster, zone_vals):
    def get_num_attributes(raster, value):
            jnk = arcpy.GetRasterProperties_management(raster, value)
            jnk= jnk.getOutput(0) 	
            jnk=float(jnk)
            return jnk
					
    zone_raster_standard=zone_raster*var_raster/var_raster
    var_raster_standard=zone_raster*var_raster/zone_raster
    
    var_zone_mean=['NA']*len(array_index)
    var_zone_area=['NA']*len(array_index)
    var_zone_std=['NA']*len(array_index)
    for z in range(len(array_index)):
        #jnk=arcpy.sa.Setnull(zone_raster_standard==i)
        expr=""" "Value" <> %i """ %(array_index[z])
        #expr="Value>%i" %(i)
        temp1=arcpy.sa.SetNull(zone_raster_standard,var_raster_standard,expr)
        temp1_pixel_sizeX=get_num_attributes(temp1, "CELLSIZEX")
        temp1_pixel_sizeY=get_num_attributes(temp1, "CELLSIZEY")
        temp1_pixel_area=temp1_pixel_sizeX*temp1_pixel_sizeY
        temp1_mean=get_num_attributes(temp1, "MEAN")
        temp1_std=get_num_attributes(temp1, "STD")
        
        if temp1_mean==0 and temp1_std==0:
            temp1_area=0
        else:
            Rows = arcpy.SearchCursor(temp1) 
            SomeValue = 'Count' # or some other column header name
            for row in Rows:
                val = row.getValue( SomeValue ) 
            temp1_area=val*temp1_pixel_area
        var_zone_area[z]=temp1_area
        var_zone_mean[z]=temp1_mean
        var_zone_std[z]=temp1_std
        del temp1
    zone_val_return=[var_zone_area,var_zone_mean,var_zone_std]
    return zone_val_return

def va_metric_wrapper(VA_func, i):
	t0 = time.time()			
	#Get species name, sp code, check if species already have been done
	jnk=CCE_Spp[i]
	jnk.encode('ascii','replace')
	inRaster = ce_data_dir + jnk
	sp_code_st=inRaster[-8:-4]
	resultsdir=resultsdir0+sp_code_st+"/"	
	sp_code=str(int(sp_code_st)) #get rid of extra zeros
	
	jnk=VA_func(sp_code_st, resultsdir, sp_code)
	
	if jnk[1]:
		print VA_func.__name__ + 'not applicable for species %s' %(sp_code_st);
	else:
		fx_nm=VA_func.__name__
		if not jnk[0]:
			t1 = time.time();
			time_elp=int(t1-t0)
			
			print 'took %i secs to apply %s for species %s' %(time_elp, fx_nm, sp_code_st);
		else:
			print 'already applied %s for species %s' %(fx_nm, sp_code_st);
	return
	

try:	
		if arcpy.CheckExtension("Spatial") == "Available":
			arcpy.CheckOutExtension("Spatial")
		Islands_name=['ko', 'ka', 'la', 'ma', 'mo', 'ni', 'oa', 'ha', 'all']
		Islands_list=['Kahoolawe', 'Kauai', 'Lanai', 'Maui', 'Molokai', 'Niihau', 'Oahu', 'Hawaii', 'all']
		Island_index=Islands_name.index(island)
		Island_name=Islands_list[Island_index]
		
		#SPECIES NOMENCLATURE TRANSLATION AND MODEL CODE LIST
		csvname="%sspp_name_synonyms.csv" %(CAO_data_dir)
		synonyms_file = csv.reader(csvname)
		f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
		reader = csv.reader(f)
		headers = reader.next()
		column = {}
		for h in headers:
		    column[h] = []
		for row in reader:
		   for h, v in zip(headers, row):
		     column[h].append(v)
		
		New_sp_names=column['Correct name']
		all_sp_codes=column['species codes']
		#Old_sp_names=column['Alternate name']
		#islands_present=column['Island']
		#all_sp_errors=column['Error type']
		
		#SPECIES HABITAT REQUIREMENT LIST
		csvname="%sspp_habitat_requirements.csv" %(CAO_data_dir)
		#hab_req_file = csv.reader(csvname)
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
		spp_hab_type=column['GAP_Habitat']
		spp_substrate_type=column['Substrate']
		spp_pioneer_data=column['Pioneer']
		spp_forest_compatibility=column['Forest']
		spp_shrubland_compatibility=column['Shrubland']
		spp_grassland_compatibility=column['Grassland']
		
		#IMPORT BIOME MAX HEIGHT DATA
		csvname="%sbiome_max_elev_by_bioregion_values.csv" %(landscape_factor_dir)
		#hab_req_file = csv.reader(csvname)
		f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
		reader = csv.reader(f)
		headers = reader.next()
		column = {}
		for h in headers:
		    column[h] = []
		for row in reader:
		   for h, v in zip(headers, row):
		     column[h].append(v)
		
		biome_elev_mat_headers=headers
		biome_elev_mat=column
		
		#END USER INPUT
		if import_cce_list:
			csvname='Y:/missing_sp_csv3.csv'
			f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
			reader = csv.reader(f)
			headers = reader.next()
			column = {}
			for h in headers:
				column[h] = []
			for row in reader:
			   for h, v in zip(headers, row):
				 column[h].append(eval(v))
			CCE_Spp=column['cce']
			FCE_Spp=column['fce']
			f.close()
			
		else:
			if all_files_in_directory==1:
				FCE_Spp = arcpy.ListRasters("FCE*", "tif")
				CCE_Spp = arcpy.ListRasters("CCE*", "tif")
				if len(subset_of_CEs)>0:
					FCE_Spp=FCE_Spp[subset_of_CEs[0]:subset_of_CEs[1]]
					CCE_Spp=CCE_Spp[subset_of_CEs[0]:subset_of_CEs[1]]
			else:
				CCE_Spp=['CCE0220.tif'] #for lanai cce0003, cce0055
				FCE_Spp=['FCE0220.tif']
		
		if reverse_spp_order==True:
			CCE_Spp=CCE_Spp[::-1]
			FCE_Spp=FCE_Spp[::-1]

		#Filter CO points to island only
		if island!='all':
			island_mask="%s%s/DEM/%s_extent.tif" %(landscape_factor_dir, island, island)
			island_mask=arcpy.Raster(island_mask)
				
		#LOAD AUXILIARY LAYERS
		#veg_zone_layer="%sVegetation Zones1.tif" %(landscape_factor_dir)
		veg_zone_layer="%sveg_zones2" %(landscape_factor_dir)
		veg_zone_layer=arcpy.Raster(veg_zone_layer)

		veg_types_layer="%slandfire_reclass_wetland_coastal_UTM_8b.tif" %(landscape_factor_dir)
		veg_types_layer=arcpy.Raster(veg_types_layer)
		
		#CO_data=r"%scorrected_CO_data2_merged_and_filtered.shp" %(CAO_data_dir) #corrected_CO_dataXY
		CO_data=r"%scorrected_CO_data4_merged_and_filtered.shp" %(CAO_data_dir) #corrected_CO_dataXY
		
		arcpy.MakeFeatureLayer_management(CO_data, "CO_lyr")
		
		Bioregions_loc="%sbioregions.shp" %(landscape_factor_dir)
		#arcpy.CopyFeatures_management(Bioregions_loc, "bioregions")
		arcpy.MakeFeatureLayer_management(Bioregions_loc, "bioregions_lyr")
		#FOR EACH SPECIES PERFORM OPERATIONS IN LOOP BELOW
		
		#if XXX:
		#	def XXX(sp_code_st, resultsdir, sp_code):	
		#		metric_NA=True
		#		#code
		#		if arcpy.Exists(loc_COR_CCE):				
		#			#code
		#			metric_previously_done=False
		#			metric_NA=False
		#		else:	
		#			metric_previously_done=True
		#			metric_NA=False
		#			
		#		return metric_previously_done, metric_NA
		#	for i in range(len(CCE_Spp)):
		#		va_metric_wrapper(XXX, i)
				

		###CREATE FUTURE AND BASELINE CLIMATE ENVELOPES
		if pre_process_envelopes:
			i=0 #for debug
			def pre_process_env_fx2(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				arcpy.MakeFeatureLayer_management(Bioregions_loc, "bioregions_lyr")
				arcpy.SelectLayerByAttribute_management ("bioregions_lyr", "CLEAR_SELECTION", )
				if not os.path.exists(resultsdir):
					os.mkdir(resultsdir)
				nf=0
				try:
					Sp_index=all_sp_codes.index(sp_code)
				except ValueError:
					nf=1
					total_CO_points=0
					total_zone_pts=0
					zone_CO=[0,0,0]
					sp_name="Unkown"
					pass
				if nf==0:
					sp_name=New_sp_names[Sp_index]
				
				expr=""" "sp_name" = '%s' """ %(sp_name)
				arcpy.SelectLayerByAttribute_management ("CO_lyr", "NEW_SELECTION", expr)
				sp_CO_points_loc=resultsdir+sp_code_st+"_sp_CO_points.shp"
				arcpy.CopyFeatures_management("CO_lyr", sp_CO_points_loc)
				if int(arcpy.GetCount_management(sp_CO_points_loc).getOutput(0))==0 and use_bio_region_filter==1:
					print 'no points to trim by bioregions'
				else:
					sp_code_st0=sp_code_st
					if use_bio_region_filter==1:
						sp_code_st=sp_code_st+"_trim"
						resultsdir=resultsdir0+sp_code_st+"/"
					if not os.path.exists(resultsdir):
						os.mkdir(resultsdir)
					jnk_dir=resultsdir+"DBFs"
					if not os.path.exists(jnk_dir):
						os.mkdir(jnk_dir)		
					part1_pre_done=0
				
					
					#print 'Starting calc for %s (%s)' %(sp_name, sp_code_st)
					
					#trim envelopes to single islands if necessary
					loc_COR_FCE=r"%sCOR_FCE%s.tif" %(resultsdir,sp_code_st)
					loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
					if arcpy.Exists(loc_COR_FCE)==False or overwrite==1:
						if island=='all':
							#MAP- SIMPLIFY CCE/CAO RASTER TO SINGLE CLASS
							inRaster = ce_data_dir + CCE_Spp[i]
							inRaster=arcpy.Raster(inRaster)
							if get_num_attributes(inRaster, "UNIQUEVALUECOUNT")==1 and get_num_attributes(inRaster, "MAXIMUM")==1: 
								CCE_full=inRaster
							else:
								CCE_full=arcpy.sa.SetNull(inRaster,1,"Value <1")
							loc_simple_CCE=r"%ssimplified_CCE_%s.tif" %(resultsdir,sp_code_st)
							CCE_full.save(loc_simple_CCE)
						
							inRaster = ce_data_dir + FCE_Spp[i]
							inRaster=arcpy.Raster(inRaster)
							if get_num_attributes(inRaster, "UNIQUEVALUECOUNT")==1 and get_num_attributes(inRaster, "MAXIMUM")==1: 
								FCE_full=inRaster
							else:
								FCE_full=arcpy.sa.SetNull(inRaster,1,"Value <1")
							#FCE_full=arcpy.sa.SetNull(inRaster,1,"Value <1")
							loc_simple_FCE=r"%ssimplified_FCE_%s.tif" %(resultsdir,sp_code_st)
							FCE_full.save(loc_simple_FCE)
							
						else:
							inRaster = ce_data_dir + CCE_Spp[i]
							inRaster=arcpy.Raster(inRaster)
							CCE_full= inRaster*island_mask
							if (get_num_attributes(inRaster, "UNIQUEVALUECOUNT")==1 and get_num_attributes(inRaster, "MAXIMUM")==1)==False: 
								CCE_full=arcpy.sa.SetNull(CCE_full,1,"Value <1")
							loc_simple_CCE=r"%ssimplified_CCE_%s.tif" %(resultsdir,sp_code_st)
							if arcpy.Exists(loc_simple_CCE)==False or overwrite==1:
								CCE_full.save(loc_simple_CCE)
								
							inRaster = ce_data_dir +FCE_Spp[i]
							inRaster=arcpy.Raster(inRaster)
							island_mask="%s%s/DEM/%s_extent.tif" %(landscape_factor_dir, island, island)
							island_mask=arcpy.Raster(island_mask)
							FCE_full= inRaster*island_mask
							if (get_num_attributes(inRaster, "UNIQUEVALUECOUNT")==1 and get_num_attributes(inRaster, "MAXIMUM")==1)==False:
								FCE_full=arcpy.sa.SetNull(FCE_full,1,"Value <1")
							loc_simple_FCE=r"%ssimplified_FCE_%s.tif" %(resultsdir,sp_code_st)
							if arcpy.Exists(loc_simple_FCE)==False or overwrite==1:
								FCE_full.save(loc_simple_FCE)
							
						#DEFINE THE ENVELOPE BIOREGIONS (USE THOSE FOR METRICS, BUT DISPLAY BOTH FULL AND OCCUPIED ENVELOPE)
						#IF NO POINTS, ASSUME ENTIRE ENVELOPE
						expr=""" "sp_name" = '%s' """ %(sp_name)##debug- need data #stupid SQL/ python parsing differences
						arcpy.SelectLayerByAttribute_management ("CO_lyr", "NEW_SELECTION", expr)
						sp_CO_points_loc=resultsdir+sp_code_st+"_sp_CO_points.shp" 
						arcpy.CopyFeatures_management("CO_lyr", sp_CO_points_loc)
						if int(arcpy.GetCount_management(sp_CO_points_loc).getOutput(0))>0 and use_bio_region_filter==1:
							#arcpy.CopyFeatures_management("CO_lyr", "sp_CO_points")
							#must first pick bioregions by CO points
							#arcpy.SelectLayerByLocation_management('bioregions', 'contains', 'sp_CO_points')
							arcpy.SelectLayerByLocation_management("bioregions_lyr", 'contains', sp_CO_points_loc)
							
							#Cut FCE and CCE by bioregion
							arcpy.Clip_management(CCE_full, "#", loc_COR_CCE,"bioregions_lyr", "0", "ClippingGeometry")
							CCE_temp=arcpy.Raster(loc_COR_CCE)
			
							arcpy.Clip_management(FCE_full, "#", loc_COR_FCE,"bioregions_lyr", "0", "ClippingGeometry")
							FCE_temp=arcpy.Raster(loc_COR_FCE)
				
						else:
							CCE_temp=CCE_full
							FCE_temp=FCE_full
							CCE_temp.save(loc_COR_CCE)
							FCE_temp.save(loc_COR_FCE)
						metric_previously_done=False
						metric_NA=False
					else:	
						metric_previously_done=True
						metric_NA=False
						
					return metric_previously_done, metric_NA				
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(pre_process_env_fx2, i)		

		#calculate veg type areas
		if calculate_veg_type_areas:
			def calculate_veg_type_areas_fx2(sp_code_st, resultsdir, sp_code):	
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_CCE):				
					#CALC area in each habitat type
					opath="%sDBFs/vegtype_areas%s.csv" %(resultsdir,sp_code_st)
					if arcpy.Exists(opath)==False or overwrite==1:
						CCE_temp=arcpy.Raster(loc_COR_CCE)
						inRaster = CCE_temp
						outname=r"%sDBFs/vegtype_areas%s.dbf" %(resultsdir,sp_code_st)
						arcpy.sa.TabulateArea(CCE_temp,"VALUE",veg_types_layer,"VALUE",outname)
						db = dbf.Dbf(outname)
						rec=db[0]
						veg_area=[0]*14
						for ire in range(0,14):
							jnk="VALUE_%i" %(ire)
							try:
									area_jnk=rec[jnk]/1000000
									veg_area[ire]=area_jnk
							except:
									pass							
						#jnk=[area_CCE]
						save_temp_csv_data(veg_area, opath)
						del CCE_temp; del inRaster; del outname; del rec; del db; del veg_area; del opath;
						metric_previously_done=False
						metric_NA=False
					else:	
						metric_previously_done=True
						metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calculate_veg_type_areas_fx2, i)
										
		#CALC CCE TOTAL AREA
		if calc_cce_total_area:
			def calc_cce_total_area_fx2(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_CCE):				
					opath="%sDBFs/calc_area_CCE%s.csv" %(resultsdir,sp_code_st)
					if arcpy.Exists(opath)==False or overwrite==1:
						CCE_temp=arcpy.Raster(loc_COR_CCE)
						inRaster = CCE_temp
						outname=r"%sDBFs/calc_area_CCE%s.dbf" %(resultsdir,sp_code_st)
						arcpy.sa.TabulateArea(CCE_temp,"VALUE",CCE_temp,"VALUE",outname)
						db = dbf.Dbf(outname)
						rec=db[0]
						area_CCE=rec["VALUE_1"]/1000000
						del db
						jnk=[area_CCE]
						save_temp_csv_data(jnk, opath)
						metric_previously_done=False
						metric_NA=False
					else:	
						metric_previously_done=True
						metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_cce_total_area_fx2, i)
					
		#CALC FCE TOTAL AREA
		if calc_fce_total_area:
			def calc_fce_total_area_fx2(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				t0 = time.time()
				jnk=CCE_Spp[i]
				jnk.encode('ascii','replace')
				inRaster = ce_data_dir + jnk
				sp_code_st=inRaster[-8:-4]
				resultsdir=resultsdir0+sp_code_st+"/"	
				sp_code=str(int(sp_code_st)) #get rid of extra zeros
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_FCE=r"%sCOR_FCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_FCE):				
					opath="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
					FCE_temp=arcpy.Raster(loc_COR_FCE)
					jnk_name=loc_COR_FCE+".xml"
					if not os.path.exists(jnk_name):
						arcpy.CalculateStatistics_management(FCE_temp)
					if arcpy.Exists(opath)==False or overwrite==1:
						try:
							jnk_FCE_exists=get_num_attributes(FCE_temp,"MEAN")>0
						except:
							jnk_FCE_exists=False
							
						if jnk_FCE_exists:
							inRaster = FCE_temp
							outname=r"%sDBFs/calc_area_FCE%s.dbf" %(resultsdir,sp_code_st)
							arcpy.sa.TabulateArea(FCE_temp,"VALUE",FCE_temp,"VALUE",outname)
							db = dbf.Dbf(outname)
							rec=db[0]
							area_FCE=rec["VALUE_1"]/1000000
						else:
							area_FCE=0
						jnk=[area_FCE]
						save_temp_csv_data(jnk, opath)						
						
						metric_previously_done=False
						metric_NA=False
					else:	
						metric_previously_done=True
						metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_fce_total_area_fx2, i)
					
		##CALC CCE-FCE
		if calc_cce_fce_dif:
			def calc_cce_fce_dif_fx2(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_CCE):
					opath0="%sDBFs/area_diff%s.csv" %(resultsdir,sp_code_st)
					if arcpy.Exists(opath0):
						opath1="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
						jnk=load_temp_csv_float_data(opath1)
						area_FCE=jnk[0]
			
						opath2="%sDBFs/calc_area_CCE%s.csv" %(resultsdir,sp_code_st)
						jnk=load_temp_csv_float_data(opath2)
						area_CCE=jnk[0]
			
						area_dif=area_CCE-area_FCE
						save_temp_csv_data(area_dif, opath0)
						del opath1; del opath2; del area_dif; del area_FCE; del area_CCE
						calc_area_dif(resultsdir,sp_code_st)
							
						metric_previously_done=False
						metric_NA=False
					else:	
						metric_previously_done=True
						metric_NA=False
						
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_cce_fce_dif_fx2, i)
				
		##MAP- TOLERATE ZONE- COMMON AREA BETWEEN CCE AND FCE
		if map_tol_zone:
			def map_tol_zone_fx2(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_FCE=r"%sCOR_FCE%s.tif" %(resultsdir,sp_code_st)
				loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_CCE):				
					CCE_temp=arcpy.Raster(loc_COR_CCE)
					FCE_temp=arcpy.Raster(loc_COR_FCE)
					loc_intersect=r"%sintersect_%s.tif" %(resultsdir,sp_code_st)
					if arcpy.Exists(loc_intersect)==False or overwrite==1:
						opath="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
						jnk=load_temp_csv_float_data(opath)
						area_FCE=jnk[0]
						if area_FCE!=0:
							Tolerate_zone=CCE_temp*FCE_temp
						else:
							Tolerate_zone=arcpy.sa.SetNull(CCE_temp,CCE_temp,"Value <=1") #changed!
						Tolerate_zone.save(loc_intersect)	
						metric_previously_done=False
						metric_NA=False
					else:	
						metric_previously_done=True
						metric_NA=False
						
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(map_tol_zone_fx2, i)


		##CALCULATE MICRO-REFUGIA ZONE AREA
		if map_mrf_zone:
			def map_mrf_zone_fx2(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_CCE):				
					CCE_temp=arcpy.Raster(loc_COR_CCE)
					loc_intersect=r"%sintersect_%s.tif" %(resultsdir,sp_code_st)
					Tolerate_zone=arcpy.Raster(loc_intersect)
					loc_refuge=r"%srefuge_%s.tif" %(resultsdir,sp_code_st)
					if arcpy.Exists(loc_refuge)==False or overwrite==1:
						opath="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
						jnk=load_temp_csv_float_data(opath)
						area_FCE=jnk[0]
						if area_FCE!=0:
							Non_overlap_temp = arcpy.sa.IsNull(Tolerate_zone)
							Microrefugia_zone=CCE_temp*Non_overlap_temp
							Microrefugia_zone=arcpy.sa.SetNull(Microrefugia_zone,1,"Value <1")
						else:
							Microrefugia_zone=CCE_temp
						metric_previously_done=False
						metric_NA=False
					else:	
						metric_previously_done=True
						metric_NA=False
						
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(map_mrf_zone_fx2, i)
									
		##MAP MIGRATE ZONE PART 1
		if map_mig_zone_pt1:
			def map_mig_zone_pt1_fx2(i):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_FCE=r"%sCOR_FCE%s.tif" %(resultsdir,sp_code_st)
				loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_CCE):				
					FCE_temp=arcpy.Raster(loc_COR_FCE)
					loc_intersect=r"%sintersect_%s.tif" %(resultsdir,sp_code_st)
					Tolerate_zone=arcpy.Raster(loc_intersect)
						
					loc_Migrate=r"%sMigrate_%s.tif" %(resultsdir,sp_code_st)
					if arcpy.Exists(loc_Migrate)==False or overwrite==1:
						opath="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
						jnk=load_temp_csv_float_data(opath)
						area_FCE=jnk[0]					
						if area_FCE!=0:
							Non_overlap_temp = arcpy.sa.IsNull(Tolerate_zone)
							Migrate_temp=FCE_temp*Non_overlap_temp
							Migrate_temp=arcpy.sa.SetNull(Migrate_temp,1,"Value <1")
						else:
							Migrate_temp=Tolerate_zone
						Migrate_temp.save(loc_Migrate)				
						metric_previously_done=False
						metric_NA=False
					else:	
						metric_previously_done=True
						metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(map_mig_zone_pt1_fx2, i)
				
		##CALCULATE DISTANCE OF FCE FROM SOURCE CCE AREAS
		##CALCULATE EUCLIDIAN DISTANCE OF ALL CELLS TO NEAREST CCE/CAO
		if calc_dist_fce_to_CCE:
			def calc_dist_fce_to_CCE_fx2(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_FCE=r"%sCOR_FCE%s.tif" %(resultsdir,sp_code_st)
				loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_CCE):				
						opath="%sDBFs/FCE_distance_%s.csv" %(resultsdir,sp_code_st)
						if arcpy.Exists(opath)==False or overwrite==1:
							opath_areaFCE="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
							jnk=load_temp_csv_float_data(opath_areaFCE)
							area_FCE=jnk[0]				
							if area_FCE!=0:
								CCE_temp=arcpy.Raster(loc_COR_CCE)
								FCE_temp=arcpy.Raster(loc_COR_FCE)
								inRaster = FCE_temp #CCE_Spp[i]
								inRaster_name = FCE_Spp[i]
								FCE_dist_temp = arcpy.sa.EucDistance(inRaster)
								#CLIP DISTANCE SURFACE USING FCE
								FCE_dist_temp=FCE_dist_temp*CCE_temp
								FCE_distance=get_num_attributes(FCE_dist_temp,"MEAN")
								if kio==0:
									try:
										arcpy.Delete_management(FCE_dist_temp)
									except:
										pass
							else:
								FCE_distance='wink out'						
							jnk=[FCE_distance]
							save_temp_csv_data(jnk, opath)
							metric_previously_done=False
							metric_NA=False
						else:	
							metric_previously_done=True
							metric_NA=False
						
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_dist_fce_to_CCE_fx2, i)
				
		##CALCULATE MEAN ELEVATION OF CCE
		if calc_mean_elev_cce:
			def calc_mean_elev_cce_fx2(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				inRasterloc2 = r"%s%s/DEM/%s_dem.tif" %(landscape_factor_dir,island,island)	
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_CCE):				
					opath="%sDBFs/CCE_elev_%s.csv" %(resultsdir,sp_code_st)
					if arcpy.Exists(opath)==False or overwrite==1:
						CCE_temp=arcpy.Raster(loc_COR_CCE)
						CCE_DEM_temp=CCE_temp*arcpy.Raster(inRasterloc2)
						CCE_mean_elev=get_num_attributes(CCE_DEM_temp,"MEAN")
						CCE_min_elev=get_num_attributes(CCE_DEM_temp,"MINIMUM")
						CCE_max_elev=get_num_attributes(CCE_DEM_temp,"MAXIMUM")
						CCE_stdev_elev=get_num_attributes(CCE_DEM_temp,"STD")
						if kio==0:
							try:
								arcpy.Delete_management(CCE_DEM_temp)
							except:
								pass
							
						jnk=[CCE_mean_elev, CCE_min_elev, CCE_max_elev, CCE_stdev_elev]
						save_temp_csv_data(jnk, opath)
					#else:
					#	jnk=load_temp_csv_float_data(opath)
					#	CCE_mean_elev=jnk[0]
					#	CCE_min_elev=jnk[1]
					#	CCE_max_elev=jnk[2]
						metric_previously_done=False
						metric_NA=False
					else:	
						metric_previously_done=True
						metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_mean_elev_cce_fx2, i)
				
		##CALCULATE MEAN ELEVATION OF FCE
		if calc_mean_elev_fce:
			def calc_mean_elev_fce_fx2(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				bioregion_loc="%sbioregions.tif" %(landscape_factor_dir)
				bioregions=arcpy.Raster(bioregion_loc)
				Sp_index=all_sp_codes.index(sp_code)
				loc_COR_FCE=r"%sCOR_FCE%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(loc_COR_FCE):				
					opath_areaFCE="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
					jnk=load_temp_csv_float_data(opath_areaFCE)
					area_FCE=jnk[0]				
					if area_FCE!=0:
						opath="%sDBFs/FCE_elev_%s.csv" %(resultsdir,sp_code_st)
						opath1="%sDBFs/min_elev_zone_vals_%s.csv" %(resultsdir,sp_code_st)
						opath2="%sDBFs/max_elev_zone_vals_%s.csv" %(resultsdir,sp_code_st)
						if arcpy.Exists(opath2)==False or overwrite==1:	
							FCE_temp=arcpy.Raster(loc_COR_FCE)
							FCE_DEM_temp=FCE_temp*arcpy.Raster(inRasterloc2)
							if arcpy.Exists(opath)==False or overwrite==1:
								FCE_mean_elev=get_num_attributes(FCE_DEM_temp,"MEAN")
								FCE_min_elev=get_num_attributes(FCE_DEM_temp,"MINIMUM")
								FCE_max_elev=get_num_attributes(FCE_DEM_temp,"MAXIMUM")
								try:
									FCE_stdev_elev=get_num_attributes(FCE_DEM_temp,"STD")
								except:
									FCE_stdev_elev=0 #this is necessary if there is single pixel envelope
								jnk=[FCE_mean_elev, FCE_min_elev, FCE_max_elev, FCE_stdev_elev]
								save_temp_csv_data(jnk, opath)
				
							if arcpy.Exists(opath2)==False or overwrite==1:
								loc_min_elev_FCE_table=r"%sDBFs/min_elev_FCE_%s.dbf" %(resultsdir,sp_code_st)
								arcpy.sa.ZonalStatisticsAsTable(bioregions,"VALUE", FCE_DEM_temp, loc_min_elev_FCE_table)
								db = dbf.Dbf(loc_min_elev_FCE_table)
								min_elev_zone_vals= [0] * 18
								max_elev_zone_vals= [0] * 18
								
								for z in range(len(db)):
									min_elev_zone_vals[db[z][0]]=db[z][3]	
									max_elev_zone_vals[db[z][0]]=db[z][4]
								
								if kio==0:
									try:
										del db
										arcpy.Delete_management(FCE_DEM_temp)
									except:
										pass							
								save_temp_csv_data(min_elev_zone_vals, opath1)
								save_temp_csv_data(max_elev_zone_vals, opath2)
					
							metric_previously_done=False
							metric_NA=False
						else:	
							metric_previously_done=True
							metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_mean_elev_fce_fx2, i)
					
		##################
		########END PART 1
		##################
		
		################################
		#########START RESPONSE ZONE MAP
		################################
		if create_rep_zones:
			def create_rep_zones_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				
				loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
				rrun=1	
				if arcpy.Exists(loc_response_zone)==False or overwrite==1:
					opath="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
					jnk=load_temp_csv_float_data(opath)
					area_FCE=jnk[0]
					if area_FCE!=0:
						loc_Migrate=r"%sMigrate_%s.tif" %(resultsdir,sp_code_st)
						Migrate_temp=arcpy.Raster(loc_Migrate)
						loc_refuge=r"%srefuge_%s.tif" %(resultsdir,sp_code_st)
						Microrefugia_zone=arcpy.Raster(loc_refuge)
						loc_intersect=r"%sintersect_%s.tif" %(resultsdir,sp_code_st)
						Tolerate_zone=arcpy.Raster(loc_intersect)
						#MAP TRANSITION ZONE BETWEEN CCE AND FCE
						#USING LINEAR DISTANCE + VIEWSHED APPROACH
						if sp_envelope_gap==1:
							FCE_Distance_dir=r"%sFCE_Distance_dir_%s.tif" %(resultsdir,sp_code_st)
							CCE_Distance_dir=r"%sCCE_Distance_dir_%s.tif" %(resultsdir,sp_code_st)
							jnk=min(max_search_dist_for_transition_zone, int(FCE_distance))
							FCE_Distance_temp = arcpy.sa.EucDistance(Migrate_temp, jnk,"",FCE_Distance_dir)
							CCE_Distance_temp = arcpy.sa.EucDistance(CCE_temp, jnk,"",CCE_Distance_dir)
							if kio==0:
								try:
									arcpy.Delete_management(CCE_Distance_temp); arcpy.Delete_management(FCE_Distance_temp)
								except:
									pass
							t1 = time.time(); print 'Step 9 done (%i secs): calc dist and dir from CCE and FCE for species %s' %(int(t1-t0), sp_code_st); t0 = time.time()
							FCE_Distance_dir_temp=arcpy.Raster(FCE_Distance_dir)
							CCE_Distance_dir_temp=arcpy.Raster(CCE_Distance_dir)
							FCE_Distance_dir_temp=arcpy.sa.SetNull(FCE_Distance_dir_temp,FCE_Distance_dir_temp,"Value=0") #get rid of areas within CEs
							CCE_Distance_dir_temp=arcpy.sa.SetNull(CCE_Distance_dir_temp,CCE_Distance_dir_temp,"Value=0")
							t1 = time.time(); print 'Step 10 done (%i secs): clip dir values within CCE and FCE for species %s' %(int(t1-t0), sp_code_st); t0 = time.time()
							FCE_Distance_dir_temp=FCE_Distance_dir_temp*(CCE_Distance_dir_temp^0) #clip direction rasters to only areas where distance to both CEs is within specified limits
							CCE_Distance_dir_temp=CCE_Distance_dir_temp*(FCE_Distance_dir_temp^0)	
							t1 = time.time(); print 'Step 11 done (%i secs): clip dir values beyond max distance from both CCE and FCE for species %s' %(int(t1-t0), sp_code_st); t0 = time.time()
							if get_num_attributes(CCE_Distance_dir_temp, "MEAN")!=0 and sp_envelope_gap==1: #no need to look at areas between envelopes if there are no candidate areas		
								angle_comparison_temp1=arcpy.sa.Cos(FCE_Distance_dir_temp*deg2rad) * arcpy.sa.Cos((CCE_Distance_dir_temp+180)*deg2rad) + arcpy.sa.Sin(FCE_Distance_dir_temp*deg2rad) * arcpy.sa.Sin((CCE_Distance_dir_temp+180)*deg2rad)
								angle_comparison_temp2=(CCE_Distance_dir_temp^0)*math.cos(90*deg2rad) #multiplying by mask to get same extent as other expression (#clip both distance buffers to only where two distances are within a given value)
								tranzition_zone_temp=angle_comparison_temp1 >= angle_comparison_temp2
								tranzition_zone_temp=arcpy.sa.SetNull(tranzition_zone_temp,tranzition_zone_temp,"Value=0")
								
								if kio==0:
									try:
										arcpy.Delete_management(FCE_Distance_dir_temp); arcpy.Delete_management(CCE_Distance_dir_temp); arcpy.Delete_management(angle_comparison_temp1);arcpy.Delete_management(angle_comparison_temp2)
										del_layer("fce_distance_dir_temp"); del_layer("cce_distance_dir_temp");
									except:
										pass
								t1 = time.time(); print 'Step 12 done (%i secs):  map transition zone for species %s' %(int(t1-t0), sp_code_st); t0 = time.time()
								
								path_cce_elev="%sDBFs/CCE_elev_%s.csv" %(resultsdir,sp_code_st)
								jnk=load_temp_csv_float_data(path_cce_elev)
								CCE_min_elev=jnk[1]

								#inDEM = r"%s%s_DEM/%s_dem" %(demdir,Island_name, Island_name)
								inDEM = r"%s%s/DEM/%s_dem.tif" %(landscape_factor_dir,island,island) #trim transition zone by min CCE and max FCE elevations
								inDEM=arcpy.Raster(inDEM)
								jnk=(inDEM < FCE_max_elev) & (inDEM > CCE_min_elev)
								jnk=arcpy.sa.SetNull(jnk,1,"Value=0")
								tranzition_zone_temp=tranzition_zone_temp*jnk
								loc_transition_zone=r"%stransition_zone_%s.tif" %(resultsdir,sp_code_st)
								tranzition_zone_temp.save(loc_transition_zone)
								if kio==0:
									try:
										arcpy.Delete_management(jnk); del_layer("jnk")
									except:
										pass
								t1 = time.time(); print 'Step 13 done (%i secs):  trim hi and lo elev values from transition zone for species %s' %(int(t1-t0), sp_code_st); t0 = time.time()
							
								migration_zone=arcpy.sa.Con(arcpy.sa.IsNull(tranzition_zone_temp),0,tranzition_zone_temp) + arcpy.sa.Con(arcpy.sa.IsNull(Migrate_temp),0,Migrate_temp)
								migration_zone=arcpy.sa.SetNull(migration_zone,migration_zone,"Value=0")	
								if kio==0:
									try:
										arcpy.Delete_management(tranzition_zone_temp); del_layer("tranzition_zone_temp")
									except:
										pass
							else:
								migration_zone=Migrate_temp
						else:
							migration_zone=Migrate_temp
							
						#migration_zone=Migrate_temp
						response_zones= arcpy.sa.Con(arcpy.sa.IsNull(Microrefugia_zone),0,Microrefugia_zone) + (arcpy.sa.Con(arcpy.sa.IsNull(Tolerate_zone),0,Tolerate_zone))*2 + (arcpy.sa.Con(arcpy.sa.IsNull(migration_zone),0,migration_zone))*3 
						response_zones=arcpy.sa.SetNull(response_zones,response_zones,"Value=0") #MRF=1, tol= 2, mig=3
			
						if kio==0:
							try: #sometimes arcgis cannot delete file if it is in use (this avoids python to return error in delete operation and stop running code)
								arcpy.Delete_management(Tolerate_zone); del_layer("Tolerate_zone")
								arcpy.Delete_management(Migrate_temp); del_layer("Migrate_temp")
								arcpy.Delete_management(Microrefugia_zone); del_layer("Microrefugia_zone")
								arcpy.Delete_management(migration_zone); del_layer("migration_zone")	
							except:
								pass
					else:
						loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
						CCE_temp=arcpy.Raster(loc_COR_CCE)
						response_zones= CCE_temp

					loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones.save(loc_response_zone)
					
					loc_response_zone_shp=r"%sresponse_zone_%s.shp" %(resultsdir,sp_code_st)
					arcpy.RasterToPolygon_conversion(loc_response_zone, loc_response_zone_shp, "SIMPLIFY", "VALUE")
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(create_rep_zones_fx, i)
				
		###############################
		########END RESPONSE ZONE MAP
		###############################
		print "calculating response zone metrics"
		
				
		#CALC RESPONSE ZONE AREA
		if calc_resp_zone_area:
			def calc_resp_zone_area_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				
				path_zone_index=r"%sDBFs/%s_zone_index.csv" %(resultsdir, sp_code_st)
				path_zone_area=r"%sDBFs/%s_zone_area.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(path_zone_index)==False or arcpy.Exists(path_zone_area)==False or overwrite==1:
					loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)
					
					outname=r"%sDBFs/response_zone_areas_%s.dbf" %(resultsdir,sp_code_st)
					arcpy.sa.TabulateArea(response_zones,"VALUE",response_zones,"VALUE",outname)
					db = dbf.Dbf(outname)
					
					#find which zones are available for species
					zone_index=[]
					zone_area=[0, 0, 0]
					for z in range(len(db)):
						zone_index.append(db[z][0]-1)
						zone_area[db[z][0]-1]=db[z][z+1]
					del db
					zone_area[:]=[x/1000000 for x in zone_area]
					
					save_temp_csv_data(zone_area, path_zone_area)
					
					ofile = open(path_zone_index, 'wb')
					writer = csv.writer(ofile, dialect='excel')
					writer.writerow(zone_index)
					ofile.close()
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_resp_zone_area_fx, i)
	
		###RESPONSE ZONES ARE DEFINED ABOVE###
		######START CALCULATING METRICS#######
		zones=[1,2,3]
		veg_zones=[0, 1, 2, 3, 4, 5, 6, 7, 8]
				#make all calcs using single raster with 3 zones
				
			
		#SLR
		if calc_zone_slr_area:
			def calc_zone_slr_area_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				
				opath=r"%sDBFs/%s_zone_slr.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1: 
					path_cce_elev="%sDBFs/CCE_elev_%s.csv" %(resultsdir,sp_code_st)
					jnk=load_temp_csv_float_data(path_cce_elev)
					CCE_min_elev=jnk[1]

					if CCE_min_elev<highest_slr_impact:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
						response_zones=arcpy.Raster(loc_response_zone)
						slr_map_loc="%s%s/DEM/%s_1mSLR.tif" %(landscape_factor_dir,island,island)
						slr_map=arcpy.Raster(slr_map_loc)
						slr_map=slr_map*response_zones
						#slr_map=arcpy.sa.SetNull(slr_map,1,"Value=0")
						if not get_num_attributes(slr_map,"MEAN")==0:
							loc_slr=r"%sslr_%s.tif" %(resultsdir,sp_code_st)
							slr_map.save(loc_slr)		
							loc_slr_table=r"%sDBFs/slr_%s.dbf" %(resultsdir,sp_code_st)
							#if use_zonal_stats==1:							
							#arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", loc_slr, loc_slr_table,"DATA")
							arcpy.sa.TabulateArea(response_zones,"VALUE", loc_slr, "VALUE", loc_slr_table)
							db = dbf.Dbf(loc_slr_table)
							temp_zone_index=[]
							for z in range(len(db)):
								temp_zone_index.append(zones.index(db[z][0]))	
							zone_slr=get_zone_stats(temp_zone_index, db, "VALUE_1")
							#else:
							#	pass
							zone_slr[:]=[x/1000000 for x in zone_slr]
							try:
								del db
								del slr_map
							except:
								pass
						else:
							zone_slr=[0, 0, 0]
					else:
						zone_slr=[0, 0, 0]
					save_temp_csv_data(zone_slr, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_zone_slr_area_fx, i)
				
		#CALCULATE habitat area within young lava flows
		if calc_zone_lava_flow_area:
			def calc_zone_lava_flow_area_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
				try:
					Sp_index=hab_sp_code.index(str(sp_code))
					Sp_pioneer_status=spp_pioneer_data[Sp_index]
					if len(Sp_pioneer_status)>0 and Sp_pioneer_status=='0': #MUST DEBUG!
						Sp_pioneer_status=eval(Sp_pioneer_status)
					#	flow_info=1
					#else:
					#	zone_lava_flows=[0, 0, 0]	
				except ValueError:
					Sp_index='9999'
					Sp_pioneer_status='NA'
			#		zone_lava_flows=[0, 0, 0]
			#		zone_bad_substrate=[0, 0, 0]
					pass
				opath=r"%sDBFs/%s_zone_lava_flows.csv" %(resultsdir, sp_code_st)
				loc_lava_flows=r"%slava_flows_%s.tif" %(resultsdir,sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1:
					loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)
					young_lava_flows = arcpy.Raster(r"%spioneer" %(landscape_factor_dir))
					young_lava_flows=young_lava_flows*response_zones
					if not get_num_attributes(young_lava_flows,"MEAN")==0:
						young_lava_flows=arcpy.sa.SetNull(young_lava_flows,1,"Value=0")
						young_lava_flows.save(loc_lava_flows)		
						#if use_zonal_stats==1:							
						loc_lava_flows_table=r"%sDBFs/lava_flows_%s.dbf" %(resultsdir,sp_code_st)
						#arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", loc_lava_flows, loc_lava_flows_table,"DATA")
						arcpy.sa.TabulateArea(response_zones,"VALUE",loc_lava_flows, "VALUE",loc_lava_flows_table)
						db = dbf.Dbf(loc_lava_flows_table)
						temp_zone_index=[]
						for z in range(len(db)):
							temp_zone_index.append(zones.index(db[z][0]))	
					
						zone_lava_flows=get_zone_stats(temp_zone_index, db, "VALUE_1")
						#else:
						#	pass
						zone_lava_flows[:]=[x/1000000 for x in zone_lava_flows]
						try:
							del db
							del young_lava_flows
						except:
							pass
						
						save_temp_csv_data(zone_lava_flows, opath)
					else:
						zone_lava_flows=[0, 0, 0]
						save_temp_csv_data(zone_lava_flows, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_zone_lava_flow_area_fx, i)
				
		#HABITAT QUALITY (UGLY)
		if calc_zone_hab_qual:
			def calc_zone_hab_qual_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)
		
				opath=r"%sDBFs/%s_Zone_ugly_hab.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1:
					loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)
					GBU_map_loc=arcpy.Raster(r"%shabqual.tif" %(landscape_factor_dir))
					outname=r"%sDBFs/GBU_areas_%s.dbf" %(resultsdir,sp_code_st)
					arcpy.sa.TabulateArea(response_zones,"VALUE",GBU_map_loc,"VALUE",outname)
					#arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", loc_Good_LC, loc_good_habitat_table,"DATA")
					db = dbf.Dbf(outname)
					temp_zone_index=[]
					for z in range(len(db)):
						temp_zone_index.append(zones.index(db[z][0]))	
					field_names=db.fieldNames
					
					avail=0
					try:				
						field_names.index('VALUE_1')
						avail=1
					except:
						avail=0
					
					if avail==1:
						Zone_ugly_hab=get_zone_stats(temp_zone_index, db, "VALUE_1")
						Zone_ugly_hab[:]=[x/1000000 for x in Zone_ugly_hab]
					else:
						Zone_ugly_hab=[0]*3
						
			
					
					save_temp_csv_data(Zone_ugly_hab, opath)
			
					try:
						del db
						
					except:
						pass			
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_zone_hab_qual_fx, i)
				
		#CALC EFFECTIVE HAB QUAL
		if calc_eff_hab_qual_nonpioneer:
			def calc_eff_hab_qual_nonpioneer_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				eff_map_loc="%sarea_subtr.tif" %(landscape_factor_dir)
				opath=r"%sDBFs/%s_eff_nonpioneer_zone_area.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1:
					loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)					
					#eff_map=arcpy.Raster(eff_map_loc)
					#eff_map=eff_map*response_zones
					#loc_eff=r"%seff_%s.tif" %(resultsdir,sp_code_st)
					#eff_map.save(loc_eff)		
					loc_eff_table=r"%sDBFs/eff_%s.dbf" %(resultsdir,sp_code_st)
					#arcpy.sa.TabulateArea(response_zones,"VALUE", loc_eff, "VALUE", loc_eff_table)
					arcpy.sa.TabulateArea(response_zones,"VALUE", eff_map_loc, "VALUE", loc_eff_table)
					db = dbf.Dbf(loc_eff_table)
					temp_zone_index=[]
					for z in range(len(db)):
						temp_zone_index.append(zones.index(db[z][0]))	
					zone_eff=get_zone_stats(temp_zone_index, db, "VALUE_1")
					zone_eff[:]=[x/1000000 for x in zone_eff]
					
					try:
						del db
						del eff_map
					except:
						pass
					save_temp_csv_data(zone_eff, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_eff_hab_qual_nonpioneer_fx, i)
				
		#CALC EFFECTIVE HAB QUAL
		if calc_eff_hab_qual_pioneer:
			def calc_eff_hab_qual_pioneer_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				eff_pioneer_map_loc="%sarea_subtr_pioneer.tif" %(landscape_factor_dir)
				opath=r"%sDBFs/%s_eff_pioneer_zone_area.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1: 
					loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)
					loc_eff_pioneer_table=r"%sDBFs/eff_pioneer_%s.dbf" %(resultsdir,sp_code_st)
					arcpy.sa.TabulateArea(response_zones,"VALUE", eff_pioneer_map_loc, "VALUE", loc_eff_pioneer_table)
					db = dbf.Dbf(loc_eff_pioneer_table)
					temp_zone_index=[]
					for z in range(len(db)):
						temp_zone_index.append(zones.index(db[z][0]))	
					zone_eff_pioneer=get_zone_stats(temp_zone_index, db, "VALUE_1")
					zone_eff_pioneer[:]=[x/1000000 for x in zone_eff_pioneer]
					
					try:
						del db
						del eff_pioneer_map
					except:
						pass
					save_temp_csv_data(zone_eff_pioneer, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_eff_hab_qual_pioneer_fx, i)
				
		#CREATE EFFECTIVE ZONES FOR HAB QUAL CALCULATIONS
		if chose_eff_hab_qual:
			def chose_eff_hab_qual_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		
				try:
					Sp_index=hab_sp_code.index(str(sp_code))
					pioneer_stat=spp_pioneer_data[Sp_index]
				except ValueError:
					pioneer_stat='0'
					pass
				opath=r"%sDBFs/%s_eff_hab_qual_zone_area.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1:
					loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)				
					if pioneer_stat=='1':
						opath0=r"%sDBFs/%s_eff_pioneer_zone_area.csv" %(resultsdir, sp_code_st)
						zone_eff_pioneer= load_temp_csv_float_data(opath0)
						zone_eff_hab_qual=zone_eff_pioneer
						eff_pioneer_map_loc="%sarea_subtr_pioneer.tif" %(landscape_factor_dir)					
						eff_response_zones=response_zones*arcpy.Raster(eff_pioneer_map_loc)
						
					else:
						opath0=r"%sDBFs/%s_eff_nonpioneer_zone_area.csv" %(resultsdir, sp_code_st)
						zone_eff= load_temp_csv_float_data(opath0) 
						zone_eff_hab_qual=zone_eff
						eff_map_loc="%sarea_subtr.tif" %(landscape_factor_dir)
						eff_response_zones=response_zones*arcpy.Raster(eff_map_loc)
					
					eff_response_zone_loc=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)
					eff_response_zones.save(eff_response_zone_loc)
					
					path_eff_zone_area=r"%sDBFs/%s_eff_zone_area.csv" %(resultsdir, sp_code_st)
					save_temp_csv_data(zone_eff_hab_qual, path_eff_zone_area)
					save_temp_csv_data(zone_eff_hab_qual, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(chose_eff_hab_qual_fx, i)
		
		#if create_eff_resp_zones:		
		#	def create_eff_resp_zone_fx(sp_code_st, resultsdir, sp_code):
		#		metric_NA=True
		#		Sp_index=all_sp_codes.index(sp_code)		
		#		try:
		#			Sp_index=hab_sp_code.index(str(sp_code))
		#			pioneer_stat=spp_pioneer_data[Sp_index]
		#		except ValueError:
		#			pioneer_stat='0'
		#			pass
		#		eff_response_zone_loc=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
		#		if arcpy.Exists(eff_response_zone_loc)==False or overwrite==1: 
		#			if pioneer_stat=='1':
		#				eff_map_loc="%sarea_subtr_pioneer.tif" %(landscape_factor_dir)
		#			else:
		#				eff_map_loc="%sarea_subtr.tif" %(landscape_factor_dir)
		#			loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
		#			response_zones=arcpy.Raster(loc_response_zone)					
		#			eff_response_zones=response_zones*arcpy.Raster(eff_map_loc)
		#			eff_response_zones.save(eff_response_zone_loc)
		#
		#			metric_previously_done=False
		#			metric_NA=False
		#		else:	
		#			metric_previously_done=True
		#			metric_NA=False
		#			
		#		return metric_previously_done, metric_NA
		#	for i in range(len(CCE_Spp)):
		#		va_metric_wrapper(create_eff_resp_zone_fx, i)		
												
		##CALC EFF RESPONSE ZONE AREA
		#if calc_eff_resp_zone_area:
		#	def calc_eff_resp_zone_area_fx(sp_code_st, resultsdir, sp_code):
		#		metric_NA=True
		#		Sp_index=all_sp_codes.index(sp_code)
		#		
		#		path_eff_zone_index=r"%sDBFs/%s_eff_zone_index.csv" %(resultsdir, sp_code_st)
		#		path_eff_zone_area=r"%sDBFs/%s_eff_zone_area.csv" %(resultsdir, sp_code_st)
		#		if arcpy.Exists(path_eff_zone_area)==False or arcpy.Exists(path_eff_zone_area)==False or overwrite==1:
		#			loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
		#			response_zones=arcpy.Raster(loc_response_zone)
		#			
		#			outname=r"%sDBFs/eff_response_zone_areas_%s.dbf" %(resultsdir,sp_code_st)
		#			arcpy.sa.TabulateArea(response_zones,"VALUE",response_zones,"VALUE",outname)
		#			db = dbf.Dbf(outname)
		#			
		#			#find which zones are available for species
		#			zone_eff_index=[]
		#			zone_area=[0, 0, 0]
		#			for z in range(len(db)):
		#				zone_eff_index.append(db[z][0]-1)
		#				zone_area[db[z][0]-1]=db[z][z+1]
		#			del db
		#			zone_area[:]=[x/1000000 for x in zone_area]
		#			
		#			save_temp_csv_data(zone_area, path_eff_zone_area)
		#			save_temp_csv_data(zone_eff_index, path_eff_zone_index)
		#			
		#			metric_previously_done=False
		#			metric_NA=False
		#		else:	
		#			metric_previously_done=True
		#			metric_NA=False
		#			
		#		return metric_previously_done, metric_NA
		#	for i in range(len(CCE_Spp)):
		#		va_metric_wrapper(calc_eff_resp_zone_area_fx, i)
	
		#HABITAT QUALITY (GOOD, BAD)
		if calc_hab_qual:
			def calc_hab_qual_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		
				
				GBU_map_loc=arcpy.Raster(r"%shabqual_simple.tif" %(landscape_factor_dir)) #saved in 2 bit format!
				sp_GBU_map_loc="%sGBU_%s.tif" %(resultsdir, sp_code_st)
				if arcpy.Exists(sp_GBU_map_loc)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)					
					outname=r"%sDBFs/GBU_areas_%s.dbf" %(resultsdir,sp_code_st)
					arcpy.sa.TabulateArea(response_zones,"VALUE",GBU_map_loc,"VALUE",outname)
					#arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", loc_Good_LC, loc_good_habitat_table,"DATA")
					db = dbf.Dbf(outname)
					temp_zone_index=[]
					for z in range(len(db)):
						temp_zone_index.append(zones.index(db[z][0]))	
					field_names=db.fieldNames
			
						
					avail=0
					try:				
						field_names.index('VALUE_2')
						avail=1
					except:
						avail=0
					if avail==1:
						Zone_bad_hab=get_zone_stats(temp_zone_index, db, "VALUE_2")
						Zone_bad_hab[:]=[x/1000000 for x in Zone_bad_hab]
					else:
						Zone_bad_hab=[0]*3
						
					
					avail=0
					try:				
						field_names.index('VALUE_3')
						avail=1
					except:
						avail=0
					if avail==1:
						Zone_good_hab=get_zone_stats(temp_zone_index, db, "VALUE_3")
						Zone_good_hab[:]=[x/1000000 for x in Zone_good_hab]
					else:
						Zone_good_hab=[0]*3
			
					opath=r"%sDBFs/%s_Zone_bad_hab.csv" %(resultsdir, sp_code_st)
					save_temp_csv_data(Zone_bad_hab, opath)
					opath=r"%sDBFs/%s_Zone_good_hab.csv" %(resultsdir, sp_code_st)
					save_temp_csv_data(Zone_good_hab, opath)
			
					GBU_map=GBU_map_loc*(response_zones>0)
					GBU_map.save(sp_GBU_map_loc)
					try:
						del db
						del GBU_map
					except:
						pass			
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_hab_qual_fx, i)
					
		#GOOD HABITAT		
		if calc_good_hab:
			def calc_good_hab_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				hab_info=0
				sub_info=0				
				opath=r"%sDBFs/%s_zone_compatible_habitat.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1: #delete previous version of output file if it exists
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)					
					try:
						Sp_index=hab_sp_code.index(str(sp_code))
						Sp_hab_req=spp_hab_type[Sp_index]
						if len(Sp_hab_req)>0 and Sp_hab_req!='0': #MUST DEBUG!
							Sp_hab_req=eval(Sp_hab_req)
							hab_info=1
						else:
							zone_compatible_habitat=[0, 0, 0]
							
						sp_substrate_type=spp_substrate_type[Sp_index]
						if len(sp_substrate_type)>0 and sp_substrate_type!='0':
							sp_substrate_type=eval(sp_substrate_type)
							sub_info=1
						else:
							zone_bad_substrate=[0, 0, 0]
							
					except ValueError:
						Sp_index='9999'
						zone_compatible_habitat=[0, 0, 0]
						#zone_bad_substrate=[0, 0, 0]
						pass
					if hab_info==1:
						GAP_LC = arcpy.Raster(r"%sgaplandcover/gaplandcov_hi.img" %(landscape_factor_dir))
						temp=str(Sp_hab_req)
						temp=temp.replace("[", "(");
						temp=temp.replace("]", ")")
						clause="VALUE IN %s" %(temp)
						Good_LC = arcpy.sa.ExtractByAttributes(GAP_LC, clause)
						#Good_LC=arcpy.sa.InList(GAP_LC, habitat_type)
						Good_LC=arcpy.sa.SetNull(Good_LC,1,"Value <1")
						loc_Good_LC=r"%sGood_LC_%s.tif" %(resultsdir,sp_code_st)
						Good_LC.save(loc_Good_LC)
						#if use_zonal_stats==1:
						loc_good_habitat_table=r"%sDBFs/good_habitat_%s.dbf" %(resultsdir,sp_code_st)
						#arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", loc_Good_LC, loc_good_habitat_table,"DATA")
						arcpy.sa.TabulateArea(response_zones,"VALUE",loc_Good_LC, "VALUE",loc_good_habitat_table)
						db = dbf.Dbf(loc_good_habitat_table)
						temp_zone_index=[]
						for z in range(len(db)):
							temp_zone_index.append(zones.index(db[z][0]))	
						zone_compatible_habitat=get_zone_stats(temp_zone_index, db, "VALUE_1")
						#else:
						#	pass
						zone_compatible_habitat[:]=[x/1000000 for x in zone_compatible_habitat]
						try:
							del Good_LC
							del db
						except:
							pass
					ofile = open(opath, 'wb')
					writer = csv.writer(ofile, dialect='excel')
					writer.writerow(zone_compatible_habitat)
					ofile.close()
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_good_hab_fx, i)
							
		#FRAGMENTATION
		if calc_fragmentation:
			def calc_fragmentation_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				opath=r"%sDBFs/%s_zone_fragmentation.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)							
					biome_data_avail=1
					try:
						Sp_index=hab_sp_code.index(str(sp_code))
					except:
						biome_index="b000"
						zone_fragmentation=[0, 0, 0]
						zone_core_biome==[0, 0, 0]
						bioreg_max_biome_elev=[0]*18
						#zone_compatible_biome=[0, 0, 0]
						biome_data_avail=0
					
					if biome_data_avail==1:	
						sp_fc=spp_forest_compatibility[Sp_index]
						sp_sc=spp_shrubland_compatibility[Sp_index]
						sp_gc=spp_grassland_compatibility[Sp_index]
						frag_map_loc="%sfragmentation/bin_%s%s%s_edge.tif" %(landscape_factor_dir,sp_fc, sp_sc, sp_gc)
						frag_map=arcpy.Raster(frag_map_loc)
						#compatible_biome_map=frag_map>0
						core_biome_map=frag_map==2
						frag_map=frag_map==1
						
						#CALC EDGE AREA
						path_zone_frag=r"%sDBFs/zone_frag_%s.csv" %(resultsdir,sp_code_st)
						if arcpy.Exists(path_zone_frag)==False or overwrite==1: 
							frag_map=frag_map*response_zones
							frag_map=arcpy.sa.SetNull(frag_map,1,"Value=0")
							loc_fragmentation=r"%sfragmentation_%s.tif" %(resultsdir,sp_code_st)
							frag_map.save(loc_fragmentation)		
							#if use_zonal_stats==1:							
							loc_fragmentation_table=r"%sDBFs/fragmentation_%s.dbf" %(resultsdir,sp_code_st)
							#arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", loc_fragmentation, loc_fragmentation_table,"DATA")
							arcpy.sa.TabulateArea(response_zones,"VALUE",loc_fragmentation, "VALUE",loc_fragmentation_table)
							db = dbf.Dbf(loc_fragmentation_table)
							temp_zone_index=[]
							for z in range(len(db)):
								temp_zone_index.append(zones.index(db[z][0]))	
							zone_fragmentation=get_zone_stats(temp_zone_index, db, "VALUE_1")
							#else:
							#	pass
							zone_fragmentation[:]=[x/1000000 for x in zone_fragmentation]
							try:
								del db
							except:
								pass
							save_temp_csv_data(zone_fragmentation, path_zone_frag)
						else:
							zone_fragmentation=load_temp_csv_float_data(path_zone_frag)
						print "calculated edge area"
						
						#CALC CORE AREA
						path_zone_core=r"%sDBFs/zone_core_%s.csv" %(resultsdir,sp_code_st)
						if arcpy.Exists(path_zone_core)==False or overwrite==1: 
							core_biome_map=core_biome_map*response_zones
							core_biome_map=arcpy.sa.SetNull(core_biome_map,1,"Value=0")
							loc_core_biome=r"%score_biome_%s.tif" %(resultsdir,sp_code_st)
							core_biome_map.save(loc_core_biome)
							#if use_zonal_stats==1:														
							loc_core_biome_table=r"%sDBFs/core_biome_%s.dbf" %(resultsdir,sp_code_st)
							#arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", loc_core_biome, loc_core_biome_table,"DATA")
							arcpy.sa.TabulateArea(response_zones,"VALUE",loc_core_biome, "VALUE",loc_core_biome_table)
							db = dbf.Dbf(loc_core_biome_table)
							temp_zone_index=[]
							for z in range(len(db)):
								temp_zone_index.append(zones.index(db[z][0]))	
							zone_core_biome=get_zone_stats(temp_zone_index, db, "VALUE_1")
							#else:
							#	pass
							
							zone_core_biome[:]=[x/1000000 for x in zone_core_biome]
							try:
								del db
							except:
								pass
							save_temp_csv_data(zone_core_biome, path_zone_core)
						else:
							zone_core_biome=load_temp_csv_float_data(path_zone_core)
						print "calculated core area"
						
						#MAX BIOME ELEVATION
						path_max_biome_elev=r"%sDBFs/max_biome_elev_%s.csv" %(resultsdir,sp_code_st)
						if arcpy.Exists(path_max_biome_elev)==False or overwrite==1: 
							biome_index="b"+sp_fc+sp_sc+sp_gc
							bioreg_max_biome_elev=biome_elev_mat[biome_index]
							bioreg_max_biome_elev[:]=[float(x) for x in bioreg_max_biome_elev]
							save_temp_csv_data(bioreg_max_biome_elev, path_max_biome_elev)
						else:
							bioreg_max_biome_elev=load_temp_csv_float_data(path_max_biome_elev)
							
						#path_max_zone_biome_elev=r"%sDBFs/max_zone_biome_elev_%s.csv" %(resultsdir,sp_code_st)
						#if arcpy.Exists(path_max_zone_biome_elev)==False or overwrite==1: 
						#	zone_compatible_biome=[]
						#	for i in range(len(zone_fragmentation)):
						#		zone_compatible_biome[i]=zone_fragmentation[i]+zone_core_biome[i]
						#	save_temp_csv_data(zone_compatible_biome, path_max_zone_biome_elev)
						#else:
						#	zone_compatible_biome=load_temp_csv_float_data(path_max_zone_biome_elev)
			
						#	compatible_biome_map=compatible_biome_map*response_zones
						#	compatible_biome_map=arcpy.sa.SetNull(compatible_biome_map,1,"Value=0")
						#	loc_compatible_biome=r"%scompatible_biome_%s.tif" %(resultsdir,sp_code_st)
						#	compatible_biome_map.save(loc_compatible_biome)		
						#	loc_compatible_biome_table=r"%sDBFs/compatible_biome_%s.dbf" %(resultsdir,sp_code_st)
						#	arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", loc_compatible_biome, loc_compatible_biome_table,"DATA")
						#	db = dbf.Dbf(loc_compatible_biome_table)
						#	temp_zone_index=[]
						#	for z in range(len(db)):
						#		temp_zone_index.append(zones.index(db[z][0]))	
						#
						#	zone_compatible_biome=get_zone_stats(temp_zone_index, db, "AREA")
						#	zone_compatible_biome[:]=[x/1000000 for x in zone_compatible_biome]
						#	del db
			
					
						jnk=[biome_index, bioreg_max_biome_elev, zone_fragmentation, zone_core_biome]
						#jnk=[biome_index, bioreg_max_biome_elev, zone_fragmentation, zone_core_biome, zone_compatible_biome]
						save_temp_csv_data(jnk, opath)
					#else:
						##jnk=load_temp_csv_float_data(opath)
						#f = open(opath, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
						#reader = csv.reader(f)
						#jnk= reader.next()
						#
						#biome_index= jnk[0]
						##zone_compatible_biome= eval(jnk[1]) 
						#bioreg_max_biome_elev= eval(jnk[1])
						#bioreg_max_biome_elev[:]=[float(x) for x in bioreg_max_biome_elev]
						#zone_fragmentation= eval(jnk[2])
						#zone_core_biome= eval(jnk[3])
						##zone_compatible_biome=eval(jnk[4])
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_fragmentation_fx, i)

		##Distance from top of island metric
		if calc_dist_to_top_of_island:
			def calc_dist_to_top_of_island_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				opath="%sDBFs/%s_prox_to_bioregion_caps.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)							
					try:
						opath1="%sDBFs/min_elev_zone_vals_%s.csv" %(resultsdir,sp_code_st)
						opath2="%sDBFs/max_elev_zone_vals_%s.csv" %(resultsdir,sp_code_st)
						path_max_biome_elev=r"%sDBFs/max_biome_elev_%s.csv" %(resultsdir,sp_code_st)
						bioreg_max_biome_elev=load_temp_csv_float_data(path_max_biome_elev)
						min_elev_zone_vals=load_temp_csv_float_data(opath1)
						max_elev_zone_vals=load_temp_csv_float_data(opath2)						
						max_elev_zone_vals[:]=[float(x) for x in max_elev_zone_vals]
						min_elev_zone_vals[:]=[float(x) for x in min_elev_zone_vals]
						c=numpy.asarray(max_elev_zone_vals)
						a=numpy.asarray(bioreg_max_biome_elev)
						a=a[c>0]
						b=numpy.asarray(min_elev_zone_vals)
						b=b[c>0]
						jnk=a-b
						
						opath22="%sDBFs/FCE_elev_%s.csv" %(resultsdir,sp_code_st)
						jnk11=load_temp_csv_float_data(opath22)
						FCE_mean_elev=jnk11[0]
						
						opath22="%sDBFs/CCE_elev_%s.csv" %(resultsdir,sp_code_st)
						jnk11=load_temp_csv_float_data(opath22)
						CCE_mean_elev=jnk11[0]
						
						elev_shift=float(FCE_mean_elev)-float(CCE_mean_elev)
						jnk2=jnk<elev_shift
						n_bioreg_in_FCE=len(c[c>0])
						n_bioreg_near_top=len(jnk2[jnk2==True])
					except:
						n_bioreg_in_FCE='Error'
						n_bioreg_near_top='Error'						
					jnk=[n_bioreg_in_FCE, n_bioreg_near_top]
					save_temp_csv_data(jnk, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_dist_to_top_of_island_fx, i)
			
		#PROTECTED AREA
		if calc_protected_area:
			def calc_protected_area_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				#Protected_areas_loc="%sreserves_120424.shp" %(landscape_factor_dir)
				Protected_areas_loc="%sreserves_120424_bin.tif" %(landscape_factor_dir)
				opath=r"%sDBFs/%s_protected_area.csv" %(resultsdir, sp_code_st)
				protected_zones_loc="%sprotected_zones_map_%s.tif" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)								
					calc=1
					try:
						jnk=response_zones>0
						protected_zones=arcpy.sa.ExtractByMask (jnk, Protected_areas_loc)
						protected_zones.save(protected_zones_loc)
						print 'prot area map'
					except arcpy.ExecuteError:
						msgs2=arcpy.GetMessages(2)
						arcpy.AddError(msgs2)
						if "ERROR 010092: Invalid output extent" in msgs:
							zone_protected_area=["-", "-", "-"]
							calc=0
							pass
						else:
							print 'error_in_ung_free_calc'
					if calc==1:	
						if use_zonal_stats==1:							
							outname=r"%sDBFs/protected_zone_area_%s.dbf" %(resultsdir,sp_code_st)
							arcpy.sa.TabulateArea(response_zones,"VALUE",protected_zones,"VALUE",outname)
							print 'tabulated prot area'
							db = dbf.Dbf(outname)
							zone_protected_area=[0, 0, 0]
							temp_zone_index=[]
							for z in range(len(db)):
								temp_zone_index.append(zones.index(db[z][0]))	
							#zone_protected_area=get_zone_stats(temp_zone_index, db, "VALUE_1")
							try:
								zone_protected_area=get_zone_stats(temp_zone_index, db, "VALUE_1")
							except:
								a=str(sys.exc_info()[1])
								if a=="list.index(x): x not in list":
									pass
								else:
									error_in_prot_area_calc
			
						else:
							pass
						try:
							del db
						except:
							pass
				
						zone_protected_area[:]=[x/1000000 for x in zone_protected_area]
					save_temp_csv_data(zone_protected_area, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_protected_area_fx, i)
			
		#UNGULATE FREE AREA
		if calc_ung_free_area:
			def calc_ung_free_area_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				#ungfree_areas_loc="%sUngUnits_20120913.shp" %(landscape_factor_dir)
				ungfree_areas_loc="%sUngUnits_20120913_bin.tif" %(landscape_factor_dir)
				opath=r"%sDBFs/%s_Ung_free_areas.csv" %(resultsdir, sp_code_st)
				sp_ungfree_map_loc="%sungfree_map_%s.tif" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)								
					calc=1
					try:
						ungfree_zones=arcpy.sa.ExtractByMask (response_zones>0, ungfree_areas_loc)
						ungfree_zones.save(sp_ungfree_map_loc)
						print 'prot area map'
					except arcpy.ExecuteError:
						msgs2=arcpy.GetMessages(2)
						arcpy.AddError(msgs2)
						if "ERROR 010092: Invalid output extent" in msgs:
							Zones_ungfree=["-", "-", "-"]
							calc=0
							pass
						else:
							error_in_ung_free_calc
					if calc==1:		
						if use_zonal_stats==1:							
							outname=r"%sDBFs/ungfree_zone_area_%s.dbf" %(resultsdir,sp_code_st)
							arcpy.sa.TabulateArea(response_zones,"VALUE",ungfree_zones,"VALUE",outname)
							print 'tabulated prot area'
							db = dbf.Dbf(outname)
							Zones_ungfree=[0, 0, 0]
							temp_zone_index=[]
							for z in range(len(db)):
								temp_zone_index.append(zones.index(db[z][0]))	
							try:
								Zones_ungfree=get_zone_stats(temp_zone_index, db, "VALUE_1")
							except:
								a=str(sys.exc_info()[1])
								if a=="list.index(x): x not in list":
									pass
								else:
									error_in_ung_free_calc
						else:
							pass
						try:
							del db
						except:
							pass
						Zones_ungfree[:]=[x/1000000 for x in Zones_ungfree]
					save_temp_csv_data(Zones_ungfree, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_ung_free_area_fx, i)
				
					
			#	t1 = time.time(); print 'Step 16d done (%i secs): protected area within response zones for species %s' %(int(t1-t0), sp_code_st); t0 = time.time()		
			#	#UNGULATE FREE AREA
			#	sp_ungfree_map_loc="%sungfree_map_%s.tif" %(resultsdir, sp_code_st)
			#	if arcpy.Exists(sp_ungfree_map_loc)==False or overwrite==1:
			#		Ung_free_areas_map_loc=arcpy.Raster(r"%sungfree07" %(landscape_factor_dir))
			#		Ung_free_areas_map_loc=arcpy.sa.SetNull(Ung_free_areas_map_loc,1,"Value <1")
			#		outname=r"%sDBFs/Ung_free_areas_%s.dbf" %(resultsdir,sp_code_st)
			#		arcpy.sa.TabulateArea(response_zones,"VALUE",Ung_free_areas_map_loc,"VALUE",outname)
			#		db = dbf.Dbf(outname)
			#		temp_zone_index=[]
			#		for z in range(len(db)):
			#			temp_zone_index.append(zones.index(db[z][0]))	
			#		Zones_ungfree=get_zone_stats(temp_zone_index, db, "VALUE_1") #MUST LOOK AT TABLE FOR RIGHT ZONE VALUE!
			#		Zones_ungfree[:]=[x/1000000 for x in Zones_ungfree]	
			#		try:
			#			del db
			#		except:
			#			pass
			#		ungfree_map=Ung_free_areas_map_loc*(response_zones>0)
			#		ungfree_map.save(sp_ungfree_map_loc)
			#		
			#		opath=r"%sDBFs/%s_Ung_free_areas.csv" %(resultsdir, sp_code_st)
			#		save_temp_csv_data(Zones_ungfree, opath)
			#	else:
			#		opath=r"%sDBFs/%s_Ung_free_areas.csv" %(resultsdir, sp_code_st)
			#		Zones_ungfree= load_temp_csv_float_data(opath)	
			#
			#	t1 = time.time(); print 'Step 16e done (%i secs): ungulate free area within response zones for species %s' %(int(t1-t0), sp_code_st); t0 = time.time()		
			#	

		#CALC ZONE SLOPE MEAN, STDE
		#CALC SLOPE QUANTILES
		if calc_slope_metrics:
			def calc_slope_metrics_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				opath=r"%sDBFs/%s_Zone_slope_max.csv" %(resultsdir, sp_code_st)
				opath2=r"%sDBFs/%s_Zone_slope_min.csv" %(resultsdir, sp_code_st)
				opath3=r"%sDBFs/%s_Zone_slope_std.csv" %(resultsdir, sp_code_st)
				opath4=r"%sDBFs/%s_Zone_slope_median.csv" %(resultsdir, sp_code_st)
				loc_CCE_slope=r"%sDBFs/slope_%s.dbf" %(resultsdir,sp_code_st)	
				if arcpy.Exists(opath)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)
					
					inRasterloc2 = r"%s%s/DEM/%s_deg_slope.tif" %(landscape_factor_dir,island,island)
					arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", inRasterloc2, loc_CCE_slope,"DATA")	
					db = dbf.Dbf(loc_CCE_slope)
					temp_zone_index=[]

					for z in range(len(db)):
						temp_zone_index.append(zones.index(db[z][0]))		
					Zone_slope_min=get_zone_stats(temp_zone_index, db, "MIN")
					Zone_slope_max=get_zone_stats(temp_zone_index, db, "MAX")
					Zone_slope_std=get_zone_stats(temp_zone_index, db, "STD")
					Zone_slope_median=get_zone_stats(temp_zone_index, db, "MEAN") #was median before??! but no such function in arcgis
					try:
						del db
					except:
						pass
					save_temp_csv_data(Zone_slope_median, opath4)
					save_temp_csv_data(Zone_slope_std, opath3)
					save_temp_csv_data(Zone_slope_min, opath2)
					save_temp_csv_data(Zone_slope_max, opath)
					metric_previously_done=False
					metric_NA=False

				#opath=r"%sDBFs/%s_Zone_slope_max_quant.csv" %(resultsdir, sp_code_st)
				#opath2=r"%sDBFs/%s_Zone_slope_min_quant.csv" %(resultsdir, sp_code_st)
				#opath3=r"%sDBFs/%s_Zone_slope_std.csv" %(resultsdir, sp_code_st)
				#opath4=r"%sDBFs/%s_Zone_slope_median.csv" %(resultsdir, sp_code_st)
			#	if arcpy.Exists(opath)==False or overwrite==1:
			#		try:
			#			inRasterloc2 = r"%s%s/DEM/%s_deg_slope.tif" %(landscape_factor_dir,island,island)	
			#			#inRasterloc3 = r"%s%s/DEM/%s_island_extent.tif" %(landscape_factor_dir,island,island)	
			#			vals=[1, 2, 3]
			#			#vals=[1]
			#			Q_threshold=0.95
			#			Zone_slope_max=[]
			#			Zone_slope_min=[]
			#			Zone_slope_median=[]
			#			Zone_slope_std=[]
			#			for val in vals:
			#			    expr="Value <>%i" %(val)
			#			    Zone_slope=arcpy.sa.SetNull(response_zones,1,expr)*inRasterloc2
			#			    #Zone_slope_filter=arcpy.sa.SetNull(response_zones,1,expr)*inRasterloc3
			#			    myArray = arcpy.RasterToNumPyArray(Zone_slope)
			#			    myArray=myArray[myArray<1000] ##GET RID OF % slope >1000
			#			    myArray=myArray[myArray>-1000]
			#			    #del temp_loc
			#			    if len(myArray)>0:
			#				    slope_median=numpy.median(myArray)
			#				    slope_std=numpy.std(myArray)
			#				    temp_hist=numpy.histogram(myArray,1000)
			#				    temp_cum_dist=temp_hist[0]
			#				    temp_slope_bins=temp_hist[1]
			#				    temp_cum_dist=numpy.cumsum(temp_cum_dist)
			#				    max_temp_cum_dist=temp_cum_dist[len(temp_cum_dist)-1]
			#				    max_temp_cum_dist=max_temp_cum_dist*Q_threshold
			#				    min_temp_cum_dist=max_temp_cum_dist*(1-Q_threshold)
			#				    
			#				    temp_index=temp_cum_dist<max_temp_cum_dist
			#				    temp_max_slope=temp_slope_bins[temp_index]
			#				    try: 
			#					temp_max_slope=max(temp_max_slope)
			#				    except ValueError:
			#					temp_max_slope=0
			#				    
			#				    temp_index=temp_cum_dist<min_temp_cum_dist
			#				    temp_min_slope=temp_slope_bins[temp_index]
			#				    try: 
			#					temp_min_slope=max(temp_min_slope)
			#				    except ValueError:
			#					temp_min_slope=0
			#			    else:
			#				    temp_max_slope=0
			#				    temp_min_slope=0
			#				    
			#			    #temp_max_slope=0
			#			    Zone_slope_max.append(temp_max_slope)
			#			    Zone_slope_min.append(temp_min_slope)
			#			    Zone_slope_median.append(slope_median)
			#			    Zone_slope_std.append(slope_std)
			#			    
			#			save_temp_csv_data(Zone_slope_median, opath4)
			#			save_temp_csv_data(Zone_slope_std, opath3)
			#			save_temp_csv_data(Zone_slope_min, opath2)
			#			save_temp_csv_data(Zone_slope_max, opath)
			#		except:
			#			Zone_slope_median= [0,0,0]
			#			Zone_slope_std= [0,0,0]
			#			Zone_slope_min= [0,0,0]
			#			Zone_slope_max= [0,0,0]
			#	else:
			#		Zone_slope_median= load_temp_csv_float_data(opath4)
			#		Zone_slope_std= load_temp_csv_float_data(opath3)
			#		Zone_slope_min= load_temp_csv_float_data(opath2)
			#		Zone_slope_max= load_temp_csv_float_data(opath)
			#	
			#
			#
			#	t1 = time.time(); print 'Step 17 done (%i secs): calculate slope values within response zones for species %s' %(int(t1-t0), sp_code_st); t0 = time.time()
			#
					
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_slope_metrics_fx, i)
							
		#CALC CCE ASPECT MEAN, STDE [[arcgis does not like this calcualtion crashes often]]
		if calc_zone_aspect_mean:
			def calc_zone_aspect_mean_fx(sp_code_st, resultsdir, sp_code):					
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				Aspect_temp = r"%s%s/DEM/%s_aspect_noflatareas.tif" %(landscape_factor_dir,island,island)		
				opath1=r"%sDBFs/%s_zone_aspect_mean.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath1)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)
					
					if use_zonal_stats==1:
						loc_CCE_aspect=r"%sDBFs/aspect_%s.dbf" %(resultsdir,sp_code_st)
						arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", Aspect_temp, loc_CCE_aspect)
						db = dbf.Dbf(loc_CCE_aspect)
						temp_zone_index=[]
						for z in range(len(db)):
							temp_zone_index.append(zones.index(db[z][0]))			
						zone_aspect_mean=get_zone_stats(temp_zone_index, db, "MEAN")
					else:
						array_index=[1,2,3]
						temp=alt_zonal_stats(response_zones, Aspect_temp, array_index)
						zone_aspect_mean=temp[1]
					try:
						del Aspect_temp
						del db
					except:
						pass
					
					save_temp_csv_data(zone_aspect_mean, opath1)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_zone_aspect_mean_fx, i)
					
		if calc_zone_cos_aspect:
			def calc_zone_cos_aspect_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				Aspect_temp = r"%s%s/DEM/%s_cos_aspect.tif" %(landscape_factor_dir,island,island)
				opath=r"%sDBFs/%s_zone_cos_aspect_std.csv" %(resultsdir, sp_code_st)	
				if arcpy.Exists(opath)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)
					
					if use_zonal_stats==1:
						loc_CCE_aspect=r"%sDBFs/cos_aspect_%s.dbf" %(resultsdir,sp_code_st)
						arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", Aspect_temp, loc_CCE_aspect,"DATA")
						db = dbf.Dbf(loc_CCE_aspect)
						if len(db)==0:
							try:
								del db
							except:
								pass
							os.unlink(loc_CCE_aspect)
							Aspect_temp = r"%s%s/DEM/%s_cos_aspect.tif" %(landscape_factor_dir,island,island)
							arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", Aspect_temp, loc_CCE_aspect)
							db = dbf.Dbf(loc_CCE_aspect)
						temp_zone_index=[]
						for z in range(len(db)):
							temp_zone_index.append(zones.index(db[z][0]))
						zone_aspect_std1=get_zone_stats(temp_zone_index, db, "STD")
					else:
						array_index=[1,2,3]
						temp=alt_zonal_stats(response_zones, Aspect_temp, array_index)
						zone_aspect_std1=temp[2]
					try:
						del Aspect_temp
						del db
					except:
						pass			
					save_temp_csv_data(zone_aspect_std1, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_zone_cos_aspect_fx, i)
				
		if calc_zone_sin_aspect:
			def calc_zone_sin_aspect_fx(sp_code_st, resultsdir, sp_code):					
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				Aspect_temp = r"%s%s/DEM/%s_sin_aspect.tif" %(landscape_factor_dir,island,island)
				opath=r"%sDBFs/%s_zone_sin_aspect_std.csv" %(resultsdir, sp_code_st)	
				if arcpy.Exists(opath)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)
					
					if use_zonal_stats==1:
						loc_CCE_aspect=r"%sDBFs/sin_aspect_%s.dbf" %(resultsdir,sp_code_st)
						arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", Aspect_temp, loc_CCE_aspect,"DATA")
						db = dbf.Dbf(loc_CCE_aspect)
						if len(db)==0:
							try:
								del db
							except:
								pass
							os.unlink(loc_CCE_aspect)
							Aspect_temp = r"%s%s/DEM/%s_sin_aspect.tif" %(landscape_factor_dir,island,island)
							arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", Aspect_temp, loc_CCE_aspect, "DATA")
							db = dbf.Dbf(loc_CCE_aspect)
						temp_zone_index=[]
						for z in range(len(db)):
							temp_zone_index.append(zones.index(db[z][0]))
						zone_aspect_std2=get_zone_stats(temp_zone_index, db, "STD")
					else:
						array_index=[1,2,3]
						temp=alt_zonal_stats(response_zones, Aspect_temp, array_index)
						zone_aspect_std2=temp[2]
						
					save_temp_csv_data(zone_aspect_std2, opath)
					
					try:
						del db
						del Aspect_temp
					except:
						pass
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_zone_sin_aspect_fx, i)
				
		if calc_zone_aspect_std:
			def calc_zone_aspect_std_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				opath1=r"%sDBFs/%s_zone_aspect_std.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath1)==False or overwrite==1:
					opath11=r"%sDBFs/%s_zone_cos_aspect_std.csv" %(resultsdir, sp_code_st)
					opath22=r"%sDBFs/%s_zone_sin_aspect_std.csv" %(resultsdir, sp_code_st)
					zone_aspect_std1= load_temp_csv_float_data(opath11)
					zone_aspect_std2= load_temp_csv_float_data(opath22)
					
					#if use_effective_CE_mask:
					#	path_zone_index=r"%sDBFs/%s_eff_zone_index.csv" %(resultsdir, sp_code_st)
					#else:
					#	path_zone_index=r"%sDBFs/%s_zone_index.csv" %(resultsdir, sp_code_st)
					#
					#f = open(path_zone_index, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
					#reader = csv.reader(f)
					#zone_index= reader.next()
					#zone_index[:]=[int(x) for x in zone_index]
					
					zone_aspect_std=[]
					for jh in range(len(zone_aspect_std2)):
						jnk=(zone_aspect_std2[jh]+zone_aspect_std1[jh])/2
						zone_aspect_std.append(jnk)
					save_temp_csv_data(zone_aspect_std, opath1)
					try:
						del db
						os.unlink(loc_CCE_aspect)
					except:
						pass
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_zone_aspect_std_fx, i)
			
				#calc average precipitation gradient within zones:
		if calc_ppt_gradient:
			def calc_ppt_gradient_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				opath=r"%sDBFs/%s_zone_ppt_gradient.csv" %(resultsdir, sp_code_st)
				ppt_gradient_raster= r"%sannual_ppt_slope_atlas.tif" %(landscape_factor_dir)	
				if arcpy.Exists(opath)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)
					
					if use_zonal_stats==1:
						loc_ppt_gradient=r"%sDBFs/ppt_gradient_%s.dbf" %(resultsdir,sp_code_st)
						arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", ppt_gradient_raster, loc_ppt_gradient,"DATA")
						#arcpy.sa.TabulateArea(response_zones,"VALUE",ppt_gradient_raster,"VALUE",loc_ppt_gradient)
						db = dbf.Dbf(loc_ppt_gradient)
						temp_zone_index=[]
						for z in range(len(db)):
							temp_zone_index.append(zones.index(db[z][0]))
						zone_mean_ppt_gradient=get_zone_stats(temp_zone_index, db, "MEAN")
						#zone_aspect_std=get_zone_stats(zone_index, db, "STD")
					else:
						array_index=[1,2,3]
						temp=alt_zonal_stats(response_zones, ppt_gradient_raster, array_index)
						zone_mean_ppt_gradient=temp[1]
			
					try:
						del ppt_gradient_raster
						del db
					except:
						pass			
					save_temp_csv_data(zone_mean_ppt_gradient, opath)
					t1 = time.time();
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_ppt_gradient_fx, i)
								
		#calc invasive suitability within zones:
		if calc_zone_invasibility:
			def calc_zone_invasibility_fx(sp_code_st, resultsdir, sp_code):
				metric_NA=True
				Sp_index=all_sp_codes.index(sp_code)		

				inv_suitability_raster= r"%sinvasibility_new_proj.tif" %(landscape_factor_dir)
				#inv_suitability_raster= r"%sScale_additive_inv_sp_richness_proj.tif" %(landscape_factor_dir)
				opath=r"%sDBFs/%s_zone_inv_suitability.csv" %(resultsdir, sp_code_st)
				if arcpy.Exists(opath)==False or overwrite==1:
					if use_effective_CE_mask:
						loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
					else:
						loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
					response_zones=arcpy.Raster(loc_response_zone)					

					if use_zonal_stats==1:
						loc_inv_suitability=r"%sDBFs/inv_suitability_%s.dbf" %(resultsdir,sp_code_st)
						arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", inv_suitability_raster, loc_inv_suitability,"DATA")
						#arcpy.sa.TabulateArea(response_zones,"VALUE",inv_suitability_raster,"VALUE",loc_inv_suitability)
						db = dbf.Dbf(loc_inv_suitability)
						temp_zone_index=[]
						for z in range(len(db)):
							temp_zone_index.append(zones.index(db[z][0]))
						zone_mean_inv_suitability=get_zone_stats(temp_zone_index, db, "MEAN")
						#zone_aspect_std=get_zone_stats(zone_index, db, "STD")
					else:
						array_index=[1,2,3]
						temp=alt_zonal_stats(response_zones, inv_suitability_raster, array_index)
						zone_mean_inv_suitability=temp[1]
			
					try:
						del inv_suitability_raster
						del db
					except:
						pass			
					save_temp_csv_data(zone_mean_inv_suitability, opath)
					metric_previously_done=False
					metric_NA=False
				else:	
					metric_previously_done=True
					metric_NA=False
					
				return metric_previously_done, metric_NA
			for i in range(len(CCE_Spp)):
				va_metric_wrapper(calc_zone_invasibility_fx, i)
			
		###must update this to new code structure (all species for each step)		
		###TABULATE CURRENT OCCUPANCY WITHIN ZONES
		###sp_name='Acacia koaia' #must ID species!!
		#if calc_dist_to_top_of_island:
		#	for i in range(len(CCE_Spp)):
		#		t0 = time.time()
		#		jnk=CCE_Spp[i]
		#		jnk.encode('ascii','replace')
		#		inRaster = ce_data_dir + jnk
		#		sp_code_st=inRaster[-8:-4]
		#		resultsdir=resultsdir0+sp_code_st+"/"	
		#		sp_code=str(int(sp_code_st)) #get rid of extra zeros
		#		Sp_index=all_sp_codes.index(sp_code)		
		#
		#		if nf==0:
		#			opath10=r"%sDBFs/%s_zone_CO.csv" %(resultsdir, sp_code_st)
		#			CEP_loc="%s%s_CO_CE_points.shp" %(resultsdir, sp_code_st)
		#			if arcpy.Exists(opath10)==False or overwrite==1:
		#				loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
		#				response_zones=arcpy.Raster(loc_response_zone)											
		#				expr=""" "sp_name" = '%s' """ %(sp_name)##debug- need data #stupid SQL/ python parsing differences
		#				arcpy.SelectLayerByAttribute_management ("CO_lyr", "NEW_SELECTION", expr)
		#				if int(arcpy.GetCount_management("CO_lyr").getOutput(0))>0:
		#					#opath10=r"%sDBFs/%s_zone_CO.csv" %(resultsdir, sp_code_st)
		#					sp_CO_points_loc=resultsdir+sp_code_st+"_sp_CO_points.shp"
		#					if arcpy.Exists(sp_CO_points_loc)==False or overwrite==1:
		#						arcpy.CopyFeatures_management("CO_lyr", sp_CO_points_loc)
		#					total_CO_points=int(arcpy.GetCount_management(sp_CO_points_loc).getOutput(0))
		#					outpoints="%s%s_CO_points_w_zones.shp" %(resultsdir, sp_code_st)
		#					arcpy.sa.ExtractValuesToPoints(sp_CO_points_loc, response_zones,outpoints,"NONE","VALUE_ONLY")
		#					#outpoints_lyr="%s%s_sp_CO_points3.lyr" %(resultsdir, sp_code_st)
		#					arcpy.MakeFeatureLayer_management(outpoints, "sp_CO_points3")
		#					#arcpy.CopyFeatures_management(outpoints, outpoints_lyr)			
		#					tableout=r"%sDBFs/%s_zone_CO_freq_table.dbf" %(resultsdir, sp_code_st)
		#					arcpy.Frequency_analysis(outpoints,tableout, ["RASTERVALU"])
		#					
		#					#save points that occur within CE
		#					clause="RASTERVALU IN (1, 2, 3)"
		#					arcpy.MakeFeatureLayer_management(outpoints, "temp_feature",clause)
		#					arcpy.CopyFeatures_management("temp_feature", CEP_loc)
		#					
		#					#SAVE POINTS THAT FALL OUTSIDE CE FOR VETTING
		#					if int(arcpy.GetCount_management(CEP_loc).getOutput(0))<total_CO_points:
		#						BP_loc="%s%s_CO_points_outside_zones.shp" %(resultsdir, sp_code_st)
		#						clause="RASTERVALU NOT IN (1, 2, 3)"
		#						arcpy.MakeFeatureLayer_management(outpoints, "temp_feature",clause)
		#						arcpy.CopyFeatures_management("temp_feature", BP_loc)
		#					
		#					#TALLY POINTS WITHIN RESPONSE ZONES
		#					total_zone_pts=0
		#					zone_CO=[]
		#					for zone in zones:
		#						expr="RASTERVALU = %i" %(zone)
		#						rows = arcpy.SearchCursor(tableout, expr, "","FREQUENCY") #"RASTERVALU = 2"
		#						row = rows.next()
		#						if type(row)== NoneType:
		#							freq=0
		#						else:
		#							freq=row.getValue("frequency")
		#						total_zone_pts=total_zone_pts+freq
		#						zone_CO.append(freq)
		#					if total_zone_pts>0:
		#						zone_CO[:]=[float(x)/total_zone_pts for x in zone_CO]
		#					jnk=[total_CO_points,total_zone_pts]; jnk.extend(zone_CO)
		#					save_temp_csv_data(jnk, opath10)	
		#	
		#				else:
		#					total_CO_points=0
		#					total_zone_pts=0
		#					zone_CO=[0, 0, 0]
		#					jnk=[total_CO_points,total_zone_pts]; jnk.extend(zone_CO)
		#					save_temp_csv_data(jnk, opath10)
		#			else:
		#				jnk=load_temp_csv_float_data(opath10)	
		#				total_CO_points=jnk[0]
		#				total_zone_pts=jnk[1]
		#				zone_CO=jnk[2:]		
		#					#POINT TABULATIONS
		#					#extraction step:
		#					#Overlay:
		#					#loc_overlay_output="%s%soverlay_pt_tabulation.shp" %(resultsdir, sp_code_st)#MUST MAKE SURE LOC VARS ARE CALLED
		#					#if arcpy.Exists(loc_overlay_output)==False:
		#					#Veg Zone rep
		#					
		#			opath20=r"%sDBFs/%s_veg_zone_CO.csv" %(resultsdir, sp_code_st)
		#			if arcpy.Exists(opath20)==False or overwrite==1:
		#				if total_zone_pts>0:
		#					CEP_loc2="%s%s_tabulate_points_temp1.shp" %(resultsdir, sp_code_st)
		#					arcpy.sa.ExtractValuesToPoints(CEP_loc, veg_zone_layer,CEP_loc2,"NONE","VALUE_ONLY")
		#					tableout2=r"%sveg_zone_CO_freq_table" %(resultsdir)
		#					arcpy.Frequency_analysis(CEP_loc2,tableout2, ["RASTERVALU"])			
		#		
		#					total_veg_zone_pts=0
		#					veg_zone_CO=[]
		#					for zone in veg_zones:
		#						expr="RASTERVALU = %i" %(zone)
		#						rows = arcpy.SearchCursor(tableout2, expr, "","FREQUENCY") #"RASTERVALU = 2"
		#						row = rows.next()
		#						if type(row)== NoneType:
		#							freq=0
		#						else:
		#							freq=row.getValue("frequency")
		#						total_veg_zone_pts=total_veg_zone_pts+freq
		#						veg_zone_CO.append(freq)
		#				else:
		#					veg_zone_CO=[0]*len(veg_zones)
		#				save_temp_csv_data(veg_zone_CO, opath20)
		#				#veg_zone_CO=load_temp_csv_float_data(opath20)
		#	
		#			#Prop lava area
		#			opath=r"%sDBFs/%s_lava_flow_CO.csv" %(resultsdir, sp_code_st)
		#			if arcpy.Exists(opath)==False or overwrite==1:
		#				if total_zone_pts>0:
		#					CEP_loc3="%s%s_tabulate_points_temp2.shp" %(resultsdir, sp_code_st)
		#					if arcpy.Exists(loc_lava_flows):
		#						arcpy.sa.ExtractValuesToPoints(CEP_loc, loc_lava_flows, CEP_loc3,"NONE","VALUE_ONLY")
		#						tableout2=r"%slava_flow_CO_freq_table" %(resultsdir)
		#						arcpy.Frequency_analysis(CEP_loc3,tableout2, ["RASTERVALU"])			
		#									
		#						lava_flow_zone_CO=[]
		#						for zone in zones:
		#							expr="RASTERVALU = %i" %(zone)
		#							rows = arcpy.SearchCursor(tableout2, expr, "","FREQUENCY") #"RASTERVALU = 2"
		#							row = rows.next()
		#							if type(row)== NoneType:
		#								freq=0
		#							else:
		#								freq=row.getValue("frequency")
		#							lava_flow_zone_CO.append(freq)
		#					else:
		#						lava_flow_zone_CO=[0, 0, 0]
		#				else:
		#					lava_flow_zone_CO=[0, 0, 0]
		#				save_temp_csv_data(lava_flow_zone_CO, opath)								
		#			
		#			#Ung free
		#			try:
		#				opath=r"%sDBFs/%s_ung_free_zone_CO.csv" %(resultsdir, sp_code_st)
		#				if arcpy.Exists(opath)==False or overwrite==1:
		#					CEP_loc4="%s%s_tabulate_points_temp3.shp" %(resultsdir, sp_code_st)
		#					if arcpy.Exists(CEP_loc4)==False or overwrite==1:
		#						arcpy.sa.ExtractValuesToPoints(CEP_loc3, sp_ungfree_map_loc,CEP_loc4,"NONE","VALUE_ONLY")
		#			except:
		#				print "no ungfree map"
		#			
		#			#Protected
		#			try:
		#				opath=r"%sDBFs/%s_protected_zone_CO.csv" %(resultsdir, sp_code_st)
		#				if arcpy.Exists(opath)==False or overwrite==1:
		#					CEP_loc5="%s%s_tabulate_points_temp4.shp" %(resultsdir, sp_code_st)
		#					if arcpy.Exists(CEP_loc5)==False or overwrite==1:
		#						arcpy.sa.ExtractValuesToPoints(CEP_loc4, protected_zones_loc,CEP_loc5,"NONE","VALUE_ONLY")
		#			except:
		#				print "no ungfree map"
				#
				#	#Window-based- metrics:
				#	#GBU proportion
				#	#Slope mean
				#	#Slope Std
				#	#Aspect Std
				#	#Frag prop
				#	#SLR prop
				#	
				#
				#
				#t1 = time.time()
				#inRaster=CCE_Spp[i]; print 'It took %i seconds to rrun code for species %s' %(int(t1-t00), sp_code_st)
				#
				#
			##END LOOP
		try:
			arcpy.Delete_management(sp_CO_points_loc)
		except:
			pass

except arcpy.ExecuteError: 
	# Get the tool error messages 
	# 
	msgs = arcpy.GetMessages(2) 
	
	# Return tool error messages for use with a script tool 
	#
	arcpy.AddError(msgs) 
	
	# Print tool error messages for use in Python/PythonWin 
	# 
	print msgs
except:
	# Get the traceback object
	tb = sys.exc_info()[2]
	tbinfo = traceback.format_tb(tb)[0]
	
	# Concatenate information together concerning the error into a message string
	pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
	msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
	
	# Return python error messages for use in script tool or Python Window
	arcpy.AddError(pymsg)
	arcpy.AddError(msgs)
		
	f = open("C:/Users/lfortini/Data/0_model_config_error_msg.txt", "r")
	jnk_msg = f.read() 
	#message = "\n\n"+ jnk_msg+ "\n\n" + "error while calculating " + sp_name + " ("+ sp_code_st + ")\n\n" + str(pymsg) + "\n" + str(msgs)
	message = "\n\n"+ jnk_msg+ "\n\n" + "error while calculating vulnerabilities"+ "\n\n" + str(pymsg) + "\n" + str(msgs)
	print message
	#SEND EMAIL MESSAGE
	if send_email_error_message==1:
		import smtplib
		s = smtplib.SMTP('smtp.gmail.com')
		recipient = "brasilbrasil@gmail.com"
		myGmail = "brasilbrasil2222@gmail.com"
		f = open("C:/Users/lfortini/Data/0_model_config_jnk.txt", "r")
		jnk = f.read() 
		s.ehlo()
		s.starttls()
		s.login(myGmail, jnk)
		s.sendmail(myGmail, recipient, message)
		s.quit()
finally:
    # Check in the 3D Analyst extension so other users can access it
    #
    arcpy.CheckInExtension("Spatial")
	

