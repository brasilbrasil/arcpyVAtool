##this code is not finished trying to do it by shapefile means
#USER INPUT
results_dir="Y:/PICCC_analysis/plant_landscape_va_results/ensemble_zone_maps/NC_Nex_vuln_quantile_maps/"
library(raster)
out_str='NC_Nex' #NC_winkout  NC_NO	NC_NEx_winkout	NC_Nex_NO OA_NC_Nex_End OA_NC_Nex_notSec
i=990
sp_code=1085
out_name=paste0(results_dir,out_str,"_",i,"_sp",sp_code,".tif")
CCE_ensemble=raster(out_name)


out_str='NC_Nex_wFCE' #NC_winkout	NC_NO	NC_NEx_winkout	NC_Nex_NO OA_NC_Nex_End OA_NC_Nex_notSec
i=955
sp_code=1085
out_name=paste0(results_dir,out_str,"_",i,"_sp",sp_code,".tif")
FCE_ensemble=raster(out_name)
FCE_ensemble2=crop(FCE_ensemble, CCE_ensemble)
FCE_ensemble2=resample(FCE_ensemble2,CCE_ensemble)
plot(CCE_ensemble)
plot(FCE_ensemble2)

richness_delta=FCE_ensemble2-CCE_ensemble
richness_delta[richness_delta>220]=220
out_name="Modelled_richness_delta_truncated.tif"
tifname=paste0(results_dir,out_name)
writeRaster(richness_delta, tifname, format="GTiff", overwrite=TRUE)

richness_relative_delta=(FCE_ensemble2-CCE_ensemble)/CCE_ensemble
richness_relative_delta[richness_relative_delta>10]=10
out_name="Modelled_richness_relative_delta_truncated.tif"
tifname=paste0(results_dir,out_name)
writeRaster(richness_relative_delta, tifname, format="GTiff", overwrite=TRUE)

#proportional Tol zone
out_str='NC_Nex' #NC_winkout  NC_NO  NC_NEx_winkout	NC_Nex_NO OA_NC_Nex_End OA_NC_Nex_notSec
i=990
sp_code=1085
out_name=paste0(results_dir,out_str,"_",i,"_sp",sp_code,".tif")
CCE_ensemble=raster(out_name)


out_name=paste0(results_dir,"956_NC_Nex_wFCE_zone2_partial_ensemble.tif")
TOL_ensemble=raster(out_name)
TOL_ensemble2=crop(TOL_ensemble, CCE_ensemble)
TOL_ensemble2=resample(TOL_ensemble2,CCE_ensemble)

propTol_spp=TOL_ensemble2/CCE_ensemble
propTol_spp[propTol_spp>10]=10
out_name="Prop_tol_spp.tif"
tifname=paste0(results_dir,out_name)
writeRaster(propTol_spp, tifname, format="GTiff", overwrite=TRUE)
plot(propTol_spp)
