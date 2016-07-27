import os
import xmltodict
import json
from technodeminer.r2.model import R2
from technodeminer.r2.util import  get_filenames

files = get_filenames('/home/brian/technodeminer/data/r2')

def xml_to_json(filename):
    this_r2 = R2.from_file(filename)
    output = os.path.splitext(filename)[0] + ".json"
    print output
    #print this_r2
    this_r2.to_json_file(output)

def xmldict_to_json(filename):
    with open(filename,'r') as fd:
        this_r2_str = fd.read()
        this_r2 = xmltodict.parse(this_r2_str)
        output = os.path.splitext(filename)[0] + ".json"
        with open(output,'w') as fd_out:
            json.dump(this_r2,fd_out)

if __name__ == '__main__':
    for file in files:
#        xml_to_json(file)
        xmldict_to_json(file)
