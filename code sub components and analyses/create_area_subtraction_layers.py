landscape_factor_dir=r"Y:/VA data/landscape/" #whichever is data dir, will have to have subfolders: la/DEM/ (where DEM based layers go), gaplandcover/ (where gaplandcov_hi is placed)

#START UNDERHOOD
import os
import arcpy
import arcpy.sa

arcpy.env.overwriteOutput = True
arcpy.env.workspace = landscape_factor_dir
arcpy.env.compression = "LZW"
mxd=arcpy.mapping.MapDocument("CURRENT")

ugly=arcpy.Raster(landscape_factor_dir+"ugly.tif")
slr=arcpy.Raster(landscape_factor_dir+"all/DEM/"+"All_1mSLR.tif")
lava=arcpy.Raster("pioneer")

area_subtr_pioneer=arcpy.sa.Con(arcpy.sa.IsNull(slr),0,slr) + arcpy.sa.Con(arcpy.sa.IsNull(ugly),0,ugly)
area_subtr_pioneer2=arcpy.sa.SetNull(area_subtr_pioneer,1,"Value >0")
loc_save="area_subtr_pioneer.tif"
area_subtr_pioneer2.save(landscape_factor_dir+loc_save)

area_subtr=arcpy.sa.Con(arcpy.sa.IsNull(slr),0,slr) + arcpy.sa.Con(arcpy.sa.IsNull(ugly),0,ugly) + arcpy.sa.Con(arcpy.sa.IsNull(lava),0,lava)
area_subtr2=arcpy.sa.SetNull(area_subtr,1,"Value >0")
loc_save="area_subtr.tif"
area_subtr2.save(landscape_factor_dir+loc_save)
