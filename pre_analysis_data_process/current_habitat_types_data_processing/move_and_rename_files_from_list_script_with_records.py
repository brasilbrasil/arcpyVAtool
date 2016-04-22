#this code has several features:
#the csv list may specify the directory for each file to be copied
#if NA is specified as the directory, script will use default sourceDir
#if exact match is specified, only full file name matches are considered and replaced

#USER INPUT
sourceDir=r"Y:/PICCC_analysis/community_SRE/necessary_data/HIGAP/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)
destinationDir="Y:/PICCC_data/VA data/landscape/revisedHIGAP/"
create_log_source=False
create_log_destination=False
find_only=False #test your results first!!
#based on moveAndRenameFile.csv, to be placed in destination directory

#UNDERHOOD
import os
import csv
import shutil
os.chdir(sourceDir)
if not os.path.exists(destinationDir):
    os.mkdir(dst_dir)
# make an empty dictionary which will hold the keys
csvname=destinationDir+'moveAndRenameFile.csv'
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



i=0
Source_dir_n = Source_dir[0]
for Source_dir_n in Source_dir:
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
    for fileName in os.listdir(Source_dir_n):
        replace=False
        if Exact_n:
            if Old_name_n == fileName:
                replace=True
        else:
            if Old_name_n in fileName:
                replace=True
        if replace:
            newName=fileName.replace(Old_name_n, New_name_n)
            print "will rename " + fileName + " from " + Source_dir_n + " to " + newName + " and place it at " + Dest_dir_n
            if not find_only:
                #os.rename(fileName, newName)
                src_file = os.path.join(Source_dir_n, fileName)
                dst_file = os.path.join(Dest_dir_n, newName)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_file)
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

