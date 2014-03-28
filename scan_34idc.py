from cam_ctrl import eiger
from dev-34idc import shttr


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
        raise "Bailing out! Exposure failed!!!"
    shttr.close()
    eiger.download_data(storage_path)


