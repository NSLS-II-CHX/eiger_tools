import sys
sys.path.insert(0,"/usr/local/dectris/python")
import dectris.albula
from eigerclient import DEigerClient
import requests

from epics import PV


class Shutter(object):
    def __init__(self):
        self.out_pv = PV('34idc:softGlue:OR-1_IN2_Signal')

    def open(self):
        self.out_pv.put(str(1))

    def close(self):
        self.out_pv.put(str(0))


class Eiger(object):
    def __init__(self, ipaddr="164.54.124.191"):
        self.ipaddr = ipaddr
        self.photon_energy = 9000
        self.threshold = None
        self.flatfield = 1
        self.num_img = 1
        self.count_time = 1
        self.seq_id = 0
        self.initialized = False

    def initialize(self, photon_energy=9000, threshold=9000/2.0):
        self.eigerclient = DEigerClient(host=self.ipaddr)
        # NOTE: initialize twice to get rid of the 'zebras'
        print "Initialize the EIGER 1st time"
        self.eigerclient.sendDetectorCommand("initialize")
        self.eigerclient.setDetectorConfig("photon_energy", photon_energy)
        self.photon_energy = photon_energy
        self.eigerclient.setDetectorConfig("threshold_energy", threshold) # added
        self.threshold = threshold # added
        # take short initial exposure to prep flatfield calibration.
        # NOTE: assumes (and recommends !!!) shutter is closed
        self.expose(0.001, 1)
        print "Initialize the EIGER 2nd time"
        self.eigerclient.sendDetectorCommand("initialize")
        self.eigerclient.setDetectorConfig("photon_energy", photon_energy)
        self.photon_energy = photon_energy
        self.eigerclient.setDetectorConfig("threshold_energy", threshold) # added
        self.threshold = threshold # added
        # FIXME: disable compression until we get lz4 support in libhdf5 !!
        self.eigerclient.setFileWriterConfig('compression_enabled', False)
        self.initialized = True
        self.expose(0.001, 1)
        print "EIGER successfully Initialized for " + str(photon_energy/1000.0) + "keV, using threshold: "+str(threshold/1000.0) +"keV"
        print "No Zebras expected! :-)"
        
    def is_initialized(self):
        return self.initialized

    def set_photon_energy(self, energy):
        self.eigerclient.setDetectorConfig("photon_energy", photon_energy)
        self.photon_energy = photon_energy
    def set_threshold(self, threshold): #added
        self.eigerclient.setDetectorConfig("threshold_energy", threshold)   #added
        self.threshold = threshold    #added
        

    # method assumes set_photon_energy() has been called previously
    # try: method assumes that set_threshold() has been called previously
    def expose(self, exposure_time, num_img=1, threshold = None, flatfield = 1):
        if (threshold == None):
            self.eigerclient.setDetectorConfig("threshold_energy",self.threshold) # changed from 'self.photon_energy/2.0'
        else:
            self.eigerclient.setDetectorConfig("threshold_energy",threshold)
        self.eigerclient.setDetectorConfig("flatfield_correction_applied",flatfield)
        self.eigerclient.setDetectorConfig("nimages",num_img)
        if (num_img == 1):
            self.eigerclient.setDetectorConfig("count_time",exposure_time)
        else:
            self.eigerclient.setDetectorConfig("frame_time",exposure_time)
            self.eigerclient.setDetectorConfig("count_time",exposure_time-0.000020)
        self.seq_id = self.eigerclient.sendDetectorCommand("arm")['sequence id']
        print "Detector triggered " + str(num_img) + " image(s) of " + str(exposure_time) + "s"
        self.eigerclient.sendDetectorCommand("trigger")
        self.eigerclient.sendDetectorCommand("disarm")
        print "data recorded"

        ct = self.eigerclient.detectorConfig("count_time")
        ft = self.eigerclient.detectorConfig("frame_time")
        thresh = self.eigerclient.detectorConfig("threshold_energy")
        print "used frame time: " + str(ft['value']) +"s"
        print "used count time: " + str(ct['value']) +"s"
        print "used threshold : " + str(thresh['value']/1000.0) +"keV"
        
    def download_data(self, storage_path, show_image=1):
        file_name = self.eigerclient.fileWriterConfig("name_pattern")['value'].replace("$id",str(self.seq_id))
        # FIXME -- put some f'ing error checking in here!!
        fm = requests.get("http://{0}/data/{1}_master.h5".format(self.ipaddr,file_name))
        open("{0}/{1}_master.h5".format(storage_path,file_name),"wb").write(fm.content)
        requests.delete("http://{0}/data/{1}_master.h5".format(self.ipaddr,file_name))
        print "saved master file: " + "{0}/{1}_master.h5".format(storage_path,file_name)

        id=0
        while True:
            fd = requests.get("http://{0}/data/{1}_data_{2:0>6}.h5".format(self.ipaddr,file_name,id))
            if not fd.ok: break
            print "saved data","{0}/{1}_data_{2:0>6}.h5".format(storage_path,file_name,id)
            open("{0}/{1}_data_{2:0>6}.h5".format(storage_path,file_name,id),"wb").write(fd.content)
            requests.delete("http://{0}/data/{1}_data_{2:0>6}.h5".format(self.ipaddr,file_name,id))
            id +=1
            
        if show_image == 1:
            try:
                # opens albula
                m = dectris.albula.openMainFrame()
                s = m.openSubFrame()
                s.loadFile("{0}/{1}_master.h5".format(storage_path,file_name))
            except:
                print "albula got closed"

eiger = Eiger(ipaddr="164.54.124.191")

def loopscan(ct, nimg=1):
    storage_path = '/home/chx/data'
    shttr = Shutter()

    if not eiger.is_initialized():
        eiger.initialize(photon_energy=9000)
        "EIGER Initialized for " + str(photon_energy/1000.0) + "keV"
    shttr.open()

    try:
        eiger.expose(ct, nimg)
    except:
        shttr.close()
        raise "Bailing out! Exposure failed!!!"
    eiger.download_data(storage_path)


