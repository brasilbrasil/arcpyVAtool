#USER INPUT
rootdir=r"C:/Users/lfortini/Data/LANDFIRE-2011_EVT/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files) 
in_raster="hi_110evt"

#START UNDERHOOD
import arcpy

arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir

basic_cover_loc=rootdir+"landfire_simple_veg.tif"

#Reclassify (in_raster, reclass_field, ([[oldValue, newValue],...]), "NO DATA")
#basic_cover=arcpy.sa.Reclassify(in_raster,"VALUE",([[11, 0], [21, 0], [22, 0], [23, 0], [24, 0], [31, 0], [82, 0], [2536, 4], [2537, 4], [2538, 4], [2545, 2], [2546, 4], [2547, 4], [2548, 0], [2549, 1], [2552, 3], [2553, 3], [2554, 3], [2555, 3], [2806, 3], [2808, 3], [2809, 3], [2810, 3], [2811, 2], [2813, 3], [2814, 3], [2815, 3], [2816, 3], [2817, 2], [2818, 2], [2819, 1], [2820, 1], [2821, 2], [2822, 1], [2823, 1], [2824, 2], [2825, 0], [2826, 4], [2827, 4], [2828, 2]]))
basic_cover=arcpy.sa.Reclassify(in_raster,"VALUE",([[11, 0], [21, 0], [22, 0], [23, 0]]))
