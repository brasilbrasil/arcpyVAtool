##this code is not finished trying to do it by shapefile means
#USER INPUT
search_term="CCE"
rootdir=r"Y:/VA data/CEs/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)

#END USER INPUT
ensemble_zone_raster_dir="Y:/PICCC_analysis/plant_landscape_va_results/ensemble_zone_maps/all combined/"
shapefile_file="Y:/PICCC_analysis/DLNR_plantVA/shapefiles/DOFAW.shp"
shapefile_col="OBJECTID"
#raster_files=["z1_1059_partial_ensemble.tif", "z2_1059_partial_ensemble.tif",
#"z3_1059_partial_ensemble.tif", "CCE_ensemble.tif", "FCE_ensemble.tif", "quantwinkout_54_map_sp1081.tif",
raster_files=["no_overlap_161_1081.tif"]
#raster_names=["Micro_refugia", "Tolerate", "Migrate", "Current", "Future", "Winkout", "No_overlap"]
raster_names=["No_overlap"]
area_type="DOFAW_areas"

results_dir="Y:/PICCC_analysis/DLNR_plantVA/results/mean_responses/"
import os
import arcpy
import csv

from types import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"

#if arcpy.CheckExtension("Spatial") == "Available":
#	arcpy.CheckOutExtension("Spatial")

for i in range(len(raster_files)):
    in_value_raster=raster_files[i]
    raster_name=raster_names[i]
    tmp_table=results_dir+area_type+" "+ raster_name + " zone stats.dbf"
    out_table=results_dir+area_type+" "+ raster_name + " zone stats.csv"
    arcpy.sa.ZonalStatisticsAsTable (shapefile_file, shapefile_col, in_value_raster, tmp_table)

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

#arcpy.CheckInExtension("Spatial")
