#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#do not have point shapefile open by any other application, especially if chosing to overwrite dbf file

#USER INPUT
CAO_data_dir="C:/Users/lfortini/Data/VA data/CAO/"
#CSV="corrected_CO_data3_merged.csv" #files to be merged
CSV="corrected_CO_data4_merged_with_HFBS.csv" #files to be merged
reference_projection_file="heritagepoints_plants.shp" #the projection of this file will be used to create shp with processed points, must be in the same working directory
#outname="corrected_CO_data2_merged_and_filtered2"
outname="corrected_CO_data4_merged_and_filtered"
remove_repeats=1 #if points have same exact X, Y and species name
correct_last_seen_info=1
remove_low_accuracy_pts=1
low_acc_class=["G", "U", "N"]
min_yr=1970

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
def f7(seq):
  seen = set()
  seen_add = seen.add
  # adds all elements it doesn't know yet to seen and all other to seen_twice
  seen_twice = set( x for x in seq if x in seen or seen_add(x) )
  # turn the set into a list (as requested)
  return list( seen_twice )

def all_indices(value, qlist):
    indices = []
    idx = -1
    while True:
        try:
            idx = qlist.index(value, idx+1)
            indices.append(idx)
        except ValueError:
            break
    return indices

csvname=CAO_data_dir+CSV
f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
reader = csv.reader(f)
headers = reader.next()
#for header in headers:    
for row in reader:
    #sp=
    for h, v in zip(headers, row):
      column[h].append(v)

if remove_repeats==1: #if points have same exact X, Y and species name
    x=column["X"]
    a=f7(x)
    to_del=[]
    for val in a:
      indices=all_indices(val,x)
      for index in indices:    
        sub_indices=indices[(indices.index(index)+1):]
        y1=column["Y"][index]
        sp1=column["sp_name"][index]
        for sub_index in sub_indices:      
          y2=column["Y"][sub_index]
          sp2=column["sp_name"][sub_index]
          if y1==y2 and sp1==sp2:
            try:
	      to_del.index(sub_index)
	    except ValueError:
	      to_del.append(sub_index)
	      pass
    #must add unique function    
    
    #DELETE ITEMS ON LIST
    rev_to_del=sorted(to_del, reverse=True)
    for del_row_index in rev_to_del:
        for header in headers:
            jnk=column[header]
            del jnk[del_row_index]
            column[header]=jnk
            #[column[header][i] for i in indices]
#column2=column
if correct_last_seen_info==1:
  for i in range(len(column["lastseen"])):
    last_seen=column["lastseen"][i]
    if type(last_seen)==int:
      if last_seen==1:
	last_seen=1984
      if last_seen==0:
	last_seen=1500
    else:
      last_seen=last_seen[:4]
      last_seen = int(last_seen.replace("?", "9")) #assume it was in latest possible year
    column["lastseen"][i]=last_seen  

if remove_low_accuracy_pts==1:
    to_del=[]
    for badclass in low_acc_class:
        jnk=all_indices(badclass,column["accuracy"])
        to_del.extend(jnk)    

    rev_to_del=sorted(to_del, reverse=True)
    for del_row_index in rev_to_del:
        for header in headers:
            jnk=column[header]
            del jnk[del_row_index]
            column[header]=jnk

if min_yr>0:
    to_del=[]
    for i in range(len(column["lastseen"])):
      if column["lastseen"][i]<min_yr:
        to_del.append(i)    
    rev_to_del=sorted(to_del, reverse=True)
    for del_row_index in rev_to_del:
        for header in headers:
            jnk=column[header]
            del jnk[del_row_index]
            column[header]=jnk    


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

