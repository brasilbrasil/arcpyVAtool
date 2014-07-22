mask_raster=response_zones
val_raster=loc_core_biome


def get_num_attributes(raster, value):
	jnk = arcpy.GetRasterProperties_management(raster, value)
	jnk= jnk.getOutput(0) 	
	jnk=float(jnk)
	return jnk
    
def f5(seq, idfun=None): 
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

array_index=[1,2,3]
mask_raster_standard=mask_raster*val_raster/val_raster
mask_pixel_sizeX=get_num_attributes(mask_raster_standard, "CELLSIZEX")
mask_pixel_sizeY=get_num_attributes(mask_raster_standard, "CELLSIZEY")
mask_pixel_area=mask_pixel_sizeX*mask_pixel_sizeY
mask_colcount=get_num_attributes(mask_raster_standard, "COLUMNCOUNT")
mask_rowcount=get_num_attributes(mask_raster_standard, "ROWCOUNT")
mask_min=get_num_attributes(mask_raster_standard, "MINIMUM")
mask_max=get_num_attributes(mask_raster_standard, "MAXIMUM")
jnk=mask_min-1
if jnk<0 and jnk >=-1:
    mask_no_data_val=mask_max+1
else:
    mask_no_data_val=mask_min-1

val_raster_standard=mask_raster*val_raster/mask_raster
val_pixel_sizeX=get_num_attributes(val_raster_standard, "CELLSIZEX")
val_pixel_sizeY=get_num_attributes(val_raster_standard, "CELLSIZEY")
val_pixel_area=val_pixel_sizeX*val_pixel_sizeY
val_colcount=get_num_attributes(val_raster_standard, "COLUMNCOUNT")
val_rowcount=get_num_attributes(val_raster_standard, "ROWCOUNT")
val_min=get_num_attributes(val_raster_standard, "MINIMUM")
val_max=get_num_attributes(val_raster_standard, "MAXIMUM")
jnk=val_min-1
if jnk<0 and jnk >=-1:
    val_no_data_val=val_max+1
else:
    val_no_data_val=val_min-1

if val_colcount==mask_colcount and val_rowcount==mask_rowcount and val_pixel_area==mask_pixel_area: 
    mask_Array = arcpy.RasterToNumPyArray(mask_raster_standard,"","","",mask_no_data_val) # (in_raster, {lower_left_corner}, {ncols}, {nrows}, {nodata_to_value})
    val_Array = arcpy.RasterToNumPyArray(val_raster_standard,"","","",val_no_data_val) # (in_raster, {lower_left_corner}, {ncols}, {nrows}, {nodata_to_value})
    mask_unique_vals=f5(mask_Array) 
    try:
        del mask_unique_vals[mask_unique_vals.index(mask_no_data_val)]
    
    for val in mask_unique_vals:
        zone_vals_mat=val_Array[mask_Array==val]
        val_zone_area=mask_pixel_area*len(zone_vals_mat)
        val_zone_mean=zone_vals_mat
        val_zone_std=
