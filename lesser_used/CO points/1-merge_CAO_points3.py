#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#do not have point shapefile open by any other application, especially if chosing to overwrite dbf file

#USER INPUT
CAO_data_dir="C:/Users/lfortini/Data/VA data/CAO/"
#CSVs=["corrected_CO_dataXY_FWS_new2.csv", "corrected_CO_dataXY_herrit.csv"] #files to be merged
CSVs=["corrected_CO_dataXY_HFBS.csv", "corrected_CO_data3_merged.csv"] #files to be merged
reference_projection_file="heritagepoints_plants.shp" #the projection of this file will be used to create shp with processed points, must be in the same working directory
#outname="corrected_CO_data3_merged"
outname="corrected_CO_data4_merged_with_HFBS"

#END USER INPUT
#START UNDERHOOD
import os
import arcpy
import arcpy.sa
import csv
import shutil
from dbfpy import dbf #module for r/w dbf files available at http://dbfpy.sourceforge.net/
arcpy.env.overwriteOutput = True
arcpy.env.workspace = CAO_data_dir

csvpath=CAO_data_dir+outname+".csv"
shppath=CAO_data_dir+outname+".shp"
#CREATE OUTPUT TABLE
#Spp_data=[]
#Spp_data.append(cols)

csvname=CAO_data_dir+CSVs[0]
f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
reader = csv.reader(f)
headers = reader.next()
column = {}
for h in headers:
    column[h] = []

for CSV in CSVs:
    csvname=CAO_data_dir+CSV
    f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
    reader = csv.reader(f)
    headers = reader.next()
    #for header in headers:    
    for row in reader:
        for h, v in zip(headers, row):
          column[h].append(v)

#save_results_to_table
if arcpy.Exists(csvpath): #delete previous version of output file if it exists
    try:
	os.remove(csvpath)
    except:
    	pass
ofile = open(csvpath, 'wb')
writer = csv.writer(ofile, dialect='excel')

for i in range(len(column[h])):
    if i==0:
        jnk=headers
    else:        
        jnk=[]
        for head in headers:
            jnk.append(column[head][i])
    writer.writerow(jnk)
ofile.close()

fc=reference_projection_file
sr = arcpy.Describe(fc).spatialReference

arcpy.MakeXYEventLayer_management (csvpath, "X", "Y", "correct_CO_data", sr,"")
arcpy.CopyFeatures_management("correct_CO_data", shppath, "", "0", "0", "0")



#EXTRA:
#    suby=[column["Y"][i] for i in indices]
#    subsp=[column["sp_name"][i] for i in indices]  
  #Bs=f7(suby)
  #for b in Bs:
  #  b_indices=all_indices(b,suby)
  #  b_indices=all_indices(b[0],suby)
  #  c=f7(subsp)
  #
  #for val in b:
  #  indices=all_indices(val,x)
  #  subsp=[column["sp_name"][i] for i in indices]
  #  c=f7(subsp)
  #column["Y"][indices]

    
#for DBF in DBFs:
#    row_data=[]
#    dbfname=CAO_data_dir+DBF
#    print dbfname
#    db = dbf.Dbf(dbfname)    
#    
#    for i in range(len(db)): #i=2 for debug
#        row_data=[]
#
#        for col in cols:
#            jnk=db[i][cols]
#            row_data.append(jnk)
#    Spp_data.append(row_data)
#    del db	
##finish loop

