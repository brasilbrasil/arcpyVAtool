#disable background processing (arcgis geoprocessing options) as it does not work well- python will call variables for routines that are not yet complete from previous routine!!
#python D:\Dropbox\code\arcpyVAtool\core_code\parallel_debug.py
#if running parallel, must run this from cmd with script above, python must be on system path

#this code works without a problem. Not sure why standard code does not.

#USER INPUT
island="all"
rootdir=r"Y:/PICCC_analysis/plant_landscape_va_results/testRuns14/" #location for outputs. ?whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)
ce_data_dir=r"Y:/PICCC_data/VA data/CEs_500m/" #location of climate envelope files
keep_intermediary_output=0 #enter 1 for debug reasons, will a lot of intermediary analyses outputs for inspection
#send_email_error_message=0
overwrite=0
parallel=True #for multiprocessing across species
all_files_in_directory=1
subset_of_CEs=[3,100]
#what pieces to run?
pre_process_envelopes=True
#START UNDERHOOD
resultsdir0=r"%sresults/%s/" %(rootdir, island)
datadir=ce_data_dir

import os
import arcpy
import arcpy.sa
import math
import csv
import shutil
import numpy
import arcgisscripting
from types import *
import time
import traceback
import sys
#from dbfpy import dbf #module for r/w dbf files with py available at http://dbfpy.sourceforge.net/
import fnmatch
from arcpy import env
from random import randrange
import itertools
import multiprocessing
from multiprocessing import Pool, freeze_support

arcpy.env.overwriteOutput = True
arcpy.env.workspace = datadir
arcpy.env.compression = "LZW"

if not os.path.exists(resultsdir0):
    os.makedirs(resultsdir0)
t0 = time.time()
kio=keep_intermediary_output
def va_metric_wrapper(VA_func, i):
    if arcpy.CheckExtension("Spatial") == "Available": #must check out license within worker process, as license does not seem to be inherited by parallel workers
        arcpy.CheckOutExtension("Spatial")
    t0 = time.time()
    print('worker', os.getpid(), ' running and doing ', i)
    jnk=randrange(100000)
    tmp_dir="D:/temp/arcgis/"+str(jnk)+"/"
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    arcpy.env.scratchWorkspace = tmp_dir
    arcpy.env.workspace= tmp_dir

    #Get species name, sp code, check if species already have been done
    jnk=CCE_Spp[i]
    jnk.encode('ascii','replace')
    inRaster = ce_data_dir + jnk
    sp_code_st=inRaster[-8:-4]
    resultsdir=resultsdir0+sp_code_st+"/"
    sp_code=str(int(sp_code_st)) #get rid of extra zeros

    jnk=VA_func(sp_code_st, resultsdir, sp_code)
    arcpy.CheckInExtension("Spatial") # Check in the 3D Analyst extension so other users can access it

    if jnk[1]:
        print VA_func.__name__ + 'not applicable for species %s' %(sp_code_st);
    else:
        fx_nm=VA_func.__name__
        if not jnk[0]:
            t1 = time.time();
            time_elp=int(t1-t0)

            print 'took %i secs to apply %s for species %s' %(time_elp, fx_nm, sp_code_st);
        else:
            print 'already applied %s for species %s' %(fx_nm, sp_code_st);
    return

def pre_parallel_wrapper(zipped_args):
    return va_metric_wrapper(*zipped_args)
def get_num_attributes(raster, value):
    jnk = arcpy.GetRasterProperties_management(raster, value)
    jnk= jnk.getOutput(0)
    jnk=float(jnk)
    return jnk

try:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")

    arcpy.env.workspace = datadir
    if all_files_in_directory==1:
        import glob
        jnk=glob.glob(datadir+"CCE*.tif")
        CCE_Spp=[os.path.basename(x) for x in jnk]
        if len(subset_of_CEs)>0:
            CCE_Spp=CCE_Spp[subset_of_CEs[0]:subset_of_CEs[1]]
    else:
        CCE_Spp=['CCE0220.tif'] #for lanai cce0003, cce0055

    if pre_process_envelopes:
        i=0 #for debug
        def pre_process_env_fx2(sp_code_st, resultsdir, sp_code): #also uses use_bio_region_filter, CO_lyr, island, landscape_factor_dir
            metric_NA=True
            sp_code_st0=sp_code_st
            loc_COR_FCE=r"%sCOR_FCE%s.tif" %(resultsdir,sp_code_st)

            #MAP- SIMPLIFY CCE/CAO RASTER TO SINGLE CLASS
            inRaster = ce_data_dir + CCE_Spp[i]
            inRaster=arcpy.Raster(inRaster)
            jnk=get_num_attributes(inRaster, "MAXIMUM")
            print "maximum raster value for " + sp_code_st + " is " + str(jnk)
            metric_previously_done=False
            metric_NA=False
            return metric_previously_done, metric_NA

        if not parallel:
            for i in range(len(CCE_Spp)):
                va_metric_wrapper(pre_process_env_fx2, i)
        else:
            import itertools
            import multiprocessing
            from multiprocessing import Pool, freeze_support
            if __name__ == '__main__':
                pool=Pool(processes=multiprocessing.cpu_count()) #multiprocessing.cpu_count()
                pool.map(pre_parallel_wrapper, itertools.izip(itertools.repeat(pre_process_env_fx2, len(CCE_Spp)), range(len(CCE_Spp))))
                pool.close()
                import time
                time.sleep(10) #give it some time before trying to terminate pool to avoid ' access is denied'  error
                #if pool.poll() is None: #http://stackoverflow.com/questions/16636095/terminating-subprocess-in-python2-7
                pool.terminate()
                pool.join()


except arcpy.ExecuteError:
    msgs = arcpy.GetMessages(2) # Get the tool error messages
    arcpy.AddError(msgs) # Return tool error messages for use with a script tool
    print msgs # Print tool error messages for use in Python/PythonWin

except socket.error as error: #http://stackoverflow.com/questions/18832643/how-to-catch-this-python-exception-error-errno-10054-an-existing-connection
    if error.errno == errno.WSAECONNRESET:
        reconnect()
        retry_action()
    else:
        raise
except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)
    jnk_msg=""
    message = "\n\n"+ jnk_msg+ "\n\n" + "error while calculating vulnerabilities"+ "\n\n" + str(pymsg) + "\n" + str(msgs)
    print message
finally:
    arcpy.CheckInExtension("Spatial") # Check in the 3D Analyst extension so other users can access it
