import eiger
from epics import PV


class shutter(object):
    def __init__(self):
        out_pv = PV('34idc:softGlue:OR-1_IN2_Signal')

    def open(self):
	self.out_pv.put(1)

    def close(self):
	self.out_pv.put(0)

#    def isopen(self):
#	return self.in_pv.get()


def loopscan(ct, nimg=1):
    shttr = shutter()

    shttr.open()
    eiger.exp(ct, nimg)
    shttr.close()


