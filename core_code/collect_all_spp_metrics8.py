#USER INPUT
#datadir=r"Y:/Py_code/test/results/all/"
datadir=r"Y:/PICCC_analysis/plant_landscape_va_results/allSpp_allIsl2/results/all/"
sp_temps=range(1,1115) #range(1,1115)
bioreg_subset=0
use_effective_CE_mask=True

import os
#import arcpy
#import arcpy.sa
#import math
import csv
import numpy
#import arcgisscripting
#from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/
#arcpy.env.overwriteOutput = True
#arcpy.env.workspace = datadir

resultsdir0=datadir
del_terms=[]
for sp_temp in sp_temps:
    sp_code=str(sp_temp)
    lspcode=len(sp_code)
    new_sp_code=(4-lspcode)*'0'+sp_code
    if bioreg_subset==1:
        new_sp_code=new_sp_code+"_trim"
    del_terms.append(new_sp_code)

dirList=os.listdir(datadir)
import fnmatch
CSV_files=fnmatch.filter(dirList, '*values.csv')

Spp_data=[]
Sp_data=['sp_name', 'sp_code', 'sqkm_area_CCE', 'sqkm_area_FCE', 'area_change', 'prop_area_change', 'winkout', 'CE_overlap', 'FCE_distance', 'CCE_mean_elev', 'CCE_min_elev', 'CCE_max_elev', 'CCE_stdev_elev',
    'FCE_mean_elev', 'FCE_min_elev', 'FCE_max_elev', 'FCE_stdev_elev',
    'FCE_min_elev_E_Ma', 'FCE_min_elev_E_Mo', 'FCE_min_elev_Hualalai', 'FCE_min_elev_Ko', 'FCE_min_elev_Kau', 'FCE_min_elev_Ka', 'FCE_min_elev_Kilauea', 'FCE_min_elev_Kohala',
    'FCE_min_elev_Kona', 'FCE_min_elev_Koolau', 'FCE_min_elev_La', 'FCE_min_elev_Maunakea', 'FCE_min_elev_NE_Maunaloa', 'FCE_min_elev_Ni', 'FCE_min_elev_NW_Maunaloa', 'FCE_min_elev_Waianae',
    'FCE_min_elev_W_Ma', 'FCE_min_elev_W_Mo',
    'FCE_max_elev_E_Ma', 'FCE_max_elev_E_Mo', 'FCE_max_elev_Hualalai', 'FCE_max_elev_Ko', 'FCE_max_elev_Kau', 'FCE_max_elev_Ka', 'FCE_max_elev_Kilauea', 'FCE_max_elev_Kohala',
    'FCE_max_elev_Kona', 'FCE_max_elev_Koolau', 'FCE_max_elev_La', 'FCE_max_elev_Maunakea', 'FCE_max_elev_NE_Maunaloa', 'FCE_max_elev_Ni', 'FCE_max_elev_NW_Maunaloa', 'FCE_max_elev_Waianae',
    'FCE_max_elev_W_Ma', 'FCE_max_elev_W_Mo',
    'Biome_max_elev_E_Ma', 'Biome_max_elev_E_Mo', 'Biome_max_elev_Hualalai', 'Biome_max_elev_Ko', 'Biome_max_elev_Kau', 'Biome_max_elev_Ka', 'Biome_max_elev_Kilauea', 'Biome_max_elev_Kohala',
    'Biome_max_elev_Kona', 'Biome_max_elev_Koolau', 'Biome_max_elev_La', 'Biome_max_elev_Maunakea', 'Biome_max_elev_NE_Maunaloa', 'Biome_max_elev_Ni', 'Biome_max_elev_NW_Maunaloa', 'Biome_max_elev_Waianae',
    'Biome_max_elev_W_Ma', 'Biome_max_elev_W_Mo',
    'Biome_index', 'n_bioreg_in_FCE', 'n_bioreg_near_top', 'prop_bioreg_near_top',
    'Other', 'Alpine_shrubland', 'Mixed_cliff_habitat', 'Dry_forest', 'Dry_grassland', 'Dry_shrubland', 'Coastal_strand', 'Mesic_forest', 'Mesic_grassland', 'Mesic_shrubland',
    'Bog', 'Wet_forest', 'Wetlands_and_marshes', 'Barren', 'Mixed_introduced',
    'BPS_Other', 'BPS_Alpine_shrubland', 'BPS_Mixed_cliff_habitat', 'BPS_Dry_forest', 'BPS_Dry_grassland', 'BPS_Dry_shrubland', 'BPS_Coastal_strand',
    'BPS_Mesic_forest', 'BPS_Mesic_grassland', 'BPS_Mesic_shrubland', 'BPS_Bog', 'BPS_Wet_forest',
    'BPS_Wetlands_and_marshes', 'BPS_Barren', 'BPS_Mixed_introduced',
    'HIGAP_all_Forest', 'HIGAP_all_Shrubland', 'HIGAP_all_Grassland', 'HIGAP_all_Bog',
    'HIGAP_all_Cliff', 'HIGAP_all_Coastal', 'HIGAP_all_Wetland',
    'HIGAP_native_Forest', 'HIGAP_native_Shrubland', 'HIGAP_native_Grassland', 'HIGAP_native_Bog',
    'HIGAP_native_Cliff', 'HIGAP_native_Coastal', 'HIGAP_native_Wetland',
    'LANDFIRE_all_Forest', 'LANDFIRE_all_Shrubland', 'LANDFIRE_all_Grassland', 'LANDFIRE_all_Bog',
    'LANDFIRE_all_Cliff', 'LANDFIRE_all_Coastal', 'LANDFIRE_all_Wetland',
    'LANDFIRE_native_Forest', 'LANDFIRE_native_Shrubland', 'LANDFIRE_native_Grassland', 'LANDFIRE_native_Bog',
    'LANDFIRE_native_Cliff', 'LANDFIRE_native_Coastal', 'LANDFIRE_native_Wetland',
    'BPS_native_Forest', 'BPS_native_Shrubland', 'BPS_native_Grassland', 'BPS_native_Bog',
    'BPS_native_Cliff', 'BPS_native_Coastal', 'BPS_native_Wetland',
    'n_habitats_BPS', 'n_habitats_landfire_native', 'n_habitats_landfire_all',
    'n_habitats_HIGAP_native', 'n_habitats_HIGAP_all',
    'E_Maui_area', 'E_Molokai_area', 'Hualalai_area', 'Kahoolawe_area', 'Kau_area',
    'Kauai_area', 'Kilauea_area', 'Kohala_area', 'Kona_area', 'Koolau_area', 'Lanai_area',
    'Mauna_Kea_area', 'NE_Mauna_Loa_area', 'Niihau_area', 'NW_Mauna_Loa_area',
    'Waianae_area', 'W_Maui_area', 'W_Molokai_area', 'n_bioreg_in_CCE',
    'Kau_Kilauea', 'Hualalai_Kona', 'Kona_Kau', 'Mauna_Kea_Kohala', 'NE_Mauna_Loa_Kau',
    'NE_Mauna_Loa_Kilauea', 'NE_Mauna_Loa_Mauna_Kea', 'Hualalai_NW_Mauna_Loa',
    'Kona_NW_Mauna_Loa', 'NW_Mauna_Loa_Mauna_Kea', 'NW_Mauna_Loa_NE_Mauna_Loa',
    'Waianae_Koolau', 'E_Maui_W_Maui', 'E_Molokai_W_Molokai', 'n_bioreg_trans_in_CCE',
    'CCE_mean_precip_CV', 'CCE_min_precip_CV', 'CCE_max_precip_CV', 'CCE_stdev_precip_CV',
    'zone_area__MR', 'zone_area___TL', 'zone_area__MG', 'eff_zone_area__MR', 'eff_zone_area__TL', 'eff_zone_area__MG',
    'eff_pioneer_zone_area__MR', 'eff_pioneer_zone_area__TL', 'eff_pioneer_zone_area__MG', 'eff_hab_qual_area__MR', 'eff_hab_qual_area__TL', 'eff_hab_qual_area__MG',
#    'zone_habitat_area__MR', 'zone_habitat_area__TL', 'zone_habitat_area__MG',
    'Sp_pioneer_status', 'zone_lavaflow_area__MR', 'zone_lavaflow_area__TL', 'zone_lavaflow_area__MG',
    'ugly__MR', 'ugly__TL', 'ugly__MG', 'bad__MR', 'bad__TL', 'bad__MG', 'good__MR', 'good__TL', 'good__MG',
    'protected_area__MR', 'protected_area__TL', 'protected_area__MG', 'Ung_free_Areas__MR', 'Ung_free_Areas__TL', 'Ung_free_Areas__MG',
    'persist_in_alien_hab', 'zone_edge__MR', 'zone_edge__TL', 'zone_edge__MG', 'zone_core__MR', 'zone_core__TL', 'zone_core__MG',
    'fragmentation__MR', 'fragmentation__TL','fragmentation__MG',
    'zone_slr__MR', 'zone_slr__TL', 'zone_slr__MG', 'mean_ppt_gradient__MR', 'mean_ppt_gradient__TL', 'mean_ppt_gradient__MG',
    'mean_inv_suitability__MR', 'mean_inv_suitability__TL', 'mean_inv_suitability__MG',
    'Topo_complexity__MR', 'Topo_complexity__TL', 'Topo_complexity__MG',
#    'Zone_slope_medMR', 'Zone_slope_medTL', 'Zone_slope_medMG',
#    'Zone_slope_minMR', 'Zone_slope_minTL', 'Zone_slope_minMG', 'Zone_slope_maxMR', 'Zone_slope_maxTL', 'Zone_slope_maxMG',
#    'Zone_slope_stdMR', 'Zone_slope_stdTL', 'Zone_slope_stdMG',
#    'Zone_slope_cvMR', 'Zone_slope_cvTL', 'Zone_slope_cvMG', 'zone_aspect_meanMR', 'zone_aspect_meanTL', 'zone_aspect_meanMG',
#    'zone_aspect_stdMR', 'zone_aspect_stdTL', 'zone_aspect_stdMG',
    'total_CO_points', 'total_zone_pts', 'pct CO in MR', 'pct_CO_in__TL', 'pct CO in MG',
    'pts in alp', 'pts in nat pioneer', 'pts in low dry', 'pts in mont dry', 'pts in subalpine',
    'pts in low mes', 'pts in mont mes', 'pts in low wet',
    'pts in mont wet', 'lavaflows MR pts', 'lavaflows TL pts', 'lavaflows MG pts', 'ung_free MR pts', 'ung_free TL pts', 'ung_free MG pts',
    'protected MR pts', 'protected TL pts', 'protected MG pts','Total_zone_edge_biome', 'Total_zone_core_biome', 'Total_zone_slr', 'Total_zone_lava_flows',
    'Total_Zone_ugly_hab', 'Total_Zone_bad_hab', 'Total_Zone_good_hab', 'Total_zone_protected_area',
    'Total_Zones_ungfree', 'Total_zone_topo_complexity',
    'Total_zone_mean_ppt_gradient', 'Total_zone_mean_inv_suitability',
    'Total_zone_fragmentation'] #'pts in NA veg',  #'MRzone_biome', 'TLzone_biome', 'MGzone_biome',
Spp_data.append(Sp_data)
def save_temp_csv_data(temp_data, opath):
    #opath=r"%sDBFs/%s_%s.csv" %(resultsdir, Sp_index, name)
    ofile = open(opath, 'wb')
    writer = csv.writer(ofile, dialect='excel')
    writer.writerow(temp_data)
    ofile.close()
    return

#def div(i,j):
#    if j==0:
#        res='NA'
#    else:
#        res=i/j
#    return res

def multpl(i,j):
    if j==0:
        res=0
    else:
        res=i*j
    return res

def nanconv(i):
    if not isinstance(i, basestring):
        if numpy.isnan(i):
            i='NA'
    return i

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

#CAO_data_dir=r"C:/Users/lfortini/Data/VA data/CAO/"
CAO_data_dir=r"Y:/PICCC_data/VA data/CAO/"
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
spp_alien_hab_compatibility=column['Alien_hab_comp']

###VA_metric_index
##csvname="%sVA_metric_index.csv" %(CAO_data_dir)
###hab_req_file = csv.reader(csvname)
##f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
##reader = csv.reader(f)
##headers = reader.next()
##column = {}
##for h in headers:
##    column[h] = []
##for row in reader:
##    for h, v in zip(headers, row):
##        column[h].append(v)
##
##metric=column['metric']
##start_metric=column['start']
##end_metric=column['end']
##length_metric=column['length']
sp_code_st='0004'
for sp_code_st in del_terms:
    resultsdir=resultsdir0+sp_code_st+"/"
    if bioreg_subset==1:
        sp_code=str(int(sp_code_st[:-5]))
    else:
        sp_code=str(int(sp_code_st)) #get rid of extra zeros

    try:
        Sp_index=all_sp_codes.index(sp_code)
        sp_name=New_sp_names[Sp_index]
    except ValueError:
        sp_name="Unkown"

    try:
        opath="%sDBFs/calc_area_CCE%s.csv" %(resultsdir,sp_code_st)
        jnk=load_temp_csv_float_data(opath)
        area_CCE=jnk[0]
    except:
        area_CCE='NA'

    #CALC FCE TOTAL AREA
    try:
        opath="%sDBFs/calc_area_FCE%s.csv" %(resultsdir,sp_code_st)
        jnk=load_temp_csv_float_data(opath)
        area_FCE=jnk[0]
    except:
        area_FCE='NA'
    #CALC CCE-FCE
    try:
        area_dif=area_CCE-area_FCE
    except:
        area_dif='NA'

    #CALC CCE-FCE
    try:
        prop_area_change=area_FCE/area_CCE
    except:
        prop_area_change='NA'

    try:
        if prop_area_change<=0.01:
            winkout=1
        else:
            winkout=0
    except:
        winkout='NA'

    try:
        opath="%sDBFs/FCE_distance_%s.csv" %(resultsdir,sp_code_st)
        jnk=load_temp_csv_float_data(opath)
        FCE_distance=jnk[0]
        #try:
        #    FCE_distance=eval(FCE_distance)
        #except:
        #    FCE_distance='wink out'
    except:
        FCE_distance='NA'

    try:
        opath="%sDBFs/CCE_elev_%s.csv" %(resultsdir,sp_code_st)
        jnk=load_temp_csv_float_data(opath)
        CCE_mean_elev=jnk[0]
        CCE_min_elev=jnk[1]
        CCE_max_elev=jnk[2]
        CCE_stdev_elev=jnk[3]
    except:
        CCE_mean_elev='NA'
        CCE_min_elev='NA'
        CCE_max_elev='NA'
        CCE_stdev_elev='NA'

    try:
        opath="%sDBFs/FCE_elev_%s.csv" %(resultsdir,sp_code_st)
        jnk=load_temp_csv_float_data(opath)
        FCE_mean_elev=jnk[0]
        FCE_min_elev=jnk[1]
        FCE_max_elev=jnk[2]
        FCE_stdev_elev=jnk[3]
    except:
        FCE_mean_elev='NA'
        FCE_min_elev='NA'
        FCE_max_elev='NA'
        FCE_stdev_elev='NA'

    try:
        opath1="%sDBFs/min_elev_zone_vals_%s.csv" %(resultsdir,sp_code_st)
        opath2="%sDBFs/max_elev_zone_vals_%s.csv" %(resultsdir,sp_code_st)
        min_elev_zone_vals=load_temp_csv_float_data(opath1)
        #min_elev_zone_vals[:]=[eval(x) for x in min_elev_zone_vals]
        max_elev_zone_vals=load_temp_csv_float_data(opath2)
        #max_elev_zone_vals[:]=[eval(x) for x in max_elev_zone_vals]
    except:
        min_elev_zone_vals=['NA']*len(range(14,32))
        max_elev_zone_vals=['NA']*len(range(32,50))

    try:
        #veg_area=Sp_data_temp[50:65]
        opath="%sDBFs/vegtype_areas%s.csv" %(resultsdir,sp_code_st)
        veg_area=load_temp_csv_float_data(opath)
        #veg_area[:]=[eval(x) for x in veg_area]
    except:
        veg_area=['NA']*len(range(50,65))

    try:
        #veg_area=Sp_data_temp[50:65]
        opath="%sDBFs/vegtype_areas_BPS%s.csv" %(resultsdir,sp_code_st)
        veg_area_BPS=load_temp_csv_float_data(opath)
        #veg_area[:]=[eval(x) for x in veg_area]
    except:
        veg_area_BPS=['NA']*len(range(50,65))

    #CCE HABITAT VALUES
    try:
        opath="%sDBFs/all_habitat_areas_HIGAP%s.csv" %(resultsdir,sp_code_st)
        all_habitat_areas_HIGAP=load_temp_csv_float_data(opath)
    except:
        all_habitat_areas_HIGAP=['NA']*7

    try:
        opath="%sDBFs/native_habitat_areas_HIGAP%s.csv" %(resultsdir,sp_code_st)
        native_habitat_areas_HIGAP=load_temp_csv_float_data(opath)
    except:
        native_habitat_areas_HIGAP=['NA']*7

    try:
        opath="%sDBFs/all_habitat_areas_LANDFIRE%s.csv" %(resultsdir,sp_code_st)
        all_habitat_areas_LANDFIRE=load_temp_csv_float_data(opath)
    except:
        all_habitat_areas_LANDFIRE=['NA']*7

    try:
        opath="%sDBFs/native_habitat_areas_LANDFIRE%s.csv" %(resultsdir,sp_code_st)
        native_habitat_areas_LANDFIRE=load_temp_csv_float_data(opath)
    except:
        native_habitat_areas_LANDFIRE=['NA']*7

    try:
        opath="%sDBFs/native_habitat_areas_BPS_LANDFIRE%s.csv" %(resultsdir,sp_code_st)
        native_habitat_areas_BPS_LANDFIRE=load_temp_csv_float_data(opath)
    except:
        native_habitat_areas_BPS_LANDFIRE=['NA']*7

    try:
        opath="%sDBFs/change_in_n_available_habitat%s.csv" %(resultsdir,sp_code_st)
        change_in_n_available_habitat=load_temp_csv_float_data(opath)
    except:
        change_in_n_available_habitat=['NA']*5

    #NEW PLASTICITY METRICS
    try:
        opath="%sDBFs/count_cce_bioreg%s.csv" %(resultsdir,sp_code_st)
        count_cce_bioreg=load_temp_csv_float_data(opath)
    except:
        count_cce_bioreg=['NA']*19

    try:
        opath="%sDBFs/count_cce_bioreg_transition_areas%s.csv" %(resultsdir,sp_code_st)
        count_cce_bioreg_transition_areas=load_temp_csv_float_data(opath)
    except:
        count_cce_bioreg_transition_areas=['NA']*15

    try:
        opath="%sDBFs/cce_precip_interannual_var%s.csv" %(resultsdir,sp_code_st)
        cce_precip_interannual_var=load_temp_csv_float_data(opath)
    except:
        cce_precip_interannual_var=['NA']*4

    #################
    #######END PART 1
    #################

    #CALC RESPONSE ZONE AREA
    try:
        path_zone_index=r"%sDBFs/%s_zone_index.csv" %(resultsdir, sp_code_st)
        path_zone_area=r"%sDBFs/%s_zone_area.csv" %(resultsdir, sp_code_st)
        total_zone_area=load_temp_csv_float_data(path_zone_area)
    except:
        total_zone_area=['NA']*3

    try:
        if isinstance(total_zone_area[1], str)==False:
            total_zone_area_weights=total_zone_area[0:3]
            total_zone_area_weights[:]=[(x/sum(total_zone_area)) for x in total_zone_area_weights]
    except:
        total_zone_area_weights=['NA']*3

    try:
        if isinstance(total_zone_area[1], str)==False:
            if area_CCE*0.01<=total_zone_area[1]:
                CE_overlap=1
            else:
                CE_overlap=0
        else:
            CE_overlap=0
    except:
        CE_overlap='NA'

    try:
        if use_effective_CE_mask:
            opath=r"%sDBFs/%s_eff_zone_area.csv" %(resultsdir, sp_code_st)
            zone_area= load_temp_csv_float_data(opath)
        else:
            zone_area=total_zone_area
    except:
        zone_area=['NA']*3

    try:
        if isinstance(zone_area[1], str)==False:
            zone_area_weights=zone_area[0:3]
            zone_area_weights[:]=[(x/sum(zone_area)) for x in zone_area_weights]
    except:
        zone_area_weights=['NA']*3

    ##RESPONSE ZONES ARE DEFINED ABOVE###
##    try:
##        opath=r"%sDBFs/%s_zone_compatible_habitat.csv" %(resultsdir, sp_code_st)
##        f = open(opath, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
##        reader = csv.reader(f)
##        zone_compatible_habitat= reader.next()
##        zone_compatible_habitat[:]=[float(x) for x in zone_compatible_habitat]
##    except:
##        zone_compatible_habitat=['NA']*3

    #FRAGMENTATION
    try:
        Sp_index=hab_sp_code.index(str(sp_code))
        Sp_alien_hab_comp=spp_alien_hab_compatibility[Sp_index]
    except:
        Sp_index='NA'
        Sp_alien_hab_comp='NA'

    try:
        opath=r"%sDBFs/%s_zone_fragmentation.csv" %(resultsdir, sp_code_st)
        jnk=load_temp_csv_data(opath)
        biome_index= jnk[0]
        bioreg_max_biome_elev= eval(jnk[1])
        bioreg_max_biome_elev[:]=[float(x) for x in bioreg_max_biome_elev]
        zone_edge_biome= eval(jnk[2])
        #zone_edge_biome[:]=[float(x) for x in zone_edge_biome]
        #zone_edge_biome=[i/j for i, j in zip(zone_edge_biome,zone_area)]
        zone_edge_biome=[numpy.float64(i)/j for i, j in zip(zone_edge_biome,zone_area)]
        zone_core_biome0=eval(jnk[3])
        zone_core_biome=[numpy.float64(i)/j for i, j in zip(zone_core_biome0,zone_area)]
        zone_fragmentation=[j/(j+i) for i, j in zip(zone_core_biome,zone_edge_biome)]
        Total_zone_edge_biome=sum(multpl(i,j) for i, j in zip(zone_edge_biome,zone_area_weights))
        Total_zone_core_biome=sum(multpl(i,j) for i, j in zip(zone_core_biome,zone_area_weights))
        Total_zone_fragmentation=sum(multpl(i,j) for i, j in zip(zone_fragmentation,zone_area_weights))
    except:
        biome_index= 'NA'
        bioreg_max_biome_elev= ['NA']*18
        zone_edge_biome= ['NA']*3
        zone_core_biome= ['NA']*3
        zone_fragmentation= ['NA']*3
        #zone_compatible_biome=['NA']*3
        Total_zone_edge_biome='NA'
        Total_zone_core_biome='NA'
        Total_zone_fragmentation='NA'
    #Distance from top of island metric
    try:
        if area_FCE>0:
            opath="%sDBFs/%s_prox_to_bioregion_caps.csv" %(resultsdir, sp_code_st)
            jnk=load_temp_csv_float_data(opath)
            n_bioreg_in_FCE=jnk[0]
            n_bioreg_near_top=jnk[1]
            prop_bioreg_near_top=n_bioreg_near_top/n_bioreg_in_FCE
        else:
            n_bioreg_in_FCE=0
            n_bioreg_near_top=0
            prop_bioreg_near_top=1

    except:
        n_bioreg_in_FCE='NA'
        n_bioreg_near_top='NA'
        prop_bioreg_near_top='NA'

    #SLR
    try:
        opath=r"%sDBFs/%s_zone_slr.csv" %(resultsdir, sp_code_st)
        zone_slr= load_temp_csv_float_data(opath)
        zone_slr=[numpy.float64(i)/j for i, j in zip(zone_slr,total_zone_area)]
        Total_zone_slr=sum(multpl(i,j) for i, j in zip(zone_slr,total_zone_area_weights))
    except:
        Total_zone_slr='NA'
        zone_slr=['NA']*3

    #CALCULATE habitat area within young lava flows
    try:
        Sp_index=hab_sp_code.index(str(sp_code))
        Sp_pioneer_status=spp_pioneer_data[Sp_index]
    except:
        Sp_index='NA'
        Sp_pioneer_status='NA'

    try:
        opath=r"%sDBFs/%s_zone_lava_flows.csv" %(resultsdir, sp_code_st)
        zone_lava_flows= load_temp_csv_float_data(opath)
        zone_lava_flows=[numpy.float64(i)/j for i, j in zip(zone_lava_flows,total_zone_area)]
        Total_zone_lava_flows=sum(multpl(i,j) for i, j in zip(zone_lava_flows,total_zone_area_weights))
    except:
        zone_lava_flows=['NA']*3
        Total_zone_lava_flows='NA'

    try:
        opath=r"%sDBFs/%s_Zone_ugly_hab.csv" %(resultsdir, sp_code_st)
        Zone_ugly_hab= load_temp_csv_float_data(opath)
        Zone_ugly_hab=[numpy.float64(i)/j for i, j in zip(Zone_ugly_hab,total_zone_area)]
        Total_Zone_ugly_hab=sum(multpl(i,j) for i, j in zip(Zone_ugly_hab,total_zone_area_weights))
    except:
        Zone_ugly_hab=['NA']*3
        Total_Zone_ugly_hab='NA'

    try:
        opath=r"%sDBFs/%s_Zone_bad_hab.csv" %(resultsdir, sp_code_st)
        Zone_bad_hab= load_temp_csv_float_data(opath)
        Zone_bad_hab=[numpy.float64(i)/j for i, j in zip(Zone_bad_hab,zone_area)]
        Total_Zone_bad_hab=sum(multpl(i,j) for i, j in zip(Zone_bad_hab,zone_area_weights))
    except:
        Zone_bad_hab=['NA']*3
        Total_Zone_bad_hab='NA'

    try:
        opath=r"%sDBFs/%s_Zone_good_hab.csv" %(resultsdir, sp_code_st)
        Zone_good_hab= load_temp_csv_float_data(opath)
        Zone_good_hab=[numpy.float64(i)/j for i, j in zip(Zone_good_hab,zone_area)]
        Total_Zone_good_hab=sum(multpl(i,j) for i, j in zip(Zone_good_hab,zone_area_weights))
    except:
        Zone_good_hab=['NA']*3
        Total_Zone_good_hab='NA'

    #Effective zone area
    try:
        opath=r"%sDBFs/%s_eff_nonpioneer_zone_area.csv" %(resultsdir, sp_code_st)
        zone_eff_nonpioneer= load_temp_csv_float_data(opath)
    except:
        zone_eff_nonpioneer=['NA']*3

    #Effective zone area
    try:
        opath=r"%sDBFs/%s_eff_pioneer_zone_area.csv" %(resultsdir, sp_code_st)
        zone_eff_pioneer= load_temp_csv_float_data(opath)
    except:
        zone_eff_pioneer=['NA']*3

    #zone_eff_hab_qual
    try:
        opath=r"%sDBFs/%s_eff_hab_qual_zone_area.csv" %(resultsdir, sp_code_st)
        zone_eff_hab_qual= load_temp_csv_float_data(opath)
    except:
        zone_eff_hab_qual=['NA']*3

    #PROTECTED AREA
    try:
        opath=r"%sDBFs/%s_protected_area.csv" %(resultsdir, sp_code_st)
        zone_protected_area= load_temp_csv_float_data(opath)
        zone_protected_area=[numpy.float64(i)/j for i, j in zip(zone_protected_area,zone_area)]
        Total_zone_protected_area=sum(multpl(i,j) for i, j in zip(zone_protected_area,zone_area_weights))
    except:
        zone_protected_area=['NA']*3
        Total_zone_protected_area='NA'
    #UNGULATE FREE AREA
    try:
        opath=r"%sDBFs/%s_Ung_free_areas.csv" %(resultsdir, sp_code_st)
        Zones_ungfree= load_temp_csv_float_data(opath)
        Zones_ungfree=[numpy.float64(i)/j for i, j in zip(Zones_ungfree,zone_area)]
        Total_Zones_ungfree=sum(multpl(i,j) for i, j in zip(Zones_ungfree,zone_area_weights))
    except:
        Zones_ungfree=['NA']*3
        Total_Zones_ungfree='NA'

    #CALC TOPO COMPLEXITY
    try:
        opath4=r"%sDBFs/%s_zone_topo_complexity.csv" %(resultsdir, sp_code_st)

        zone_topo_complexity= load_temp_csv_float_data(opath4)
        #Zone_slope_cv=[numpy.float64(i)/j for i, j in zip(Zone_slope_std,zone_topo_complexity)]
        Total_zone_topo_complexity=sum(multpl(i,j) for i, j in zip(zone_topo_complexity,zone_area_weights))
        #Total_Zone_slope_cv=sum(multpl(i,j) for i, j in zip(Zone_slope_cv,zone_area_weights))

    except:
        zone_topo_complexity= ['NA']*3
        Total_zone_topo_complexity='NA'

##    #CALC SLOPE QUANTILES
##    try:
##        opath=r"%sDBFs/%s_Zone_slope_max.csv" %(resultsdir, sp_code_st)
##        opath2=r"%sDBFs/%s_Zone_slope_min.csv" %(resultsdir, sp_code_st)
##        opath3=r"%sDBFs/%s_Zone_slope_std.csv" %(resultsdir, sp_code_st)
##        opath4=r"%sDBFs/%s_Zone_slope_median.csv" %(resultsdir, sp_code_st)
##
##        Zone_slope_median= load_temp_csv_float_data(opath4)
##        Zone_slope_std= load_temp_csv_float_data(opath3)
##        Zone_slope_min= load_temp_csv_float_data(opath2)
##        Zone_slope_max= load_temp_csv_float_data(opath)
##        Zone_slope_cv=[numpy.float64(i)/j for i, j in zip(Zone_slope_std,Zone_slope_median)]
##        Total_Zone_slope_median=sum(multpl(i,j) for i, j in zip(Zone_slope_median,zone_area_weights))
##        Total_Zone_slope_std=sum(multpl(i,j) for i, j in zip(Zone_slope_std,zone_area_weights))
##        Total_Zone_slope_min=sum(multpl(i,j) for i, j in zip(Zone_slope_min,zone_area_weights))
##        Total_Zone_slope_max=sum(multpl(i,j) for i, j in zip(Zone_slope_max,zone_area_weights))
##        Total_Zone_slope_cv=sum(multpl(i,j) for i, j in zip(Zone_slope_cv,zone_area_weights))
##
##    except:
##        Zone_slope_median= ['NA']*3
##        Zone_slope_std= ['NA']*3
##        Zone_slope_min= ['NA']*3
##        Zone_slope_max= ['NA']*3
##        Zone_slope_cv= ['NA']*3
##        Total_Zone_slope_median='NA'
##        Total_Zone_slope_std='NA'
##        Total_Zone_slope_min='NA'
##        Total_Zone_slope_max='NA'
##        Total_Zone_slope_cv='NA'
##
##    #CALC CCE ASPECT MEAN, STDE
##    try:
##        opath1=r"%sDBFs/%s_zone_aspect_mean.csv" %(resultsdir, sp_code_st)
##        opath2=r"%sDBFs/%s_zone_aspect_std.csv" %(resultsdir, sp_code_st)
##        zone_aspect_mean= load_temp_csv_float_data(opath1)
##        zone_aspect_std= load_temp_csv_float_data(opath2)
##        Total_zone_aspect_mean=sum(multpl(i,j) for i, j in zip(zone_aspect_mean,zone_area_weights))
##        Total_zone_aspect_std=sum(multpl(i,j) for i, j in zip(zone_aspect_std,zone_area_weights))
##    except:
##        zone_aspect_mean= ['NA']*3
##        zone_aspect_std= ['NA']*3
##        Total_zone_aspect_mean='NA'
##        Total_zone_aspect_std='NA'
##
##    try:
##        opath1=r"%sDBFs/%s_zone_aspect_std.csv" %(resultsdir, sp_code_st)
##        zone_aspect_std= load_temp_csv_float_data(opath1)
##        Total_zone_aspect_std=sum(multpl(i,j) for i, j in zip(zone_aspect_std,zone_area_weights))
##    except:
##        zone_aspect_std=['NA']*3
##        Total_zone_aspect_std='NA'
    #calc average precipitation gradient within zones:
    try:
        opath=r"%sDBFs/%s_zone_ppt_gradient.csv" %(resultsdir, sp_code_st)
        zone_mean_ppt_gradient= load_temp_csv_float_data(opath)
        Total_zone_mean_ppt_gradient=sum(multpl(i,j) for i, j in zip(zone_mean_ppt_gradient,zone_area_weights))
    except:
        zone_mean_ppt_gradient=['NA']*3
        Total_zone_mean_ppt_gradient='NA'
    #calc average invasive suitability within zones:
    try:
        opath=r"%sDBFs/%s_zone_inv_suitability.csv" %(resultsdir, sp_code_st)
        zone_mean_inv_suitability= load_temp_csv_float_data(opath)
        Total_zone_mean_inv_suitability=sum(multpl(i,j) for i, j in zip(zone_mean_inv_suitability,zone_area_weights))
    except:
        zone_mean_inv_suitability=['NA']*3
        Total_zone_mean_inv_suitability='NA'

    #TABULATE CURRENT OCCUPANCY WITHIN ZONES
    try:
        opath10=r"%sDBFs/%s_zone_CO.csv" %(resultsdir, sp_code_st)
        opath20=r"%sDBFs/%s_veg_zone_CO.csv" %(resultsdir, sp_code_st)
        jnk=load_temp_csv_float_data(opath10)
        total_CO_points=jnk[0]
        total_zone_pts=jnk[1]
        if total_zone_pts>3:
            zone_CO=jnk[2:]
        else:
            zone_CO=['NA']*3
        veg_zone_CO=load_temp_csv_float_data(opath20)
    except:
        total_CO_points='NA'
        total_zone_pts='NA'
        zone_CO=['NA']*3
        veg_zone_CO=['NA']*9

    #lava flow tabulation
    try:
        opath=r"%sDBFs/%s_lava_flow_CO.csv" %(resultsdir, sp_code_st)
        lava_flow_zone_CO=load_temp_csv_float_data(opath)
    except:
        lava_flow_zone_CO=['NA']*3

    #Ung free tabulation
    try:
        opath=r"%sDBFs/%s_ung_free_zone_CO.csv" %(resultsdir, sp_code_st)
        ung_free_zone_CO=load_temp_csv_float_data(opath)
    except:
        ung_free_zone_CO=['NA']*3

    #Protected area tabulation
    try:
        opath=r"%sDBFs/%s_protected_zone_CO.csv" %(resultsdir, sp_code_st)
        protected_zone_CO=load_temp_csv_float_data(opath)
    except:
        protected_zone_CO=['NA']*3

    #SAVE CALCULATION OUTPUT TO MATRIX
    Sp_data=[]
    #j=i+1; Sp_data.append(sp_code)
    Sp_data.append(sp_name)
    Sp_data.append(sp_code_st)
    Sp_data.append(area_CCE)
    Sp_data.append(area_FCE)
    Sp_data.append(area_dif)
    Sp_data.append(prop_area_change)
    Sp_data.append(winkout)
    Sp_data.append(CE_overlap)
    Sp_data.append(FCE_distance)
    Sp_data.append(CCE_mean_elev)
    Sp_data.append(CCE_min_elev)
    Sp_data.append(CCE_max_elev)
    Sp_data.append(CCE_stdev_elev)
    Sp_data.append(FCE_mean_elev)
    Sp_data.append(FCE_min_elev)
    Sp_data.append(FCE_max_elev)
    Sp_data.append(FCE_stdev_elev)
    Sp_data.extend(min_elev_zone_vals)
    Sp_data.extend(max_elev_zone_vals)
    Sp_data.extend(bioreg_max_biome_elev)
    Sp_data.append(biome_index)
    Sp_data.append(n_bioreg_in_FCE)
    Sp_data.append(n_bioreg_near_top)
    Sp_data.append(prop_bioreg_near_top)
    Sp_data.extend(veg_area)
    Sp_data.extend(veg_area_BPS)
    Sp_data.extend(all_habitat_areas_HIGAP)
    Sp_data.extend(native_habitat_areas_HIGAP)
    Sp_data.extend(all_habitat_areas_LANDFIRE)
    Sp_data.extend(native_habitat_areas_LANDFIRE)
    Sp_data.extend(native_habitat_areas_BPS_LANDFIRE)
    Sp_data.extend(change_in_n_available_habitat)
    Sp_data.extend(count_cce_bioreg)
    Sp_data.extend(count_cce_bioreg_transition_areas)
    Sp_data.extend(cce_precip_interannual_var)
    Sp_data.extend(total_zone_area)
    Sp_data.extend(zone_eff_nonpioneer)
    Sp_data.extend(zone_eff_pioneer)
    Sp_data.extend(zone_eff_hab_qual)
##    Sp_data.extend(zone_compatible_habitat)
    Sp_data.append(Sp_pioneer_status)
    Sp_data.extend(zone_lava_flows)
    Sp_data.extend(Zone_ugly_hab)
    Sp_data.extend(Zone_bad_hab)
    Sp_data.extend(Zone_good_hab)
    Sp_data.extend(zone_protected_area)
    Sp_data.extend(Zones_ungfree)
    Sp_data.append(Sp_alien_hab_comp)
    Sp_data.extend(zone_edge_biome)
    Sp_data.extend(zone_core_biome)
    Sp_data.extend(zone_fragmentation)
    #Sp_data.append(zone_compatible_biome)
    Sp_data.extend(zone_slr)
    Sp_data.extend(zone_mean_ppt_gradient)
    Sp_data.extend(zone_mean_inv_suitability)
    Sp_data.extend(zone_topo_complexity)
##    Sp_data.append(Zone_slope_median)
##    Sp_data.append(Zone_slope_min)
##    Sp_data.append(Zone_slope_max)
##    Sp_data.append(Zone_slope_std)
##    Sp_data.append(Zone_slope_cv)
##    Sp_data.append(zone_aspect_mean)
##    Sp_data.append(zone_aspect_std)
    Sp_data.append(total_CO_points)
    Sp_data.append(total_zone_pts)
    Sp_data.extend(zone_CO)
    Sp_data.extend(veg_zone_CO)
    Sp_data.extend(lava_flow_zone_CO)
    Sp_data.extend(ung_free_zone_CO)
    Sp_data.extend(protected_zone_CO)

    #Total_zone_edge_biome=round(Total_zone_edge_biome,4)
    Sp_data.append(Total_zone_edge_biome)
    Sp_data.append(Total_zone_core_biome)
    Sp_data.append(Total_zone_slr)
    Sp_data.append(Total_zone_lava_flows)
    Sp_data.append(Total_Zone_ugly_hab)
    Sp_data.append(Total_Zone_bad_hab)
    Sp_data.append(Total_Zone_good_hab)
    Sp_data.append(Total_zone_protected_area)
    Sp_data.append(Total_Zones_ungfree)
    Sp_data.append(Total_zone_topo_complexity)
##    Sp_data.append([Total_Zone_slope_median])
##    Sp_data.append([Total_Zone_slope_std])
##    Sp_data.append([Total_Zone_slope_min])
##    Sp_data.append([Total_Zone_slope_max])
##    Sp_data.append([Total_zone_aspect_mean])
##    Sp_data.append([Total_zone_aspect_std])
    Sp_data.append(Total_zone_mean_ppt_gradient)
    Sp_data.append(Total_zone_mean_inv_suitability)
    Sp_data.append(Total_zone_fragmentation)
##    Sp_data.append([Total_Zone_slope_cv])

    Sp_data=[nanconv(i) for i in Sp_data]

    Spp_data.append(Sp_data)

import os.path
opath=r"%sall_spp_values.csv" %(datadir)
#if arcpy.Exists(opath): #delete previous version of output file if it exists
if os.path.isfile(opath): #delete previous version of output file if it exists
    os.remove(opath)
else:
    pass
ofile = open(opath, 'wb')
writer = csv.writer(ofile, dialect='excel')
for i in range(len(Spp_data)):
    writer.writerow(Spp_data[i])
ofile.close()

