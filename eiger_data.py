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

class Eiger_Dataset(object):
    def __init__(self, master_filename):
        self.master_file = master_filename

        file = h5py.File(master_filename, 'r')
        nodes = file['/entry']
        datatuples = [item for item in nodes.items() if item[0].startswith('data_') ]
        # sort the datatuples by dataset order - modifies object inline
        datatuples.sort()
        # the np.arrays are the 2nd item of the datatuple
        self.datasets = [ d[1] for d in datatuples ]
        self.num_datasets = len(self.datasets)
        self.num_images = 0
        for d in self.datasets:
            self.num_images += d.shape[0]

    # or, just access the object attribute - obj.datasets
    def getDatasets(self):
        return self.datasets

    def __getitem__(self, item):
        print item
