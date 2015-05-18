library(raster)
library(rgdal)
#####SET DIRECTORIS AND PERSONAL INFO####
Topowd<-("D:/PICCC_data/DEM_data_HI/") #running on beast up to line 11
setwd(Topowd)
#memory.limit(size=2400000)

#cALCULATED TOPO INDICES = Slope, Aspect, Topographic position index (TPI), Topographic Ruggedness Index (TRI), Roughness####
DEM<-raster(paste(Topowd, "all_dem.tif", sep=""))
alltopo<-terrain(DEM, opt = c('slope', 'aspect', 'TPI', 'TRI','roughness', 'flowdir'), unit='degrees', neighbors=8, filename='alltopo.tif', overwrite = T) 
writeRaster(alltopo, "tmp_alltopo.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #
removeTmpFiles(h=0) #remove all tmp files and reload raster
alltopo<-stack(paste("tmp_alltopo.tif", sep=""))


#Aspect<-raster(alltopo, layer=5)
TRASP=(1-cos(alltopo[[5]]-30))/2 # from http://code.google.com/p/bcal-lidar-tools/wiki/TopoAll and used by: Roberts. D. W. and Cooper, S. V. (1989). Concepts and techniques of vegetation mapping. In: Land Classifications Based on Vegetation - Applications for Resource Management. USDA Forest Service GTR INT-257, Ogden, UT, pp 90-96.
#slope=raster(alltopo, layer=4)
#tpi=raster(alltopo, layer=2)
#roughness=raster(alltopo, layer=3)
#tri=raster(alltopo, layer=1)
northness = cos(alltopo[[5]])
westness = sin(alltopo[[5]])
slpsinaspect = alltopo[[4]] * northness # from http://code.google.com/p/bcal-lidar-tools/wiki/TopoAll and used by: Stage, A.R., 1976. An Expression for the Effect of Aspect, Slope, and Habitat Type on Tree Growth. Forest Science, 22: 457-460.
slpcosaspect = alltopo[[4]] * westness #see above for variable def.

writeRaster(TRASP, "tmp_TRASP.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #
writeRaster(northness, "tmp_northness.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #
writeRaster(westness, "tmp_westness.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #
writeRaster(slpsinaspect, "tmp_slpsinaspect.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #
writeRaster(slpcosaspect, "tmp_slpcosaspect.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #
removeTmpFiles(h=0) #remove all tmp files and reload raster
northness<-raster("tmp_northness.tif")
westness<-raster("tmp_westness.tif")


#Terrain variability calc (places with maximum stdev of either northness, westness, or slope)
f <- matrix(1, nrow=9, ncol=9)
slope_stdev <- focal(alltopo[[4]], w=f, fun=function(x, ...) sd(x), pad=TRUE, padValue=NA, na.rm=TRUE)
writeRaster(slope_stdev, "tmp_slope_stdev.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #

jnk=data.frame(from=c(-Inf, 0.0000001), to=c(0, Inf), becomes=c(NA, 1))
noSlope=reclassify(alltopo[[4]], jnk, right=NA)
jnk=northness*noSlope
plot(noSlope)
northness_stdev <- focal(jnk, w=f, fun=function(x, ...) sd(x), pad=TRUE, padValue=NA, na.rm=TRUE)
writeRaster(northness_stdev, "tmp_northness_stdev.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #

jnk=westness*noSlope
westness_stdev <- focal(jnk, w=f, fun=function(x, ...) sd(x), pad=TRUE, padValue=NA, na.rm=TRUE)
writeRaster(westness_stdev, "tmp_westness_stdev.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #

removeTmpFiles(h=0) #remove all tmp files and reload raster
slope_stdev<-raster("tmp_slope_stdev.tif")
northness_stdev<-raster("tmp_northness_stdev.tif")
westness_stdev<-raster("tmp_westness_stdev.tif")

#standardize
slope_stdev=slope_stdev/cellStats(slope_stdev, max)
northness_stdev=northness_stdev/cellStats(northness_stdev, max)
westness_stdev=westness_stdev/cellStats(westness_stdev, max)
tmp=stack(slope_stdev, northness_stdev, westness_stdev)
terrain_var=max(tmp, na.rm=T) #max across 3 variables


##new attempt to create variability index (standardize variables first, then make calculations)
#Terrain variability calc (places with maximum stdev of either northness, westness, or slope)
f <- matrix(1, nrow=9, ncol=9)
jnk=data.frame(from=c(-Inf, 0.0000001), to=c(0, Inf), becomes=c(NA, 1))
noSlope=reclassify(alltopo[[4]], jnk, right=NA)
plot(noSlope)
notSL=reclassify(DEM, jnk, right=NA)

jnk=alltopo[[4]]*notSL
mx=cellStats(jnk, 'max', na.rm=T)
mn=cellStats(jnk, 'min', na.rm=T)
jnk=(jnk-mn)/(mx-mn)
#standardized_var=(alltopo[[4]]-cellStats(alltopo[[4]], mean))/cellStats(alltopo[[4]], sd)
#standardized_var=(alltopo[[4]]*notSL)/cellStats(alltopo[[4]], max)
slope_stdev <- focal(jnk, w=f, fun=function(x, ...) sd(x), pad=TRUE, padValue=NA, na.rm=TRUE)
writeRaster(slope_stdev, "tmp_std_slope_stdev.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #

#jnk=northness*noSlope
jnk=northness*notSL
mx=cellStats(jnk, max)
mn=cellStats(jnk, min)
jnk=(jnk-mn)/(mx-mn)
#standardized_var=(jnk-cellStats(jnk, mean))/cellStats(jnk, sd)
northness_stdev <- focal(jnk, w=f, fun=function(x, ...) sd(x), pad=TRUE, padValue=NA, na.rm=TRUE)
writeRaster(northness_stdev, "tmp_std_northness_stdev.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #

#jnk=westness*noSlope
jnk=westness*notSL
mx=cellStats(jnk, max)
mn=cellStats(jnk, min)
jnk=(jnk-mn)/(mx-mn)
#standardized_var=(jnk-cellStats(jnk, mean))/cellStats(jnk, sd)
westness_stdev <- focal(jnk, w=f, fun=function(x, ...) sd(x), pad=TRUE, padValue=NA, na.rm=TRUE)
writeRaster(westness_stdev, "tmp_std_westness_stdev.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #


removeTmpFiles(h=24)
slope_stdev=raster("tmp_std_slope_stdev.tif")
northness_stdev=raster("tmp_std_northness_stdev.tif")
westness_stdev=raster("tmp_std_westness_stdev.tif")
tmp=stack(slope_stdev, northness_stdev, westness_stdev)
terrain_var_max=max(tmp, na.rm=T) #max across 3 variables
writeRaster(terrain_var_max, "terrain_var_max.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #
terrain_var_mean=mean(tmp, na.rm=T) #max across 3 variables
writeRaster(terrain_var_mean, "terrain_var_mean.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=F, suffix='names') #


TRASP<-raster("tmp_TRASP.tif")
slpsinaspect<-raster("tmp_slpsinaspect.tif")
slpcosaspect<-raster("tmp_slpcosaspect.tif")

####rounding of rasters
TRASP=TRASP*100
northness=northness*100
westness=westness*100
terrain_var=terrain_var*100

alltopo = stack(alltopo[[5]], TRASP, alltopo[[4]], alltopo[[4]], alltopo[[3]], alltopo[[1]], northness, westness, slpsinaspect, slpcosaspect, terrain_var)
names(alltopo)<-c("Aspect", "TRASP", "slope", "tpi", "roughness", "tri", "northness", "westness", "slpsinaspect", "slpcosaspect", "terrain_var")
####PLOT ALL TOPO INDICES, CHECK TO MAKE SURE THEY COME OUT WITHOUT ODD "NO DATA" LINES OR PIXELS RUNNING THROUGH THEM####
#plot(alltopo, col=rev(terrain.colors(255)), maxpixels=1000000, useRaster=FALSE, axe =TRUE, addfun=NULL, interpolate=TRUE)
plot(alltopo)
allTopoRound=round(alltopo)
names(allTopoRound)<-c("Aspect", "TRASP", "slope", "tpi", "roughness", "tri", "northness", "westness", "slpsinaspect", "slpcosaspect", "terrain_var")
writeRaster(allTopoRound, "alltopo_10m_layer_rounded.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=TRUE, suffix='names', datatype='INT2S') #


# #Terrain variability calc (places with maximum stdev of either northness, westness, or slope)
# f <- matrix(1, nrow=9, ncol=9)
# slope_stdev <- focal(WGS250_alltopo[[3]], w=f, fun=function(x, ...) sd(x), pad=TRUE, padValue=NA, na.rm=TRUE)
# #calc sd northnes but remove places with no slope/ aspect
# jnk=WGS250_alltopo[[7]]
# jnk[WGS250_alltopo[[3]]==0]=NA
# northness_stdev <- focal(jnk, w=f, fun=function(x, ...) sd(x), pad=TRUE, padValue=NA, na.rm=TRUE)
# jnk=WGS250_alltopo[[8]]
# jnk[WGS250_alltopo[[3]]==0]=NA
# westness_stdev <- focal(jnk, w=f, fun=function(x, ...) sd(x), pad=TRUE, padValue=NA, na.rm=TRUE)
# #standardize
# slope_stdev2=slope_stdev/cellStats(slope_stdev, max)
# northness_stdev2=northness_stdev/cellStats(northness_stdev, max)
# westness_stdev2=westness_stdev/cellStats(westness_stdev, max)
# tmp=stack(slope_stdev2, northness_stdev2, westness_stdev2)
# tmp[is.na(tmp)]=0
# terrain_var=max(tmp, na.rm=T) #max across 3 variables

####RESAMPLING AND REPROJECTING RASTERS FROM 10M####
####READING BASE TEMPLATE (DEFINED BY LUCAS) AT 100 AND 250M RESOLUTION AT THE EXTENT NECESSARY####
template_250m=raster("Y:/PICCC_data/climate_data/bioclim_data_Aug2013/complete_rasters/allYrs_avg/bioclims_abs/all_baseline/250m/bio1.tif")
template_125m=raster("Y:/PICCC_data/climate_data/bioclim_data_Aug2013/complete_rasters/allYrs_avg/bioclims_abs/all_baseline/125m/bio1.tif")

align_files_low_res=function(low_res_raster, high_res_raster, res_ratio){ #returns stack with two aligned rasters
  tmp_raster=aggregate(high_res_raster,fact=res_ratio,fun=mean, expand=T) #mean not mode
  tmp_raster=projectRaster(tmp_raster, low_res_raster, method = 'bilinear')
}

WGS250_alltopo=align_files_low_res(template_250m, alltopo, 25)
WGS250_alltopo=round(WGS250_alltopo)
names(WGS250_alltopo)<-c("Aspect", "TRASP", "slope", "tpi", "roughness", "tri", "northness", "westness", "slpsinaspect", "slpcosaspect", "terrain_var")
writeRaster(WGS250_alltopo, "alltopo_250m_layer.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=TRUE, suffix='names', datatype='INT2U')
#plot(WGS250_alltopo, col=rev(terrain.colors(255)), maxpixels=1000000, useRaster=FALSE, axe =TRUE, addfun=NULL, interpolate=TRUE)

WGS125_alltopo=align_files_low_res(template_125m, alltopo, 12)
WGS125_alltopo=round(WGS125_alltopo)
names(WGS125_alltopo)<-c("Aspect", "TRASP", "slope", "tpi", "roughness", "tri", "northness", "westness", "slpsinaspect", "slpcosaspect", "terrain_var")
writeRaster(WGS125_alltopo, "alltopo_125m_layer.tif", format='GTiff', options=c("COMPRESS=LZW"),  overwrite=TRUE,bylayer=TRUE, suffix='names', datatype='INT2U')
#plot(WGS125_alltopo, col=rev(terrain.colors(255)), maxpixels=1000000, useRaster=FALSE, axe =TRUE, addfun=NULL, interpolate=TRUE)



# SlpAsp<-subset(WGS250_alltopo, 9:10)
# plot(SlpAsp, col=rev(terrain.colors(255)), maxpixels=1000000, useRaster=FALSE, axe =TRUE, addfun=NULL, interpolate=TRUE)
# jpeg_name=paste("SlpAsp.jpg", sep = "")
# jpeg(jpeg_name,
#      width = 10, height = 10, units = "in",
#      pointsize = 12, quality = 90, bg = "white", res = 300)
# par(mfrow=c(1,2))
# tryplot(SlpAsp, col=rev(terrain.colors(255)), maxpixels=1000000, useRaster=FALSE, axe =TRUE, addfun=NULL, interpolate=TRUE)
# dev.off()
# 
# 
# ####ODDITY IN THE MANNER IN WHICH ROUGHNESS WAS DEFINED/DRAWN, RE-ANALYZED HERE but still didn't work####
# alltopo_rough<-terrain(DEM, opt = c('roughness'), unit='degrees', neighbors=8, filename='roughness', overwrite=TRUE)
# alltopo_rough
# plot(alltopo_rough, col=rev(terrain.colors(255)), maxpixels=1000000, useRaster=FALSE, axe =TRUE, addfun=NULL, interpolate=TRUE)
# WGS100_topos<-projectRaster(alltopo_rough, template_100m, method = 'ngb')
# WGS250_topos<-projectRaster(alltopo_rough, template_250m, method = 'ngb')
