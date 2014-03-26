""" 
EIGER Test client 
This is only a simple script to start using the detector. 
Copyright See General Terms and Conditions (GTC) on http://www.dectris.com 
""" 

import sys 
sys.path.insert(0,"/usr/local/dectris/python")
import dectris.albula 
import requests
from eigerclient import DEigerClient 

# detector ip
ip = "164.54.124.191" 
# image storage path (must exist), files will be overwritten if EIGER is restarted
storage_path="/home/chx/data" 

# opens albula
m = dectris.albula.openMainFrame() 
s = m.openSubFrame() 

e=DEigerClient(host=ip) 
print "Initialize the EIGER"
e.sendDetectorCommand("initialize") 
print "Set energy to 9keV" 
e.setDetectorConfig("photon_energy",9000) 
 

# Expose images 
def exp(ct, nimg = 1, show_im = 1, pe = 9000, t = None, ff = 1): 
   e.setDetectorConfig("photon_energy",pe) 
   if (t==None):
     e.setDetectorConfig("threshold_energy",pe/2)
   else:
     e.setDetectorConfig("threshold_energy",t)
   e.setDetectorConfig("flatfield_correction_applied",ff) 
   e.setDetectorConfig("nimages",nimg)
   if (nimg == 1):
     e.setDetectorConfig("count_time",ct)
   else:
     e.setDetectorConfig("frame_time",ct)  
     e.setDetectorConfig("count_time",ct-0.000020)
   sq_id = e.sendDetectorCommand("arm")['sequence id']
   print "Detector triggered " + str(nimg) + " image(s) of " + str(ct) + "s"
   e.sendDetectorCommand("trigger")
   e.sendDetectorCommand("disarm") 
   print "data recorded"
   
   ct = e.detectorConfig("count_time") 
   ft = e.detectorConfig("frame_time") 
   thresh = e.detectorConfig("threshold_energy") 
   
   print "used frame time: " + str(ft['value']) 
   print "used count time: " + str(ct['value']) 
   print "used threshold : " + str(thresh['value']) 
 
   file_name = e.fileWriterConfig("name_pattern")['value'].replace("$id",str(sq_id)) 
   fm = requests.get("http://{0}/data/{1}_master.h5".format(ip,file_name)) 
   open("{0}/{1}_master.h5".format(storage_path,file_name),"wb").write(fm.content) 
   requests.delete("http://{0}/data/{1}_master.h5".format(ip,file_name)) 
   print "saved master file: " + "{0}/{1}_master.h5".format(storage_path,file_name) 

   id=0
   while True:
      fd = requests.get("http://{0}/data/{1}_data_{2:0>6}.h5".format(ip,file_name,id)) 
      if not fd.ok: break
      print "saved data","{0}/{1}_data_{2:0>6}.h5".format(storage_path,file_name,id)      
      open("{0}/{1}_data_{2:0>6}.h5".format(storage_path,file_name,id),"wb").write(fd.content) 
      requests.delete("http://{0}/data/{1}_data_{2:0>6}.h5".format(ip,file_name,id))
      id +=1
   
   if show_im == 1:
    try:
      s.loadFile("{0}/{1}_master.h5".format(storage_path,file_name)) 
    except:
      print "albula got closed"
 
 
 
 
 
 
 
 
 
 
 
 

