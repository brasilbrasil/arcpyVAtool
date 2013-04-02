sp_code_st='0126'
loc_core_biome=r"%score_biome_%s.tif" %(resultsdir,sp_code_st)
loc_lava_flows=r"%slava_flows_%s.tif" %(resultsdir,sp_code_st)
loc_response_zone=r"%sresponse_zone_%s.tif" %(resultsdir,sp_code_st)
response_zones=arcpy.Raster(loc_response_zone)
mask_raster=response_zones
val_raster=loc_core_biome
array_index=[1,2,3]
alt_zonal_stats(mask_raster, val_raster, array_index)

def alt_zonal_stats(zone_raster, var_raster, zone_vals):
    def get_num_attributes(raster, value):
            jnk = arcpy.GetRasterProperties_management(raster, value)
            jnk= jnk.getOutput(0) 	
            jnk=float(jnk)
            return jnk
        
    mask_raster_standard=mask_raster*val_raster/val_raster
    val_raster_standard=mask_raster*val_raster/mask_raster
    
    var_zone_mean=['NA']*len(array_index)
    var_zone_area=['NA']*len(array_index)
    var_zone_std=['NA']*len(array_index)
    for z in range(len(array_index)):
        #jnk=arcpy.sa.Setnull(mask_raster_standard==i)
        expr=""" "Value" <> %i """ %(array_index[z])
        #expr="Value>%i" %(i)
        temp1=arcpy.sa.SetNull(mask_raster_standard,val_raster_standard,expr)
        temp1_pixel_sizeX=get_num_attributes(temp1, "CELLSIZEX")
        temp1_pixel_sizeY=get_num_attributes(temp1, "CELLSIZEY")
        temp1_pixel_area=temp1_pixel_sizeX*temp1_pixel_sizeY
        temp1_mean=get_num_attributes(temp1, "MEAN")
        temp1_std=get_num_attributes(temp1, "STD")
        
        if temp1_mean==0 and temp1_std==0:
            temp1_area=0
        else:
            Rows = arcpy.SearchCursor(temp1) 
            SomeValue = 'Count' # or some other column header name
            for row in Rows:
                val = row.getValue( SomeValue ) 
            temp1_area=val*temp1_pixel_area
        var_zone_area[z]=temp1_area
        var_zone_mean[z]=temp1_mean
        var_zone_std[z]=temp1_std
        del temp1
    zone_val_return=[var_zone_area,var_zone_mean,var_zone_std]
    return zone_val_return
    