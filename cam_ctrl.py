from eigerclient import DEigerClient
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

    def initialize(self, photon_energy=9000):
        self.eigerclient = DEigerClient(host=self.ipaddr)
        print "Initialize the EIGER"
        self.eigerclient.sendDetectorCommand("initialize")
        print "Set energy to %.3f keV" % photon_energy/1000.0 
        self.photon_energy = photon_energy
        self.eigerclient.setDetectorConfig("photon_energy", photon_energy)

    def set_photon_energy(self, energy):
        self.eigerclient.setDetectorConfig("photon_energy", photon_energy)
        self.photon_energy = photon_energy
        print "Set energy to %.3f keV" % photon_energy/1000.0

    # method assumes set_photon_energy() has been called previously
    def expose(self, exposure_time, num_img=1, threshold = None, flatfield = 1):
        if (threshold == None):
            self.eigerclientsetDetectorConfig("threshold_energy",self.photon_energy/2.0)
        else:
            self.eigerclientsetDetectorConfig("threshold_energy",threshold)
        self.eigerclientsetDetectorConfig("flatfield_correction_applied",flatfield)
        self.eigerclientsetDetectorConfig("nimages",num_img)
        if (num_img == 1):
            self.eigerclientsetDetectorConfig("count_time",exposure_time)
        else:
            self.eigerclientsetDetectorConfig("frame_time",exposure_time)
            self.eigerclientsetDetectorConfig("count_time",exposure_time-0.000020)
        self.seq_id = self.eigerclientsendDetectorCommand("arm")['sequence id']
        print "Detector triggered " + str(num_img) + " image(s) of " + str(exposure_time) + "s"
        self.eigerclientsendDetectorCommand("trigger")
        self.eigerclientsendDetectorCommand("disarm")
        print "data recorded"

        ct = self.eigerclientdetectorConfig("count_time")
        ft = self.eigerclientdetectorConfig("frame_time")
        thresh = self.eigerclientdetectorConfig("threshold_energy")
        print "used frame time: " + str(ft['value'])
        print "used count time: " + str(ct['value'])
        print "used threshold : " + str(thresh['value'])
        
    def download_data(self, storage_path, show_image=1):
        file_name = e.fileWriterConfig("name_pattern")['value'].replace("$id",str(self.seq_id))
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

    
def loopscan(ct, nimg=1):
    storage_path = '/home/chx/data/032714'
    shttr = Shutter()
    eiger = Eiger(ipaddr="164.54.124.191")

    eiger.initialize(photon_energy=9000)
    shttr.open()
    eiger.expose(ct, nimg)
    shttr.close()
    eiger.download_data(storage_path)


