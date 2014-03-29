from cam_ctrl import eiger
from dev_34idc import shttr
import sys


def loopscan(ct, nimg=1, storage_path='/home/chx/data'):

    if not eiger.is_initialized():
        eiger.initialize(photon_energy=9000)
        "EIGER Initialized for " + str(photon_energy/1000.0) + "keV"
    # shttr is from dev-34idc.py
    shttr.open()

    try:
        eiger.expose(ct, nimg)
    except:
        shttr.close()
        print 'eiger.expose() error: ', sys.exc_info()[0]
        raise Exception("Bailing out! Exposure failed!!!")
    shttr.close()
    eiger.download_data(storage_path)


