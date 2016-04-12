#this code has several features:
#the csv list may specify the directory for each file to be copied
#if NA is specified as the directory, script will use default sourceDir
#if exact match is specified, only full file name matches are considered and replaced

#USER INPUT
sourceDir=r"Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/range maps archipelago reprojected 2bits/" #what is part of directory string that will be changed? #DD A1B HRCM v2 CEs // SD RCP85 CEs // SD RCP45 CEs
destinationDir="Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/range maps archipelago reprojected 2bits excluded spp/" #what will it be changed to?
create_log_source=False #If turned on, will create a txt file for each file copied with info about transfer
create_log_destination=False #If turned on, will create a txt file for each file copied with info about transfer
find_only=False #test your results first!!
#based on moveAndRenameFile.csv, to be placed in destination directory
delete_source=True

#UNDERHOOD
import os
import csv
import shutil
os.chdir(sourceDir)
if not os.path.exists(destinationDir):
    os.mkdir(destinationDir)
# make an empty dictionary which will hold the keys
csvname=destinationDir+'moveAndRenameCoastalCEs.csv'
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
New_name=column['New_name']
Old_name=column['Old_name']
Source_dir=column['Source_dir']
Exact=column['Exact']
Dest_dir=column['Dest_dir']

#code specific to plant VA
#add leading zeros to number string
del_terms=[]
for sp_temp in Old_name:
    sp_code=str(sp_temp)
    lspcode=len(sp_code)
    new_sp_code=(4-lspcode)*'0'+sp_code
    del_terms.append(new_sp_code)
Old_name=del_terms
#adding space before name
#New_name=[" " + x for x in New_name]
#end plant VA specific code

i=0
Source_dir_n = Source_dir[0]
for Source_dir_n in Source_dir: #iterate through number of rows in CSV file
    Old_name_n=Old_name[i]
    if New_name[i] =="NA":
        New_name_n=Old_name_n
    else:
        New_name_n=New_name[i]
    Exact_n=Exact[i]
    Dest_dir_n=Dest_dir[i]

    if Source_dir_n=="NA":
        Source_dir_n=sourceDir
    if Dest_dir_n=="NA":
        Dest_dir_n=destinationDir
    if Exact_n=="N":
        Exact_n=False
    else:
        Exact_n=True

    #jnk=os.listdir(Source_dir_n)[13]
    root_src_dir = Source_dir_n
    root_dst_dir = Dest_dir_n
    for src_dir, dirs, files in os.walk(Source_dir_n):
        for fileName in files:
            replace=False
            if Exact_n:
                if Old_name_n == fileName:
                    replace=True
            else:
                if Old_name_n in fileName:
                    replace=True
            if replace:
                dst_dir = src_dir.replace(root_src_dir, root_dst_dir)
                src_file = os.path.join(src_dir, fileName)

                newName=fileName.replace(Old_name_n, New_name_n)
                print "will rename " + fileName + " from " + Source_dir_n + " to " + newName + " and place it at " + Dest_dir_n
                if not find_only:
                    #os.rename(fileName, newName)
                    #src_file = os.path.join(Source_dir_n, fileName)
                    dst_file = os.path.join(Dest_dir_n, newName)
                    if os.path.exists(dst_file):
                        os.remove(dst_file)
                    shutil.copy(src_file, dst_file)
                    if delete_source:
                        os.remove(src_file)
                    if create_log_source:
                        import time
                        date=time.strftime("%Y%m%d")
                        #print "creating record of move on source"
                        jnk=Source_dir_n + "move_record_"+date+ "_"+ fileName+ ".txt"
                        file = open(jnk, 'w+')
                        jnk=fileName +"\n" + "was moved from" + "\n" + Source_dir_n +"\n" + "to" +"\n" + Dest_dir_n +"\n" + "on" +"\n" + date +"\n"
                        file.write(jnk)
                        if Old_name_n!=New_name_n:
                            jnk="\n" + "#######" + "\n" + "file renamed to " +"\n" + newName
                            file.write(jnk)
                        file.close()
                        #file name: move_record_DATE_file
                        #content: from, to,

                    if create_log_destination:
                        import time
                        date=time.strftime("%Y%m%d")
                        #print "creating record of move on source"
                        jnk=Dest_dir_n + "move_record_"+date+ "_"+ fileName+ ".txt"
                        file = open(jnk, 'w+')
                        jnk=fileName +"\n" + "was moved from" + "\n" + Source_dir_n +"\n" + "to" +"\n" + Dest_dir_n +"\n" + "on" +"\n" + date +"\n"
                        file.write(jnk)
                        if Old_name_n!=New_name_n:
                            jnk="\n" + "#######" + "\n" + "file renamed to " +"\n" + newName
                            file.write(jnk)
                        file.close()
                        #file name: move_record_DATE_file
                        #content: from, to,

    i=i+1

