#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#must have open document with hillshade background image

#USER INPUT
island="all" #la ha all
landscape_factor_dir=r"Y:/VA data/landscape/" #whichever is data dir, will have to have subfolders: la/DEM/ (where DEM based layers go), gaplandcover/ (where gaplandcov_hi is placed)
CAO_data_dir=r"Y:/VA data/CAO/"
#landscape_factor_dir=r"C:/Users/lfortini/Data/VA data/landscape/" #whichever is data dir, will have to have subfolders: la/DEM/ (where DEM based layers go), gaplandcover/ (where gaplandcov_hi is placed)
#CAO_data_dir=r"C:/Users/lfortini/Data/VA data/CAO/"
highest_slr_impact=3 #max elev of slr impacts (this avoids SLR impact calc for high elev species)
#f = open("C:/Users/lfortini/Data/0_model_config_sp_to_run.txt", "r")
#sub_spp_CE_folder= f.read() 
#ce_data_dir=r"C:/Users/lfortini/Data/VA data/CEs/%s/" %(sub_spp_CE_folder)
ce_data_dir=r"Y:/VA data/CEs/"
max_search_dist_for_transition_zone= 5000 #in m
use_bio_region_filter=0
subset_of_CEs=[0,1084] #1084 leave empty [] for no subset, if subset: [300,400]
import_cce_list=False
use_effective_CE_mask=True
use_zonal_stats=1
all_files_in_directory=1 #1 to do batch processing of all files in a directory, 0 if want to specify which species below
save_results_to_table=1
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
##
create_rep_zones=False
calc_resp_zone_area=False
calc_zone_slr_area=False
calc_zone_lava_flow_area=False #missing
calc_zone_hab_qual=False
calc_eff_hab_qual=False
calc_eff_hab_qual_pioneer=False
chose_eff_hab_qual=False
create_eff_resp_zones=False
calc_eff_resp_zone_area=False #debug: why dying after species 549?
calc_hab_qual=False #none after sp 42
calc_good_hab=False #always off
calc_fragmentation=False
calc_dist_to_top_of_island=False
calc_protected_area=True #none after 276
calc_ung_free_area=True #missing
calc_slope_metrics=False
calc_zone_aspect_mean=False
calc_zone_cos_aspect=False
calc_zone_sin_aspect=False
calc_zone_aspect_std=False
calc_ppt_gradient=True #missing
calc_zone_invasibility=True #missing

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

def dbfreader(f):
    """Returns an iterator over records in a Xbase DBF file.

    The first row returned contains the field names.
    The second row contains field specs: (type, size, decimal places).
    Subsequent rows contain the data records.
    If a record is marked as deleted, it is skipped.

    File should be opened for binary reads.

    """
    # See DBF format spec at:
    #     http://www.pgts.com.au/download/public/xbase.htm#DBF_STRUCT

    numrec, lenheader = struct.unpack('<xxxxLH22x', f.read(32))    
    numfields = (lenheader - 33) // 32

    fields = []
    for fieldno in xrange(numfields):
        name, typ, size, deci = struct.unpack('<11sc4xBB14x', f.read(32))
        name = name.replace('\0', '')       # eliminate NULs from string   
        fields.append((name, typ, size, deci))
    yield [field[0] for field in fields]
    yield [tuple(field[1:]) for field in fields]

    terminator = f.read(1)
    assert terminator == '\r'

    fields.insert(0, ('DeletionFlag', 'C', 1, 0))
    fmt = ''.join(['%ds' % fieldinfo[2] for fieldinfo in fields])
    fmtsiz = struct.calcsize(fmt)
    for i in xrange(numrec):
        record = struct.unpack(fmt, f.read(fmtsiz))
        if record[0] != ' ':
            continue                        # deleted record
        result = []
        for (name, typ, size, deci), value in itertools.izip(fields, record):
            if name == 'DeletionFlag':
                continue
            if typ == "N":
                value = value.replace('\0', '').lstrip()
                if value == '':
                    value = 0
                elif deci:
                    value = decimal.Decimal(value)
                else:
                    value = int(value)
            elif typ == 'D':
                y, m, d = int(value[:4]), int(value[4:6]), int(value[6:8])
                value = datetime.date(y, m, d)
            elif typ == 'L':
                value = (value in 'YyTt' and 'T') or (value in 'NnFf' and 'F') or '?'
            elif typ == 'F':
                value = float(value)
            result.append(value)
        yield result

def zonal_area_from_dbf(outname, temp_zones):
    f = open(outname, 'rb')
    db = list(dbfreader(f))
    f.close()
    
    cover, cover_area = db[0], db[2]
    cover=cover[1:]
    cover_area =cover_area [1:]
    cover=[int(x[6:]) for x in cover]
    all_cover_area=[0]*len(temp_zones)
    for ire in cover:
        all_cover_area[temp_zones.index(ire)]=cover_area[cover.index(ire)]/1000000
    return all_cover_area

def read_dbf_stat_vals(filename, stat, zones):
    f = open(filename, 'rb')
    db = list(dbfreader(f))
    f.close()
    #for record in db:
    #    print record
    colnames, zone_records = db[0], db[2:]
    zones_present=[]
    for weri in range(len(zone_records)):
        zones_present.append(zone_records[weri][colnames.index('VALUE')])
    zone_stats=[]
    for weri in range(len(zone_records)):
        zone_stats.append(zone_records[weri][colnames.index(stat)])
    all_zone_stats=[0]*len(zones)
    zone=zones_present[0]
    for zone in zones_present:
        all_zone_stats[zones.index(zone)]=zone_stats[zones_present.index(zone)]
    zone_stat=all_zone_stats
    return zone_stat

def zonal_area_from_dbf_matrix(outname, temp_zones):
	f = open(outname, 'rb')
	db = list(dbfreader(f))
	f.close()
	cover, cover_area = db[0], db[2:]
	cover=cover[1:]
	if len(cover_area)==len(cover):
		cover_area0=[]
		for jij in range(len(cover_area)):
			cover_area0.append(cover_area[jij][jij+1])
		cover_area=cover_area0
	cover=[int(x[6:]) for x in cover]
	all_cover_area=[0]*len(temp_zones)
	for ire in cover:
		all_cover_area[temp_zones.index(ire)]=cover_area[cover.index(ire)]/1000000
	return all_cover_area		
    #f = open(outname, 'rb')
    #db = list(dbfreader(f))
    #f.close()
    #cover, cover_area = db[0], db[2]
    #cover=cover[1:]
    #cover_area =cover_area [1:]
    #cover=[int(x[6:]) for x in cover]
    #all_cover_area=[0]*len(temp_zones)
    #for ire in cover:
    #    all_cover_area[temp_zones.index(ire)]=cover_area[cover.index(ire)]/1000000
    #return all_cover_area
    
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
		

i=116
t0 = time.time()			
#Get species name, sp code, check if species already have been done
jnk=CCE_Spp[i]
jnk.encode('ascii','replace')
inRaster = ce_data_dir + jnk
sp_code_st=inRaster[-8:-4]
resultsdir=resultsdir0+sp_code_st+"/"	
sp_code=str(int(sp_code_st)) #get rid of extra zeros

overwrite=1
zones=[1,2,3]
####################
metric_NA=True
Sp_index=all_sp_codes.index(sp_code)		

GBU_map_loc=arcpy.Raster(r"%shabqual_simple.tif" %(landscape_factor_dir))
sp_GBU_map_loc="%sGBU_%s.tif" %(resultsdir, sp_code_st)




if use_effective_CE_mask:
    loc_response_zone=r"%sresponse_zone_eff_%s.tif" %(resultsdir, sp_code_st)							
else:
    loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
response_zones=arcpy.Raster(loc_response_zone)					
outname=r"%sDBFs/GBU_areas_%s.dbf" %(resultsdir,sp_code_st)
arcpy.sa.TabulateArea(response_zones,"VALUE",GBU_map_loc,"VALUE",outname)
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
    Zone_bad_hab0=get_zone_stats(temp_zone_index, db, "VALUE_2")
    Zone_bad_hab0[:]=[x/1000000 for x in Zone_bad_hab0]
else:
    Zone_bad_hab0=[0]*3
    

avail=0
try:				
    field_names.index('VALUE_3')
    avail=1
except:
    avail=0
if avail==1:
    Zone_good_hab0=get_zone_stats(temp_zone_index, db, "VALUE_3")
    Zone_good_hab0[:]=[x/1000000 for x in Zone_good_hab0]
else:
    Zone_good_hab0=[0]*3

f = open(outname, 'rb')
db = list(dbfreader(f))
f.close()
colnames= db[0]

avail=0
try:				
    colnames.index('VALUE_2')
    avail=1
except:
    avail=0
    pass

if avail==1:
    temp_zones=[1,2,3]
    Zone_bad_hab=read_dbf_stat_vals(outname, 'VALUE_2',temp_zones)
    Zone_bad_hab[:]=[x/1000000 for x in Zone_bad_hab]	
else:
    Zone_bad_hab=[0]*3


try:				
    colnames.index('VALUE_3')
    avail=1
except:
    avail=0
    pass

if avail==1:
    temp_zones=[1,2,3]
    Zone_good_hab=read_dbf_stat_vals(outname, 'VALUE_3',temp_zones)
    Zone_good_hab[:]=[x/1000000 for x in Zone_good_hab]	
else:
    Zone_good_hab=[0]*3
