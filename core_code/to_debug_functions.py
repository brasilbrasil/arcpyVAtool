
i=124
jnk=CCE_Spp[i]
jnk.encode('ascii','replace')
inRaster = ce_data_dir + jnk
sp_code_st=inRaster[-8:-4]
resultsdir=resultsdir0+sp_code_st+"/"
sp_code=str(int(sp_code_st)) #get rid of extra zeros
