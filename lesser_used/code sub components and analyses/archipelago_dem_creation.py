###USER INPUT
SLR=6000 #in meters
datadir="C:/Users/lfortini/Data/DEMs/"
Islands=['Hawaii', 'Kahoolawe', 'Kauai', 'Lanai', 'Maui', 'Molokai', 'Niihau', 'Oahu']
#Islands=['Oahu']
###END USER INPUT

#START UNDERHOOD
resultsdir=datadir
import arcpy
import arcpy.sa
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir

#FOR EACH ISLAND PERFORM OPERATIONS IN LOOP BELOW
for i in range(len(Islands)):
	inRaster = "%s%s_DEM/%s_dem" %(datadir,Islands[i], Islands[i]) 
	all_dem= arcpy.sa.Con(arcpy.sa.IsNull(Microrefugia_zone),0,Microrefugia_zone) + (arcpy.sa.Con(arcpy.sa.IsNull(Tolerate_zone),0,Tolerate_zone)) + (arcpy.sa.Con(arcpy.sa.IsNull(migration_zone),0,migration_zone)) 
	loc_SLR="%sall_dem.img" %(resultsdir,Islands[i],SLR)
	SLR_temp.save(loc_SLR)
	
	
