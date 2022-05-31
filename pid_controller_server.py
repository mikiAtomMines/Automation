import socket
from sys import platform
import time

from device_models import Spd3303x
from assemblies import HeaterAssembly
from device_type import Heater
try:
    from device_models import ETcWindows
except (ModuleNotFoundError, ImportError):
    pass
try:
    from device_models import ETcLinux
except (ModuleNotFoundError, ImportError):
    pass
try:
    import fcntl
    import struct
except (ModuleNotFoundError, ImportError):
    pass


def get_host_ip(loopback=False):
    """
    Gets the IP of the host machine, or the default loopback ip address.

    Parameters
    ----------
    loopback : bool
        Set to True to return the default loopback ip address

    Returns
    -------
    str
        The host IP addres, or the loopback address if loopback is True.
    """
    if loopback:
        return '127.0.0.1'

    if platform == 'linux' or platform == 'linux2':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', bytes('eth0'[:15], 'utf-8'))
            )[20:24]
        )
    else:
        return socket.gethostbyname(socket.gethostname())


def process_command(cmd, asm_dict):
    """
    Takes a command and tries to process it. Processing can mean to change a setting in a device of a HeaterAssembly, or
    to return the value of a setting from one of these devices. The syntax of the commands are as follows:

                        <assembly key> <command> <parameter (optional)>\r

    <assembly key> denotes the key of assembly dictionary asm_dict that maps to the desired HeaterAssembly object.
    <command> denotes the command. This command has synta: XX:YYYY. More information on README.md file
    <parameter (optional)> this can be a question mark for queries, ints, floats, or string, depending on the command.
    Some commands don't take parameters.
    \r All commands need to end with a carriage return character.

    Paramters
    ---------
    cmd : str
        The command to be processed. For information of the syntax, refer to README.md
    asm_dict : dictionary of str: HeaterAssembly
        Contains the HeaterAssembly objects to be used by the oven and their respective keys used to access them.
    """
    try:
        asm_key, comm, param = cmd.split()
        param = param.upper()
    except ValueError:
        try:
            asm_key, comm = cmd.split()
        except ValueError:
            return 'ERROR: ' + str(cmd) + ' could not be processed. Missing assembly key or command'

    asm_key = asm_key.upper()
    comm = comm.upper()

    # Oven commands
    # -------------
    if asm_key == 'OVEN':
        if comm == 'OV:KEYS':
            out = ''
            for key in asm_dict.keys():
                out += key + ' '
            return out
        else:
            return 'ERROR: bad command' + str(cmd)

    try:
        asm = asm_dict[asm_key.upper()]
    except KeyError:
        return 'ERROR: HeaterAssembly name ' + asm_key + ' not found'
    # Power supply commands
    # ---------------------
    try:
        if comm == 'PS:IDN':
            return asm.power_supply
        elif comm == 'PS:RSET':
            asm.reset_power_supply()
        elif comm == 'PS:STOP':
            asm.stop_supply()
        elif comm == 'PS:REDY':
            asm.ready_power_supply()
        elif comm == 'PS:VOLT':
            if param == '?':
                return asm.supply_actual_voltage
            else:
                asm.supply_set_voltage = float(param)
        elif comm == 'PS:VSET':
            if param == '?':
                return asm.supply_set_voltage
            else:
                asm.supply_set_voltage = float(param)
        elif comm == 'PS:AMPS':
            if param == '?':
                return asm.supply_actual_current
            else:
                asm.supply_set_current = float(param)
        elif comm == 'PS:ASET':
            if param == '?':
                return asm.supply_set_current
            else:
                asm.supply_set_current = float(param)
        elif comm == 'PS:VLIM':
            if param == '?':
                return asm.supply_voltage_limit
            else:
                asm.supply_voltage_limit = float(param)
        elif comm == 'PS:ALIM':
            if param == '?':
                return asm.supply_current_limit
            else:
                asm.supply_current_limit = float(param)
        elif comm == 'PS:CHIO':
            if param == '?':
                return asm.supply_channel_state
            else:
                asm.supply_channel_state = bool(int(param))
        elif comm == 'PS:CHAN':
            if param == '?':
                return asm.supply_channel
            else:
                asm.supply_channel = int(param)

        # DAQ commands
        elif comm == 'DQ:IDN':
            return asm.daq
        elif comm == 'DQ:TEMP':
            return asm.temp
        elif comm == 'DQ:CHAN':
            if param == '?':
                return asm.daq_channel
            else:
                asm.daq_channel = int(param)
        elif comm == 'DQ:TCTY':
            if param == '?':
                return asm.thermocouple_type
            else:
                asm.thermocouple_type = param
        elif comm == 'DQ:UNIT':
            if param == '?':
                return asm.temp_units
            else:
                asm.temp_units = param

        # PID settings
        elif comm == 'PD:IDN':
            return asm.pid_function
        elif comm == 'PD:RSET':
            return asm.reset_pid()
        elif comm == 'PD:RLIM':
            return asm.reset_pid_limits()
        elif comm == 'PD:KPRO':
            if param == '?':
                return asm.pid_kp
            else:
                asm.pid_kp = float(param)
        elif comm == 'PD:KINT':
            if param == '?':
                return asm.pid_ki
            else:
                asm.pid_ki = float(param)
        elif comm == 'PD:KDER':
            if param == '?':
                return asm.pid_kd
            else:
                asm.pid_kd = float(param)
        elif comm == 'PD:SETP':
            if param == '?':
                return asm.set_temperature
            else:
                asm.set_temperature = float(param)
        elif comm == 'PD:SAMP':
            if param == '?':
                return asm.sample_time
            else:
                asm.sample_time = float(param)
        elif comm == 'PD:REGT':
            if param == '?':
                return asm.pid_regulating
            elif int(param) == 1:
                asm.ready_assembly()
                asm.pid_regulating = bool(int(param))
            elif int(param) == 0:
                asm.pid_regulating = bool(int(param))
                asm.supply_set_voltage = 0

        # Assembly
        elif comm == 'AM:STOP':
            return asm.stop()
        elif comm == 'AM:RSET':
            return asm.reset_assembly()
        elif comm == 'AM:REDY':
            return asm.ready_assembly()
        elif comm == 'AM:MAXV':
            return asm.MAX_voltage_limit
        elif comm == 'AM:MAXA':
            return asm.MAX_current_limit

        # Bad Command
        else:
            return 'ERROR: bad command' + str(cmd)
    except NameError:
        return 'ERROR: parameter missing'
    return


def update_heaters(asm_dict, t0_dict):
    """
    For all HeaterAssembly object used by the Oven, check if the pid is set to regulate and check if the sampling
    time has passed. If yes, then set the power supply to a new value based on the PID output.
    Parameters
    ----------
    asm_dict : dictionary of str: HeaterAssembly
        Should contain all the HeaterAssembly objects used by the oven. The function will iterate through this
        dictionary checking if it should update their respective power supply.
    t0_dict: dictionary of str: float
        Used to keep track of the sampling time for each individual HeaterAssembly

    Returns
    -------
    dictionary of str: float
        the same dictionary used to keep track of sampling time. Should be used as the input for the same function
        in the next iteration.
    """
    for key, asm in asm_dict.items():
        if time.time() - t0_dict[key] >= asm.sample_time and asm.pid_regulating:
            asm.update_supply()
            t0_dict[key] = time.time()
            print(asm.temp)

    return t0_dict


def server_loop(asm_dict):
    """
    Server that controls all the HeaterAssembly objects to be used in the oven. Listens for commands from a remote
    machine. The server remembers PID settings even if a connection with the remote machine is lost. This means that
    temperature regulation can still happen even without a remote machine connected to the server.

    Parameters:
    asm_dict : dictionary of str: HeaterAssembly
        dictionary containing all the HeaterAssembly objects to be used by the oven and their respective keys. The
        keys are used to identify each HeaterAssembly in the Oven class. Keys are not case-sensitive.

    """
    keys_raw = list(asm_dict)
    for key in keys_raw:  # change all keys to uppercase
        asm_dict[key.upper()] = asm_dict.pop(key)

    HOST = get_host_ip(True)
    PORT = 65432
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print('Bound to', HOST, PORT)

    while True:
        t0_dict1 = {}
        for key in asm_dict.keys():
            t0_dict1[key] = time.time()
        while True:
            # While disconnected, listen to connection requests.
            # Additionally, keep updating the power supplies from the heater assemblies.
            # break if a connection request is received.
            s.settimeout(1)
            try:
                print('listening')
                s.listen()
                conn, addr = s.accept()
                break
            except socket.timeout:
                t0_dict1 = update_heaters(asm_dict, t0_dict1)

        # With the connection: update heaters.
        # Additionally, receive and process commands.
        # If connection is broken, power supplies from heater assemblies will continue to be updated.
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


def main():
    ps = Spd3303x('10.176.42.121')
    h = Heater(MAX_temp=100, MAX_volts=30, MAX_current=0.5)
    daq_ip = '10.176.42.200'

    try:
        daq = ETcWindows(0, daq_ip)
    except NameError:
        daq = ETcLinux(daq_ip)

    asm1 = HeaterAssembly((ps, 1), (daq, 0), h)

    asm_dict = {'asm1': asm1}  # keys for assemblies are not case-sensitive. OVEN is reserved

    server_loop(asm_dict)

main()
