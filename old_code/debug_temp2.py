outname=loc_min_elev_FCE_table
temp_zones=tmp_zn
col_name=stat

def zonal_area_from_dbf_byCol(outname, temp_zones,col_name):
    outputVec=[0]*len(temp_zones) #create empty results vector
    rows = arcpy.SearchCursor(outname)
    fields = arcpy.ListFields(outname)
    for field in fields:
        name = field.name
        print name
        if name==col_name:
            for row in rows:
                jnk=row.getValue("VALUE")
                ind=temp_zones.index(jnk)
                outputVec[ind]=row.getValue(name)
                print field.name
                print row.getValue(name)
    return outputVec
