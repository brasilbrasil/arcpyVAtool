#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#do not have point shapefile open by any other application, especially if chosing to overwrite dbf file

#USER INPUT
CAO_data_dir="C:/Users/lfortini/Data/VA data/CAO/"
merge_subspp=1
correct_last_seen_info=1
sp_col_name="SciName" #SciName #SNAME
last_seen_col_name="LastObs" #LastObs #LASTOBS
accuracy_col_name="Accuracy" #Accuracy #ACCURACY
x_col_name="POINT_X" #POINT_X #X
y_col_name="POINT_Y" #POINT_Y #Y

#WHICH SPECIES ARE THERE
#dbfname="%sFWSHeritageDatabase_PlantUpdates_Aug2012.dbf" %(CAO_data_dir) #FWSHeritageDatabase_PlantUpdates_Aug2012 #heritagepoints_plants
#outname="corrected_CO_dataXY_FWS_new2" #corrected_CO_dataXY_FWS_new2 #corrected_CO_dataXY_herrit

dbfname="%sHFBS_DataMerge_FAA_12Oct12_ALL_nativeonly.dbf" %(CAO_data_dir) #FWSHeritageDatabase_PlantUpdates_Aug2012 #heritagepoints_plants
outname="corrected_CO_dataXY_HFBS" #corrected_CO_dataXY_FWS_new2 #corrected_CO_dataXY_herrit
#END USER INPUT

#START UNDERHOOD
import os
import arcpy
import arcpy.sa
#import xlrd
import csv
import shutil
#import unicodedata
from dbfpy import dbf #module for r/w dbf files available at http://dbfpy.sourceforge.net/
arcpy.env.overwriteOutput = True
arcpy.env.workspace = CAO_data_dir
csvpath=CAO_data_dir+outname+".csv"
shppath=outname+".shp"

db = dbf.Dbf(dbfname)
	    
#SPECIES CORRECTION LIST
csvname="%sspp_name_synonyms.csv" %(CAO_data_dir)
synonyms_file = csv.reader(csvname)
f = open(csvname, 'rb') #http://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is
reader = csv.reader(f)
headers = reader.next()
column = {}
for h in headers:
    column[h] = []
for row in reader:
   for h, v in zip(headers, row):
     column[h].append(v)

Old_sp_names=column['Alternate name']
New_sp_names=column['Correct name']
islands_present=column['Island']
all_sp_codes=column['species codes']
all_sp_errors=column['Error type']

#CREATE OUTPUT TABLE
Spp_data=[]
XY_data=[]
AUX_data=[]
Sp_data=['X', 'Y', 'sp_name', 'ID_error', 'JP_code', 'lastseen', 'accuracy']

Spp_data.append(Sp_data)

for i in range(len(db)): #i=2 for debug
	#SELECT EACH INDIVIDUAL SPECIES FROM SHP
	#expr="db[0]['%s']" %(sp_col_name)
	#eval()
	sp=db[i][sp_col_name]
	#sp = sp.replace(".", "") #get rid of punctuations to avoid filen renaming errors
	#sp = sp.replace("-", " ") #get rid of punctuations to avoid filen renaming errors
	nf=0
	error_type='ok'

	try:
		Sp_index=Old_sp_names.index(sp)
	except ValueError:
		sp='%s not found' %(sp)
		JP_code=0
		nf=1
		error_type='not found'
		pass
	if nf==0:
		if type(Sp_index)=='list':
		    islands_present=islands[Sp_index]
		    Sp_index=Sp_index[islands_present==island]    
		if len(all_sp_errors[Sp_index])==0:
			sp=New_sp_names[Sp_index]
			JP_code=all_sp_codes[Sp_index]
		else:
			if all_sp_errors[Sp_index]== 'sub sp':
				sp=New_sp_names[Sp_index]
				JP_code=all_sp_codes[Sp_index]
				error_type=all_sp_errors[Sp_index]
			else:
				sp='%s incorrect' %(sp)
				JP_code=0
				error_type=all_sp_errors[Sp_index]
	
	try:
	    last_seen=db[i][last_seen_col_name]
	    last_seen=str(last_seen)
	except:
	    last_seen=''    
	if correct_last_seen_info==1:
	  if type(last_seen)==int:
	    if last_seen==1:
	      last_seen=1984
	    if last_seen==0:
	      last_seen=1500
	  if type(last_seen)==str:
	    if len(last_seen)>3:
	      last_seen=last_seen[:4]
	      last_seen = int(last_seen.replace("?", "9")) #assume it was in latest possible year
		
	accuracy=db[i][accuracy_col_name]
	
	Xcord=db[i][x_col_name]
	Ycord=db[i][y_col_name]
	
	Sp_data=[Xcord, Ycord, sp, error_type, JP_code, last_seen, accuracy]
	Spp_data.append(Sp_data)
	
#finish loop

#save_results_to_table
import csv

if arcpy.Exists(csvpath): #delete previous version of output file if it exists
    try:
	os.remove(csvpath)
    except:
    	pass
ofile = open(csvpath, 'wb')
writer = csv.writer(ofile, dialect='excel')
for i in range(len(Spp_data)):
	writer.writerow(Spp_data[i])
ofile.close()

fc=dbfname[:-4]+'.shp'
sr = arcpy.Describe(fc).spatialReference

arcpy.MakeXYEventLayer_management (csvpath, "X", "Y", "correct_CO_data", sr,"")
arcpy.CopyFeatures_management("correct_CO_data", shppath, "", "0", "0", "0")

#extras:

	#if overwrite_dbf==1:
	#	db[i]["SNAME"]=sp
	#	db[i]["LASTOBS"]=last_seen

#if overwrite_dbf==1:
#	db.store()
		
#if debuging==1:
#	print 'will rewrite in 30 seconds'
#	time.sleep(30)
#	print 'done rewriting'
#	src="%sheritagepoints_plants_backup.dbf" %(CAO_data_dir)
#	dst="%sheritagepoints_plants.dbf" %(CAO_data_dir)
#	shutil.copyfile(src, dst) #"%sheritagepoints_plants.dbf" %(CAO_data_dir)

#dbfname="%sspecies_name_synonyms.dbf" %(CAO_data_dir)
#sp_name_corrct_db = dbf.Dbf(dbfname)
#Old_sp_names=db[:]["Alternate name"] #Old_sp_names
#New_sp_names=db[:]["Correct name"] #New_sp_names
#islands_present=db[:]["islands"] #islands
#all_sp_codes=db[:]["species codes"] #islands

#csvname="%sspp_name_synonyms.csv" %(CAO_data_dir)
#synonyms_file = xlrd.open_workbook(xlsname)
#synonym_sheet= synonyms_file.sheet_by_index(0) #synonym sheet must be first one in file
#syn_headings= synonym_sheet.row(0)

#Old_sp_names=db[:]["Alternate name"] #Old_sp_names
#New_sp_names=db[:]["Correct name"] #New_sp_names
#islands_present=db[:]["islands"] #islands
#all_sp_codes=db[:]["species codes"] #islands

#synonym_sheet= synonyms_file.sheet_by_index(0) #synonym sheet must be first one in file
#syn_headings= synonym_sheet.row(0)

