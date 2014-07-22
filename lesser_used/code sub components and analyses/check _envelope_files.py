import csv

datadir="C:/Users/lfortini/Data/VA data/NewCEs/"
prefix_or_suffix=0 #0- p, 1- s
ID_text=['FCE', 'CCE'] #va=CCE, CC=FCE

#END USER INPUT

import os
import fnmatch
mxd=arcpy.mapping.MapDocument("CURRENT")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
arcpy.env.compression = "LZW"

all_CE_names=[]
for i in range(len(ID_text)):
    if prefix_or_suffix==0:
        expr="%s*" %(ID_text[i])
    else:
        expr="*%s" %(ID_text[i])
    
    rasterList = arcpy.ListRasters(expr, "tif")
    
    for rastername_u in rasterList:
        rastername=rastername_u.encode('ascii','replace')
        sp_code=rastername[len(ID_text[i]):-4]
	
	CE_data=[ID_text[i], sp_code]
	all_CE_names.append(CE_data)

opath=r"%sall_ce_names.csv" %(datadir)
if arcpy.Exists(opath): #delete previous version of output file if it exists
	os.remove(opath) 
else:
	pass
ofile = open(opath, 'wb')
writer = csv.writer(ofile, dialect='excel')
for i in range(len(all_CE_names)):
	writer.writerow(all_CE_names[i])
ofile.close()