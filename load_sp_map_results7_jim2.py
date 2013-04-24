#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#must have island map open
#must have option to show temp output on map; if multiple frames, click on properties and fix scale and extent so redrawing does not screw with map layout

#USER INPUT
resultsdir=r"Y:/PICCC_analysis/tempmap/" #where climate envelopes are located  
CAO_data_dir=r"Y:/PICCC_analysis/tempmap/CAO/" #point data, spp_name_synonyms.csv
ref_lyr_dir=r"Y:/PICCC_analysis/tempmap/reflyrs/"
print_map_output=0
#sp_codes=["0710", "1081", "0384", "0499", "0260", "1031", "0328"]
sp_codes=["0003"]#, "0664", "0502", "0134"] #"0664", "0502", "0134", "0671"
overwrite_res=1

sp_temps=range(253,1087)
del_terms=[]
bioreg_subset=0
for sp_temp in sp_temps:
	sp_code=str(sp_temp)
	lspcode=len(sp_code)
	new_sp_code=(4-lspcode)*'0'+sp_code
	if bioreg_subset==1:
            new_sp_code=new_sp_code+"_trim"
        del_terms.append(new_sp_code)
#sp_codes=del_terms
#sp_codes=reversed(sp_codes)

#START UNDERHOOD


import arcpy, os, string, logging, datetime
from arcpy import env
import csv
import time
arcpy.env.overwriteOutput = True
arcpy.env.workspace = resultsdir
mxd=arcpy.mapping.MapDocument("CURRENT")
#open Island extent raster or dem raster
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
sp_code_st="0003"	
output_text_ID="test"
names_to_load1=["current_envelope", "all_points"]
#XXXXXXXXXXXXXXXXXXX
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
	current_envelope='%sCEs/CCE%s.tif' %(resultsdir,sp_code_st)
	all_points=r"%scorrected_CO_data4_merged_and_filtered.shp" %(CAO_data_dir)
	
	To_load0=[current_envelope, all_points]
	names_to_load0=["current_envelope", "all_points"]
	ref_layers0=["ref_lyr_protected_zones_map1.lyr", "ref_lyr_CEP.lyr"] #
	
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
				sourceLayer0=ref_lyr_dir+ref_layers[i]
				arcpy.MakeRasterLayer_management(fc_pluspath, fc_rl_temp, "#", "", "#")
		
			if fc[-4:]==".shp":
				fc_lyr=fc[:-4] +"_temp.lyr" 
				fc_pluspath=fc
				fc_rl_temp=names_to_load[i] #fc[:-4]+"temp"
				sourceLayer0=ref_lyr_dir+ref_layers[i]
				expr=""" "sp_name" = '%s' """ %(sp_name)
				arcpy.MakeFeatureLayer_management (fc_pluspath, fc_rl_temp, expr, "", "#")
				
				extent = fc_pluspath.getExtent()
				df.extent = extent

			arcpy.ApplySymbologyFromLayer_management(fc_rl_temp, sourceLayer0)
				
		
		#dataframe = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]	
		#df.zoomToSelectedFeatures()
		#fc_pluspath.zoomToSelectedFeatures()
		
		arcpy.RefreshActiveView() 
		arcpy.RefreshTOC()
	

	
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
	
	names_to_load1=["current_envelope", "all_points"] #, "Points beyond response zone" 
	output_text_ID = "points_and_current_CE"
	print_map(names_to_load1, output_text_ID, sp_code_st, resultsdir, overwrite_res)
	
	t1 = time.time()
	print 'It took %i seconds to rrun code for species %s' %(int(t1-t00), sp_code_st)
 
