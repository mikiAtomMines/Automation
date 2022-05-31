import socket
import fcntl
import struct
import time
from device_models import Spd3303x
from device_type import MccDeviceLinux
import numpy as np
import simple_pid


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(
        fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(ifname[:15], 'utf-8')))[20:24])


hostname = socket.gethostname() + '.local'
ip4_address = get_ip_address('eth0')

HOST = ip4_address
PORT = 65432

# Devices
# -------                                                                                                           
ps = Spd3303x('10.176.42.121')
ps.set_set_current(1, 0.5)
ps.set_channel_state(1, 'on')

daq = MccDeviceLinux('10.176.42.200')
pid = simple_pid.PID()
pid.setpoint = 60
pid.output_limits = (0, 30)
pid.tunings = (0.7, 0.01, 0)
pid.sample_time = 1

# Buttons
# -------                                                                                                           
regulate = False
t0 = time.time()
t = time.time() - t0
dt = time.time() - t0

# Connection
# ----------                                                                                                        
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print('Bound to', HOST, PORT)
    print('listening')
    s.listen()
    conn, addr = s.accept()
    with conn:
        conn.setblocking(False)
        print(f"Connected by {addr}")







        while True:
            temp = daq.temp_ch0
            new_volts = pid(temp)

            if regulate:
                ps.set_set_voltage(1, new_volts)
            else:
                ps.set_set_voltage(1, 0)






            try:
                data = conn.recv(1024)

                cmd = data.decode('utf-8')
                if cmd == 'get temp':
                    print(temp)
                elif cmd == 'get volts':
                    print(new_volts)
                elif cmd == 'regulate on':
                    regulate = True
                elif cmd == 'regulate off':
                    regulate = False

                if not data:
                     print(f"Disconnected by {addr}")
                     break

            except BlockingIOError:
                pass

