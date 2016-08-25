#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import argparse
from os.path import basename, splitext, isfile, getmtime
import itertools
from root_numpy import root2array
from pandas import HDFStore,DataFrame
import numpy as np
from di_higgs.hh2bbbb_mva.load_data import add_dijet_vars
from glob import glob
import json
import sys
import itertools as it

parser = argparse.ArgumentParser(prog='ToDataframeDisk')
parser.add_argument('--path', required=True, type=str)
args = parser.parse_args()

jet_vars = ["Pt()", "Eta()", "Phi()", "E()" ,
            "Px()", "Py()", "Pz()","getDiscriminatorC(\"CSV\")"] 
branch_names = ["pfjets[{}].{}".format(i, var) for i, var in itertools.product(range(4), jet_vars)]

weights = ["bTagWeight", "puWeight", "puWeightUp", "puWeightDown"]
bt_var = ["JES","LF","HF","LFStats1","LFStats2",
          "HFStats1","HFStats2","cErr1","cErr2"]
bt_shifts = ["Up", "Down"]
weights += [ "bTagWeight{}{}".format(var,sh) for var, sh in it.product(bt_var, bt_shifts)]
weights += ["LHE_weights_scale_wgt{}".format(i) for i in range(6)]
weights += ["LHE_weights_pdf_wgt{}".format(i) for i in range(101)]
extra_branches = ["eventInfo.getWeightC(\"{}\")".format(weight)
                  for weight in weights]

data_dir = args.path 


reg_fn = data_dir+"registry.json"
if isfile(reg_fn):
    with open(reg_fn) as reg_file:
        reg = json.load(reg_file)    
else:
    reg = {}

root_files = glob(data_dir+"*.root")
store = HDFStore(data_dir+'data.h5')

for root_f in root_files:
     f_time = getmtime(root_f) 
     if root_f in reg:
         if (reg[root_f] + 1.) <= f_time:
             continue #skip if up to date 
     else:
        reg[root_f] = f_time
     
     d_name = splitext(basename(root_f))[0]
     

     if "BTagCSV" in root_f:
        print("{0} - to dataframe ...".format(d_name), end="")
        sys.stdout.flush()
        s_array = root2array(root_f,"tree",branch_names)
        s_array.dtype.names = [n.replace(jet_vars[-1], "CSV()") for n in s_array.dtype.names]
        s_array.dtype.names = [n.replace("eventInfo.getWeightC(\"","")
                                .replace("\")","") for n in s_array.dtype.names]
        m_array = root2array(root_f,"mix_tree",branch_names)
        m_array.dtype.names = [n.replace(jet_vars[-1], "CSV()") for n in m_array.dtype.names]
        m_array.dtype.names = [n.replace("eventInfo.getWeightC(\"","")
                                .replace("\")","") for n in m_array.dtype.names]
        print(" to HDF ...", end="")
        store[d_name] = DataFrame(add_dijet_vars(s_array))
        store[d_name+"_mix"] = DataFrame(add_dijet_vars(m_array))
        print(" DONE ")
     else:   
        print("{0} - to dataframe ...".format(d_name), end="")
        sys.stdout.flush()
        s_array = root2array(root_f,"tree",branch_names+extra_branches)
        s_array.dtype.names = [n.replace(jet_vars[-1], "CSV()") for n in s_array.dtype.names]
        s_array.dtype.names = [n.replace("eventInfo.getWeightC(\"","")
                                .replace("\")","") for n in s_array.dtype.names]
        print(" to HDF ...", end="")
        store[d_name] = DataFrame(add_dijet_vars(s_array))
        print(" DONE ")

with open(reg_fn,"w") as reg_file:
    json.dump(reg,reg_file)    

print(store)
store.close()     
