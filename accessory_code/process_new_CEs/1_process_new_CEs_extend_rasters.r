rm(list = ls()) #remove all past worksheet variables
library(raster)
source_dir="Y:/PICCC_data/VA data/CEs_KB/range maps bin/"
wd="Y:/PICCC_data/VA data/CEs_KB/range maps bin extended/"
dir.create(wd, showWarnings = F)
setwd(wd)
cpucores=20

tif_file_nms=list.files(source_dir, pattern="\\.tif$", recursive=T)


#extend rasters
extend_fx=function(tif_file_nm, source_dir.=source_dir, wd.=wd){
  tif_file=raster(paste0(source_dir., tif_file_nm))
  e=extent(-159.8003, -154.8053, 18.88725, 22.25325)
  tif_file=extend(tif_file, e, value=NA)  
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
sfLapply(tif_file_nms,fun=extend_fx)
#system.time(sfClusterApplyLB(iter_strings,fun=sp_parallel_run)) #why not alway us LB? Reisensburg2009_TutParallelComputing_Knaus_Porzelius.pdf
sfRemoveAll()
sfStop()



