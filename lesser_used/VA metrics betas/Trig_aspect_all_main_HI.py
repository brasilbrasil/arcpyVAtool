###USER INPUT
datadir="C:/Users/lfortini/Data/VA data/landscape/"
#Islands=['ko', 'ka', 'la', 'ma', 'mo', 'ni', 'oa', 'ha', 'all']
Islands=['All']
###END USER INPUT

#START UNDERHOOD
resultsdir=datadir
import arcpy
import arcpy.sa
import math
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
deg2rad = math.pi / 180.0

#FOR EACH ISLAND PERFORM OPERATIONS IN LOOP BELOW
for i in range(len(Islands)):
	inRaster0 = "%s%s/DEM/%s_aspect_withflatareas.tif" %(datadir,Islands[i], Islands[i]) 
	inRaster=arcpy.Raster(inRaster0)
	
	inRaster1 = "%s%s/DEM/%s_pct_slope.tif" %(datadir,Islands[i], Islands[i]) 
	inRaster2=arcpy.Raster(inRaster1)
	inRaster2=inRaster2>=10
	#inRaster2=arcpy.sa.SetNull(inRaster2,1,"Value=0")
	inRaster3=inRaster*inRaster2
	
	cos_temp=arcpy.sa.Cos(inRaster3*deg2rad)
	loc_cos="%s%s/DEM/%s_cos_aspect.tif" %(resultsdir, Islands[i], Islands[i])
	cos_temp.save(loc_cos)
	
	sin_temp=arcpy.sa.Sin(inRaster3*deg2rad)
	loc_sin="%s%s/DEM/%s_sin_aspect.tif" %(resultsdir, Islands[i], Islands[i])
	sin_temp.save(loc_sin)

