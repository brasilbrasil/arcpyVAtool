del_terms=["map4", "map5", "map3"]#,"_eff_pioneer_zone_area.csv"] #eff_hab_qual_zone_area.csv
#del_terms=["compatible", "lava", "protected", "Ung_free", "core_biome_", "fragmentation_", "aspect", "slope", "suitability", "gradient", "GBU", "good", "ungfree"]
rootdir=r"Y:/PICCC_analysis/plant_landscape_va_results/redone_w_eff_CE/results/all/output_maps_report/" #whichever is data dir, will have to have subfolders: results/, results/la/, la/ (where you place CCE and FCE files)

#END USER INPUT
import os
from types import *
for del_term in del_terms:
	for root, dirs, files in os.walk(rootdir):
		for f in files:
			if del_term in f:
				#os.unlink(os.path.join(root, f))
				print "deleted " + f


