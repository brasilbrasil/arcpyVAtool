#USER INPUT
sp_temps=[3, 9, 15, 23, 35, 55, 68, 70, 78, 84, 94, 96, 99, 100, 119, 120, 167, 173, 176, 181, 200, 207, 210, 221, 223, 226, 231, 234, 240, 242, 247, 274, 278, 287, 312, 315, 351, 395, 438, 445, 453, 456, 458, 466, 482, 491, 492, 509, 513, 528, 609, 596, 598, 605, 618, 620, 636, 641, 646, 655, 669, 704, 713, 761, 767, 773, 776, 782, 784, 817, 818, 860, 866, 889, 891, 890, 915, 924, 936, 938, 944, 954, 981, 983, 988, 989, 992, 997, 1020, 1021, 1027, 1058] #range(4,6)
other_term="response_zone"
other_term2="" #.tif

rootdir=r"Y:/PICCC_analysis/plant_landscape_va_results/redone_w_eff_CE/results/all/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)
resultsdir="Y:/PICCC_analysis/data_requests/AI_data_request_150114/response_maps/green/"

#END USER INPUT

#START UNDERHOOD
del_terms=[]
for sp_temp in sp_temps:
    sp_code=str(sp_temp)
    lspcode=len(sp_code)
    new_sp_code=(4-lspcode)*'0'+sp_code
    del_terms.append(new_sp_code)

import os
import shutil
#import arcgisscripting
from types import *
import fnmatch
#arcpy.env.overwriteOutput = True
#arcpy.env.workspace = resultsdir
#mxd=arcpy.mapping.MapDocument("CURRENT")
#arcpy.env.compression = "LZW"

#del_term = del_terms[0]
#for del_term in del_terms:
#    print "starting with " + del_term
root_src_dir = rootdir
root_dst_dir = resultsdir
for src_dir, dirs, files in os.walk(root_src_dir):
    for f in files:
        if any(x in f for x in del_terms):
            if other_term in f:
                if other_term2 in f:
                    print "match found: " + f
                    dst_dir = src_dir.replace(root_src_dir, root_dst_dir)
                    if not os.path.exists(root_dst_dir):
                        os.mkdir(root_dst_dir)
                    if not os.path.exists(dst_dir):
                        os.mkdir(dst_dir)
                    src_file = os.path.join(src_dir, f)
                    dst_file = os.path.join(dst_dir, f)
                    if os.path.exists(dst_file):
                        os.remove(dst_file)
                    shutil.copy(src_file, dst_dir)
    #print "done with " + del_term