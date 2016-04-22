loc_COR_CCE=r"%sCOR_CCE%s.tif" %(resultsdir,sp_code_st)
if get_num_attributes(loc_COR_CCE, "UNIQUEVALUECOUNT")==1 and get_num_attributes(loc_COR_CCE, "MAXIMUM")==1)==False:
    a=0
#will have to include in wrapper function!