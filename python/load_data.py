
import numpy as np
from numpy.lib.recfunctions import stack_arrays, append_fields
from root_numpy import root2array
# to get cross sections and number of gen events
from di_higgs.hh2bbbb.samples_25ns import mc_samples


def load_data( data_path, branch_names, dataset_names, dataset_ranges = []):  
    """ Import data from several ROOT files to a recarray """
    l_raw_vars = []
    l_weight = []
    l_origin = []
    for i, d_name in enumerate(dataset_names):
        f_name =  "{}{}.root".format(data_path,d_name)
        if "BTagCSV" in d_name:
            d_weight = 1.
        else:
            d_weight = mc_samples[d_name]["xs"]/mc_samples[d_name]["gen_events"] 
        if len(dataset_ranges) == len(dataset_names): 
            l_raw_vars.append(root2array(f_name,"tree", branch_names,
                              stop=dataset_ranges[i]))
        else:    
            l_raw_vars.append(root2array(f_name,"tree", branch_names))
        n_ev = l_raw_vars[-1].shape[0]
        l_weight.append(np.full((n_ev),d_weight, 'f8'))
        l_origin.append(np.full((n_ev),d_name, 'a20'))
    raw_vars = stack_arrays(l_raw_vars, asrecarray=True, usemask=False)     
    weight = stack_arrays(l_weight, asrecarray=True, usemask=False)     
    origin = stack_arrays(l_origin, asrecarray=True, usemask=False)     
    raw_vars = append_fields(raw_vars, ["origin","weight"], [origin, weight],
                             asrecarray=True, usemask=False)
    return raw_vars

def add_cartesian(data, j_n = "pfjets[{}]"):
    """ Add Px, Py, Pz of each jets to the recarray """
    e_vars = {}
    for i in range(4):
        jet = j_n.format(i)
        e_vars[jet+".Px()"] = data[jet+".Pt()"]*np.cos(data[jet+".Phi()"]) 
        e_vars[jet+".Py()"] = data[jet+".Pt()"]*np.sin(data[jet+".Phi()"]) 
        e_vars[jet+".Pz()"] = data[jet+".Pt()"]/np.tan(2*np.arctan( 
                              np.exp(-data[jet+".Eta()"])))
    data = append_fields(data, e_vars.keys(), e_vars.values(), asrecarray=True, usemask=False)
    return data
        
def add_dijet_vars(data, dijet_indices = [(0,1),(2,3)], j_n = "pfjets[{}]"):
    """ Obtain dijet variables and add to record array """        
    e_vars = {}
    m_c = [".Px()", ".Py()", ".Pz()"]
    for i, ids in enumerate(dijet_indices):
        dj_n = "dijet[{}]".format(i)
        for v in [".E()"]+m_c: 
            e_vars[dj_n+v] = sum([data[j_n.format(ij)+v] for ij in ids])
        e_vars[dj_n+".M()"] = np.sqrt(e_vars[dj_n+".E()"]**2 - 
                                      sum([e_vars[dj_n+c]**2 for c in m_c]))
        e_vars[dj_n+".Phi()"] = np.arctan2(e_vars[dj_n+".Py()"],
                                           e_vars[dj_n+".Px()"])
        e_vars[dj_n+".ModP()"] = np.sqrt(sum([e_vars[dj_n+c]**2 for c in m_c]))
        e_vars[dj_n+".Eta()"] = np.arctanh(e_vars[dj_n+".Pz()"]/
                                           e_vars[dj_n+".ModP()"])

        e_vars[dj_n+".Pt()"] = np.sqrt(sum([e_vars[dj_n+c]**2 for c in m_c[0:2]]))
        e_vars[dj_n+".DPhi()"] = (np.pi -
                                 np.abs(np.abs(data[j_n.format(ids[0])+".Phi()"] -
                                 data[j_n.format(ids[1])+".Phi()"])- np.pi))
        e_vars[dj_n+".DEta()"] = np.abs(data[j_n.format(ids[0])+".Eta()"] -
                                 data[j_n.format(ids[1])+".Eta()"])
        e_vars[dj_n+".DR()"] = np.sqrt(sum([e_vars[dj_n+c]**2 for c in [".DEta()",
                                                                        ".DPhi()"]]))
    data = append_fields(data, e_vars.keys(), e_vars.values(), asrecarray=True, usemask=False)
    return data


                                            
            

        
