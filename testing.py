import time
from matplotlib import pyplot as plt
from device_models import Gm3
from device_models import Series9550
from device_models import Vxm

m = Vxm(name='COM6')
m.set_origin(1)
m.displace(1, +300)
time.sleep(1)
m.displace(1, +500)
time.sleep(1)
m.set_position(1, 0)
