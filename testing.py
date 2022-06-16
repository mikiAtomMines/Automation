import time
from matplotlib import pyplot as plt
from device_models import Srs100


s = Srs100('COM7')
print(s.idn)
time.sleep(3)

s.set_ionizer_filament_state(True)

ti = time.time()
out = s.get_analog_scan(m_lo=1, m_hi=100, speed=3)
tf = time.time()

s.set_ionizer_filament_state(False)

print(tf - ti)

plt.figure(figsize=[6,8])
plt.plot(out, label='little')
plt.legend()
plt.show()
