import h5py

def get_datasets(master_filename):
    
    file = h5py.File(master_filename, 'r')
    nodes = file['/entry']
    datatuples = [item for item in nodes.items() if item[0].startswith('data_') ]
    # sort the datatuples by dataset order - modifies object inline
    datatuples.sort()
    # the np.arrays are the 2nd item of the datatuple
    datasets = [ d[1] for d in datatuples ]
    return datasets


