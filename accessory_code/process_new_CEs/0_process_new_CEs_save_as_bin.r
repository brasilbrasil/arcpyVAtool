rm(list = ls()) #remove all past worksheet variables
library(raster)
source_dir="Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/raw_CEs/" #DD A1B HRCM v2 CEs // SD RCP45 CEs // SD RCP85 CEs
wd="Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/range maps bin/"
dir.create(wd, showWarnings = F)
setwd(wd)
cpucores=20

tif_file_nms=list.files(source_dir, pattern="\\.tif$", recursive=T)
# tif_file_nm=tif_file_nms[2000]
# for (tif_file_nm in tif_file_nms){
#   tif_file=raster(paste0(source_dir, tif_file_nm))
#   #plot(tif_file)
#   tif_file[tif_file==0]=NA
#   #plot(tif_file)
#   #basename(tif_file_nm)
#   dir.create(dirname(tif_file_nm), showWarnings = F)
#   writeRaster(tif_file, paste0(wd, tif_file_nm), format="GTiff", overwrite=TRUE, datatype='INT1U')  
# }

bin_fx=function(tif_file_nm, source_dir.=source_dir, wd.=wd){
    tif_file=raster(paste0(source_dir., tif_file_nm))
    tif_file[tif_file==0]=NA
    dir.create(dirname(tif_file_nm), showWarnings = F)
    writeRaster(tif_file, paste0(wd., tif_file_nm), format="GTiff", overwrite=TRUE, datatype='INT1U')  
}
require(snowfall)
if (is.null(cpucores)){
  cpucores=as.integer(Sys.getenv('NUMBER_OF_PROCESSORS'))  
}else{
  cpucores=min(cpucores, as.integer(Sys.getenv('NUMBER_OF_PROCESSORS')))
}
sfInit( parallel=T, cpus=cpucores) # 
sfExportAll() 
sfLibrary(raster)
sfLapply(tif_file_nms,fun=bin_fx)
#system.time(sfClusterApplyLB(iter_strings,fun=sp_parallel_run)) #why not alway us LB? Reisensburg2009_TutParallelComputing_Knaus_Porzelius.pdf
sfRemoveAll()
sfStop()


#extend rasters
bin_fx=function(tif_file_nm, source_dir.=source_dir, wd.=wd){
  tif_file=raster(paste0(source_dir., tif_file_nm))
  e=extent(-159.8003, -154.8053, 18.88725, 22.25325)
  jnk=extend(jnk, e, value=NA)  
  dir.create(dirname(tif_file_nm), showWarnings = F)
  writeRaster(tif_file, paste0(wd., tif_file_nm), format="GTiff", overwrite=TRUE, datatype='INT1U')  
}





# #mosaic rasters:
# dir_list=list.dirs(path = wd, full.names = F, recursive = TRUE)
# dir_list=dir_list[-1]
# dir_selection=dir_list[1]
# 
# sp_code=as.character(strsplit(dir_selection, " ")[[1]][1])
# library(stringr)
# sp_code=str_pad(sp_code, 4, pad = "0")
# 
# maps=c("2000 range\\.tif", "2000\\-2090 difference\\.tif", "2090 range\\.tif")
# 
# map=maps[1]
# for (map in maps){
#   tif_file_nms=list.files(dir_selection, pattern=paste0(map, "$"), recursive=T)
#   jnk=raster(paste0(dir_selection, "/", tif_file_nms[3]))
#   e=extent(-159.8003, -154.8053, 18.88725, 22.25325)
#   #plot(jnk)
#   jnk=extend(jnk, e, value=NA)
#   #plot(jnk)
#   
#   #m2 <- mosaic(tif_file_nms, fun=min)
#   
#   #m2 <- mosaic(s1, s2, s3, fun=min)
#   
# }
# 
# islands=c("Hawaii", "Kahoolawe" , "Kauai", "Lanai", "Maui", "Molokai", "Oahu")


