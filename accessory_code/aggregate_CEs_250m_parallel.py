#python D:\Dropbox\code\arcpyVAtool\accessory_code\aggregate_CEs_500m_parallel.py
#must run this from cmd with script above, python must be on system path

#USER INPUT
rootdir=r"Y:/PICCC_data/VA data/CEs/"
results_dir="Y:/PICCC_data/VA data/CEs_250m_parallel/"
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
#from multiprocessing.dummy import Pool as ThreadPool

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

if not os.path.exists(results_dir):
    os.mkdir(results_dir)

def parallel_folder_aggregate(f):
    print('worker', os.getpid(), ' running and doing ', f)
    jnk=randrange(10000)
    tmp_dir="D:/temp/arcgis/"+str(jnk)+"/"
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    arcpy.env.scratchWorkspace = tmp_dir
    cell_factor=250/30
    out_name=results_dir+f
    if arcpy.Exists(out_name) and overwrite==False:
		print "raster " + out_name+" already done"
    else:
        #maskedRaster = arcpy.sa.SetNull(mask_layer, f, "Value = 100")
        if arcpy.CheckExtension("Spatial") == "Available":
        	arcpy.CheckOutExtension("Spatial")
        outRas=arcpy.sa.Aggregate(f, cell_factor, "MAXIMUM", "TRUNCATE", "DATA")
        arcpy.CopyRaster_management(outRas,out_name,"","","","","","2_BIT")
        arcpy.CheckInExtension("Spatial")


if __name__ == '__main__':
    rasterList = arcpy.ListRasters("*", "tif")
    #rasterList=rasterList[0:10]
    #f=rasterList[0]
    #parallel_folder_aggregate(f)
    t1 = time.time()
    pool = Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
    #pool = ThreadPool(24) # Sets the pool size to 4
    results=pool.map(parallel_folder_aggregate, rasterList)
    pool.close()
    pool.join()
    t2 = time.time()
    print results
    print len(rasterList),"elements","pool.map() time",(t2-t1),"s"


#multiple arguments
#python D:\Dropbox\code\arcpyVAtool\accessory_code\aggregate_CEs_500m_parallel.py