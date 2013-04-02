#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#USER INPUT
rootdir=r"C:/Users/lfortini/Data/fragmentation/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
edge_effect_size=100

#END USER INPUT

#START UNDERHOOD
import os
import arcpy
import arcpy.sa
import csv
#from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/

#conversion of line to raster done in arcgis: conversion tools: polyline to raster
arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
mxd=arcpy.mapping.MapDocument("CURRENT")

ugly=rootdir+"HI_bad_and_ugly_map.tif"
ugly=arcpy.Raster(ugly)

veg=rootdir+"landfire_veg_classes2.tif"
veg=arcpy.Raster(veg)

loc_extent=rootdir+"island_extent.tif"
if arcpy.Exists(loc_extent)==False:
    island_extent=veg>-1
    island_extent.save(loc_extent)
else:
    island_extent=arcpy.Raster(loc_extent)
    
#loc_steep=rootdir+"steep.tif"
#if arcpy.Exists(loc_steep)==False:
#    steep=rootdir+"slope_gtr_45deg_sm.tif"
#    steep=arcpy.Raster(steep)
#    steep=arcpy.sa.Con(arcpy.sa.IsNull(steep),0,steep)*island_extent
#    steep.save(loc_steep)
#else:
#    steep=arcpy.Raster(loc_steep)
steep=island_extent*0 

loc_road=rootdir+"road.tif"
if arcpy.Exists(loc_road)==False:
    road=rootdir+"road_raster_single_val.tif"
    road=arcpy.Raster(road)
    road=arcpy.sa.Con(arcpy.sa.IsNull(road),0,road)*island_extent
    road.save(loc_road)
else:
    road=arcpy.Raster(loc_road)


#BINARY FRAGMENTATION SURFACES
#binary non-forest
loc_bin_NF=rootdir+"bin_NF.tif"
loc_bin_F_edge=rootdir+"bin_100_edge.tif"
if arcpy.Exists(loc_bin_NF)==False:
    bin_NF=((veg!=3)+steep+road+ugly)>0
    jnk=arcpy.sa.SetNull(bin_NF,1,"Value <1")
    jnk=arcpy.sa.EucDistance(jnk, edge_effect_size)
    jnk=jnk>0
    F_edge=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)*island_extent
    F_edge=(F_edge+steep+road+ugly)>0
    F_edge=F_edge+(veg==3)
    F_edge.save(loc_bin_F_edge)
    #bin_NF=(bin_NF+jnk)>0
    bin_NF.save(loc_bin_NF)
else:
    bin_NF=arcpy.Raster(loc_bin_NF)

#binhary non-grassland
loc_bin_NG=rootdir+"bin_NG.tif"
loc_bin_G_edge=rootdir+"bin_001_edge.tif"
if arcpy.Exists(loc_bin_NG)==False:
    bin_NG=((veg!=1)+steep+road+ugly)>0
    jnk=arcpy.sa.SetNull(bin_NG,1,"Value <1")
    jnk=arcpy.sa.EucDistance(jnk, edge_effect_size)
    jnk=jnk>0
    G_edge=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)*island_extent
    G_edge=(G_edge+steep+road+ugly)>0
    G_edge=G_edge+(veg==1)
    G_edge.save(loc_bin_G_edge)
    #bin_NF=(bin_NF+jnk)>0
    bin_NG.save(loc_bin_NG)
else:
    bin_NG=arcpy.Raster(loc_bin_NG)

#binary non-shrubland
loc_bin_NS=rootdir+"bin_NS.tif"
loc_bin_S_edge=rootdir+"bin_010_edge.tif"
if arcpy.Exists(loc_bin_NS)==False:
    bin_NS=((veg!=2)+steep+road+ugly)>0
    jnk=arcpy.sa.SetNull(bin_NS,1,"Value <1")
    jnk=arcpy.sa.EucDistance(jnk, edge_effect_size)
    jnk=jnk>0
    S_edge=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)*island_extent
    S_edge=(S_edge+steep+road+ugly)>0
    S_edge=S_edge+(veg==2)
    S_edge.save(loc_bin_S_edge)
    #bin_NF=(bin_NF+jnk)>0
    bin_NS.save(loc_bin_NS)
else:
    bin_NS=arcpy.Raster(loc_bin_NS)

#Binary non-shrubland+forest
loc_bin_NSF=rootdir+"bin_NSF.tif"
loc_bin_SF_edge=rootdir+"bin_110_edge.tif"
if arcpy.Exists(loc_bin_NSF)==False:
    #jnk9=arcpy.sa.Con(veg, 1, 0, "Value != 2 & Value != 3")
    bin_NSF=((((veg!=2) + (veg!=3))==2)+steep+road+ugly)>0
    jnk=arcpy.sa.SetNull(bin_NSF,1,"Value <1")
    jnk=arcpy.sa.EucDistance(jnk, edge_effect_size)
    jnk=jnk>0
    SF_edge=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)*island_extent
    SF_edge=(SF_edge+steep+road+ugly)>0
    SF_edge=SF_edge+(veg==2)+(veg==3)
    SF_edge.save(loc_bin_SF_edge)
    #bin_NF=(bin_NF+jnk)>0
    bin_NSF.save(loc_bin_NSF)
else:
    bin_NSF=arcpy.Raster(loc_bin_NSF)

#Binary non-shrubland+grassland
loc_bin_NSG=rootdir+"bin_NSG.tif"
loc_bin_SG_edge=rootdir+"bin_011_edge.tif"
if arcpy.Exists(loc_bin_NSG)==False:
    bin_NSG=((((veg!=1) + (veg!=2))==2)+steep+road+ugly)>0
    jnk=arcpy.sa.SetNull(bin_NSG,1,"Value <1")
    jnk=arcpy.sa.EucDistance(jnk, edge_effect_size)
    jnk=jnk>0
    SG_edge=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)*island_extent
    SG_edge=(SG_edge+steep+road+ugly)>0
    SG_edge=SG_edge+((veg==1)+(veg==2))
    SG_edge.save(loc_bin_SG_edge)
    #bin_NF=(bin_NF+jnk)>0
    bin_NSG.save(loc_bin_NSG)
else:
    bin_NSG=arcpy.Raster(loc_bin_NSG)

loc_bin_NGF=rootdir+"bin_NGF.tif"
loc_bin_GF_edge=rootdir+"bin_101_edge.tif"
if arcpy.Exists(loc_bin_NGF)==False:
    bin_NGF=((((veg!=1) + (veg!=3))==2)+steep+road+ugly)>0
    jnk=arcpy.sa.SetNull(bin_NGF,1,"Value <1")
    jnk=arcpy.sa.EucDistance(jnk, edge_effect_size)
    jnk=jnk>0
    GF_edge=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)*island_extent
    GF_edge=(GF_edge+steep+road+ugly)>0
    GF_edge=GF_edge+((veg==1)+(veg==3))
    GF_edge.save(loc_bin_GF_edge)
    #bin_NF=(bin_NF+jnk)>0
    bin_NGF.save(loc_bin_NGF)
else:
    bin_NGF=arcpy.Raster(loc_bin_NGF)

loc_bin_NFSG=rootdir+"bin_NFSG.tif"
loc_bin_FSG_edge=rootdir+"bin_111_edge.tif"
if arcpy.Exists(loc_bin_NFSG)==False:
    bin_NFSG=((((veg!=1)+ (veg!=2) + (veg!=3))==3)+steep+road+ugly)>0
    jnk=arcpy.sa.SetNull(bin_NFSG,1,"Value <1")
    jnk=arcpy.sa.EucDistance(jnk, edge_effect_size)
    jnk=jnk>0
    FSG_edge=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)*island_extent
    FSG_edge=(FSG_edge+steep+road+ugly)>0
    FSG_edge=FSG_edge+((veg==1)+(veg==2)+(veg==3))
    FSG_edge.save(loc_bin_FSG_edge)
    #bin_NF=(bin_NF+jnk)>0
    bin_NFSG.save(loc_bin_NFSG)
else:
    bin_NFSG=arcpy.Raster(loc_bin_NFSG)

