#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#python D:\Dropbox\code\arcpyVAtool\core_code\arcpy_spp_code_batch_RD72_no_dbfpy_P1_CEs.py
#if running parallel, must run this from cmd with script above, python must be on system path

#USER INPUT
island="all" #
rootdir=r"Y:/PICCC_analysis/plant_landscape_va_results/allSpp_allIsl_P1_CEs_500/" #location for outputs. ?whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)
#rootdir=r"Y:/PICCC_analysis/plant_landscape_va_results/allSpp_allIsl2/" #location for outputs. ?whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)
landscape_factor_dir=r"Y:/PICCC_data/VA data/landscape/" #whichever is data dir,will have to have subfolders: gaplandcover/ (where gaplandcov_hi is placed)
CAO_data_dir=r"Y:/PICCC_data/VA data/CAO/" #this directory is where the species points are located
highest_slr_impact=2 #max elev of slr impacts (this avoids SLR impact calc for high elev species)
ce_data_dir=r"Y:/PICCC_data/VA data/CEs_500m/" #location of climate envelope files "Y:/PICCC_data/VA data/CEs_500m/"
#ce_data_dir=r"Y:/PICCC_data/VA data/CEs_KB/range maps archipelago/" #location of climate envelope files "Y:/PICCC_data/VA data/CEs_500m/"
use_bio_region_filter=0 #
subset_of_CEs=[0,1084] #[3,60] 1084 leave empty [] for no subset, if subset: [300,400]
import_cce_list=False #option to provide list of species names
use_effective_CE_mask=True #remove non-habitat areas from habitat quality calculations
use_zonal_stats=1 #SIMPLIFY
all_files_in_directory=1 #SIMPLIFY #1 to do batch processing of all files in a directory, 0 if want to specify which species below
reverse_spp_order=False
keep_intermediary_output=0 #enter 1 for debug reasons, will a lot of intermediary analyses outputs for inspection
#send_email_error_message=0
overwrite=0
sp_envelope_gap=0 #REMOVE?? #this will avoid the computationally intensive mapping of the transition zone if value is 0
max_search_dist_for_transition_zone= 5000 #in m #only used if trying to interpolate areas between response zones. This parameter determines the distance
parallel=False #for multiprocessing across species

#what pieces to run?
pre_process_envelopes=False
calculate_veg_type_areas_current=False
calculate_veg_type_areas_BPS=False
calculate_native_habitat_areas_HIGAP=False
calculate_all_habitat_areas_HIGAP=False
calculate_native_habitat_areas_LANDFIRE=False
calculate_all_habitat_areas_LANDFIRE=False
calculate_native_habitat_areas_BPS_LANDFIRE=False
calculate_change_in_n_available_habitat=False
calc_cce_total_area=False
calc_fce_total_area=False
calc_cce_fce_dif=False
map_tol_zone=False
map_mrf_zone=False
map_mig_zone_pt1=False
calc_dist_fce_to_CCE=False
calc_mean_elev_cce=False
calc_mean_elev_fce=False #still crashing
count_cce_bioreg=False
count_cce_bioreg_transition_areas=False
calc_cce_precip_interannual_var=False
##
create_rep_zones=False
calc_resp_zone_area=False
calc_zone_slr_area=False
calc_zone_lava_flow_area=False
calc_zone_hab_qual=False #this is breaking randomly
calc_eff_hab_qual_nonpioneer=False
calc_eff_hab_qual_pioneer=False
chose_eff_hab_qual=False
#create_eff_resp_zones=True
#calc_eff_resp_zone_area=True #debug: why dying after species 549?
calc_hab_qual=False
calc_fragmentation=False
calc_dist_to_top_of_island=False
calc_protected_area=False
calc_ung_free_area=False
calc_slope_metrics=False
##calc_zone_aspect_mean=True
##calc_zone_cos_aspect=True
##calc_zone_sin_aspect=True
##calc_zone_aspect_std=True
calc_zone_topo_complexity=False
calc_ppt_gradient=False
calc_zone_invasibility=False

#START UNDERHOOD
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
#from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/
import fnmatch
from arcpy import env
from random import randrange
import itertools
import multiprocessing
from multiprocessing import Pool, freeze_support

arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
arcpy.env.compression = "LZW"
#jnk=randrange(10000)
#arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
#arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"

if not os.path.exists(resultsdir0):
    os.makedirs(resultsdir0)
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

def zonal_area_from_dbf2(outname, temp_zones,multFactor=(1.0/1000000)):
    outputVec=[0]*len(temp_zones) #create empty results vector
    rows = arcpy.SearchCursor(outname)
    fields = arcpy.ListFields(outname)
    for row in rows:
        for field in fields:
            name = field.name
            if name[:6]=="VALUE_":
                calcVal=int(name[6:])
                if calcVal in temp_zones:
                    ind=temp_zones.index(calcVal)
                    outputVec[ind]=float(row.getValue(name))*multFactor
                    #outputVec[ind]= [x*multFactor for x in row.getValue(name)]
    return outputVec

#matrix!
def zonal_area_from_dbf_matrix2(outname, temp_zones,multFactor=(1.0/1000000)):
    outputVec=[0]*len(temp_zones) #create empty results vector
    rows = arcpy.SearchCursor(outname)
    fields = arcpy.ListFields(outname)
    for row in rows:
        for field in fields:
            name = field.name
            if name[:6]=="VALUE_":
                calcVal=int(name[6:])
                if calcVal in temp_zones:
                    if row.getValue("VALUE")==calcVal:
                        ind=temp_zones.index(calcVal)
                        outputVec[ind]=float(row.getValue(name))*multFactor
                        #print field.name
                        #print row.getValue(name)
    return outputVec

#by_column_name
def zonal_area_from_dbf_byCol(outname, temp_zones,col_name,multFactor=(1.0/1000000), default_val=0):
    outputVec=[default_val]*len(temp_zones) #create empty results vector
    rows = arcpy.SearchCursor(outname)
    fields = arcpy.ListFields(outname)
    for field in fields:
        name = field.name
        #print name
        if name==col_name:
            for row in rows:
                jnk=row.getValue("VALUE")
                ind=temp_zones.index(jnk)
                outputVec[ind]=float(row.getValue(name))*multFactor
                #print field.name
                #print row.getValue(name)
    return outputVec

def va_metric_wrapper(VA_func, i):
    if arcpy.CheckExtension("Spatial") == "Available": #must check out license within worker process, as license does not seem to be inherited by parallel workers
        arcpy.CheckOutExtension("Spatial")
    t0 = time.time()
    print('worker', os.getpid(), ' running and doing ', i)
    jnk=randrange(100000)
    tmp_dir="D:/temp/arcgis/"+str(jnk)+"/"
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    arcpy.env.scratchWorkspace = tmp_dir
    arcpy.env.workspace= tmp_dir

    #Get species name, sp code, check if species already have been done
    jnk=CCE_Spp[i]
    jnk.encode('ascii','replace')
    inRaster = ce_data_dir + jnk
    sp_code_st=inRaster[-8:-4]
    resultsdir=resultsdir0+sp_code_st+"/"
    sp_code=str(int(sp_code_st)) #get rid of extra zeros

    jnk=VA_func(sp_code_st, resultsdir, sp_code)
    arcpy.CheckInExtension("Spatial") # Check in the 3D Analyst extension so other users can access it

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

def pre_parallel_wrapper(zipped_args):
    return va_metric_wrapper(*zipped_args)

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
    #csvname="%sbiome_max_elev_by_bioregion_values.csv" %(landscape_factor_dir)
    csvname="%sbiome_max_elev_by_bioregion_values_v2.csv" %(landscape_factor_dir)
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

    bioreg_elev_mat_headers=headers
    bioreg_elev_mat=column

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
        arcpy.env.workspace = datadir
        if all_files_in_directory==1:
            import glob
            jnk=glob.glob(datadir+"CCE*.tif")
            CCE_Spp=[os.path.basename(x) for x in jnk]
            jnk=glob.glob(datadir+"FCE*.tif")
            FCE_Spp=[os.path.basename(x) for x in jnk]

            #FCE_Spp = arcpy.ListRasters("FCE*", "tif")
            #CCE_Spp = arcpy.ListRasters("CCE*", "tif")
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

    #load current landfire map
    veg_types_layer_current="%slandfire_reclassed_125m_UTM_NAD83.tif" %(landscape_factor_dir) #HI_110BPS.tif
    #veg_types_layer_current="%slandfire_reclass_wetland_coastal_UTM_8b.tif" %(landscape_factor_dir) #HI_110BPS.tif
    #veg_types_layer_current="%sHI_110BPS.tif" %(landscape_factor_dir) #HI_110BPS.tif
    veg_types_layer_current=arcpy.Raster(veg_types_layer_current)
    arcpy.BuildRasterAttributeTable_management(veg_types_layer_current, "NONE")
    arcpy.CalculateStatistics_management(veg_types_layer_current, "", "", "", "SKIP_EXISTING")

    #load BPS landfire map
    veg_types_layer_BPS="%slandfire_BPS_reclassed_125m_UTM_NAD83.tif" %(landscape_factor_dir) #HI_110BPS.tif
    veg_types_layer_BPS=arcpy.Raster(veg_types_layer_BPS)
    arcpy.BuildRasterAttributeTable_management(veg_types_layer_BPS, "NONE")
    arcpy.CalculateStatistics_management(veg_types_layer_BPS, "", "", "", "SKIP_EXISTING")

    #LOAD SIMPLIFIED VEGETATION MAPS
    #These are maps that cover is simplified into broad categories of habitat:
    #forest, Shrubland, grassland, bog, cliff, coastal, wetland, other
    #each map (except BPS) has a version only including native areas, or including all native/alien areas
    #so the metrics generated can be chosen depending if a species can inhabit alien habitat.

    #current native habitat (HIGAP)
    HIGAP_revised_simple_native_veg="%srevisedHIGAP/HIGAP_revised_simple_native_veg.tif" %(landscape_factor_dir) #HI_110BPS.tif
    HIGAP_revised_simple_native_veg=arcpy.Raster(HIGAP_revised_simple_native_veg)
    arcpy.BuildRasterAttributeTable_management(HIGAP_revised_simple_native_veg, "NONE")
    arcpy.CalculateStatistics_management(HIGAP_revised_simple_native_veg, "", "", "", "SKIP_EXISTING")

    #current total habitat (HIGAP)
    HIGAP_revised_simple_native_and_alien_veg="%srevisedHIGAP/HIGAP_revised_simple_native_and_alien_veg.tif" %(landscape_factor_dir) #HI_110BPS.tif
    HIGAP_revised_simple_native_and_alien_veg=arcpy.Raster(HIGAP_revised_simple_native_and_alien_veg)
    arcpy.BuildRasterAttributeTable_management(HIGAP_revised_simple_native_and_alien_veg, "NONE")
    arcpy.CalculateStatistics_management(HIGAP_revised_simple_native_and_alien_veg, "", "", "", "SKIP_EXISTING")

    #current native habitat (LANDFIRE)
    landfire_veg_cover_500m_simple_native_veg="%srevisedHIGAP/landfire_veg_cover_500m_simple_native_veg.tif" %(landscape_factor_dir) #HI_110BPS.tif
    landfire_veg_cover_500m_simple_native_veg=arcpy.Raster(landfire_veg_cover_500m_simple_native_veg)
    arcpy.BuildRasterAttributeTable_management(landfire_veg_cover_500m_simple_native_veg, "NONE")
    arcpy.CalculateStatistics_management(landfire_veg_cover_500m_simple_native_veg, "", "", "", "SKIP_EXISTING")

    #current total habitat (LANDFIRE)
    landfire_veg_cover_500m_simple_native_and_alien_veg="%srevisedHIGAP/landfire_veg_cover_500m_simple_native_and_alien_veg.tif" %(landscape_factor_dir) #HI_110BPS.tif
    landfire_veg_cover_500m_simple_native_and_alien_veg=arcpy.Raster(landfire_veg_cover_500m_simple_native_and_alien_veg)
    arcpy.BuildRasterAttributeTable_management(landfire_veg_cover_500m_simple_native_and_alien_veg, "NONE")
    arcpy.CalculateStatistics_management(landfire_veg_cover_500m_simple_native_and_alien_veg, "", "", "", "SKIP_EXISTING")

    #original native habitat (LANDFIRE BPS)
    HI_110BPS_simple_native_veg="%srevisedHIGAP/HI_110BPS_simple_native_veg.tif" %(landscape_factor_dir) #HI_110BPS.tif
    HI_110BPS_simple_native_veg=arcpy.Raster(HI_110BPS_simple_native_veg)
    arcpy.BuildRasterAttributeTable_management(HI_110BPS_simple_native_veg, "NONE")
    arcpy.CalculateStatistics_management(HI_110BPS_simple_native_veg, "", "", "", "SKIP_EXISTING")


    #CO_data=r"%scorrected_CO_data2_merged_and_filtered.shp" %(CAO_data_dir) #corrected_CO_dataXY
    CO_data=r"%scorrected_CO_data4_merged_and_filtered.shp" %(CAO_data_dir) #corrected_CO_dataXY

    arcpy.MakeFeatureLayer_management(CO_data, "CO_lyr")

    Bioregions_loc="%sbioregions.shp" %(landscape_factor_dir)
    #arcpy.CopyFeatures_management(Bioregions_loc, "bioregions")
    arcpy.MakeFeatureLayer_management(Bioregions_loc, "bioregions_lyr")


    ###CREATE FUTURE AND BASELINE CLIMATE ENVELOPES
    if pre_process_envelopes:
        i=0 #for debug
        def pre_process_env_fx2(sp_code_st, resultsdir, sp_code): #also uses use_bio_region_filter, CO_lyr, island, landscape_factor_dir
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
                        if get_num_attributes(inRaster, "MINIMUM")==1 and get_num_attributes(inRaster, "MAXIMUM")==1:
                            CCE_full=inRaster
                        else:
                            CCE_full=arcpy.sa.SetNull(inRaster,1,"Value <1")
                        loc_simple_CCE=r"%ssimplified_CCE_%s.tif" %(resultsdir,sp_code_st)
                        #CCE_full.save(loc_simple_CCE)
                        arcpy.CopyRaster_management(CCE_full, loc_simple_CCE, "", "0", "0", "", "", "2_BIT", "", "")

                        inRaster = ce_data_dir + FCE_Spp[i]
                        inRaster=arcpy.Raster(inRaster)
                        if inRaster.maximum!=None:
                            if get_num_attributes(inRaster, "MINIMUM")==1 and get_num_attributes(inRaster, "MAXIMUM")==1:
                                FCE_full=inRaster
                            else:
                                FCE_full=arcpy.sa.SetNull(inRaster,1,"Value <1")
                        else:
                            FCE_full=inRaster
                        #FCE_full=arcpy.sa.SetNull(inRaster,1,"Value <1")
                        loc_simple_FCE=r"%ssimplified_FCE_%s.tif" %(resultsdir,sp_code_st)
                        #FCE_full.save(loc_simple_FCE)
                        arcpy.CopyRaster_management(FCE_full, loc_simple_FCE, "", "0", "0", "", "", "2_BIT", "", "")

                    else:
                        inRaster = ce_data_dir + CCE_Spp[i]
                        inRaster=arcpy.Raster(inRaster)
                        CCE_full= inRaster*island_mask
                        if (get_num_attributes(inRaster, "MINIMUM")==1 and get_num_attributes(inRaster, "MAXIMUM")==1)==False:
                            CCE_full=arcpy.sa.SetNull(CCE_full,1,"Value <1")
                        loc_simple_CCE=r"%ssimplified_CCE_%s.tif" %(resultsdir,sp_code_st)
                        if arcpy.Exists(loc_simple_CCE)==False or overwrite==1:
                            #CCE_full.save(loc_simple_CCE)
                            arcpy.CopyRaster_management(CCE_full, loc_simple_CCE, "", "0", "0", "", "", "2_BIT", "", "")

                        inRaster = ce_data_dir +FCE_Spp[i]
                        inRaster=arcpy.Raster(inRaster)
                        island_mask="%s%s/DEM/%s_extent.tif" %(landscape_factor_dir, island, island)
                        island_mask=arcpy.Raster(island_mask)
                        FCE_full= inRaster*island_mask
                        if (get_num_attributes(inRaster, "MINIMUM")==1 and get_num_attributes(inRaster, "MAXIMUM")==1)==False:
                            FCE_full=arcpy.sa.SetNull(FCE_full,1,"Value <1")
                        loc_simple_FCE=r"%ssimplified_FCE_%s.tif" %(resultsdir,sp_code_st)
                        if arcpy.Exists(loc_simple_FCE)==False or overwrite==1:
                            #FCE_full.save(loc_simple_FCE)
                            arcpy.CopyRaster_management(FCE_full, loc_simple_FCE, "", "0", "0", "", "", "2_BIT", "", "")

                    #DEFINE THE ENVELOPE BIOREGIONS (USE THOSE FOR METRICS, BUT DISPLAY BOTH FULL AND OCCUPIED ENVELOPE)
                    #IF NO POINTS, ASSUME ENTIRE ENVELOPE
                    expr=""" "sp_name" = '%s' """ %(sp_name)##debug- need data #stupid SQL/ python parsing differences
                    arcpy.SelectLayerByAttribute_management ("CO_lyr", "NEW_SELECTION", expr)
                    sp_CO_points_loc=resultsdir+sp_code_st+"_sp_CO_points.shp"
                    arcpy.CopyFeatures_management("CO_lyr", sp_CO_points_loc)
                    if int(arcpy.GetCount_management(sp_CO_points_loc).getOutput(0))>0 and use_bio_region_filter==1:
                        arcpy.SelectLayerByLocation_management("bioregions_lyr", 'contains', sp_CO_points_loc)

                        #Cut FCE and CCE by bioregion
                        arcpy.Clip_management(CCE_full, "#", loc_COR_CCE,"bioregions_lyr", "0", "ClippingGeometry")
                        CCE_temp=arcpy.Raster(loc_COR_CCE)

                        arcpy.Clip_management(FCE_full, "#", loc_COR_FCE,"bioregions_lyr", "0", "ClippingGeometry")
                        FCE_temp=arcpy.Raster(loc_COR_FCE)

                    else:
                        CCE_temp=CCE_full
                        FCE_temp=FCE_full
                        arcpy.CopyRaster_management(CCE_temp, loc_COR_CCE, "", "0", "0", "", "", "2_BIT", "", "")
                        arcpy.CopyRaster_management(FCE_temp, loc_COR_FCE, "", "0", "0", "", "", "2_BIT", "", "")
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

                return metric_previously_done, metric_NA

        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(pre_process_env_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(pre_process_env_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10) #give it some time before trying to terminate pool to avoid ' access is denied'  error
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    #calculate veg type areas
    if calculate_veg_type_areas_current:
        def calculate_veg_type_areas_current_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
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
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",veg_types_layer_current,"VALUE",outname)
                    temp_zones=range(0,15)
                    veg_area=zonal_area_from_dbf2(outname, temp_zones)

                    save_temp_csv_data(veg_area, opath)
                    del CCE_temp; del inRaster; del outname; del veg_area; del opath;
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_veg_type_areas_current_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_veg_type_areas_current_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if calculate_veg_type_areas_BPS:
        def calculate_veg_type_areas_BPS_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                #CALC area in each habitat type
                opath="%sDBFs/vegtype_areas_BPS%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    inRaster = CCE_temp
                    outname=r"%sDBFs/vegtype_areas%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",veg_types_layer_BPS,"VALUE",outname)
                    temp_zones=range(0,15)
                    veg_area=zonal_area_from_dbf2(outname, temp_zones)

                    save_temp_csv_data(veg_area, opath)
                    del CCE_temp; del inRaster; del outname; del veg_area; del opath;
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_veg_type_areas_BPS_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_veg_type_areas_BPS_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if calculate_native_habitat_areas_HIGAP:
        def calculate_native_habitat_areas_HIGAP_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                #CALC area in each habitat type
                opath="%sDBFs/native_habitat_areas_HIGAP%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    inRaster = CCE_temp
                    outname=r"%sDBFs/native_habitat_areas_HIGAP%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",HIGAP_revised_simple_native_veg,"VALUE",outname)
                    temp_zones= range(1,8) #only classes 1-7, excluding 10 (other/ non vegetated)
                    veg_area=zonal_area_from_dbf2(outname, temp_zones)

                    save_temp_csv_data(veg_area, opath)
                    del CCE_temp; del inRaster; del outname; del veg_area; del opath;
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_native_habitat_areas_HIGAP_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_native_habitat_areas_HIGAP_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if calculate_all_habitat_areas_HIGAP:
        def calculate_all_habitat_areas_HIGAP_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                #CALC area in each habitat type
                opath="%sDBFs/all_habitat_areas_HIGAP%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    inRaster = CCE_temp
                    outname=r"%sDBFs/all_habitat_areas_HIGAP%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",HIGAP_revised_simple_native_and_alien_veg,"VALUE",outname)
                    temp_zones=range(1,8) #only classes 1-7, excluding 10 (other/ non vegetated)
                    veg_area=zonal_area_from_dbf2(outname, temp_zones)

                    save_temp_csv_data(veg_area, opath)
                    del CCE_temp; del inRaster; del outname; del veg_area; del opath;
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_all_habitat_areas_HIGAP_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_all_habitat_areas_HIGAP_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if calculate_native_habitat_areas_LANDFIRE:
        def calculate_native_habitat_areas_LANDFIRE_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                #CALC area in each habitat type
                opath="%sDBFs/native_habitat_areas_LANDFIRE%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    inRaster = CCE_temp
                    outname=r"%sDBFs/native_habitat_areas_LANDFIRE%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",landfire_veg_cover_500m_simple_native_veg,"VALUE",outname)
                    temp_zones=range(1,8) #only classes 1-7, excluding 10 (other/ non vegetated)
                    veg_area=zonal_area_from_dbf2(outname, temp_zones)

                    save_temp_csv_data(veg_area, opath)
                    del CCE_temp; del inRaster; del outname; del veg_area; del opath;
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_native_habitat_areas_LANDFIRE_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_native_habitat_areas_LANDFIRE_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if calculate_all_habitat_areas_LANDFIRE:
        def calculate_all_habitat_areas_LANDFIRE_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                #CALC area in each habitat type
                opath="%sDBFs/all_habitat_areas_LANDFIRE%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    inRaster = CCE_temp
                    outname=r"%sDBFs/all_habitat_areas_LANDFIRE%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",landfire_veg_cover_500m_simple_native_and_alien_veg,"VALUE",outname)
                    temp_zones=range(1,8) #only classes 1-7, excluding 10 (other/ non vegetated)
                    veg_area=zonal_area_from_dbf2(outname, temp_zones)

                    save_temp_csv_data(veg_area, opath)
                    del CCE_temp; del inRaster; del outname; del veg_area; del opath;
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_all_habitat_areas_LANDFIRE_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_all_habitat_areas_LANDFIRE_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if calculate_native_habitat_areas_BPS_LANDFIRE:
        def calculate_native_habitat_areas_BPS_LANDFIRE_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                #CALC area in each habitat type
                opath="%sDBFs/native_habitat_areas_BPS_LANDFIRE%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    inRaster = CCE_temp
                    outname=r"%sDBFs/native_habitat_areas_BPS_LANDFIRE%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",HI_110BPS_simple_native_veg,"VALUE",outname)
                    temp_zones=range(1,8) #only classes 1-7, excluding 10 (other/ non vegetated)
                    veg_area=zonal_area_from_dbf2(outname, temp_zones)

                    save_temp_csv_data(veg_area, opath)
                    del CCE_temp; del inRaster; del outname; del veg_area; del opath;
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_native_habitat_areas_BPS_LANDFIRE_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_native_habitat_areas_BPS_LANDFIRE_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if calculate_change_in_n_available_habitat:
        def calculate_change_in_n_available_habitat_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                opath0="%sDBFs/change_in_n_available_habitat%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath0)==False:
                    opath1="%sDBFs/native_habitat_areas_BPS_LANDFIRE%s.csv" %(resultsdir,sp_code_st)
                    jnk=load_temp_csv_float_data(opath1)
                    n_habitats_BPS=sum([x>0 for x in jnk])

                    opath2="%sDBFs/all_habitat_areas_LANDFIRE%s.csv" %(resultsdir,sp_code_st)
                    jnk=load_temp_csv_float_data(opath2)
                    n_habitats_landfire_all=sum([x>0 for x in jnk])

                    opath3="%sDBFs/native_habitat_areas_LANDFIRE%s.csv" %(resultsdir,sp_code_st)
                    jnk=load_temp_csv_float_data(opath3)
                    n_habitats_landfire_native=sum([x>0 for x in jnk])

                    opath4="%sDBFs/all_habitat_areas_HIGAP%s.csv" %(resultsdir,sp_code_st)
                    jnk=load_temp_csv_float_data(opath4)
                    n_habitats_HIGAP_all=sum([x>0 for x in jnk])

                    opath5="%sDBFs/native_habitat_areas_HIGAP%s.csv" %(resultsdir,sp_code_st)
                    jnk=load_temp_csv_float_data(opath5)
                    n_habitats_HIGAP_native=sum([x>0 for x in jnk])

                    n_habitats=[n_habitats_BPS, n_habitats_landfire_native, n_habitats_landfire_all, n_habitats_HIGAP_native, n_habitats_HIGAP_all]
                    save_temp_csv_data(n_habitats, opath0)
                    del opath1; del opath2; del opath3; del opath4; del opath5;
                    del n_habitats_BPS; del n_habitats_landfire_all; del n_habitats_landfire_native
                    del n_habitats_HIGAP_all; del n_habitats_HIGAP_native;

                    #calc_area_dif(resultsdir,sp_code_st)

                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_change_in_n_available_habitat_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_change_in_n_available_habitat_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()



    if calc_cce_total_area:
        def calc_cce_total_area_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            #Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                opath="%sDBFs/calc_area_CCE%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    inRaster = CCE_temp
                    outname=r"%sDBFs/calc_area_CCE%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",CCE_temp,"VALUE",outname)

                    temp_zones=range(1,2)
                    jnk=zonal_area_from_dbf2(outname, temp_zones)

                    #del db
                    save_temp_csv_data(jnk, opath)
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA

        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_cce_total_area_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_cce_total_area_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    #CALC FCE TOTAL AREA
    if calc_fce_total_area:
        def calc_fce_total_area_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            #t0 = time.time()
            #jnk=CCE_Spp[i]
            #jnk.encode('ascii','replace')
            #inRaster = ce_data_dir + jnk
            #sp_code_st=inRaster[-8:-4]
            #resultsdir=resultsdir0+sp_code_st+"/"
            #sp_code=str(int(sp_code_st)) #get rid of extra zeros
            #Sp_index=all_sp_codes.index(sp_code)
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
                        temp_zones=range(1,2)
                        jnk=zonal_area_from_dbf2(outname, temp_zones)
                    else:
                        jnk=[0]
                    #jnk=[area_FCE]
                    save_temp_csv_data(jnk, opath)

                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_fce_total_area_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_fce_total_area_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    ##CALC CCE-FCE
    if calc_cce_fce_dif:
        def calc_cce_fce_dif_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                opath0="%sDBFs/area_diff%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath0)==False:
                    opath1="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
                    jnk=load_temp_csv_float_data(opath1)
                    area_FCE=jnk[0]

                    opath2="%sDBFs/calc_area_CCE%s.csv" %(resultsdir,sp_code_st)
                    jnk=load_temp_csv_float_data(opath2)
                    area_CCE=jnk[0]

                    area_dif=[area_CCE-area_FCE]
                    save_temp_csv_data(area_dif, opath0)
                    del opath1; del opath2; del area_dif; del area_FCE; del area_CCE
                    #calc_area_dif(resultsdir,sp_code_st)

                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_cce_fce_dif_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_cce_fce_dif_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    ##MAP- TOLERATE ZONE- COMMON AREA BETWEEN CCE AND FCE
    if map_tol_zone:
        def map_tol_zone_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
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
                    #Tolerate_zone.save(loc_intersect)
                    arcpy.CopyRaster_management(Tolerate_zone, loc_intersect, "", "0", "0", "", "", "2_BIT", "", "")

                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(map_tol_zone_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(map_tol_zone_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()


    ##CALCULATE MICRO-REFUGIA ZONE AREA
    if map_mrf_zone:
        def map_mrf_zone_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                CCE_temp=arcpy.Raster(loc_COR_CCE)
                loc_intersect=r"%sintersect_%s.tif" %(resultsdir,sp_code_st)
                Tolerate_zone=arcpy.Raster(loc_intersect)
                loc_MRFzn=r"%sMRFzn_%s.tif" %(resultsdir,sp_code_st)
                if arcpy.Exists(loc_MRFzn)==False or overwrite==1: ##renamed refuge to MRFzn across file
                    opath="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
                    jnk=load_temp_csv_float_data(opath)
                    area_FCE=jnk[0]
                    if area_FCE!=0:
                        Non_overlap_temp = arcpy.sa.IsNull(Tolerate_zone)
                        Microrefugia_zone=CCE_temp*Non_overlap_temp
                        Microrefugia_zone=arcpy.sa.SetNull(Microrefugia_zone,1,"Value <1")
                    else:
                        Microrefugia_zone=CCE_temp
                    #Microrefugia_zone.save(loc_MRFzn)
                    arcpy.CopyRaster_management(Microrefugia_zone, loc_MRFzn, "", "0", "0", "", "", "2_BIT", "", "")

                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(map_mrf_zone_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(map_mrf_zone_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    ##MAP MIGRATE ZONE PART 1
    if map_mig_zone_pt1:
        def map_mig_zone_pt1_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
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
                    #Migrate_temp.save(loc_Migrate)
                    arcpy.CopyRaster_management(Migrate_temp, loc_Migrate, "", "0", "0", "", "", "2_BIT", "", "")

                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(map_mig_zone_pt1_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(map_mig_zone_pt1_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    ##CALCULATE DISTANCE OF FCE FROM SOURCE CCE AREAS
    ##CALCULATE EUCLIDIAN DISTANCE OF ALL CELLS TO NEAREST CCE/CAO
    if calc_dist_fce_to_CCE:
        def calc_dist_fce_to_CCE_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
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
                        #inRaster = FCE_temp #CCE_Spp[i]
                        FCE_dist_temp = arcpy.sa.EucDistance(FCE_temp)
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
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_dist_fce_to_CCE_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_dist_fce_to_CCE_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    ##CALCULATE MEAN ELEVATION OF CCE
    if calc_mean_elev_cce:
        def calc_mean_elev_cce_fx2(sp_code_st, resultsdir, sp_code): #landscape_factor_dir,island
            metric_NA=True
            inRasterloc2 = r"%sHI_dem.tif" %(landscape_factor_dir)
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
                #       jnk=load_temp_csv_float_data(opath)
                #       CCE_mean_elev=jnk[0]
                #       CCE_min_elev=jnk[1]
                #       CCE_max_elev=jnk[2]
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_mean_elev_cce_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_mean_elev_cce_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    ##CALCULATE MEAN ELEVATION OF FCE
    if calc_mean_elev_fce:
        def calc_mean_elev_fce_fx2(sp_code_st, resultsdir, sp_code): #landscape_factor_dir
            metric_NA=True
            bioregion_loc="%sbioregions.tif" %(landscape_factor_dir)
            bioregions=arcpy.Raster(bioregion_loc)
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_FCE=r"%sCOR_FCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_FCE):
                opath_areaFCE="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
                jnk=load_temp_csv_float_data(opath_areaFCE)
                area_FCE=jnk[0]

                opath="%sDBFs/FCE_elev_%s.csv" %(resultsdir,sp_code_st)
                opath1="%sDBFs/min_elev_zone_vals_%s.csv" %(resultsdir,sp_code_st)
                opath2="%sDBFs/max_elev_zone_vals_%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath2)==False or overwrite==1:
                    metric_previously_done=False
                    metric_NA=False
                    if area_FCE!=0:
                        inRasterloc2 = r"%sHI_dem.tif" %(landscape_factor_dir)
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
                            print "done calculating FCE mean elev"

                        if arcpy.Exists(opath2)==False or overwrite==1:
                            loc_min_elev_FCE_table=r"%sDBFs/min_elev_FCE_%s.dbf" %(resultsdir,sp_code_st)
                            arcpy.env.scratchWorkspace = landscape_factor_dir #os.path.dirname(loc_min_elev_FCE_table)#resultsdir
                            arcpy.env.workspace= landscape_factor_dir #os.path.dirname(loc_min_elev_FCE_table)#resultsdir
                            arcpy.sa.ZonalStatisticsAsTable(bioregions,"VALUE", FCE_DEM_temp, loc_min_elev_FCE_table)
                            print "done calculating FCE elev by bioreg"

                            tmp_zn=range(0,18)
                            stat='MIN'
                            #min_elev_zone_vals=read_dbf_stat_vals(loc_min_elev_FCE_table, stat, tmp_zn) #
                            min_elev_zone_vals=zonal_area_from_dbf_byCol(loc_min_elev_FCE_table, tmp_zn, stat, multFactor=1)
                            print "done extracting FCE min elev by bioreg"
                            stat='MAX'
                            #max_elev_zone_vals=read_dbf_stat_vals(loc_min_elev_FCE_table, stat, tmp_zn)
                            max_elev_zone_vals=zonal_area_from_dbf_byCol(loc_min_elev_FCE_table, tmp_zn, stat, multFactor=1)
                            print "done extracting FCE max elev by bioreg"

                            if kio==0:
                                try:
                                    #del db
                                    arcpy.Delete_management(FCE_DEM_temp)
                                except:
                                    pass
                            print "saving min and max bioreg FCE elev"
                            save_temp_csv_data(min_elev_zone_vals, opath1)
                            save_temp_csv_data(max_elev_zone_vals, opath2)
                    else:
                        jnk=[0, 0, 0, 0]
                        save_temp_csv_data(jnk, opath)
                        tmp_zn=range(0,18)
                        save_temp_csv_data(tmp_zn, opath1)
                        save_temp_csv_data(tmp_zn, opath2)
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_mean_elev_fce_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_mean_elev_fce_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if count_cce_bioreg:
        def calculate_count_cce_bioreg_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            bioregion_loc="%sbioregions.tif" %(landscape_factor_dir)
            bioregions=arcpy.Raster(bioregion_loc)
            if arcpy.Exists(loc_COR_CCE):
                #CALC area in each habitat type
                opath="%sDBFs/count_cce_bioreg%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    inRaster = CCE_temp
                    outname=r"%sDBFs/count_cce_bioreg%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",bioregions,"VALUE",outname)
                    tmp_zn=range(0,18)
                    veg_area=zonal_area_from_dbf2(outname, tmp_zn)
                    n_areas=sum([x>0 for x in veg_area])
                    veg_area.append(n_areas)

                    save_temp_csv_data(veg_area, opath)
                    del CCE_temp; del inRaster; del outname; del veg_area; del opath;
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_count_cce_bioreg_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_count_cce_bioreg_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if count_cce_bioreg_transition_areas:
        def calculate_count_cce_bioreg_transition_areas_fx2(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            bioregion_loc="%sbioregions_boundaries_buffer_no_coastal.tif" %(landscape_factor_dir)
            bioregions=arcpy.Raster(bioregion_loc)
            if arcpy.Exists(loc_COR_CCE):
                #CALC area in each habitat type
                opath="%sDBFs/count_cce_bioreg_transition_areas%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    inRaster = CCE_temp
                    outname=r"%sDBFs/count_cce_bioreg_transition_areas%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(CCE_temp,"VALUE",bioregions,"VALUE",outname)
                    tmp_zn=range(1,15)
                    veg_area=zonal_area_from_dbf2(outname, tmp_zn)
                    n_areas=sum([x>0 for x in veg_area])
                    veg_area.append(n_areas)

                    save_temp_csv_data(veg_area, opath)
                    del CCE_temp; del inRaster; del outname; del veg_area; del opath;
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calculate_count_cce_bioreg_transition_areas_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calculate_count_cce_bioreg_transition_areas_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    ##CALCULATE calc_cce_precip_interannual_var
    if calc_cce_precip_interannual_var:
        def calc_cce_precip_interannual_var_fx2(sp_code_st, resultsdir, sp_code): #landscape_factor_dir,island
            metric_NA=True
            inRasterloc2 = r"%shist_ppt_var/annual_CV.tif" %(landscape_factor_dir)
            Sp_index=all_sp_codes.index(sp_code)
            loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(loc_COR_CCE):
                opath="%sDBFs/cce_precip_interannual_var%s.csv" %(resultsdir,sp_code_st)
                if arcpy.Exists(opath)==False or overwrite==1:
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    CCE_DEM_temp=CCE_temp*arcpy.Raster(inRasterloc2)
                    if CCE_DEM_temp.maximum>0:
                        CCE_mean_elev=get_num_attributes(CCE_DEM_temp,"MEAN")
                        CCE_min_elev=get_num_attributes(CCE_DEM_temp,"MINIMUM")
                        CCE_max_elev=get_num_attributes(CCE_DEM_temp,"MAXIMUM")
                        CCE_stdev_elev=get_num_attributes(CCE_DEM_temp,"STD")
                    else:
                        CCE_mean_elev=0
                        CCE_min_elev=0
                        CCE_max_elev=0
                        CCE_stdev_elev=0

                    if kio==0:
                        try:
                            arcpy.Delete_management(CCE_DEM_temp)
                        except:
                            pass

                    jnk=[CCE_mean_elev, CCE_min_elev, CCE_max_elev, CCE_stdev_elev]
                    save_temp_csv_data(jnk, opath)
                #else:
                #       jnk=load_temp_csv_float_data(opath)
                #       CCE_mean_elev=jnk[0]
                #       CCE_min_elev=jnk[1]
                #       CCE_max_elev=jnk[2]
                    metric_previously_done=False
                    metric_NA=False
                else:
                    metric_previously_done=True
                    metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_cce_precip_interannual_var_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_cce_precip_interannual_var_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()


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
            if arcpy.Exists(loc_response_zone)==False or overwrite==1:
                opath="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
                jnk=load_temp_csv_float_data(opath)
                area_FCE=jnk[0]
                if area_FCE!=0:
                    loc_Migrate=r"%sMigrate_%s.tif" %(resultsdir,sp_code_st)
                    Migrate_temp=arcpy.Raster(loc_Migrate)
                    loc_MRFzn=r"%sMRFzn_%s.tif" %(resultsdir,sp_code_st)
                    Microrefugia_zone=arcpy.Raster(loc_MRFzn)
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
                            inDEM = r"%sHI_dem.tif" %(landscape_factor_dir) #trim transition zone by min CCE and max FCE elevations
                            inDEM=arcpy.Raster(inDEM)
                            jnk=(inDEM < FCE_max_elev) & (inDEM > CCE_min_elev)
                            jnk=arcpy.sa.SetNull(jnk,1,"Value=0")
                            tranzition_zone_temp=tranzition_zone_temp*jnk
                            loc_transition_zone=r"%stransition_zone_%s.tif" %(resultsdir,sp_code_st)
                            #tranzition_zone_temp.save(loc_transition_zone)
                            arcpy.CopyRaster_management(tranzition_zone_temp, loc_transition_zone, "", "0", "0", "", "", "2_BIT", "", "")
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

                else:
                    loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
                    CCE_temp=arcpy.Raster(loc_COR_CCE)
                    response_zones= CCE_temp

                loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
                #response_zones.save(loc_response_zone)
                arcpy.CopyRaster_management(response_zones, loc_response_zone, "", "0", "0", "", "", "4_BIT", "", "")

                loc_response_zone_shp=r"%sresponse_zone_%s.shp" %(resultsdir,sp_code_st)
                arcpy.RasterToPolygon_conversion(loc_response_zone, loc_response_zone_shp, "SIMPLIFY", "VALUE")
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(create_rep_zones_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(create_rep_zones_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    ###############################
    ########END RESPONSE ZONE MAP
    ###############################
    print "calculating response zone metrics"


    #CALC RESPONSE ZONE AREA
    if calc_resp_zone_area:
        def calc_resp_zone_area_fx(sp_code_st, resultsdir, sp_code): #no other var calls
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)

            #path_zone_index=r"%sDBFs/%s_zone_index.csv" %(resultsdir, sp_code_st)
            path_zone_area=r"%sDBFs/%s_zone_area.csv" %(resultsdir, sp_code_st)
            if arcpy.Exists(path_zone_area)==False or overwrite==1:
                loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
                response_zones=arcpy.Raster(loc_response_zone)

                outname=r"%sDBFs/response_zone_areas_%s.dbf" %(resultsdir,sp_code_st)
                arcpy.sa.TabulateArea(response_zones,"VALUE",response_zones,"VALUE",outname)
                zones=[1, 2, 3]
                zone_area=zonal_area_from_dbf_matrix2(outname, zones)

                save_temp_csv_data(zone_area, path_zone_area)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_resp_zone_area_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_resp_zone_area_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    ###RESPONSE ZONES ARE DEFINED ABOVE###
    ######START CALCULATING METRICS#######
    zones=[1,2,3]
    veg_zones=[0, 1, 2, 3, 4, 5, 6, 7, 8]
            #make all calcs using single raster with 3 zones
    #SLR
    if calc_zone_slr_area:
        def calc_zone_slr_area_fx(sp_code_st, resultsdir, sp_code): #highest_slr_impact, landscape_factor_dir, island
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
                    slr_map_loc="%sall_island_1m_slr.tif" %(landscape_factor_dir)
                    slr_map=arcpy.Raster(slr_map_loc)
                    slr_map2=slr_map*response_zones

                    arcpy.BuildRasterAttributeTable_management(slr_map2, "Overwrite")
                    arcpy.CalculateStatistics_management(slr_map2, "", "", "", "OVERWRITE")
                    if slr_map2.maximum>0: #arcpy.GetRasterProperties_management(slr_map2, "MINIMUM"), get_num_attributes(slr_map2,"MEAN")==0
                        loc_slr=r"%sslr_%s.tif" %(resultsdir,sp_code_st)
                        #slr_map2.save(loc_slr)
                        arcpy.CopyRaster_management(slr_map2, loc_slr, "", "0", "0", "", "", "4_BIT", "", "")
                        loc_slr_table=r"%sDBFs/slr_%s.dbf" %(resultsdir,sp_code_st)
                        arcpy.sa.TabulateArea(response_zones,"VALUE", loc_slr, "VALUE", loc_slr_table)
                        #zones=[1,2,3]
                        zone_slr=zonal_area_from_dbf_matrix2(loc_slr_table, zones)
                        try:
                            #del db
                            del slr_map
                            del slr_map2
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
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_zone_slr_area_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_zone_slr_area_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    #CALCULATE habitat area within young lava flows
    if calc_zone_lava_flow_area:
        def calc_zone_lava_flow_area_fx(sp_code_st, resultsdir, sp_code): #landscape_factor_dir
            metric_NA=True
            #Sp_index=all_sp_codes.index(sp_code)
            try:
                Sp_index=hab_sp_code.index(str(sp_code))
                Sp_pioneer_status=spp_pioneer_data[Sp_index]
                if len(Sp_pioneer_status)>0 and Sp_pioneer_status=='0': #MUST DEBUG!
                    Sp_pioneer_status=eval(Sp_pioneer_status)
            except ValueError:
                Sp_index='9999'
                Sp_pioneer_status='NA'
                pass
            opath=r"%sDBFs/%s_zone_lava_flows.csv" %(resultsdir, sp_code_st)
            loc_lava_flows=r"%slava_flows_%s.tif" %(resultsdir,sp_code_st)
            if arcpy.Exists(opath)==False or overwrite==1:
                loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
                response_zones=arcpy.Raster(loc_response_zone)
                young_lava_flows = arcpy.Raster(r"%spioneer" %(landscape_factor_dir))
                young_lava_flows=young_lava_flows*response_zones
                if not get_num_attributes(young_lava_flows,"MEAN")==0:
                    loc_lava_flows_table=r"%sDBFs/lava_flows_%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.TabulateArea(response_zones,"VALUE",young_lava_flows, "VALUE",loc_lava_flows_table)
                    #zones=[1,2,3]
                    zone_lava_flows=zonal_area_from_dbf_matrix2(loc_lava_flows_table, temp_zones=zones)

                    young_lava_flows=arcpy.sa.SetNull(young_lava_flows,1,"Value=0")
                    arcpy.CopyRaster_management(young_lava_flows, loc_lava_flows, "", "0", "0", "", "", "4_BIT", "", "")
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
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_zone_lava_flow_area_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_zone_lava_flow_area_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    #HABITAT QUALITY (UGLY)
    if calc_zone_hab_qual:
        def calc_zone_hab_qual_fx(sp_code_st, resultsdir, sp_code):
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)

            opath=r"%sDBFs/%s_Zone_ugly_hab.csv" %(resultsdir, sp_code_st)
            if arcpy.Exists(opath)==False or overwrite==1:
                loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
                response_zones=arcpy.Raster(loc_response_zone)
                GBU_map_loc=arcpy.Raster(r"%shabqual_v3_4.tif" %(landscape_factor_dir))
                outname=r"%sDBFs/GBU_areas_%s.dbf" %(resultsdir,sp_code_st)
                arcpy.sa.TabulateArea(response_zones,"VALUE",GBU_map_loc,"VALUE",outname)

                #zones=[1,2,3]
                Zone_ugly_hab=zonal_area_from_dbf_byCol(outname, zones, 'VALUE_1')
                save_temp_csv_data(Zone_ugly_hab, opath)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_zone_hab_qual_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_zone_hab_qual_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

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
                loc_eff_table=r"%sDBFs/eff_%s.dbf" %(resultsdir,sp_code_st)
                arcpy.sa.TabulateArea(response_zones,"VALUE", eff_map_loc, "VALUE", loc_eff_table)

                #zones=[1,2,3]
                zone_eff=zonal_area_from_dbf_byCol(loc_eff_table, zones, 'VALUE_1')
                save_temp_csv_data(zone_eff, opath)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_eff_hab_qual_nonpioneer_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_eff_hab_qual_nonpioneer_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

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

                #zones=[1,2,3]
                zone_eff_pioneer=zonal_area_from_dbf_byCol(loc_eff_pioneer_table, zones, 'VALUE_1')

                save_temp_csv_data(zone_eff_pioneer, opath)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_eff_hab_qual_pioneer_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_eff_hab_qual_pioneer_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

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
                #eff_response_zones.save(eff_response_zone_loc)
                arcpy.CopyRaster_management(eff_response_zones, eff_response_zone_loc, "", "0", "0", "", "", "4_BIT", "", "")

                path_eff_zone_area=r"%sDBFs/%s_eff_zone_area.csv" %(resultsdir, sp_code_st)
                save_temp_csv_data(zone_eff_hab_qual, path_eff_zone_area)
                save_temp_csv_data(zone_eff_hab_qual, opath)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False
            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(chose_eff_hab_qual_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(chose_eff_hab_qual_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()


    #HABITAT QUALITY (GOOD, BAD)
    if calc_hab_qual:
        def calc_hab_qual_fx(sp_code_st, resultsdir, sp_code):
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)

            GBU_map_loc=arcpy.Raster(r"%shabqual_v3_4.tif" %(landscape_factor_dir))
            sp_GBU_map_loc="%sGBU_%s.tif" %(resultsdir, sp_code_st)
            if arcpy.Exists(sp_GBU_map_loc)==False or overwrite==1:
                if use_effective_CE_mask:
                    loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)
                else:
                    loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
                response_zones=arcpy.Raster(loc_response_zone)
                outname=r"%sDBFs/GBU_areas_%s.dbf" %(resultsdir,sp_code_st)
                arcpy.sa.TabulateArea(response_zones,"VALUE",GBU_map_loc,"VALUE",outname)
                #zones=[1,2,3]
                Zone_bad_hab=zonal_area_from_dbf_byCol(outname, zones, 'VALUE_2')
                Zone_good_hab=zonal_area_from_dbf_byCol(outname, zones, 'VALUE_3')
                opath=r"%sDBFs/%s_Zone_bad_hab.csv" %(resultsdir, sp_code_st)
                save_temp_csv_data(Zone_bad_hab, opath)
                opath=r"%sDBFs/%s_Zone_good_hab.csv" %(resultsdir, sp_code_st)
                save_temp_csv_data(Zone_good_hab, opath)

                GBU_map=GBU_map_loc*(response_zones>0)
                #GBU_map.save(sp_GBU_map_loc)
                arcpy.CopyRaster_management(GBU_map, sp_GBU_map_loc, "", "0", "0", "", "", "4_BIT", "", "")
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_hab_qual_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_hab_qual_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

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
                bioreg_data_avail=1
                try:
                    Sp_index=hab_sp_code.index(str(sp_code))
                except:
                    bioreg_index="b000"
                    zone_fragmentation=[0, 0, 0]
                    zone_core_biome==[0, 0, 0]
                    bioreg_max_elev=[0]*18
                    #zone_compatible_biome=[0, 0, 0]
                    bioreg_data_avail=0

                if bioreg_data_avail==1:
                    sp_fc=spp_forest_compatibility[Sp_index]
                    sp_sc=spp_shrubland_compatibility[Sp_index]
                    sp_gc=spp_grassland_compatibility[Sp_index]
                    #frag_map_loc="%sfragmentation/bin_%s%s%s_edge.tif" %(landscape_factor_dir,sp_fc, sp_sc, sp_gc)
                    frag_map_loc="%sfragmentation_map.tif" %(landscape_factor_dir)
                    frag_map=arcpy.Raster(frag_map_loc)
                    #compatible_biome_map=frag_map>0
                    core_biome_map=frag_map==2
                    frag_map=frag_map==1

                    #CALC EDGE AREA
                    path_zone_frag=r"%sDBFs/zone_frag_%s.csv" %(resultsdir,sp_code_st)
                    if arcpy.Exists(path_zone_frag)==False or overwrite==1:
                        frag_map=frag_map*response_zones
                        if frag_map.maximum>0: #arcpy.GetRasterProperties_management(slr_map2, "MINIMUM"), get_num_attributes(slr_map2,"MEAN")==0
                            frag_map=arcpy.sa.SetNull(frag_map,1,"Value=0")
                            loc_fragmentation=r"%sfragmentation_%s.tif" %(resultsdir,sp_code_st)
                            frag_map.save(loc_fragmentation)
                            loc_fragmentation_table=r"%sDBFs/fragmentation_%s.dbf" %(resultsdir,sp_code_st)
                            arcpy.sa.TabulateArea(response_zones,"VALUE",loc_fragmentation, "VALUE",loc_fragmentation_table)
                            #zones=[1,2,3]
                            zone_fragmentation=zonal_area_from_dbf_byCol(loc_fragmentation_table, zones, 'VALUE_1')
                        else:
                            zone_fragmentation=[0, 0, 0]
                        save_temp_csv_data(zone_fragmentation, path_zone_frag)
                    else:
                        zone_fragmentation=load_temp_csv_float_data(path_zone_frag)
                    print "calculated edge area"

                    #CALC CORE AREA
                    path_zone_core=r"%sDBFs/zone_core_%s.csv" %(resultsdir,sp_code_st)
                    if arcpy.Exists(path_zone_core)==False or overwrite==1:
                        core_biome_map=core_biome_map*response_zones
                        if core_biome_map.maximum>0: #arcpy.GetRasterProperties_management(slr_map2, "MINIMUM"), get_num_attributes(slr_map2,"MEAN")==0
                            core_biome_map=arcpy.sa.SetNull(core_biome_map,1,"Value=0")
                            loc_core_biome=r"%score_biome_%s.tif" %(resultsdir,sp_code_st)
                            core_biome_map.save(loc_core_biome)
                            loc_core_biome_table=r"%sDBFs/core_biome_%s.dbf" %(resultsdir,sp_code_st)
                            #arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", loc_core_biome, loc_core_biome_table,"DATA")
                            arcpy.sa.TabulateArea(response_zones,"VALUE",loc_core_biome, "VALUE",loc_core_biome_table)
                            #zones=[1,2,3]
                            zone_core_biome=zonal_area_from_dbf_byCol(loc_core_biome_table, zones, 'VALUE_1')
                        else:
                            zone_core_biome=[0,0,0]
                        save_temp_csv_data(zone_core_biome, path_zone_core)
                    else:
                        zone_core_biome=load_temp_csv_float_data(path_zone_core)
                    print "calculated core area"

                    #MAX BIOREG ELEVATION
                    path_max_bioreg_elev=r"%sDBFs/max_biome_elev_%s.csv" %(resultsdir,sp_code_st)
                    if arcpy.Exists(path_max_bioreg_elev)==False or overwrite==1:
                        #bioreg_index="b"+sp_fc+sp_sc+sp_gc
                        try:
                            Sp_index=hab_sp_code.index(str(sp_code))
                            Sp_pioneer_status=spp_pioneer_data[Sp_index]
                            if len(Sp_pioneer_status)>0 and Sp_pioneer_status=='0': #MUST DEBUG!
                                Sp_pioneer_status=eval(Sp_pioneer_status)
                        except ValueError:
                            Sp_index='9999'
                            Sp_pioneer_status='NA'
                            pass
                        if Sp_pioneer_status==1:
                            bioreg_index="pioneer"
                        else:
                            bioreg_index="non_pioneer"

                        bioreg_max_elev=bioreg_elev_mat[bioreg_index]
                        bioreg_max_elev[:]=[float(x) for x in bioreg_max_elev]
                        save_temp_csv_data(bioreg_max_elev, path_max_bioreg_elev)
                    else:
                        bioreg_max_elev=load_temp_csv_float_data(path_max_bioreg_elev)

                    jnk=[bioreg_index, bioreg_max_elev, zone_fragmentation, zone_core_biome]
                    #jnk=[bioreg_index, bioreg_max_elev, zone_fragmentation, zone_core_biome, zone_compatible_biome]
                    save_temp_csv_data(jnk, opath)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_fragmentation_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_fragmentation_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

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
                    path_max_bioreg_elev=r"%sDBFs/max_biome_elev_%s.csv" %(resultsdir,sp_code_st)
                    bioreg_max_elev=load_temp_csv_float_data(path_max_bioreg_elev)
                    min_elev_zone_vals=load_temp_csv_float_data(opath1)
                    max_elev_zone_vals=load_temp_csv_float_data(opath2)
                    max_elev_zone_vals[:]=[float(x) for x in max_elev_zone_vals]
                    min_elev_zone_vals[:]=[float(x) for x in min_elev_zone_vals]
                    c=numpy.asarray(max_elev_zone_vals)
                    a=numpy.asarray(bioreg_max_elev)
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
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_dist_to_top_of_island_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_dist_to_top_of_island_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

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


                        #zones=[1,2,3]
                        zone_protected_area=zonal_area_from_dbf_byCol(outname, zones, 'VALUE_1')

                    else:
                        pass
                save_temp_csv_data(zone_protected_area, opath)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_protected_area_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_protected_area_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

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
                        print 'tabulated ungulate free area'
                        #zones=[1,2,3]
                        Zones_ungfree=zonal_area_from_dbf_byCol(outname, zones, 'VALUE_1')
                    else:
                        pass
                save_temp_csv_data(Zones_ungfree, opath)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_ung_free_area_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_ung_free_area_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

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

                #zones=[1,2,3]
                Zone_slope_min=zonal_area_from_dbf_byCol(loc_CCE_slope, zones, 'MIN', multFactor=1, default_val=0)
                Zone_slope_max=zonal_area_from_dbf_byCol(loc_CCE_slope, zones, 'MAX', multFactor=1, default_val=0)
                Zone_slope_std=zonal_area_from_dbf_byCol(loc_CCE_slope, zones, 'STD', multFactor=1, default_val=0)
                Zone_slope_median=zonal_area_from_dbf_byCol(loc_CCE_slope, zones, 'MEDIAN', multFactor=1, default_val=0)

                save_temp_csv_data(Zone_slope_median, opath4)
                save_temp_csv_data(Zone_slope_std, opath3)
                save_temp_csv_data(Zone_slope_min, opath2)
                save_temp_csv_data(Zone_slope_max, opath)
                metric_previously_done=False
                metric_NA=False


            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_slope_metrics_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_slope_metrics_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

    if calc_zone_topo_complexity:
        def calc_zone_topo_complexity_fx(sp_code_st, resultsdir, sp_code):
            metric_NA=True
            Sp_index=all_sp_codes.index(sp_code)

            topo_complexity_raster = r"%sterrain_var_mean_rounded.tif" %(landscape_factor_dir)
            opath1=r"%sDBFs/%s_zone_topo_complexity.csv" %(resultsdir, sp_code_st)
            if arcpy.Exists(opath1)==False or overwrite==1:
                if use_effective_CE_mask:
                    loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)
                else:
                    loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
                response_zones=arcpy.Raster(loc_response_zone)

                if use_zonal_stats==1:
                    loc_topo_complexity=r"%sDBFs/aspect_%s.dbf" %(resultsdir,sp_code_st)
                    arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", topo_complexity_raster, loc_topo_complexity)
                    #zones=[1,2,3]
                    zone_topo_complexity=zonal_area_from_dbf_byCol(loc_topo_complexity, zones, 'MEAN', multFactor=1, default_val='NA')

                else:
                    array_index=[1,2,3]
                    temp=alt_zonal_stats(response_zones, topo_complexity_raster, array_index)
                    zone_topo_complexity=temp[1]

                save_temp_csv_data(zone_topo_complexity, opath1)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_zone_topo_complexity_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_zone_topo_complexity_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

##    #CALC CCE ASPECT MEAN, STDE [[arcgis does not like this calcualtion crashes often]]
##    if calc_zone_aspect_mean:
##        def calc_zone_aspect_mean_fx(sp_code_st, resultsdir, sp_code):
##            metric_NA=True
##            Sp_index=all_sp_codes.index(sp_code)
##
##            Aspect_temp = r"%s%s/DEM/%s_aspect_noflatareas.tif" %(landscape_factor_dir,island,island)
##            opath1=r"%sDBFs/%s_zone_aspect_mean.csv" %(resultsdir, sp_code_st)
##            if arcpy.Exists(opath1)==False or overwrite==1:
##                if use_effective_CE_mask:
##                    loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)
##                else:
##                    loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
##                response_zones=arcpy.Raster(loc_response_zone)
##
##                if use_zonal_stats==1:
##                    loc_CCE_aspect=r"%sDBFs/aspect_%s.dbf" %(resultsdir,sp_code_st)
##                    arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", Aspect_temp, loc_CCE_aspect)
##
##                    #zones=[1,2,3]
##                    zone_aspect_mean=zonal_area_from_dbf_byCol(loc_CCE_aspect, zones, 'MEAN', multFactor=1, default_val='NA')
##
##                else:
##                    array_index=[1,2,3]
##                    temp=alt_zonal_stats(response_zones, Aspect_temp, array_index)
##                    zone_aspect_mean=temp[1]
##
##                save_temp_csv_data(zone_aspect_mean, opath1)
##                metric_previously_done=False
##                metric_NA=False
##            else:
##                metric_previously_done=True
##                metric_NA=False
##
##            return metric_previously_done, metric_NA
##        if not parallel:
##            for i in range(len(CCE_Spp)):
##                va_metric_wrapper(calc_zone_aspect_mean_fx, i)
##        else:
##            import itertools
##            import multiprocessing
##            from multiprocessing import Pool, freeze_support
##            if __name__ == '__main__':
##                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
##                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_zone_aspect_mean_fx, len(CCE_Spp)), range(len(CCE_Spp))))
##                pool.close()
##                import time
##                time.sleep(10)
##                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
##                pool.terminate()
##                pool.join()
##
##    if calc_zone_cos_aspect:
##        def calc_zone_cos_aspect_fx(sp_code_st, resultsdir, sp_code):
##            metric_NA=True
##            Sp_index=all_sp_codes.index(sp_code)
##
##            Aspect_temp = r"%s%s/DEM/%s_cos_aspect.tif" %(landscape_factor_dir,island,island)
##            opath=r"%sDBFs/%s_zone_cos_aspect_std.csv" %(resultsdir, sp_code_st)
##            if arcpy.Exists(opath)==False or overwrite==1:
##                if use_effective_CE_mask:
##                    loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)
##                else:
##                    loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
##                response_zones=arcpy.Raster(loc_response_zone)
##
##                if use_zonal_stats==1:
##                    loc_CCE_aspect=r"%sDBFs/cos_aspect_%s.dbf" %(resultsdir,sp_code_st)
##                    arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", Aspect_temp, loc_CCE_aspect,"DATA")
##
##                    #zones=[1,2,3]
##                    zone_aspect_std1=zonal_area_from_dbf_byCol(loc_CCE_aspect, zones, 'STD', multFactor=1, default_val='NA')
##                else:
##                    array_index=[1,2,3]
##                    temp=alt_zonal_stats(response_zones, Aspect_temp, array_index)
##                    zone_aspect_std1=temp[2]
##                save_temp_csv_data(zone_aspect_std1, opath)
##                metric_previously_done=False
##                metric_NA=False
##            else:
##                metric_previously_done=True
##                metric_NA=False
##
##            return metric_previously_done, metric_NA
##        if not parallel:
##            for i in range(len(CCE_Spp)):
##                va_metric_wrapper(calc_zone_cos_aspect_fx, i)
##        else:
##            import itertools
##            import multiprocessing
##            from multiprocessing import Pool, freeze_support
##            if __name__ == '__main__':
##                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
##                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_zone_cos_aspect_fx, len(CCE_Spp)), range(len(CCE_Spp))))
##                pool.close()
##                import time
##                time.sleep(10)
##                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
##                pool.terminate()
##                pool.join()
##
##    if calc_zone_sin_aspect:
##        def calc_zone_sin_aspect_fx(sp_code_st, resultsdir, sp_code):
##            metric_NA=True
##            Sp_index=all_sp_codes.index(sp_code)
##
##            Aspect_temp = r"%s%s/DEM/%s_sin_aspect.tif" %(landscape_factor_dir,island,island)
##            opath=r"%sDBFs/%s_zone_sin_aspect_std.csv" %(resultsdir, sp_code_st)
##            if arcpy.Exists(opath)==False or overwrite==1:
##                if use_effective_CE_mask:
##                    loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)
##                else:
##                    loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
##                response_zones=arcpy.Raster(loc_response_zone)
##
##                if use_zonal_stats==1:
##                    loc_CCE_aspect=r"%sDBFs/sin_aspect_%s.dbf" %(resultsdir,sp_code_st)
##                    arcpy.sa.ZonalStatisticsAsTable(response_zones,"VALUE", Aspect_temp, loc_CCE_aspect,"DATA")
##
##                    #zones=[1,2,3]
##                    zone_aspect_std2=zonal_area_from_dbf_byCol(loc_CCE_aspect, zones, 'STD', multFactor=1, default_val='NA')
##
##                else:
##                    array_index=[1,2,3]
##                    temp=alt_zonal_stats(response_zones, Aspect_temp, array_index)
##                    zone_aspect_std2=temp[2]
##
##                save_temp_csv_data(zone_aspect_std2, opath)
##                metric_previously_done=False
##                metric_NA=False
##            else:
##                metric_previously_done=True
##                metric_NA=False
##
##            return metric_previously_done, metric_NA
##        if not parallel:
##            for i in range(len(CCE_Spp)):
##                va_metric_wrapper(calc_zone_sin_aspect_fx, i)
##        else:
##            import itertools
##            import multiprocessing
##            from multiprocessing import Pool, freeze_support
##            if __name__ == '__main__':
##                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
##                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_zone_sin_aspect_fx, len(CCE_Spp)), range(len(CCE_Spp))))
##                pool.close()
##                import time
##                time.sleep(10)
##                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
##                pool.terminate()
##                pool.join()
##
##    if calc_zone_aspect_std:
##        def calc_zone_aspect_std_fx(sp_code_st, resultsdir, sp_code):
##            metric_NA=True
##            Sp_index=all_sp_codes.index(sp_code)
##
##            opath1=r"%sDBFs/%s_zone_aspect_std.csv" %(resultsdir, sp_code_st)
##            if arcpy.Exists(opath1)==False or overwrite==1:
##                opath11=r"%sDBFs/%s_zone_cos_aspect_std.csv" %(resultsdir, sp_code_st)
##                opath22=r"%sDBFs/%s_zone_sin_aspect_std.csv" %(resultsdir, sp_code_st)
##                zone_aspect_std1= load_temp_csv_float_data(opath11)
##                zone_aspect_std2= load_temp_csv_float_data(opath22)
##
##                zone_aspect_std=[]
##                for jh in range(len(zone_aspect_std2)):
##                    jnk=(zone_aspect_std2[jh]+zone_aspect_std1[jh])/2
##                    zone_aspect_std.append(jnk)
##                save_temp_csv_data(zone_aspect_std, opath1)
##                try:
##                    #del db
##                    os.unlink(loc_CCE_aspect)
##                except:
##                    pass
##                metric_previously_done=False
##                metric_NA=False
##            else:
##                metric_previously_done=True
##                metric_NA=False
##
##            return metric_previously_done, metric_NA
##        if not parallel:
##            for i in range(len(CCE_Spp)):
##                va_metric_wrapper(calc_zone_aspect_std_fx, i)
##        else:
##            import itertools
##            import multiprocessing
##            from multiprocessing import Pool, freeze_support
##            if __name__ == '__main__':
##                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
##                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_zone_aspect_std_fx, len(CCE_Spp)), range(len(CCE_Spp))))
##                pool.close()
##                import time
##                time.sleep(10)
##                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
##                pool.terminate()
##                pool.join()

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
                    #zones=[1,2,3]
                    zone_mean_ppt_gradient=zonal_area_from_dbf_byCol(loc_ppt_gradient, zones, 'MEAN', multFactor=1, default_val='NA')

                    #zone_aspect_std=get_zone_stats(zone_index, db, "STD")
                else:
                    array_index=[1,2,3]
                    temp=alt_zonal_stats(response_zones, ppt_gradient_raster, array_index)
                    zone_mean_ppt_gradient=temp[1]
                save_temp_csv_data(zone_mean_ppt_gradient, opath)
                t1 = time.time();
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_ppt_gradient_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_ppt_gradient_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

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
                    #zones=[1,2,3]
                    zone_mean_inv_suitability=zonal_area_from_dbf_byCol(loc_inv_suitability, zones, 'MEAN', multFactor=1, default_val='NA')
                else:
                    array_index=[1,2,3]
                    temp=alt_zonal_stats(response_zones, inv_suitability_raster, array_index)
                    zone_mean_inv_suitability=temp[1]

                save_temp_csv_data(zone_mean_inv_suitability, opath)
                metric_previously_done=False
                metric_NA=False
            else:
                metric_previously_done=True
                metric_NA=False

            return metric_previously_done, metric_NA
        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(calc_zone_invasibility_fx, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(calc_zone_invasibility_fx, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10)
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()

        ##END LOOP
    try:
        arcpy.Delete_management(sp_CO_points_loc)
    except:
        pass

except arcpy.ExecuteError:
    msgs = arcpy.GetMessages(2) # Get the tool error messages
    arcpy.AddError(msgs) # Return tool error messages for use with a script tool
    print msgs # Print tool error messages for use in Python/PythonWin

##except socket.error as error: #http://stackoverflow.com/questions/18832643/how-to-catch-this-python-exception-error-errno-10054-an-existing-connection
##    if error.errno == errno.WSAECONNRESET:
##        reconnect()
##        retry_action()
##    else:
##        raise
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
    jnk_msg=""
    message = "\n\n"+ jnk_msg+ "\n\n" + "error while calculating vulnerabilities"+ "\n\n" + str(pymsg) + "\n" + str(msgs)
    print message
finally:
    arcpy.CheckInExtension("Spatial") # Check in the 3D Analyst extension so other users can access it
