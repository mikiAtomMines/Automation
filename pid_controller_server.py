import socket
from sys import platform
import time

from device_models import SPD3303X
from assemblies import HeaterAssembly
from device_type import Heater
try:
    from device_models import E_Tc
except (ModuleNotFoundError, ImportError):
    pass
try:
    from device_models import E_Tc_Linux
except (ModuleNotFoundError, ImportError):
    pass
try:
    import fcntl
    import struct
except (ModuleNotFoundError, ImportError):
    pass


def get_host_ip(ifname='eth0'):
    if ifname == 'loopback':
        return '127.0.0.1'
    elif platform == 'linux' or platform == 'linux2':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(
            fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(ifname[:15], 'utf-8')))[20:24])
    else:
        return socket.gethostbyname(socket.gethostname())


def process_command(cmd, asm_dict):
    """
    takes a string cmd and executes the respective function.

    :param str cmd: command from made-up communication protocol. See ReadMe for more details.
    :param dict of HeaterAssembly asm_dict: dictionary of heater assembly objects that contain the power supply,
    temperature daq, and simple_pid objects to interact with their physical counterparts to control the oven
    :return str or float or None: return query request. If it's a command, return None.
    """
    try:
        asm_key, f, s = cmd.split()
    except ValueError:
        asm_key, f = cmd.split()

    try:
        asm = asm_dict[asm_key]
    except KeyError:
        return 'ERROR: HeaterAssmebly name ' + asm_key + ' not valid'

    # Power supply commands
    # ---------------------
    if f == 'PS:IDN':
        return asm.power_supply
    elif f == 'PS:RSET':
        asm.reset_power_supply()
    elif f == 'PS:STOP':
        asm.stop_supply()
    elif f == 'PS:REDY':
        asm.ready_power_supply()
    elif f == 'PS:VOLT':
        if s == '?':
            return asm.supply_actual_voltage
        else:
            asm.supply_set_voltage = float(s)
    elif f == 'PS:VSET':
        if s == '?':
            return asm.supply_set_voltage
        else:
            asm.supply_set_voltage = float(s)
    elif f == 'PS:AMPS':
        if s == '?':
            return asm.supply_actual_current
        else:
            asm.supply_set_current = float(s)
    elif f == 'PS:ASET':
        if s == '?':
            return asm.supply_set_current
        else:
            asm.supply_set_current = float(s)
    elif f == 'PS:VLIM':
        if s == '?':
            return asm.supply_voltage_limit
        else:
            asm.supply_voltage_limit = float(s)
    elif f == 'PS:ALIM':
        if s == '?':
            return asm.supply_current_limit
        else:
            asm.supply_current_limit = float(s)
    elif f == 'PS:CHIO':
        if s == '?':
            return int(asm.supply_channel_state)
        else:
            asm.supply_channel_state = bool(int(s))
    elif f == 'PS:CHAN':
        if s == '?':
            return asm.supply_channel
        else:
            asm.supply_channel = int(s)

    # DAQ commands
    elif f == 'DQ:IDN':
        return asm.daq
    elif f == 'DQ:TEMP':
        return asm.temp
    elif f == 'DQ:CHAN':
        if s == '?':
            return asm.daq_channel
        else:
            asm.daq_channel = int(s)
    elif f == 'DQ:TCTY':
        if s == '?':
            return asm.thermocouple_type
        else:
            asm.thermocouple_type = s
    elif f == 'DQ:UNIT':
        if s == '?':
            return asm.temp_units
        else:
            asm.temp_units = s

    # PID settings
    elif f == 'PD:IDN':
        return asm.pid_function
    elif f == 'PD:RSET':
        return asm.reset_pid()
    elif f == 'PD:RLIM':
        return asm.reset_pid_limits()
    elif f == 'PD:KPRO':
        if s == '?':
            return asm.pid_kp
        else:
            asm.pid_kp = float(s)
    elif f == 'PD:KINT':
        if s == '?':
            return asm.pid_ki
        else:
            asm.pid_ki = float(s)
    elif f == 'PD:KDER':
        if s == '?':
            return asm.pid_kd
        else:
            asm.pid_kd = float(s)
    elif f == 'PD:SETP':
        if s == '?':
            return asm.set_temperature
        else:
            asm.set_temperature = float(s)
    elif f == 'PD:SAMP':
        if s == '?':
            return asm.sample_time
        else:
            asm.sample_time = float(s)
    elif f == 'PD:REGT':
        if s == '?':
            return asm.pid_regulating
        elif int(s) == 1:
            asm.ready_assembly()
            asm.pid_regulating = bool(int(s))
        elif int(s) == 0:
            asm.pid_regulating = bool(int(s))

    # Assembly
    elif f == 'AM:STOP':
        return asm.stop()
    elif f == 'AM:RSET':
        return asm.reset_assembly()
    elif f == 'AM:REDY':
        return asm.ready_assembly()
    elif f == 'AM:MAXV':
        return asm.MAX_voltage_limit
    elif f == 'AM:MAXA':
        return asm.MAX_current_limit
    else:
        return 'ERROR: bad command' + str(cmd)
    return


def update_heaters(asm_dict, t0_dict):
    for key, asm in asm_dict.items():
        if time.time() - t0_dict[key] >= asm.sample_time:
            if asm.pid_regulating:
                asm.update_supply()
                t0_dict[key] = time.time()
                print(asm.temp)
            else:
                asm.supply_set_voltage = 0
    return t0_dict


def main():
    HOST = get_host_ip('loopback')
    PORT = 65432

    # Devices
    # -------
    ps = SPD3303X('10.176.42.121')
    h = Heater(MAX_temp=100, MAX_volts=30, MAX_current=0.5)
    daq_ip = '10.176.42.200'
    try:
        daq = E_Tc(0, daq_ip)
    except NameError:
        pass
    try:
        daq = E_Tc_Linux(daq_ip)
    except NameError:
        pass

    asm1 = HeaterAssembly((ps, 1), (daq, 0), h)

    asm_dict = {'ASM1': asm1}

    # Connection
    # ----------
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print('Bound to', HOST, PORT)

    while True:
        t0_dict1 = {}
        for key in asm_dict.keys():
            t0_dict1[key] = time.time()
        while True:
            s.settimeout(1)
            try:
                print('listening')
                s.listen()
                conn, addr = s.accept()
                break
            except socket.timeout:
                t0_dict1 = update_heaters(asm_dict, t0_dict1)

        conn.setblocking(False)
        print(f"Connected by {addr}")
        with conn:
            t0_dict2 = {}
            for key in asm_dict.keys():
                t0_dict2[key] = time.time()
            while True:
                update_heaters(asm_dict, t0_dict2)

                try:
                    data = conn.recv(1024).decode('utf-8').upper()
                    if not data:
                        print(f"Disconnected by {addr}")
                        break
                    out = process_command(data, asm_dict)

                    if out is not None:
                        conn.sendall((str(out) + '\r').encode('utf-8'))

                except BlockingIOError:
                    pass
                except ConnectionResetError:
                    print(f"Disconnected by {addr}")
                    break


main()
