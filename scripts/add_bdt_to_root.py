#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser(description='Add bdt value to ROOT file.')

parser.add_argument('root_files', nargs='+', help='the root files where bdt has to be added')
parser.add_argument('--bdt_name', help='branch name for bdt value', default = "bdt_value")
args = parser.parse_args()

import numpy as np
from sklearn.externals import joblib
from root_numpy import root2array, rec2array, array2root

bdt_file = '/lustre/cmswork/hh/mvas/old_bdt/bdt.pkl' 

branch_names = ["H1_pT", "H2_pT",
                "H1_dEta_abs", "H2_dEta_abs",
                "H1_dPhi_abs", "H2_dPhi_abs"]

# compute bdt values
bdt = joblib.load(bdt_file)

for root_file in args.root_files:
    print "processing {}".format(root_file)
    # load vars data from ROOT
    data = root2array(root_file, "tree", branch_names)

    data_bdt = bdt.decision_function(rec2array(data[branch_names]))

    # save to ROOT file
    data_bdt.dtype = [(args.bdt_name, np.float64)]
    array2root(data_bdt, root_file, "tree")









