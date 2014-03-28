from epics import Motor, PV

class Shutter(object):
    def __init__(self, pvname):
        self.out_pv = PV(pvname)

    def open(self):
        self.out_pv.put(str(1))

    def close(self):
        self.out_pv.put(str(0))



