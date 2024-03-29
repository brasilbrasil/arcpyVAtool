##this code is not finished trying to do it by shapefile means
#USER INPUT
#search_term="CCE"
rootdir=r"Y:/VA data/CEs/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)
ensemble_zone_raster_dir="Y:/PICCC_analysis/plant_landscape_va_results/ensemble_zone_maps/NC_Nex_vuln_quantile_maps/"
shapefile_file0="Y:/PICCC_analysis/DLNR_plantVA/FWS_kauai_analysis/shapefiles/Kauai_MgmtUnits_20140505_final.shp"
shapefile_col="FID" #"AreaNumber"
#raster_files=["z1_1059_partial_ensemble.tif", "z2_1059_partial_ensemble.tif",
#"z3_1059_partial_ensemble.tif", "CCE_ensemble.tif", "FCE_ensemble.tif", "quantwinkout_54_map_sp1081.tif",
raster_files=["NC_Nex_HiVul_CCE_297_sp1081.tif", "NC_Nex_HiVul_FCE_297_sp1081.tif",
"297_NC_Nex_HiVul_zone2_partial_ensemble.tif", "NC_Nex_NO_101_sp1081.tif",
"NC_Nex_winkout_35_sp1081.tif", "Modelled_richness_delta_truncated.tif",
"Modelled_richness_relative_delta_truncated.tif", "956_NC_Nex_wFCE_zone2_partial_ensemble.tif"]
#raster_names=["Micro_refugia", "Tolerate", "Migrate", "Current", "Future", "Winkout", "No_overlap"]
raster_names=["NC_Nex_HiVul_CCE", "NC_Nex_HiVul_FCE", "NC_Nex_HiVul_zone2", "NC_Nex_NO_CCE", "NC_Nex_winkout_CCE",
"Richness_delta", "Rel_richness_delta", "NC_Nex_zone2"]
fieldNames=["HiVul_CCE", "HiVul_FCE", "HiVul_Z2", "NO_CCE", "WO_CCE", "R_delta", "Rel_R_dt", "NcNex_Tol"]
area_type="Kauai_FWS_MUs"
results_dir="Y:/PICCC_analysis/DLNR_plantVA/FWS_kauai_analysis/results/"

#END USER INPUT
import os
import arcpy
import csv

from types import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"

def FieldExist(featureclass, fieldname):
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount == 1):
        return True
    else:
        return False

if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")

shapefile_file=shapefile_file0[:-4]+"_withVAdata.shp"
arcpy.Copy_management(shapefile_file0, shapefile_file)

#create row with exclusive numbers
#fields=arcpy.ListFields(shapefile_file)
if not FieldExist(shapefile_file, "AreaNums"):
    arcpy.AddField_management(shapefile_file, "AreaNums", "SHORT", "", "", "", "", "")

rows = arcpy.UpdateCursor(shapefile_file)
counter = 1
for row in rows:
    #print row.Subunit
    row.AreaNums = counter
    rows.updateRow(row)
    counter += 1
    print row.AreaNums
#remove lock from file
if row:
    del row
if rows:
    del rows
import gc
gc.collect()

for i in range(len(raster_files)):
    in_value_raster=ensemble_zone_raster_dir+raster_files[i]
    raster_name=raster_names[i]
    fieldName=fieldNames[i]
    tmp_table=results_dir+area_type+" "+ raster_name + " zone stats.dbf"
    out_table=results_dir+area_type+" "+ raster_name + " zone stats.csv"
    arcpy.sa.ZonalStatisticsAsTable(shapefile_file, shapefile_col, in_value_raster, tmp_table)

    #rename shapefile field!
    #arcpy.AlterField_management(tmp_table, 'MEAN', 'Mean2') #this does not work with shapefiles
    arcpy.JoinField_management(shapefile_file, shapefile_col, tmp_table, shapefile_col, ["Mean"])
    arcpy.AddField_management(shapefile_file, fieldName, "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(shapefile_file, fieldName, "!" +'Mean' + "!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(shapefile_file,'Mean')

    #arcpy.AlterField_management(shapefile_file, 'MEAN', 'Mean2', ) #fieldName
    import arcpy,csv
    table =tmp_table
    outfile = out_table

    #--first lets make a list of all of the fields in the table
    fields = arcpy.ListFields(table)
    field_names = [field.name for field in fields]
    fields = arcpy.ListFields(table)
    field_names = [field.name for field in fields]

    with open(outfile,'wb') as f:
        w = csv.writer(f)
        #--write all field names to the output file
        w.writerow(field_names)

        #--now we make the search cursor that will iterate through the rows of the table
        for row in arcpy.SearchCursor(table):
            field_vals = [row.getValue(field.name) for field in fields]
            w.writerow(field_vals)
        del row

arcpy.CheckInExtension("Spatial")
