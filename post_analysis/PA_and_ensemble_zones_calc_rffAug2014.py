##this code is not finished trying to do it by shapefile means
#USER INPUT
#search_term="CCE"
rootdir=r"Y:/VA data/CEs/"
ensemble_zone_raster_dir="Y:/PICCC_analysis/plant_landscape_va_results/ensemble_zone_maps/NC_Nex_vuln_quantile_maps/"
shapefile_file0="Y:/PICCC_analysis/DLNR_plantVA/RFF request Aug 2014/shapefiles/CIP FY 16 & 17 Request.shp"
shapefile_col="AreaNumber"
raster_files=["NC_Nex_HiVul_CCE_297_sp1081.tif", "NC_Nex_HiVul_FCE_297_sp1081.tif",
"297_NC_Nex_HiVul_zone2_partial_ensemble.tif", "NC_Nex_wFCE_955_sp1085.tif",
"956_NC_Nex_wFCE_zone2_partial_ensemble.tif"]
raster_names=["NC_Nex_HiVul_CCE", "NC_Nex_HiVul_FCE", "NC_Nex_HiVul_zone2", "NC_Nex_FCE",
"NC_Nex_FCE_zone2"]
fieldNames=["HiVul_CCE", "HiVul_FCE", "HiVul_Z2", "FCE", "FCE_Z2"]
area_type="Fencing_areas_FY16_17"
results_dir="Y:/PICCC_analysis/DLNR_plantVA/RFF request Aug 2014/results/"

#END USER INPUT
import os
import arcpy
import csv

from types import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"

if arcpy.CheckExtension("Spatial") == "Available":
	arcpy.CheckOutExtension("Spatial")

shapefile_file=shapefile_file0[:-4]+"_withVAdata.shp"
arcpy.Copy_management(shapefile_file0, shapefile_file)

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
