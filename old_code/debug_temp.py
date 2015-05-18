i=0
t0 = time.time()
#Get species name, sp code, check if species already have been done
jnk=CCE_Spp[i]
jnk.encode('ascii','replace')
inRaster = ce_data_dir + jnk
sp_code_st=inRaster[-8:-4]
resultsdir=resultsdir0+sp_code_st+"/"
sp_code=str(int(sp_code_st)) #get rid of extra zeros



metric_NA=True
Sp_index=all_sp_codes.index(sp_code)
loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
if arcpy.Exists(loc_COR_CCE):
    #CALC area in each habitat type
    opath="%sDBFs/vegtype_areas%s.csv" %(resultsdir,sp_code_st)
    if arcpy.Exists(opath)==False or overwrite==1:
        CCE_temp=arcpy.Raster(loc_COR_CCE)
        inRaster = CCE_temp
        outname=r"%sDBFs/vegtype_areas%s.dbf" %(resultsdir,sp_code_st)
        arcpy.sa.TabulateArea(CCE_temp,"VALUE",veg_types_layer,"VALUE",outname)
        #db = dbf.Dbf(outname)
        #rec=db[0]
        #veg_area=[0]*14
        #for ire in range(0,14):
        #       jnk="VALUE_%i" %(ire)
        #       try:
        #                       area_jnk=rec[jnk]/1000000
        #                       veg_area[ire]=area_jnk
        #       except:
        #                       pass
        temp_zones=range(0,14)
        veg_area=zonal_area_from_dbf2(outname, temp_zones)

        save_temp_csv_data(veg_area, opath)
        del CCE_temp; del inRaster; del outname; del rec; del db; del veg_area; del opath;
        metric_previously_done=False
        metric_NA=False
    else:
        metric_previously_done=True
        metric_NA=False
