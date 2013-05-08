##must have island map open: open Island extent raster or dem raster
#must have option to show temp output on map; if multiple frames, click on properties and fix scale and extent so redrawing does not screw with map layout
#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!

#USER INPUT
rootdir=r"Y:/PICCC_analysis/plant_landscape_va_results/redone_w_eff_CE/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
island="all" #la ha all
landscape_factor_dir=r"Y:/VA data/landscape/" #whichever is data dir, will have to have subfolders: la/DEM/ (where DEM based layers go), gaplandcover/ (where gaplandcov_hi is placed)
CAO_data_dir=r"Y:/VA data/CAO/"
print_map_output=1
#sp_codes=["0664"]#, "0664", "0134", "0357", "0909", "0034", "0789", "0439", "0402", "0032", "0039", "0433", "0825", "0263", "0426", "0499", "0157", "0438", "0028", "1031", "0358", "094", "1084", "0187", "0671", "0991", "0988", "0884", "0909", "0664"]
sp_codes=["0671", "0664"] #"0664", "0502", "0134", "0671"
overwrite_res=1

sp_temps=range(1,1087)
del_terms=[]
bioreg_subset=0
for sp_temp in sp_temps:
	sp_code=str(sp_temp)
	lspcode=len(sp_code)
	new_sp_code=(4-lspcode)*'0'+sp_code
	if bioreg_subset==1:
		new_sp_code=new_sp_code+"_trim"
	del_terms.append(new_sp_code)
sp_codes=del_terms
#sp_codes=reversed(sp_codes)

#START UNDERHOOD
resultsdir=r"%sresults/%s/" %(rootdir, island)

import arcpy, os, string, logging, datetime
from arcpy import env
import csv
import time
arcpy.env.overwriteOutput = True
arcpy.env.workspace = resultsdir
mxd=arcpy.mapping.MapDocument("CURRENT")
arcpy.env.compression = "LZW"
df = arcpy.mapping.ListDataFrames(mxd)[0]
refLayer = arcpy.mapping.ListLayers(mxd, "*", df)[0]

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

def del_layer(layer_name):	
	for df in arcpy.mapping.ListDataFrames(mxd):
	    for lyr in arcpy.mapping.ListLayers(mxd, "", df):
			if lyr.name.lower() == layer_name:
				arcpy.mapping.RemoveLayer(df, lyr)
	return

def print_map(names_to_load1, output_text_ID, sp_code_st, resultsdir, overwrite_res):	
    sp_code=int(sp_code_st)
    sp_code=str(sp_code)
    nf=0
    try:
        Sp_index=all_sp_codes.index(sp_code)
    except ValueError:
        nf=1
        sp_name="Unkown"
    if nf==0:
        sp_name=New_sp_names[Sp_index]
	output_path = resultsdir+ "output_maps/"+ sp_code_st +"_"+ sp_name + "_" + output_text_ID + ".tif"
	if overwrite_res==0 and arcpy.Exists(output_path):
		print sp_code + " calculated already"
	else:
		path=resultsdir+sp_code_st+"/"
		if os.path.exists(path):
			ungfree='%s%s/ungfree_map_%s.tif' %(resultsdir,sp_code_st, sp_code_st)
			protected='%s%s/protected_zones_map_%s.tif' %(resultsdir,sp_code_st, sp_code_st)
			GBU='%s%s/GBU_%s.tif' %(resultsdir, sp_code_st, sp_code_st)
			lava_flows='%s%s/lava_flows_%s.tif' %(resultsdir,sp_code_st, sp_code_st)
			response_zones='%s%s/response_zone_%s.shp' %(resultsdir,sp_code_st, sp_code_st)
			response_zones_raster='%s%s/response_zone_%s.tif' %(resultsdir,sp_code_st, sp_code_st)
			edge_biome=r"%s%s/fragmentation_%s.tif" %(resultsdir,sp_code_st, sp_code_st)
			core_biome=r"%s%s/core_biome_%s.tif" %(resultsdir,sp_code_st, sp_code_st)
			slr=r"%s%s/slr_%s.tif" %(resultsdir,sp_code_st, sp_code_st)
			BP_loc="%s%s/%s_CO_points_outside_zones.shp" %(resultsdir, sp_code_st, sp_code_st)
			#BP_loc="%s%s/%s_sp_CO_points.shp" %(resultsdir, sp_code_st, sp_code_st) #DEBUG!!
			CEP_loc="%s%s/%s_CO_CE_points.shp" %(resultsdir, sp_code_st, sp_code_st)
			response_zones_raster='%s%s/response_zone_%s.tif' %(resultsdir,sp_code_st, sp_code_st)
			fishnet="%s%s/%s_fishnet.shp" %(resultsdir, sp_code_st, sp_code_st)
			
			To_load0=[response_zones, GBU, lava_flows, protected, ungfree, edge_biome, core_biome,
				  slr, BP_loc, CEP_loc, response_zones_raster, fishnet]
			names_to_load0=["Response zones", "Habitat quality", "Lava flows", "Protected areas",
			"Ungulate free areas", "Edge area", "Core biome area",
			"Sea level rise impacted areas", "Points beyond response zone",
			"Current occurence records", "Response zone raster", "Fishnet"]
			ref_layers0=["ref_lyr_response_zone_vec5.lyr", "ref_lyr_hab_qual3.lyr", "ref_lyr_lava_flows.lyr", "ref_lyr_protected_zones_map1.lyr",
			 "ref_lyr_ungulate_protected_areas1.lyr", "ref_lyr_edge.lyr", "ref_lyr_core.lyr",
			 "ref_lyr_slr.lyr", "ref_lyr_BP.lyr", "ref_lyr_CEP.lyr",
			 "ref_lyr_response_zone.lyr", "ref_lyr_fishnet.lyr"]
		
			To_load00=[]
			ref_layers00=[]
			names_to_load00=[]
			for name in names_to_load1:
				jnk=names_to_load0.index(name)    
				To_load00.append(To_load0[jnk])
				ref_layers00.append(ref_layers0[jnk])
				names_to_load00.append(name)
			
			To_load=[]
			ref_layers=[]
			names_to_load=[]
			for i in range(len(To_load00)):
				if arcpy.Exists(To_load00[i]):
					To_load.append(To_load00[i])
					ref_layers.append(ref_layers00[i])
					names_to_load.append(names_to_load00[i])   
			
			for df in arcpy.mapping.ListDataFrames(mxd):
				mxd.activeView = df.name
				for i in range(len(To_load)):
					fc=To_load[i]
					if fc[-4:]==".tif":
						fc_lyr=fc[:-4] +"_temp.lyr" 
						fc_pluspath=fc
						fc_rl_temp=names_to_load[i] #fc[:-4]+"temp"
						sourceLayer0=landscape_factor_dir+ref_layers[i]
						#sourceLayer=arcpy.mapping.Layer(sourceLayer0)  ###MUST MAKE NEW REFERENCE LAYERS!
					
						arcpy.MakeRasterLayer_management(fc_pluspath, fc_rl_temp, "#", "", "#") 
					#arcpy.SaveToLayerFile_management(fc_rl_temp, fc_lyr)
					
					#lyr_file = arcpy.mapping.Layer(fc_lyr)   
					
					#arcpy.mapping.InsertLayer(df, refLayer, lyr_file, "AFTER") # Insert New
					if fc[-4:]==".shp":
						#import shp!
						fc_lyr=fc[:-4] +"_temp.lyr" 
						fc_pluspath=fc
						fc_rl_temp=names_to_load[i] #fc[:-4]+"temp"
						sourceLayer0=landscape_factor_dir+ref_layers[i]
						#sourceLayer=arcpy.mapping.Layer(sourceLayer0)  ###MUST MAKE NEW REFERENCE LAYERS!
						arcpy.MakeFeatureLayer_management (fc_pluspath, fc_rl_temp, "#", "", "#") 
						#pass
					
					arcpy.ApplySymbologyFromLayer_management(fc_rl_temp, sourceLayer0)
				arcpy.RefreshActiveView() 
				arcpy.RefreshTOC()
		else:
			print "no result directory found for ", sp_code_st
		#MUST ZOOM TO AREA WHERE SPECIES OCCUR!
		#    extent = RASTER1.getExtent()
		#    df.extent = extent          
		if len(To_load)>0:
			if print_map_output==1:
				arcpy.mapping.ExportToTIFF(mxd, output_path)			
				for df in arcpy.mapping.ListDataFrames(mxd):       
					mxd.activeView = df.name
					for i in range(len(To_load)):
						fc_rl_temp=names_to_load[i] #fc[:-4]+"temp"
						try:
							del_layer(fc_rl_temp)
						except:
							pass
						try:                
							arcpy.Delete_management(fc_rl_temp)
						except:
							pass
						jnks=arcpy.mapping.ListBrokenDataSources(df)
						for jnk in jnks:
							arcpy.mapping.RemoveLayer(df, jnk)
					
				arcpy.RefreshActiveView() 
				arcpy.RefreshTOC()
			#remove these map layers!!
	return
#sp_code_st = sp_codes[0]
for sp_code_st in sp_codes:
    t0 = time.time()
    t00=t0
	
    names_to_load1=["Response zones", "Current occurence records"] #, "Points beyond response zone" 
    output_text_ID = "VA_C1_map1_zones_and_pts_map2"
    print_map(names_to_load1, output_text_ID, sp_code_st, resultsdir, overwrite_res)
    
    names_to_load1=["Response zones", "Habitat quality"]
    output_text_ID= "VA_C1_map2_hab_qual"
    print_map(names_to_load1, output_text_ID, sp_code_st, resultsdir, overwrite_res)
    
    names_to_load2=["Response zones", "Lava flows", "Sea level rise impacted areas"]
    #names_to_load2=["Response zones", "Sea level rise impacted areas", "Protected areas", "Ungulate free areas", "Lava flows"]
    output_text_ID2 = "VA_C1_map3_hab_qual2"
    print_map(names_to_load2, output_text_ID2, sp_code_st, resultsdir, overwrite_res)
    
    names_to_load1=["Response zones", "Edge area", "Core biome area"] 
    output_text_ID = "VA_C1_map4_zones_and_frag"
    print_map(names_to_load1, output_text_ID, sp_code_st, resultsdir, overwrite_res)
    
    ##names_to_load1=["Response zones", "Current occurence records", "Points beyond response zone", "Fishnet" ] 
    ##output_text_ID = "VA_C1_map1_zones_and_pts_map2_with_net"
    ##print_map(names_to_load1, output_text_ID, sp_code_st, resultsdir, overwrite_res)
    #
    names_to_load2=["Response zones", "Protected areas", "Ungulate free areas"]
    output_text_ID2 = "VA_C1_map5_prot_and_ungfree_areas"
    print_map(names_to_load2, output_text_ID2, sp_code_st, resultsdir, overwrite_res)

    names_to_load2=["Response zones", "Protected areas"]
    output_text_ID2 = "VA_C1_map6_prot_areas"
    print_map(names_to_load2, output_text_ID2, sp_code_st, resultsdir, overwrite_res)
    
    t1 = time.time()
    print 'It took %i seconds to rrun code for species %s' %(int(t1-t00), sp_code_st)
 
