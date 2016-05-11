#!/usr/bin/env python

import numpy as np
import itertools as it
from di_higgs.hh2bbbb_mva.load_data import load_data, add_cartesian, add_dijet_vars
from numpy.lib.recfunctions import stack_arrays, append_fields
from sklearn.externals import joblib
from root_numpy import rec2array


asc_file = '/lustre/cmswork/dorigo/13TeV/hhbbbb/mixing/ascii_bdt/MixEvt_2097152_1_100_15v_tr.asc'
bdt_file = '/lustre/cmswork/hh/mvas/old_bdt/bdt.pkl' 
out_file = 'output.asc' 

j_v = ["Pt()", "Eta()", "Phi()", "E()" , "CSV()"] 
j_n = "pfjets[{}].{}"
branch_names = [j_n.format(i, v) for i,v in it.product(range(4), j_v)]

mix_data = np.genfromtxt(asc_file, names=branch_names)
mix_data.dtype.names = branch_names # fix names (symbols were erased)

mix_data = add_cartesian(mix_data)
mix_data = add_dijet_vars(mix_data)

bdt = joblib.load(bdt_file)

features = ["dijet[0].Pt()","dijet[1].Pt()",
            "dijet[0].DEta()","dijet[1].DEta()",
            "dijet[0].DPhi()","dijet[1].DPhi()"]

mix_data_bdt = bdt.decision_function(rec2array(mix_data[features]))

bdt_name = "bdt_value"
mix_data = append_fields(mix_data, [bdt_name], [mix_data_bdt] , asrecarray=True, usemask=False)

to_write = branch_names + [bdt_name]

np.savetxt(out_file, rec2array(mix_data[to_write]))







