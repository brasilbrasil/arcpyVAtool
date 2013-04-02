#USER INPUT
datadir="Y:/Py_code/results/all/" 
#datadir="C:/Users/lfortini/Data/Py_code/results/all/" 
#2_BIT: "slr", "Migrate",  "intersect", "fragmentation", "core_biome", "simplified_FCE", "simplified_CCE", "lava_flows", "refuge", "COR_CCE", "COR_CCE"
#4_BIT: "GBU", "response_zone"
ID_text=["slr", "Migrate",  "intersect", "fragmentation", "core_biome", "simplified_FCE", "simplified_CCE", "lava_flows", "refuge", "COR_CCE", "COR_CCE", "GBU", "response_zone"] #va=CCE, CC=FCE
bit_lengths=["2_BIT", "2_BIT", "2_BIT", "2_BIT", "2_BIT", "2_BIT", "2_BIT", "2_BIT", "2_BIT", "2_BIT", "2_BIT", "4_BIT", "4_BIT"]
file_size_threshold=15 #in Mb, will only reduce file size if file is bigger than threshold

#END USER INPUT
import os
mxd=arcpy.mapping.MapDocument("CURRENT")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
arcpy.env.compression = "LZW"

def del_layer(layer_name):	
	for df in arcpy.mapping.ListDataFrames(mxd):
	    for lyr in arcpy.mapping.ListLayers(mxd, "", df):
		if lyr.name.lower() == layer_name:
		    arcpy.mapping.RemoveLayer(df, lyr)
	return

for i in range(len(ID_text)):
    for root, dirs, files in os.walk(datadir):
	for f in files:
            if ID_text[i] in f:
		if f[-4:]==".tif":
                    jnk=rastername=os.path.join(root, f)
                    if file_size_threshold>0:
                        if (os.path.getsize(jnk)/(1024*1024.0))>file_size_threshold:   
                            #rastername=rastername_u.encode('ascii','replace')
                            print "starting %s" %(f)
                            tiffl=root+"/temp_"+f
                            print tiffl
                            
                            arcpy.CopyRaster_management(rastername, tiffl, "LZW", "","0","","",bit_lengths[i]) #COMPRESSION!
                            arcpy.BuildRasterAttributeTable_management(tiffl, "")
                            print 'Saved %s' %(rastername)
                            
                            arcpy.Delete_management(jnk)
                            arcpy.Rename_management(tiffl,jnk)
                            print "resaved %s" %(jnk)

