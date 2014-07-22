###USER INPUT
datadir="C:/Users/lfortini/Data/DEMs/"
#Islands=['ko', 'ka', 'la', 'ma', 'mo', 'ni', 'oa', 'ha']
Islands=['oa']

###END USER INPUT

#START UNDERHOOD
resultsdir="%sAspect/" %(datadir)
import arcpy
import arcpy.sa
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir

#FOR EACH ISLAND PERFORM OPERATIONS IN LOOP BELOW
for i in range(len(Islands)):
	inRaster = "%s%s_slope.img" %(resultsdir,Islands[i])
        temp_DEM=arcpy.Raster(inRaster)
	slopemax = arcpy.GetRasterProperties_management(temp_DEM, "MAXIMUM")
	slopemax= slopemax.getOutput(0) 	
	slopemax=float(slopemax)
	inRaster2 = "%s%s_peaks.img" %(resultsdir,Islands[i])
        temp_DEM2=arcpy.Raster(inRaster2)
	#must number each peak area
	
	inverted_slope=slopemax-temp_DEM
	costAllocOut=arcpy.sa.CostAllocation(temp_DEM2, inverted_slope)
	costAllocOut.save("c:/sapyexamples/output/costalloc")

	loc_peak="%s%s_peaks.img" %(resultsdir,Islands_name_output[i])
	outpeak.save(loc_peak)
	
	