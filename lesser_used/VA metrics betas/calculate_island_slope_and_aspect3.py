###USER INPUT
datadir="C:/Users/lfortini/Data/VA data/landscape/"
Islands=['all'] #Enter any combination of these values: 'Kahoolawe', 'Kauai', 'Lanai', 'Maui', 'Molokai', 'Niihau', 'Oahu', 'Hawaii'
remove_flat_areas=1 #right now arcgis bug is not allowing to run this code DO IT BY HAND- SA>CONDITIONAL
Slope_or_Aspect=2 #1 for slope, 2 for aspect

###END USER INPUT

#START UNDERHOOD
#Islands_list=['Kahoolawe', 'Kauai', 'Lanai', 'Maui', 'Molokai', 'Niihau', 'Oahu', 'Hawaii']
#Islands_name_output=['ko', 'ka', 'la', 'ma', 'mo', 'ni', 'oa', 'ha']

resultsdir=datadir
import arcpy
import arcpy.sa
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir

#FOR EACH ISLAND PERFORM OPERATIONS IN LOOP BELOW
for i in range(len(Islands)):
	#Island_index=Islands_list.index(Islands[i])
	inRaster = "%s%s/DEM/%s_dem.tif" %(datadir,Islands[i], Islands[i]) 
	if Slope_or_Aspect==1:
		outSlope = arcpy.sa.Slope(inRaster, "PERCENT_RISE")
		loc_slope="%s%s/DEM/%s_pct_slope.tif" %(resultsdir,Islands[i],Islands[i])
		outSlope.save(loc_slope)        
	if Slope_or_Aspect==2:
		outAspect = arcpy.sa.Aspect(inRaster)
		loc_aspect="%s%s/DEM/%s_aspect_withflatareas.tif" %(resultsdir,Islands[i],Islands[i])#_aspect_withflatareas
		outAspect.save(loc_aspect)
		
		if remove_flat_areas==1:
			inraster=arcpy.Raster(loc_aspect)
			#slope_raster="%s%s/DEM/%s_pct_slope.tif" %(resultsdir,Islands[i],Islands[i])
			#slope_raster=arcpy.Raster(slope_raster)
			#slope_mask=arcpy.sa.SetNull(slope_raster,1,"Value <= 0") # exclude flat areas
			#Aspect_temp=slope_mask*inraster
			
			Aspect_temp=arcpy.sa.SetNull(inraster,inraster,"Value < 0") # exclude flat areas (aspect = -1)
			loc_aspect="%s%s/DEM/%s_aspect_noflatareas.tif" %(resultsdir,Islands[i],Islands[i]) #_aspect_noflatareas
			Aspect_temp.save(loc_aspect)
	

