#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!

#USER INPUT
island="all" #la ha all
landscape_factor_dir=r"Y:/VA data/landscape/" #whichever is data dir, will have to have subfolders: la/DEM/ (where DEM based layers go), gaplandcover/ (where gaplandcov_hi is placed)
rootdir=r"Y:/Py_code/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
resultsdir=r"%sresults/%s/" %(rootdir, island)

import os
import arcpy
import arcpy.sa
import csv
import shutil
import sys
from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/
import fnmatch
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"
mxd=arcpy.mapping.MapDocument("CURRENT")

def save_temp_csv_data(temp_data, opath):
	#opath=r"%sDBFs/%s_%s.csv" %(resultsdir, Sp_index, name)
	ofile = open(opath, 'wb')
	writer = csv.writer(ofile, dialect='excel')
	writer.writerow(temp_data)
	ofile.close()
	return

#CALC area in each habitat type
opath="%svegtype_areas_all_islands.csv" %(resultsdir)
veg_types_layer="%slandfire_reclass_wetland_coastal_UTM_8b.tif" %(landscape_factor_dir)
veg_types_layer=arcpy.Raster(veg_types_layer)
loc_COR_CCE=landscape_factor_dir+"all/DEM/all_island_extent.tif"
CCE_temp=arcpy.Raster(loc_COR_CCE)
inRaster = CCE_temp
outname=r"%svegtype_areas_all_islands.dbf" %(resultsdir)
arcpy.sa.TabulateArea(veg_types_layer,"VALUE",veg_types_layer,"VALUE",outname)
db = dbf.Dbf(outname)
#rec=db[0]
veg_area=[0]*14
for ire in range(0,14):
        rec=db[ire]
        jnk="VALUE_%i" %(ire)
        try:
                        area_jnk=rec[jnk]/1000000
                        veg_area[ire]=area_jnk
        except:
                        pass
#del db

save_temp_csv_data(veg_area, opath)
