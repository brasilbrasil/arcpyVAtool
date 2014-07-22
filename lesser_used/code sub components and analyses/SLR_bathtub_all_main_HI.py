###USER INPUT
SLR=1 #in meters
datadir="C:/Users/lfortini/Data/DEMs/"
#Islands=['Hawaii', 'Kahoolawe', 'Kauai', 'Lanai', 'Maui', 'Molokai', 'Niihau', 'Oahu']
Islands=['ha', 'ko', 'ka', 'la', 'ma', 'mo', 'ni', 'oa']
#Islands=['All']
###END USER INPUT

#START UNDERHOOD
resultsdir="%sSLR_output/" %(datadir)
import arcpy
import arcpy.sa
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir

#FOR EACH ISLAND PERFORM OPERATIONS IN LOOP BELOW
for i in range(len(Islands)):
	inRaster = "%s%s_DEM/%s_dem" %(datadir,Islands[i], Islands[i]) 
	expr="Value > %s" %(SLR)
	SLR_temp=arcpy.sa.SetNull(inRaster,1,expr)
	loc_SLR="%s%s_%smSLR.tif" %(resultsdir,Islands[i],SLR)
	SLR_temp.save(loc_SLR)
	
