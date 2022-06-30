import time
from matplotlib import pyplot as plt
from device_models import Gm3


gm = Gm3('COM3', 5)
ti = time.time()

# print(gm.reset_time())
# time.sleep(1)
# to = time.time()
# print(to - ti)
# ti = to
for i in range(100):
    print(gm.get_datapoint())
    to = time.time()
    print('\t\t\t', to - ti)
    ti = to