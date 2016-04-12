#this code has several features:
#the csv list may specify the file to be copied/ moved

#USER INPUT
#based on moveAndRenameFile.csv, to be placed in destination directory
sourceDir_str=r"Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/range maps archipelago/" #what is part of directory string that will be changed?
destinationDir_str="Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/range maps archipelago excluded spp/" #what will it be changed to?
find_only=True #test your results first!!
delete_source=False

#UNDERHOOD
import os
import csv
import shutil

# make an empty dictionary which will hold the keys
csvname=destinationDir_str+'moveAndRenameCoastalCEs.csv'
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
Source_file=column['Source_file']


Source_file_n = Source_file[100]
for Source_file_n in Source_file: #iterate through number of rows in CSV file
    src_file = Source_file_n
    dst_file = src_file.replace(sourceDir_str,destinationDir_str)

    if os.path.exists(Source_file_n):
        print "moving " + Source_file_n
        if not find_only:
            #os.rename(fileName, newName)
            #src_file = os.path.join(Source_file_n, fileName)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            directory=os.path.dirname(dst_file)
            if not os.path.exists(directory):
                os.makedirs(directory)
            shutil.copy(src_file, dst_file)
            if delete_source:
                os.remove(src_file)
    else:
        print "did not find " + Source_file_n



