wd="Y:/PICCC_data/climate_data/rainfall_hindcast/Month_Rasters_State_mm/Annual/"
setwd(wd)
library(raster)

dest_dir="Y:/PICCC_data/VA data/landscape/hist_ppt_var/"
dir.create(dest_dir, showWarnings = F)
#annual_rasters=list.files(wd, pattern="^stann_", recursive=T)
dir_list=list.dirs(path = wd, full.names = F, recursive = TRUE)
jnk=grep(pattern="^stann_", dir_list)
dir_list=dir_list[jnk]

annual_stack=stack(dir_list)
early_stack=stack(dir_list[1:20])
l=length(dir_list)
late_stack=stack(dir_list[(l-19):l])

annual_mean=calc(annual_stack, mean, na.rm=T)
early_mean=calc(early_stack, mean, na.rm=T)
late_mean=calc(late_stack, mean, na.rm=T)
trend_diff=late_mean-early_mean

annual_sd=calc(annual_stack, sd, na.rm=T)
annual_CV=annual_sd/annual_mean

plot(annual_mean)
plot(annual_sd)
plot(annual_CV)
plot(trend_diff)

writeRaster(annual_CV, paste0(dest_dir, "annual_CV"), format="GTiff", overwrite=TRUE, compression="LZW")
writeRaster(annual_sd, paste0(dest_dir, "annual_sd"), format="GTiff", overwrite=TRUE, compression="LZW")
writeRaster(annual_mean, paste0(dest_dir, "annual_mean"), format="GTiff", overwrite=TRUE, compression="LZW")
writeRaster(trend_diff, paste0(dest_dir, "trend_diff"), format="GTiff", overwrite=TRUE, compression="LZW")


#this code below was not executed since the way it is constructed would be looking at monthly variability across multiple years
#when in fact we need annual or decadal variability

# #wet season
# wd="Y:/PICCC_data/climate_data/rainfall_hindcast/Month_Rasters_State_mm/"
# setwd(wd)
# raster_subdirs=c(paste0("State_", c("11Nov", "12Dec", "01Jan", "02Feb", "03Mar", "04Apr")))
# dir_list=c()
# for (raster_subdir in raster_subdirs){
#   tmp_dirs=list.dirs(path = paste0(wd, raster_subdir), full.names = F, recursive = TRUE)
#   jnk=grep(pattern="^st", tmp_dirs)
#   tmp_dirs=tmp_dirs[jnk]
#   tmp_dirs=paste0(wd, raster_subdir, "/", raster_subdir)
#   dir_list=c(dir_list, tmp_dirs)  
# }
# 
# 
# wet_stack=stack(dir_list)
# wet_mean=calc(wet_stack, mean, na.rm=T)
# wet_sd=calc(wet_stack, sd, na.rm=T)
# wet_CV=wet_sd/wet_mean
# 
# plot(wet_mean)
# plot(wet_sd)
# plot(wet_CV)
# 
# writeRaster(wet_CV, paste0(dest_dir, "wet_CV"), format="GTiff", overwrite=TRUE, compression="LZW")
# writeRaster(wet_sd, paste0(dest_dir, "wet_sd"), format="GTiff", overwrite=TRUE, compression="LZW")
# writeRaster(wet_mean, paste0(dest_dir, "wet_mean"), format="GTiff", overwrite=TRUE, compression="LZW")
# 
# 
# 
