import socket
from sys import platform
import time

from device_models import Spd3303x
from device_models import Mr50040
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

    Returns
    -------
    str
        Might return requested output string or error string.
    """
    try:
        asm_key, dev_comm, param = cmd.split()
        param = param.upper()
    except ValueError:
        try:
            asm_key, dev_comm = cmd.split()
        except ValueError:
            return 'ERROR: ' + str(cmd) + ' could not be processed. Missing assembly key or command'

    asm_key = asm_key.upper()
    dev_comm = dev_comm.upper()
    dev, comm = dev_comm.split(':')

    # Oven commands
    # -------------
    if asm_key == 'OVEN':
        if dev_comm == 'OV:KEYS':
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
        if dev == 'PS':
            if comm == 'IDN':
                return asm.power_supply
            elif comm == 'RSET':
                asm.reset_power_supply()
            elif comm == 'STOP':
                asm.stop_supply()
            elif comm == 'REDY':
                asm.ready_power_supply()
            elif comm == 'VOLT':
                if param == '?':
                    return asm.get_supply_actual_voltage()
                else:
                    return asm.set_supply_voltage(float(param))
            elif comm == 'VSET':
                if param == '?':
                    return asm.get_supply_setpoint_voltage()
                else:
                    return asm.set_supply_voltage(float(param))
            elif comm == 'AMPS':
                if param == '?':
                    return asm.get_supply_actual_current()
                else:
                    return asm.set_supply_current(float(param))
            elif comm == 'ASET':
                if param == '?':
                    return asm.get_supply_setpoint_current()
                else:
                    return asm.set_supply_current(float(param))
            elif comm == 'VLIM':
                if param == '?':
                    return asm.get_supply_voltage_limit()
                else:
                    return asm.set_supply_voltage_limit(float(param))
            elif comm == 'ALIM':
                if param == '?':
                    return asm.get_supply_current_limit()
                else:
                    return asm.set_supply_current_limit(float(param))
            elif comm == 'CHIO':
                if param == '?':
                    return asm.get_supply_channel_state()
                else:
                    return asm.set_supply_channel_state(bool(int(param)))
            elif comm == 'CHAN':
                if param == '?':
                    return asm.get_supply_channel()
                else:
                    return asm.set_supply_channel(int(param))
            else:
                return 'ERROR: bad command ' + str(cmd)

            # DAQ commands
        elif dev == 'DQ':
            if comm == 'IDN':
                return asm.daq
            elif comm == 'TEMP':
                return asm.get_daq_temp()
            elif comm == 'CHAN':
                if param == '?':
                    return asm.get_daq_channel()
                else:
                    return asm.set_daq_channel(int(param))
            elif comm == 'TCTY':
                if param == '?':
                    return asm.get_daq_tc_type()
                else:
                    return asm.set_daq_tc_type(param)
            elif comm == 'UNIT':
                if param == '?':
                    return asm.get_daq_temp_units()
                else:
                    return asm.set_daq_temp_units(param)
            else:
                return 'ERROR: bad command ' + str(cmd)

            # PID settings
        elif dev == 'PD':
            if comm == 'IDN':
                return asm.pid_settings
            elif comm == 'RSET':
                return asm.reset_pid()
            elif comm == 'RLIM':
                return asm.reset_pid_limits()
            elif comm == 'LIMS':
                if param == '?':
                    return asm.get_pid_limits()
            elif comm == 'KPRO':
                if param == '?':
                    return asm.pid_kp
                else:
                    asm.pid_kp = float(param)
            elif comm == 'KINT':
                if param == '?':
                    return asm.pid_ki
                else:
                    asm.pid_ki = float(param)
            elif comm == 'KDER':
                if param == '?':
                    return asm.pid_kd
                else:
                    asm.pid_kd = float(param)
            elif comm == 'SETP':
                if param == '?':
                    return asm.get_pid_setpoint()
                else:
                    return asm.set_pid_setpoint(float(param))
            elif comm == 'SAMP':
                if param == '?':
                    return asm.get_pid_sample_time()
                else:
                    return asm.set_pid_sample_time(float(param))
            elif comm == 'REGT':
                if param == '?':
                    return asm.get_pid_regulation()
                elif int(param) == 1:
                    asm.ready_assembly()
                    return asm.set_pid_regulation(True)
                elif int(param) == 0:
                    asm.set_pid_regulation(False)
                    return asm.set_supply_voltage(0)
            else:
                return 'ERROR: bad command ' + str(cmd)

            # Assembly
        elif dev == 'AM':
            if comm == 'STOP':
                return asm.stop()
            elif comm == 'RSET':
                return asm.reset_assembly()
            elif comm == 'REDY':
                return asm.ready_assembly()
            elif comm == 'MAXV':
                return asm.MAX_voltage
            elif comm == 'MAXA':
                return asm.MAX_current
            elif comm == 'DISC':
                return asm.disconnect()
            else:
                return 'ERROR: bad command ' + str(comm)

            # Bad Device
        else:
            return 'ERROR: bad device ' + str(dev)

    except NameError:
        return 'ERROR: parameter missing for ' + str(cmd)
    except ValueError:
        return 'ERROR: bad parameter ' + str(param)
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
    out_dict = {}
    for key, asm in asm_dict.items():
        if asm.pid_is_regulating and time.time() - t0_dict[key] >= asm.get_pid_sample_time():
            out_or_err = asm.update_supply()
            t0_dict[key] = time.time()
            out_dict[key] = out_or_err

    for key in out_dict:
        print(key + ':', out_dict[key])

    return t0_dict, out_dict


def server_loop(asm_dict):
    """
    Server that istens for commands from a remote machine, then executes the command on the respective assembly object.
    The server will continue to regulate an oven regardless of the connection of the remote machine. This means that if
    the connection to the remote machine is lost, the server will still continue to regulate the temperature of the
    heater assembly.

    Parameters:
    asm_dict : dictionary of str: HeaterAssembly
        dictionary containing all the HeaterAssembly objects to be used by the oven and their respective keys. The
        keys are used to identify each HeaterAssembly in the Oven class. Keys are not case-sensitive.

    """
    keys_raw = list(asm_dict)
    for key in keys_raw:  # change all keys to uppercase
        asm_dict[key.upper()] = asm_dict.pop(key)

    HOST = get_host_ip(loopback=False)
    PORT = 65432

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print('Bound to', HOST, PORT)

    while True:
        t0_dict = {}
        for key in asm_dict.keys():
            t0_dict[key] = time.time()  # Keeps track of time for every assembly. Used for update_heaters()

        while True:  # Listen for connections for one second. If timeout, update heaters using stored PID settings.
            s.settimeout(1)
            try:
                print('listening')
                s.listen()
                conn, addr = s.accept()
                break
            except socket.timeout:
                t0_dict, out_dict = update_heaters(asm_dict, t0_dict)

        conn.setblocking(False)
        print(f"Connected by {addr}")
        with conn:  # with connection: regulate oven, then listen for commands to carry on.
            while True:
                t0_dict, out_dict = update_heaters(asm_dict, t0_dict)
                time.sleep(0.2)
                try:
                    data = conn.recv(1024).decode('utf-8').upper()
                    if not data:
                        print(f"Disconnected by {addr}")
                        break

                    print(data)
                    out = process_command(data, asm_dict)
                    if out is None:
                        out = 'NOERROR'
                    conn.sendall((str(out) + '\r').encode('utf-8'))

                except BlockingIOError:
                    pass
                except ConnectionResetError:  # if connection is lost, go back to listening for connections.
                    print(f"Disconnected by {addr}")
                    break


def main():
    ps = Mr50040('10.176.42.220')
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
