rm(list = ls()) #remove all past worksheet variables
library(raster)
library(stringr)
source_dir="Y:/PICCC_data/VA data/CEs_KB/range maps bin extended/"
wd="Y:/PICCC_data/VA data/CEs_KB/range maps archipelago/"
dir.create(wd, showWarnings = F)
setwd(wd)
cpucores=20

#mosaic rasters:
dir_list=list.dirs(path = source_dir, full.names = F, recursive = TRUE)
dir_list=dir_list[-1]

#dir_selection=dir_list[262]
create_CEs_fx=function(dir_selection){
  sp_code=as.character(strsplit(dir_selection, " ")[[1]][1])
  sp_code=str_pad(sp_code, 4, pad = "0")
  maps=c("2000 range\\.tif", "2000\\-2090 difference\\.tif", "2090 range\\.tif")
  names=c("CCE", "resp_zone", "FCE")
  
  #map=maps[2]
  for (map in maps){ 
    tif_file_nms=list.files(paste0(source_dir, "/", dir_selection), pattern=paste0(map, "$"), recursive=T)
    island_stack=stack(paste0(source_dir, dir_selection, "/", tif_file_nms))
    m2 <- mosaic(island_stack[[1]], island_stack[[2]], island_stack[[3]], island_stack[[4]], 
                 island_stack[[5]], island_stack[[6]], island_stack[[7]], fun=max)
    jnk=which(map==maps)
    outname=paste0(wd, names[jnk], sp_code, ".tif")  
    writeRaster(m2, outname, format="GTiff", overwrite=TRUE, datatype='INT1U')    
  }  
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
sfLibrary(stringr)
sfLapply(dir_list,fun=create_CEs_fx)
#system.time(sfClusterApplyLB(iter_strings,fun=sp_parallel_run)) #why not alway us LB? Reisensburg2009_TutParallelComputing_Knaus_Porzelius.pdf
sfRemoveAll()
sfStop()


