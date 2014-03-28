from shutter import Shutter
from epics import Motor

# diffractometer/sample stage motors
phi = Motor('34idc:mxv:c1:m1')
chi = Motor('34idc:mxv:c1:m2')
th = Motor('34idc:aero:c0:m1')
xm = Motor('34idc:mxv:c1:m5')
ym = Motor('34idc:mxv:c1:m6')
zm = Motor('34idc:mxv:c0:m1')
gam = Motor('34idc:m4k:c1:m5')
delta = Motor('34idc:m4k:c1:m6')

# fast-shutter
shttr = Shutter('34idc:softGlue:OR-1_IN2_Signal')

