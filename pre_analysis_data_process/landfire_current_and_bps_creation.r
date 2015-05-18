rm(list = ls()) #remove all past worksheet variables
library(raster)
library(stringr)
library(biomod2)

###USER CONFIGURATION
working_dir="Y:/PICCC_data/VA data/Phase2/veg_data/" #this is where r will create a mirror folder structure with the 
setwd(working_dir)

#CURRENT LANDFIRE COVER
###create landfire reclass 2
jnk=raster(paste(working_dir, "landfire_data/hi_130evt_wgs84.tif", sep=""))
reclass_table=(read.csv('EVT_hawaii_classes2.csv',header=T, stringsAsFactors=F))
reclass_table=reclass_table[,c("VALUE", "Reclass_simple")]
landfire_reclass=subs(jnk,  reclass_table)
writeRaster(landfire_reclass, "landfire_reclassed.tif", format="GTiff", overwrite=TRUE)
 
# ###resample
clim_data_dir="Y:/PICCC_data/climate_data/bioclim_data_Aug2013/complete_rasters/allYrs_avg/bioclims_abs/all_baseline/125m/" #this is the root directory of all the current env rasters
biovars2000 = raster(paste(clim_data_dir, "bio1.tif", sep=""))
landfire_reclass=raster("landfire_reclassed.tif")
low_res_raster_proj_res=res(landfire_reclass)[1]
high_res_raster_proj_res=res(biovars2000)[1]
res_ratio=round(low_res_raster_proj_res/high_res_raster_proj_res)
landfire_reclass_aggregate=aggregate(landfire_reclass, 3, fun=modal, expand=TRUE)
original_veg_map=resample(landfire_reclass_aggregate, biovars2000, method='ngb')
writeRaster(original_veg_map, "landfire_reclassed_125m.tif", format="GTiff", overwrite=TRUE)


#LANDFIRE BPS
#CURRENT LANDFIRE COVER
###create landfire reclass 2
jnk=raster(paste(working_dir, "landfire_data/HI_110BPS.tif", sep=""))
jnk=projectRaster(jnk, crs=CRS("+proj=longlat +ellps=WGS84 +datum=WGS84"))
reclass_table=(read.csv('BPS_hawaii_classes2.csv',header=T, stringsAsFactors=F))
reclass_table=reclass_table[,c("VALUE", "Reclass_simple")]
landfire_BPS_reclass=subs(jnk,  reclass_table)
writeRaster(landfire_BPS_reclass, "landfire_BPS_reclassed.tif", format="GTiff", overwrite=TRUE)

# ###resample
clim_data_dir="Y:/PICCC_data/climate_data/bioclim_data_Aug2013/complete_rasters/allYrs_avg/bioclims_abs/all_baseline/125m/" #this is the root directory of all the current env rasters
biovars2000 = raster(paste(clim_data_dir, "bio1.tif", sep=""))
landfire_BPS_reclass=raster("landfire_BPS_reclass.tif")
low_res_raster_proj_res=res(biovars2000)[1]
high_res_raster_proj_res=res(landfire_BPS_reclass)[1]
res_ratio=round(low_res_raster_proj_res/high_res_raster_proj_res)
landfire_BPS_reclass_aggregate=aggregate(landfire_BPS_reclass, res_ratio, fun=modal, expand=TRUE)
original_veg_map=resample(landfire_BPS_reclass_aggregate, biovars2000, method='ngb')
writeRaster(original_veg_map, "landfire_BPS_reclassed_125m.tif", format="GTiff", overwrite=TRUE)

