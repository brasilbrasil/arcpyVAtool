import multiprocessing
import os
import re
import arcpy

def test_fx(i):
    x=i
    veg_area=[i,]
    save_temp_csv_data(veg_area, opath)
    print "the answer is %i" %(i)
    return

fc_list=[0,1,2]
pool = multiprocessing.Pool()
pool.map(test_fx, fc_list)
# Synchronize the main process with the job processes to
# ensure proper cleanup.
pool.close()
pool.join()
# End main