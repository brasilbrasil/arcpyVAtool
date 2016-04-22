import os
import arcpy
import arcpy.sa
import arcgisscripting
#from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/
from arcpy import env

wd="Y:/PICCC_data/VA data/landscape/"
arcpy.env.overwriteOutput = True
arcpy.env.workspace = wd
arcpy.env.compression = "LZW"
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")

bioreg=arcpy.Shapefile("bioregions.shp")
inFeatureClass="bioregions.shp"
outFeatureClass="bioregions_boundaries.shp"
arcpy.PolygonToLine_management(inFeatureClass, outFeatureClass, "IDENTIFY_NEIGHBORS")

inFeatureClass="bioregions_boundaries.shp"
outFeatureClass="bioregions_boundaries_buffer.shp"
arcpy.Buffer_analysis(inFeatureClass, outFeatureClass, "1000", "FULL", "ROUND", "LIST", ["LEFT_FID", "RIGHT_FID"])

#here I manually edited the polygon to make add a column with unique IDs for each unique
#bioreg transition
arcpy.AddField_management(outFeatureClass, "Boundary", "SHORT", "", "", "", "", "")
#next step I created shapefile with subset of boundaries that excluded all coastal boundaries
#then on boundary column I coded the different boundaries using the "bioregions_boundaries_buffer_codes.csv"

inFeatureClass="bioregions_boundaries_buffer_no_coast.shp"
outRasterClass="bioregions_boundaries_buffer_no_coastal.tif"
arcpy.PolygonToRaster_conversion(inFeatureClass, "Boundary", outRasterClass,
                                 "CELL_CENTER", "", 250)

arcpy.CheckInExtension("Spatial") # Check in the 3D Analyst extension so other users can access it

