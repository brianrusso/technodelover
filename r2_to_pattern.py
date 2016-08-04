from technodeminer.r2.model import R2
from technodeminer.r2.util import get_filenames


r2_files = get_filenames('/media/sf_Data/CTV_R2/2015/RDT-E/Air Force/')

r2_list = []
for file in r2_files:
    if file.lower().endswith(".xml"):
        r2_list.append(R2.from_file(file).as_pattern_doc())
