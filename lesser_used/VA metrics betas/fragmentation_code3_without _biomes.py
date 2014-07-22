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

ugly=rootdir+"HI_bad_and_ugly_map_maj.tif"
ugly=arcpy.Raster(ugly)

good=rootdir+"HI_good_map_maj.tif"
good=arcpy.Raster(good)

veg=rootdir+"landfire_veg_classes3_maj.tif"
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
loc_bin_NFSG=rootdir+"bin_Nhabitat.tif"
loc_bin_FSG_edge=rootdir+"bin_111.tif"
if arcpy.Exists(loc_bin_NFSG)==False:
    good_habitat=good-((steep+road+(veg==0))>0)
    good_habitat=good_habitat==1
    bin_NFSG=(steep+road+ugly+(veg==0))>0
    jnk=arcpy.sa.SetNull(bin_NFSG,1,"Value <1")
    jnk=arcpy.sa.EucDistance(jnk, edge_effect_size)
    jnk=jnk>0
    FSG_edge=arcpy.sa.Con(arcpy.sa.IsNull(jnk),0,jnk)*island_extent
    FSG_edge=(FSG_edge+steep+road+ugly+(veg==0))>0
    FSG_edge_and_core= (good_habitat*2)-(FSG_edge*good_habitat)
    FSG_edge_and_core=arcpy.sa.SetNull(FSG_edge_and_core,FSG_edge_and_core,"Value<1")
    #FSG_edge=FSG_edge+((veg==1)+(veg==2)+(veg==3))
    FSG_edge_and_core.save(loc_bin_FSG_edge)
    
    #bin_NF=(bin_NF+jnk)>0
    bin_NFSG.save(loc_bin_NFSG)
else:
    bin_NFSG=arcpy.Raster(loc_bin_NFSG)

