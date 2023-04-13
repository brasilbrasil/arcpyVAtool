#python D:\Dropbox\code\arcpyVAtool\accessory_code\process_new_CEs\4_create_raster_attribute_table_for_CEs_500m_parallelC.py
#must run this from cmd with script above, python must be on system path

#USER INPUT
rootdir=r"Y:/PICCC_data/VA data/DD A1B HRCM v2 CEs/range maps archipelago reprojected/" #"Y:/PICCC_data/VA data/CEs_500m/"
overwrite=False

#END USER INPUT
import os
import arcpy
from random import randrange
from types import *
import time
#https://medium.com/@thechriskiehl/parallelism-in-one-line-40e9b2b36148
from multiprocessing import Pool
import multiprocessing

arcpy.env.overwriteOutput = True
arcpy.env.workspace = rootdir
arcpy.env.compression = "LZW"
#arcpy.CreateFileGDB_management("D:/temp/arcgis/", "scratchoutput"+str(jnk)+".gdb")
#arcpy.env.scratchWorkspace = "D:/temp/arcgis/scratchoutput"+str(jnk)+".gdb"
#cannot have gdb scratch file because of parallelization
""""
http://blogs.esri.com/esri/arcgis/2012/09/26/distributed-processing-with-arcgis-part-1/
http://pythongisandstuff.wordpress.com/2013/07/31/using-arcpy-with-multiprocessing-%E2%80%93-part-3/
Whenever possible, take advantage of the ?in_memory? workspace for creating temporary data
to improve performance. However, depending on the size of data being created in-memory, it may
be necessary to write temporary data to disk. Temporary datasets cannot be created in a file
geodatabase because of schema locking. Deleting the in-memory dataset when you are finished can
prevent out of memory errors.
"""

def parallel_create_raster_attribute_table(f):
    print('worker', os.getpid(), ' running and doing ', f)
    jnk=randrange(1000000)
    tmp_dir="D:/temp/arcgis/"+str(jnk)+"/"
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    arcpy.env.scratchWorkspace = tmp_dir
    arcpy.BuildRasterAttributeTable_management(f, "Overwrite")


if __name__ == '__main__':
    rasterList = arcpy.ListRasters("*", "tif")
    t1 = time.time()
    pool = Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
    results=pool.map(parallel_create_raster_attribute_table, rasterList)
    pool.close()
    pool.join()
    t2 = time.time()

