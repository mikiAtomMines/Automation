import time
from matplotlib import pyplot as plt
from device_models import Gm3
from device_models import Series9550


gm = Series9550(15)
ti = time.time()

# print(gm.reset_time())
# time.sleep(1)
to = time.time()
# print(to - ti)
# ti = to
while time.time() - to < 30:
    print(gm.get_zfield())
    time.sleep(0.2)
    # to = time.time()
    # print('\t\t\t', to - ti)
    # ti = to