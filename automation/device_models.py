"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""
import numpy as np
import serial
import time
from serial import Serial
from sys import platform
import pyvisa

from connection_type import SocketEthernetDevice
from device_type import PowerSupply
try:
    from device_type import MccDeviceWindows
except (ImportError, NameError):
    pass

try:
    from device_type import MccDeviceLinux
except (ImportError, NameError):
    pass

try:
    from mcculw import ul
    from mcculw import enums
except ModuleNotFoundError:
    pass


# ======================================================================================================================
# Gaussmeters
# ======================================================================================================================
class Gm3:
    def __init__(self, port, tmout=3):
        """
        Parameters
        ----------
        port : str
            Device port name. Can be found on device manager. Example: COM3
        tmout : float
            read timeout in seconds. Time that read() will wait for response before exiting.
        """
        self._ser = Serial(
            port=port,
            baudrate=115200,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=tmout
        )

        self.flush_buffer()

    def _query_(self, qry, read_size):
        """
        send a 6-length bytes object from qry message. Read the corresponding number of bytes.

        Parameters
        ----------
        qry : str
            command code from AlphaLab communication protocol. Format is two digits: 00.
        read_size : int
            number of bytes to receive from gaussmeter

        Returns
        -------
        bytes
            the stream of bytes from the gaussmeter.
        """
        for i in range(10):
            self._ser.write(bytes.fromhex(qry * 6))
            out = self._ser.read(read_size)
            time.sleep(0.01)
            if len(out) == read_size:
                return out
            time.sleep(0.3)
            self.flush_buffer()

        return 'ERROR: could not sent query: ' + str(qry)

    def parse_measurables(self, stream):
        """
        Translate the bytes stream from the STREAM_DATA and RESET_TIME commands into floats. The procedure is as
        follows:
            1 - Separate the entire stream into chunks of 6 bytes. Each chunk represents the measured quantities of
            time, x-field, y-field, z-field, and total magnetic field.
            2 - For each chunk, separate into individual bytes.
            3 - To get the raw digits of the measurable, bytes 3, 4, 5, and 6 should be interpreted as a 4-digit
            256-base number, with byte 3 being the most significant digit, and byte 6 being the least significant digit.
            3 - To get the sign of the measurable, read the bit in position 00001000 from byte 2. If
            the bit is 1, the sign is negative. Else, the sign is positive.
            4 - To get the order of magnitude of the measurable, first read the bits in positions 00000111 as an int. The
            order of magnitude is given by dividing the raw digits by 10 to the negative power given by the int.

        Parameters
        ----------
        stream : bytes
            the stream of bytes received from the gaussmeter. Should be 31 bytes long for STREAM_DATA, or 32 bytes
            long for RESET_TIME.

        Returns
        -------
        list of floats
            contains the float values for the measurables in the following order: time, x-field, y-filed, z-field,
            and total magnitude.
        """
        t, x, y, z, total = stream[0:6], stream[6:12], stream[12:18], stream[18:24], stream[24:30]
        variables = [t, x, y, z, total]
        out = []
        for var in variables:  # var is a bytes object with 6 bytes
            b1, b2, b3, b4, b5, b6 = var[0], var[1], var[2], var[3], var[4], var[5]  # bn variable are an int object
            raw = b3*256**3 + b4*256**2 + b5*256 + b6
            sign = (-2 * (b2 & 0b00001000) / 8) + 1  # if the bit is 1, sign is negative. If the bit is 0,
            # sign is positive.
            magn = 10 ** (b2 & 0b00000111)
            out.append(raw*sign/magn)

        return out

    def flush_buffer(self):
        self._ser.write(bytes.fromhex('FF' * 6))

    def autozero(self):
        pass

    def get_datapoint(self):
        """
        query the gaussmeter for an instantenous reading of the time index, x-axis, y-axis, z-axis, and magnitude in
        Gauss readings of a magnetic field. Note the time points only serve as an index for the data points but do
        not give meaningful time information.
        :return: list containing the float values for time (s), x-axis (G), y-axis (G), z-axis (G), and magnitude (G).

        The response from the gaussmeter comes as a long byte string containing hex numbers in the format 'AA. The
        data can be thought to be split in sections of 6 bytes. Each section contains the information for each
        measurable that the gaussmeter collects. Currently, there are only 5 measurables, which means that the
        response has a total of 30 bytes.

        The response is then converted into a python string. Since each hex number has two characters, the string is
        60 characters long.
        """
        try:
            out = self._query_('03', 31)
            return self.parse_measurables(out)
        except IndexError:
            try:
                self.flush_buffer()
                out = self._query_('03', 31)
                return self.parse_measurables(out)
            except IndexError:
                return 'ERROR: field could not be measured. Check connection to gaussmeter.'

    def get_zfield(self):
        return self.get_datapoint()[3]

    def reset_time(self):
        """
        query the gaussmeter for an instantenous reading of the time index, x-axis, y-axis, z-axis, and magnitude in
        Gauss readings of a magnetic field. Note the time points only serve as an index for the data points but do
        not give meaningful time information.
        :return: list containing the float values for time (s), x-axis (G), y-axis (G), z-axis (G), and magnitude (G).

        The response from the gaussmeter comes as a long byte string containing hex numbers in the format 'AA. The
        data can be thought to be split in sections of 6 bytes. Each section contains the information for each
        measurable that the gaussmeter collects. Currently, there are only 5 measurables, which means that the
        response has a total of 30 bytes.

        The response is then converted into a python string. Since each hex number has two characters, the string is
        60 characters long.
        """
        try:
            out = self._query_('04', 32)
            return self.parse_measurables(out)
        except IndexError:
            try:
                self.flush_buffer()
                out = self._query_('04', 32)
                return self.parse_measurables(out)
            except IndexError:
                return 'ERROR: field could not be measured. Check connection to gaussmeter.'

    def get_avg_zfield(self, t):
        ti = time.time()
        sum_ = 0
        i = 0
        while time.time() - ti <= t:
            sum_ += self.get_zfield()
            time.sleep(0.2)
            i += 1

        return abs(sum_ / i)

    @property
    def idn(self):
        out = self._query_('01', 21)
        time.sleep(0.05)
        while out[-1] != 7:
            out += self._query_('08', 21)
            time.sleep(0.05)
        return str(out)

    @property
    def settings(self):
        out = self._query_('02', 21)
        time.sleep(0.05)
        while out[-1] != 7:
            out += self._query_('08', 21)
            time.sleep(0.05)
        return str(out)


class Series9550:
    def __init__(self, gpib_address):
        rm = pyvisa.ResourceManager()
        self._inst = rm.open_resource('GPIB0::' + str(gpib_address) + '::INSTR')
        self.clear()

    def query(self, qry):
        qry += '\n'
        return self._inst.query(qry)

    def clear(self):
        self._inst.write('*CLS')

    def autozero(self):
        self._inst.write(':SYSTem:AZERo1')
        time.sleep(13)

    def get_zfield(self):
        s = self._inst.query(':MEASure:FLUX1?').split('G')[0]
        return float("".join(s.split()))

    def get_avg_zfield(self, n=10):
        n += 4
        f_l = np.asarray([])
        for i in range(n):
            f = self.get_zfield()
            time.sleep(0.2)
            f_l = np.append(f_l, f)

        f_l.sort()
        out = np.average(f_l[2:-2])
        mean_std = np.std(f_l[2:-2]) / np.sqrt(n-4)

        print(round(out, 5), '+-', mean_std)
        return out, mean_std

    def disconnect(self):
        self._inst.write('*GTL')

    @property
    def idn(self):
        return str(self._inst.query('*IDN?'))

    @property
    def field(self):
        return self.get_zfield()


# ======================================================================================================================
# Power Supplies
# ======================================================================================================================
class Spd3303x(SocketEthernetDevice, PowerSupply):
    """
    An ethernet-controlled power supply. Querys and commands based on manual for Siglent SPD3303X power supply.
    All voltages and currents are in Volts and Amps unless specified otherwise.
    """

    def __init__(
            self,
            ip4_address,
            port=5025,
            channel_voltage_limits=None,
            channel_current_limits=None,
            zero_on_startup=True
    ):
        """
        Parameters
        ----------
        ip4_address : str
            IPv4 address of the power supply.
        port : int
            port used for communication. Siglent recommends to use 5025 for the SPD3303X power supply. For other
            devices, can use any between 49152 and 65536.
        channel_voltage_limits : list
            Set an upper limit on the set voltage of the channels. Entry 0 represents channel 1, entry 1 represents 
            channel 2, and so on.
        channel_current_limits : list
            Set an upper limit on the set current of the channels. Entry 0 represents channel 1, entry 1 represents 
            channel 2, and so on.
        zero_on_startup : bool
            If True, run a routine to set turn off the output of both channels and set the set


        Note that all channel voltage limits are software-based since the power supply does not have any built-in limit
        features. This means that the channel limits are checked before sending a command to the power supply. If the
        requested set voltage is higher than the channel voltage limit, the command will not go through.
        """
        physical_parameters = {
            'MAX_voltage_limit': 32,
            'MAX_current_limit': 3.3,
            'number_of_channels': 2,
        }

        SocketEthernetDevice.__init__(
            self,
            ip4_address=ip4_address,
            port=port
        )
        PowerSupply.__init__(
            self,
            MAX_voltage=physical_parameters['MAX_voltage_limit'],
            MAX_current=physical_parameters['MAX_current_limit'],
            number_of_channels=physical_parameters['number_of_channels'],
            channel_voltage_limits=channel_voltage_limits,
            channel_current_limits=channel_current_limits,
            zero_on_startup=zero_on_startup,
        )

        if self._zero_on_startup:
            self.zero_all_channels()

    def _query_(self, qry):
        """
        Parameters
        ----------
        qry : str
            The qry can have only certain values. Check manual for valid queries.
        Return
        ------
        str
            Decode the response in bytes using utf-8
        """
        return self._query(qry.encode('utf-8')).decode('utf-8').strip()
    
    def _command_(self, cmd):
        """
        Parameters
        ----------
        cmd : str
            Check manual for valid commands
        Return
        ------
        Nonetype
            returns None if command is sent succesfully.
        """
        return self._command(cmd.encode('utf-8'))

    # Methods
    # -------
    def get_channel_state(self, channel):
        """
        The 5th digit from right to left of the binary output from the system status query gives the state of channel 1,
        1 for on and 0 for off.

        Parameters
        ----------
        channel : int
            channel to get the state from. Number is from 1 up to the number of channels of the power supply.

        Returns
        -------
        bool
            If succesful, True for ON, False for OFF.
        str
            Else, return error string
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        out = self.system_status[-4-channel]
        try:
            return bool(int(out))
        except ValueError:
            return out

    def set_channel_state(self, channel, state):
        """
        Parameters
        ----------
        channel : int
            channel to set the state. Number is from 1 up to the number of channels of the power supply.
        state : bool, int
            True or 1 for ON, False or 0 for OFF

        Returns
        -------
        None
            If succesful, return None
        str
            Else, return error string
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        if type(state) is not bool and type(state) is not int:
            return 'ERROR: type ' + str(type(state)) + ' not supported. Input True or 1 for ON, or False or 0 for OFF'

        state = bool(state)
        if state:
            state_str = 'ON'
        else:
            state_str = 'OFF'

        cmd = 'Output CH' + str(channel) + ',' + state_str
        self._command_(cmd)

    def get_setpoint_voltage(self, channel):
        """
        Parameters
        ----------
        channel : int
            channel to get the voltage from. Number is from 1 up to the number of channels of the power supply.

        Returns
        -------
        float
            If succesful.
        str
            Else, return error string
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        qry = 'CH' + str(channel) + ':voltage?'
        return float(self._query_(qry))

    def set_voltage(self, channel, volts):
        """
        Parameters
        ----------
        channel : int
            channel to set the state. Number is from 1 up to the number of channels of the power supply.
        volts : float
            new setpoint voltage in Volts

        Returns
        -------
        None
            If succesful, return None
        str
            Else, return error string
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        if volts > self.get_voltage_limit(channel):
            return 'ERROR: CH' + str(channel) + ' voltage not set. New voltage is higher than limit'

        volts = round(volts, 3)
        chan = 'CH' + str(channel)
        cmd = chan + ':voltage ' + str(volts)
        self._command_(cmd)

    def get_actual_voltage(self, channel):
        """
        Parameters
        ----------
        channel : int
            channel to get the voltage from. Number is from 1 up to the number of channels of the power supply.

        Returns
        -------
        float
            If succesful.
        str
            Else, return error string
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        qry = 'measure:voltage? ' + 'CH' + str(channel)
        return float(self._query_(qry))

    def get_setpoint_current(self, channel):
        """
        Parameters
        ----------
        channel : int
            channel to get the current from. Number is from 1 up to the number of channels of the power supply.

        Returns
        -------
        float
            If succesful.
        str
            Else, return error string
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        qry = 'CH' + str(channel) + ':current?'
        return float(self._query_(qry))

    def set_current(self, channel, amps):
        """
        Parameters
        ----------
        channel : int
            channel to set the state. Number is from 1 up to the number of channels of the power supply.
        amps : float
            new setpoint current in Amps

        Returns
        -------
        None
            If succesful, return None
        str
            Else, return error string
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        if amps > self.get_current_limit(channel):
            return 'ERROR: CH' + str(channel) + ' current not set. New current is higher than limit'

        amps = round(amps, 3)
        chan = 'CH' + str(channel)
        cmd = chan + ':current ' + str(amps)
        self._command_(cmd)

    def get_actual_current(self, channel):
        """
        Parameters
        ----------
        channel : int
            channel to get the current from. Number is from 1 up to the number of channels of the power supply.

        Returns
        -------
        float
            If succesful.
        str
            Else, return error string
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        qry = 'measure:current? ' + 'CH' + str(channel)
        return float(self._query_(qry))

    # Properties
    # ----------
    @property
    def idn(self):
        qry = '*IDN?'
        return self._query_(qry)

    @property
    def ip4_address(self):
        qry = 'IP?'
        return self._query_(qry)

    @property
    def system_status(self):
        """
        Query the power supply for its status. The output is a hex number represented in bytes. To be interpreted, it
        needs to be converted into a 10-digit binary number. Each digit in the binary number represents a state for
        some physical attribute of the power supply. Refer to the manual for the meaning of each digit.

        Return
        ------
        str
            10-digit binary number as a string representing the status of the system
        """
        qry = 'system:status?'
        reply_hex_str = self._query_(qry)  # hex number represented in bytes
        reply_bin_str = f'{int(reply_hex_str, 16):0>10b}'  # 10 digit binary num, padded with 0, as string
        return reply_bin_str

    @property
    def ch1_state(self):
        """
        :return bool: True for on, False for off.
        """
        return self.get_channel_state(1)

    @ch1_state.setter
    def ch1_state(self, state):
        """
        :param bool state: True for on, False for off.
        """
        self.set_channel_state(1, state)

    @property
    def ch2_state(self):
        """
        :return bool: True for on, False for off.
        """
        return self.get_channel_state(2)

    @ch2_state.setter
    def ch2_state(self, state):
        """
        :param bool state: True for on, False for off.
        """
        self.set_channel_state(2, state)

    @property
    def ch1_set_voltage(self):
        return self.get_setpoint_voltage(1)

    @ch1_set_voltage.setter
    def ch1_set_voltage(self, volts):
        self.set_voltage(1, volts)

    @property
    def ch2_set_voltage(self):
        return self.get_setpoint_voltage(2)

    @ch2_set_voltage.setter
    def ch2_set_voltage(self, volts):
        self.set_voltage(2, volts)

    @property
    def ch1_actual_voltage(self):
        return self.get_actual_voltage(1)

    @property
    def ch2_actual_voltage(self):
        return self.get_actual_voltage(2)

    @property
    def ch1_set_current(self):
        return self.get_setpoint_current(1)

    @ch1_set_current.setter
    def ch1_set_current(self, amps):
        self.set_current(1, amps)

    @property
    def ch2_set_current(self):
        return self.get_setpoint_current(2)

    @ch2_set_current.setter
    def ch2_set_current(self, amps):
        self.set_current(2, amps)

    @property
    def ch1_actual_current(self):
        return self.get_actual_current(1)

    @property
    def ch2_actual_current(self):
        return self.get_actual_current(2)

    @property
    def ch1_voltage_limit(self):
        return self._channel_voltage_limits[0]

    @ch1_voltage_limit.setter
    def ch1_voltage_limit(self, volts):
        self.set_voltage_limit(1, volts)

    @property
    def ch1_current_limit(self):
        return self._channel_current_limits[0]

    @ch1_current_limit.setter
    def ch1_current_limit(self, amps):
        self.set_current_limit(1, amps)

    @property
    def ch2_voltage_limit(self):
        return self._channel_voltage_limits[1]

    @ch2_voltage_limit.setter
    def ch2_voltage_limit(self, volts):
        self.set_voltage_limit(2, volts)

    @property
    def ch2_current_limit(self):
        return self._channel_current_limits[1]

    @ch2_current_limit.setter
    def ch2_current_limit(self, amps):
        self.set_current_limit(2, amps)


class Mr50040(SocketEthernetDevice, PowerSupply):
    def __init__(
            self,
            ip4_address=None,
            port=5025,
            zero_on_startup=True
    ):
        """
        Parameters
        ----------
        ip4_address : str
            IPv4 address of the power supply.
        port : int
            port used for communication. Siglent recommends to use 5025 for the SPD3303X power supply. For other
            devices, can use any between 49152 and 65536.
        zero_on_startup : bool
            If True, run a routine to set turn off the output of both channels and set the set
        """
        physical_parameters = {
            'MAX_voltage_limit': 500,
            'MAX_current_limit': 40,
            'number_of_channels': 1,
        }

        SocketEthernetDevice.__init__(
            self,
            ip4_address=ip4_address,
            port=port
        )
        PowerSupply.__init__(
            self,
            MAX_voltage=physical_parameters['MAX_voltage_limit'],
            MAX_current=physical_parameters['MAX_current_limit'],
            number_of_channels=physical_parameters['number_of_channels'],
            channel_voltage_limits=None,  # not used by this class. Limit is enforced by hardware.
            channel_current_limits=None,  # not used by this class. Limit is enforced by hardware.
            zero_on_startup=zero_on_startup,
        )

        if self._zero_on_startup is True and ip4_address is not None:
            self.zero_all_channels()

    def get_error_code(self):
        """
        Queries the supply for an error, then extracts the error code from the message

        Returns
        -------
        int
            error code as an int. Refer to MR50040 programming manual to see the meaning of error code.
        """
        return int(self._query('system:error?\n'.encode('utf-8')).decode('utf-8').split(',')[0])

    def get_error(self):
        """
        Queries the supply for an error, then returns the error code and the error message in a single string
        separated by a comma.

        Returns
        -------
        str
            format: '<code>,<message>'
        """
        return self._query('system:error?\n'.encode('utf-8')).decode('utf-8').strip()

    def _query_(self, qry, data_type):
        """
        query the device through a socket connection using the self._query method from the SocketEthernetDevice
        master class. After querying, check for errors directly to the power supply. If an error occured, return the
        error message.

        Parameters:
        -----------
        qry : str
            message to send as a string. No need to add \n.
        data_type : type
            should be the callable object of int, float, or str. This is used to change the string query from
            the power supply into its correct type.

        Returns
        -------
        str
            Either the requested information or an error string
        float
            Requested value as a float
        int
            Requested value as an int. Usually for True/False requests or status bytes.
        """
        qry += '\n'
        out = self._query(qry.encode('utf-8')).decode('utf-8').strip()
        code, err = self.get_error().split(',')
        if int(code) != 0:
            return str(out) + '\nERROR: ' + str(err)
        else:
            return data_type(out)

    def _command_(self, cmd):
        """
        send a command to the device through a socket connection using the self._command method from the
        SocketEthernetDevice master class. After sending the command, check for errors directly to the power supply.
        If an error occured, return the error message.
        Returns
        -------
        None
            If succesful, return None
        str
            Else, return an error string
        """
        cmd += '\n'
        out = self._command(cmd.encode('utf-8'))
        time.sleep(0.3)
        code, err = self.get_error().strip().split(',')
        if int(code) != 0:
            return 'ERROR: ' + str(err)
        else:
            return out

    def get_status_byte(self):
        """
        Refer to Mr50040 programming manual for more info on status byte

        Returns
        -------
        int
            representing the status byte
        """
        return self._query_('*stb?', int)

    def get_cc_to_cv_protection_state(self):
        """
        Get if Constant Current to Constant Voltage protection is on or off. If this protection is on, the power supply
        will shut off the output whenever the supply switched from Constant Current operation to Constant Voltage.

        Returns
        -------
        bool
            True for on, False for off
        str
            If an error occurs, return the error string
        """
        out = self._query_('cccv:protection?', int)
        try:  # if out is error string, return error string
            return bool(out)
        except ValueError:
            return out

    def set_cc_to_cv_protection_state(self, state):
        """
        Set Constant Current to Constant Voltage protection on or off. If this protection is on, the power supply
        will shut off the output whenever the supply is switched from Constant Current operation to Constant Voltage.

        Parameters
        ----------
        state : bool
            True for on, False for off.

        Returns
        -------
        None
            If succesful, return None
        str
            If an error occurs, return the error string
        """
        try:
            return self._command_('cccv:protection ' + str(int(state)))
        except ValueError:
            return 'ERROR: type ' + str(type(state)) + ' not supported, state should be a bool'

    def get_cv_to_cc_protection_state(self):
        """
        Get if Constant Voltage to Constant Current protection is on or off. If this protection is on, the power supply
        will shut off the output whenever the supply is switched from Constant Voltage operation to Constant Current.

        Returns
        -------
        bool
            True for on, False for off
        str
            If an error occurs, return the error string
        """
        out = self._query_('cvcc:protection?', int)
        try:  # if out is error string, return error string
            return bool(out)
        except ValueError:
            return out

    def set_cv_to_cc_protection_state(self, state):
        """
        Set Constant Voltage to Constant Current protection on or off. If this protection is on, the power supply
        will shut off the output whenever the supply is switched from Constant Voltage operation to Constant Current.

        Parameters
        ----------
        state : bool
            True for on, False for off.

        Returns
        -------
        None
            If succesful, return None
        str
            If an error occurs, return the error string
        """
        try:
            return self._command_('cvcc:protection ' + str(int(state)))
        except ValueError:
            return 'ERROR: type ' + str(type(state)) + ' not supported, state should be a bool'

    def get_channel_state(self, channel=1):
        """
        Get if output is on or off.

        Parameters
        ----------
        channel : int, optional
            Anything else than 1 will result in error. Exists only for compatibility with the library.

        Returns
        -------
        None
            If succesful, return None
        str
            If an error occurs, return the error string
        """
        out = self._query_('output?', int)
        try:  # if out is error string, return error string.
            return bool(out)
        except ValueError:
            return out

    def set_channel_state(self, channel=1, state=None):
        """
        Set the output of the supply on or off.

        Parameters:
        -----------
        channel : int, optional
            Anything else than 1 will result in error. Exists only for compatibility with the library.
        state : bool
            True for on, False for off

        Returns
        -------
        None
            If succesful, return None
        str
            If an error occurs, return the error string
        """
        if state is None:
            return 'ERROR: keyword argument state parameter missing'
        try:
            return self._command_('output ' + str(int(state)))
        except ValueError:
            return 'ERROR: type ' + str(type(state)) + ' not supported, state should be a bool'

    def get_setpoint_voltage(self, channel=1):
        """

        Parameters:
        -----------
        channel : int, optional
            Anything else than 1 will result in error. Exists only for compatibility with the library.

        Returns
        -------
        float
            If succesful, return float value
        str
            If an error occurs, return the error string
        """
        return self._query_('voltage?', float)

    def set_voltage(self, channel=1, volts=None):
        """

        Parameters:
        -----------
        channel : int, optional
            Anything else than 1 will result in error. Exists only for compatibility with the library.
        volts : float
            setpoint voltage in volts.

        Returns
        -------
        None
            If succesful, return None
        str
            If an error occurs, return the error string
        """
        if volts is None:
            raise TypeError('ERROR: volts parameter missing')
        return self._command_('voltage ' + str(volts))

    def get_actual_voltage(self, channel=1):
        return self._query_('measure:voltage?', float)

    def get_setpoint_current(self, channel=1):
        return self._query_('current?', float)

    def set_current(self, channel=1, amps=None):
        if amps is None:
            raise TypeError('ERROR: amps parameter missing')
        return self._command_('current ' + str(amps))

    def get_actual_current(self, channel=1):
        return self._query_('measure:current?', float)

    def get_setpoint_power(self):
        return self._query_('power?', float)

    def get_actual_power(self):
        return self._query_('measure:power?', float)

    def get_voltage_limit(self, channel=1):
        """
        This is a voltage limit enforced by the power supply.

        Parameters:
        -----------
        channel : int, optional
            Anything else than 1 will result in error. Exists only for compatibility with the library.

        Returns
        -------
        float
            If succesful, return float value
        str
            If an error occurs, return the error string
        """
        return self._query_('voltage:max?', float)

    def set_voltage_limit(self, channel=1, volts=None):
        """
        This is a voltage limit enforced by the power supply.

        Parameters:
        -----------
        channel : int, optional
            Anything else than 1 will result in error. Exists only for compatibility with the library.
        volts : float
            voltage limit in volts

        Returns
        -------
        None
            If succesful, return None
        str
            If an error occurs, return the error string
        """
        if volts is None:
            return 'ERROR: volts parameter missing'
        return self._command_('voltage:max ' + str(volts))

    def get_current_limit(self, channel=1):
        """
        This is a current limit enforced by the power supply.

        Parameters:
        -----------
        channel : int, optional
            Anything else than 1 will result in error. Exists only for compatibility with the library.

        Returns
        -------
        float
            If succesful, return float value
        str
            If an error occurs, return the error string
        """
        return self._query_('current:max?', float)

    def set_current_limit(self, channel=1, amps=None):
        """
        This is a current limit enforced by the power supply.

        Parameters:
        -----------
        channel : int, optional
            Anything else than 1 will result in error. Exists only for compatibility with the library.
        amps : float
            current limit in volts

        Returns
        -------
        None
            If succesful, return None
        str
            If an error occurs, return the error string
        """
        if amps is None:
            return 'ERROR: amps parameter missing'
        return self._command_('current:max ' + str(amps))

    @property
    def idn(self):
        return self._query_('*IDN?', str)

    @property
    def is_current_limited(self):
        out = self._query_('status:operation:condition?', int)
        try:
            return out & 0b0000010
        except TypeError:
            return out
    @property
    def is_voltage_limited(self):
        out = self._query_('status:operation:condition?', int)
        try:
            return out & 0b0000001
        except TypeError:
            return out

    @property
    def error_code(self):
        return self.get_error_code()

    @property
    def error_message(self):
        return self.get_error().split(',')[1]

    @property
    def voltage(self):
        return self.get_actual_voltage()

    @property
    def current(self):
        return self.get_actual_current()

    @property
    def power(self):
        return self.get_actual_power()


# ======================================================================================================================
# Temperature DAQs
# ======================================================================================================================
if platform == 'win32':
    class WebTc(MccDeviceWindows):
        def __init__(self, board_number, ip4_address=None, port=54211, default_units='celsius'):
            """
            Class for a Web_Tc device from MCC. Might make a master class for temperature daq

            Parameters
            ----------
            ip4_address : string
                The current IPv4 address of the device. Can be found through instacal. For the Web_TC,
                the ip4_address is unused because the API functions that use it are not supported by this device.
            port : int
                The port number to be used. MCC recommends to use 54211. Port 80 is reserved for the web browser
                application. For the Web_TC, the port number is unused because the API functions that use it are not
                supported by this device.
            board_number : int
                All MCC devices have a board number which can be configured using instacal. The instance of Web_Tc must
                match the board number of its associated device. Possible values from 0 to 99.
            default_units : string
                the units in which the temperature is shown, unless specified otherwise in the method. Possible values
                (not
                case-sensitive):
                for Celsius                 celsius,               c
                for Fahrenheit              fahrenheit,            f
                for Kelvin                  kelvin,                k
                for calibrated voltage      volts, volt, voltage,  v
                for uncalibrated voltage    raw, none, noscale     r
            """

            super().__init__(board_number=board_number, ip4_address=ip4_address, port=port,
                             default_units=default_units)


    class ETcWindows(MccDeviceWindows):
        # TODO: check if the io methods can be moved to the super class MccDeviceWindows
        def __init__(self, board_number, ip4_address=None, port=54211, default_units='celsius'):
            """
            Class for a Web_Tc device from MCC. Might make a master class for temperature daq

            Parameters
            ----------
            ip4_address : string
                The current IPv4 address of the device. Can be found through instacal. For the Web_TC,
                the ip4_address is unused because the API functions that use it are not supported by this device.
            port : int
                The port number to be used. MCC recommends to use 54211. Port 80 is reserved for the web browser
                application. For the Web_TC, the port number is unused because the API functions that use it are not
                supported by this device.
            board_number : int
                All MCC devices have a board number which can be configured using instacal. The instance of Web_Tc must
                match the board number of its associated device. Possible values from 0 to 99.
            default_units : string
                the units in which the temperature is shown, unless specified otherwise in the method. Possible values
                (not
                case-sensitive):
                for Celsius                 celsius,               c
                for Fahrenheit              fahrenheit,            f
                for Kelvin                  kelvin,                k
                for calibrated voltage      volts, volt, voltage,  v
                for uncalibrated voltage    raw, none, noscale     r
            """

            super().__init__(board_number=board_number, ip4_address=ip4_address, port=port,
                             default_units=default_units)

        # -------------------
        # Auxiliary I/O ports
        # -------------------
        def config_io_channel(self, chan, direction):
            if not (0 <= chan <= 7):
                raise ValueError('ERROR: bit_num ' + str(chan) + ' not allowed. Must be between 0 and 7, inclusive.'
                                 )
            direction_dict = {
                'in': 2,
                'i': 2,
                'out': 1,
                'o': 1
            }

            ul.d_config_bit(
                board_num=self._board_number,
                port_type=enums.DigitalPortType.AUXPORT,
                bit_num=chan,
                direction=direction_dict[direction])

        def get_bit(self, chan):
            return ul.d_bit_in(board_num=self._board_number, port_type=enums.DigitalPortType.AUXPORT, bit_num=chan)

        def set_bit(self, chan, out):
            ul.d_bit_out(self._board_number, port_type=enums.DigitalPortType.AUXPORT, bit_num=chan, bit_value=out)

        def config_io_byte(self, direction):
            direction_dict = {
                'in': 2,
                'i': 2,
                'out': 1,
                'o': 1
            }

            ul.d_config_port(
                board_num=self._board_number,
                port_type=enums.DigitalPortType.AUXPORT,
                direction=direction_dict[direction])

        def get_byte(self):
            return ul.d_in(board_num=self._board_number, port_type=enums.DigitalPortType.AUXPORT)

        def set_byte(self, val):
            ul.d_out(board_num=self._board_number, port_type=enums.DigitalPortType.AUXPORT, data_value=val)


if platform == 'linux' or platform == 'linux2':
    class ETcLinux(MccDeviceLinux):
        def __init__(self, ip4_address, port=54211, default_units='celsius'):
            super().__init__(ip4_address, port, default_units)


# ======================================================================================================================
# Picomotor controller
# ======================================================================================================================
class Model8742(SocketEthernetDevice):
    # TODO: Add error handling
    # TODO: Add comments
    """
    Newport picomotor controller.
    """
    def __init__(
            self,
            ip4_address,
            port=23,
            number_of_channels=4
    ):
        """
        Parameters
        ----------
        ip4_address : str
        port : int
            Model8742 uses Telnet therefore need to use port 23.
        number_of_channels : int
            number of physical motor channels

        """
        SocketEthernetDevice.__init__(self, ip4_address=ip4_address, port=port)
        if self._ip4_address is not None:
            self._socket.recv(4096)  # Receive connection acknowledgement

        self._number_of_channels = number_of_channels

    def _query_(self, qry):
        qry += '\r'
        reply = self._query(qry.encode('utf-8'))
        return reply.decode('utf-8')

    def _command_(self, cmd=None):
        """
        :param str cmd:
        :return:
        """

        cmd += '\r'
        out = self._command(cmd.encode('utf-8'))
        return out

    def restart_controller(self):
        """
        Upon restart the controller reloads parameters (e.g., velocity and acceleration) last saved in non-volatile
        memory and sets Home (DH) position to 0.
        """
        self._command_('RS')

    def save_settings(self):
        """
        Settigns to be saved:
        1. Hostname (see HOSTNAME command)
        2. IP Mode (see IPMODE command)
        3. IP Address (see IPADDRESS command)
        4. Subnet mask address (see NETMASK command)
        5. Gateway address (see GATEWAY command)
        6. Configuration register (see ZZ command)
        7. Motor type (see QM command)
        8. Desired Velocity (see VA command)
        9. Desired Acceleration (see AC command)
        """
        self._command_('SM')

    def load_settings(self):
        self._command_('*RCL1')

    def _reset_factory_settings(self):
        """
        Settigns to be reset:
        1. Hostname (see HOSTNAME command)
        2. IP Mode (see IPMODE command)
        3. IP Address (see IPADDRESS command)
        4. Subnet mask address (see NETMASK command)
        5. Gateway address (see GATEWAY command)
        6. Configuration register (see ZZ command)
        7. Motor type (see QM command)
        8. Desired Velocity (see VA command)
        9. Desired Acceleration (see AC command)
        """
        self._command_('*RCL0')

    def is_motion_done(self, chan):
        """
        Returns True if the picomotor is not moving. Returns False if the picomotor is currently moving.
        :param int chan:
        :return bool:
        """
        return bool(int(self._query_(str(chan) + 'MD?')))

    def get_instant_position(self, chan):
        """
        get the instantenous position with respect to the origin (0-step coordinate) in steps. Can be called in the
        middle of the picomotor moving.
        :param int chan:
        :return int: number of steps from the origin.
        """
        return int(self._query_(str(chan) + 'TP?'))

    def get_setpoint_position(self, chan):
        """
        get the position at which the picomotor is set to move to. If the picomotor is currently not moving,
        this position is the same as the instantenous position.
        :param chan:
        :return:
        """
        return int(self._query_(str(chan) + 'PA?'))

    def get_velocity(self, chan):
        """
        get the velocity at which the picomotor will move for any displacement command. Measured in steps per second.
        :param chan:
        :return int: steps per second.
        """
        return int(self._query_(str(chan) + 'VA?'))

    def get_acceleration(self, chan):
        """
        get the acceleration at which the picomotor will stop and accelerate from rest. Measured in steps per second
        per second.
        :param int chan:
        :return int: steps per second per second.
        """
        return int(self._query_(str(chan) + 'AC?'))

    def hard_stop_all(self):
        """
        stop all movement if the picomotor as fast as it can stop. Does not take into account the acceleration
        parameter.
        """
        self._command_('AB')

    def soft_stop(self, chan=''):
        """
        decelerate the selected channel until it comes to a stop at the acceleration specified by the acceleration
        parameter. If no channel is selected, the controller will automatically choose the channel that is currently
        moving.
        :param int chan:
        """
        self._command_(str(chan) + 'ST')

    def set_origin(self, chan):
        """
        sets the current physical position as the position with the 0-steps coordinate.
        :param int chan:
        """
        self._command_(str(chan) + 'DH' + '0')

    def set_position(self, chan, position):
        """
        :param int chan:
        :param int position: measured in steps with respect to the home position  # TODO: check home position or origin
        :return:
        """
        self._command_(str(chan) + 'PA' + str(position))
        while not self.is_motion_done(chan=chan):
            pass

    def displace(self, chan, dis):
        """
        :param int chan:
        :param dis: measured in steps. With respect to the position just before starting to move. # TODO: check
        :return:
        """
        self._command_(str(chan) + 'PR' + str(dis))
        while not self.is_motion_done(chan=chan):
            pass

    def move_indefinetely(self, chan, direction):
        """
        Moves indefinetely. Need to use hard_stop or other stopping command to stop the motion.
        :param int chan:
        :param str direction: possible values for positive direction: +, pos, or positive. For negative direction: -,
        neg, or negative.
        """
        while not self.is_motion_done(chan=chan):
            pass
        time.sleep(0.5)

        direct_dict = {
            '+': '+',
            'pos': '+',
            'positive': '+',
            '-': '-',
            'neg': '-',
            'negative': '-'
        }

        self._command_(str(chan) + 'MV' + str(direct_dict[direction]))

    def set_velocity(self, chan, vel):
        """
        :param int chan:
        :param int vel:
        """
        self._command_(str(chan) + 'VA' + str(vel))

    def set_acceleration(self, chan, acc):
        self._command_(str(chan) + 'AC' + str(acc))

    @property
    def idn(self):
        return self._query_('*IDN?')

    @property
    def mac_address(self):
        return self._query_('MACADDR?')

    @property
    def hostname(self):
        return self._query_('HOSTNAME?')

    @property
    def position_ch1(self):
        return self.get_instant_position(chan=1)

    @property
    def position_ch2(self):
        return self.get_instant_position(chan=2)

    @property
    def position_ch3(self):
        return self.get_instant_position(chan=3)

    @property
    def position_ch4(self):
        return self.get_instant_position(chan=4)

    @property
    def setpoint_position_ch1(self):
        return self.get_setpoint_position(chan=1)

    @setpoint_position_ch1.setter
    def setpoint_position_ch1(self, new_pos):
        self.set_position(chan=1, position=new_pos)

    @property
    def setpoint_position_ch2(self):
        return self.get_setpoint_position(chan=2)

    @setpoint_position_ch2.setter
    def setpoint_position_ch2(self, new_pos):
        self.set_position(chan=2, position=new_pos)

    @property
    def setpoint_position_ch3(self):
        return self.get_setpoint_position(chan=3)

    @setpoint_position_ch3.setter
    def setpoint_position_ch3(self, new_pos):
        self.set_position(chan=3, position=new_pos)

    @property
    def setpoint_position_ch4(self):
        return self.get_setpoint_position(chan=4)

    @setpoint_position_ch4.setter
    def setpoint_position_ch4(self, new_pos):
        self.set_position(chan=4, position=new_pos)

    @property
    def velocity_ch1(self):
        return self.get_velocity(chan=1)

    @velocity_ch1.setter
    def velocity_ch1(self, new_vel):
        self.set_velocity(chan=1, vel=new_vel)

    @property
    def velocity_ch2(self):
        return self.get_velocity(chan=2)

    @velocity_ch2.setter
    def velocity_ch2(self, new_vel):
        self.set_velocity(chan=2, vel=new_vel)

    @property
    def velocity_ch3(self):
        return self.get_velocity(chan=3)

    @velocity_ch3.setter
    def velocity_ch3(self, new_vel):
        self.set_velocity(chan=3, vel=new_vel)

    @property
    def velocity_ch4(self):
        return self.get_velocity(chan=4)

    @velocity_ch4.setter
    def velocity_ch4(self, new_vel):
        self.set_velocity(chan=4, vel=new_vel)


class Vxm:
    def __init__(self, port, tmout=10):
        self._ser = serial.Serial(port=port, baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1,
                                  timeout=tmout)
        self.initialize()


    def _query_(self, qry):
        qry += ',R'
        self._ser.write(qry.encode('utf-8'))
        out = self._ser.read_until(b'^')
        time.sleep(0.3)
        self._ser.write('C'.encode('utf-8'))
        return out

    def _command_(self, cmd):
        self._ser.write(cmd.encode('utf-8'))
        time.sleep(0.3)
        self._ser.write('C'.encode('utf-8'))

    def initialize(self):
        """
        Initialize remote connection to motor controller.
        """
        self._ser.write('F'.encode('utf-8'))
        time.sleep(0.1)
        self._ser.write('N'.encode('utf-8'))
        time.sleep(0.1)
        self._ser.write('C'.encode('utf-8'))
        time.sleep(0.1)
        self._ser.write('C'.encode('utf-8'))
        time.sleep(0.1)

    def disconnect(self):
        self._ser.write('Q'.encode('utf-8'))

    def displace(self, channel, steps):
        """
        displace the slide a number of steps with respect to its standing position. If the number of steps to
        dispalce is larger than 10000, the displacement will be done in two motions.
        :param int channel: motor channel.
        :param int steps: steps to displace
        :return str: return '^' when the motor has completed the motion
        """
        if abs(steps) > 10000:
            self.displace(channel, steps//2)
            return self.displace(channel, steps - steps//2)
        else:
            return self._query_('I' + str(channel) + 'M' + str(steps))

    def set_position(self, channel, pos):
        """
        displace the slide to the specified position with respect to the origin
        :param int channel: motor channel.
        :param int pos: final position with respect to the origin
        :return str: return '^' when the motor has completed the motion
        """
        return self._query_('IA' + str(channel) + 'M' + str(pos))

    def set_origin(self, channel):
        """
        set the current standing position as the origin
        :param int channel: motor channel.
        :return str: return '^' when the motor has completed the motion

        """
        return self._query_('IA' + str(channel) + 'M-0')

    def set_speed(self, channel, speed):
        """
        set the speed at which the motor will move in steps per second. Factory value is 2000 steps per second. 1 <=
        speed <= 6000
        :param int channel: motor channel.
        :param int speed: steps per second
        :return str: return '^' when the motor has completed the motion
        """
        return self._query_('S' + str(channel) + 'M' + str(speed))

    def set_acceleration(self, channel, acc):
        """
        Set the acceleration at which the motor will stop and start movign. Factory value is 2. possible values: 1 <=
        acc <= 127
        :param int channel: motor channel.
        :param int acc: arbitrary units
        :return str: return '^' when the motor has completed the motion
        """
        return self._query_('A' + str(channel) + 'M' + str(acc))

    def get_negative_limit_switch(self):
        self._ser.write('?'.encode('utf-8'))
        return bool(ord(self._ser.read(1).decode('utf-8')) & 0b00000010)

    @property
    def idn(self):
        return 'VXM VelMex motor controller, two channels'
# ======================================================================================================================
# RGA
# ======================================================================================================================
class Srs100:
    def __init__(
            self,
            port,
            read_timeout=3
    ):
        s = serial.Serial(
            port=port,
            baudrate=28800,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=read_timeout
        )
        self._port = port
        self._read_timeout = read_timeout
        self._serial_port = s
        self._filament_state = False
        self._cdem_state = False
        self._noise_floor = 0

        self.initialize()

    def _query_(self, qry):
        """
        query the RGA.

        Parameters
        ----------
        qry : str
            RGA command to send.

        Returns
        -------
        str
            the requested query or error string
        """
        qry += '\r'
        self._serial_port.write(data=qry.encode('utf-8'))
        time.sleep(0.3)
        return self._serial_port.read_until(expected='\n\r'.encode('utf-8')).decode('utf-8').strip()

    def _command_noresponse_(self, cmd):
        """
        send command to RGA. Used only for commands that do not return the status byte once the RGA has completed the
        command. The status byte is queried once the command has been sent and used for error handling.

        Paramters
        ---------
        cmd : str
            RGA command to send

        Returns
        -------
        str
            If an error occurs, return an error string

        None
            Else, return None
        """
        cmd += '\r'
        self._serial_port.write(data=cmd.encode('utf-8'))
        time.sleep(0.3)
        return self.get_error_message_all()

    def _command_(self, cmd):
        """
        send command to RGA. Used only for commands that return the status byte once the RGA has completed the command.

        Paramters
        ---------
        cmd : str
            RGA command to send

        Returns
        -------
        str
            If an error occurs, return an error string

        None
            Else, return None
        """

        stat = int(self._query_(cmd))
        return self.get_error_message_all(status=stat)

    # General
    # -------
    def initialize(self):
        print(self.idn)
        self._noise_floor = self.get_detector_scan_speed()
        print('Flushing communication buffers')
        return self.flush_buffers()

    def flush_buffers(self):
        return self._command_('IN0')

    # Error handling
    # --------------
    def _create_error_msg(self, byte, lst):
        """
        Creates an error message based on a status or error byte and a list containing the error messages
        corresponding to each bit inside the status byte.

        Parameters
        ----------
        byte : int
            status or error byte. Should be 8-bit
        lst : list
            Contains the error messages associated with each bit in the status byte. The index corresponds to
            the message's respective bit.

        Returns
        -------
        None
            if no errors are found (status byte is 0), return None
        str
            else, return the error string
        """
        if byte == 0:
            return None
        final_msg = ''
        for i in range(8):
            if byte & int(2 ** i):
                final_msg += ' - ' + lst[i] + '\n'
        return final_msg

    def _translate_to_decimal(self, raw):
        """
        takes raw bytes output from RGA measurement and turns it into a base 10 int. RGA output is 4-bytes int, signed.

        Parameters
        ----------
        raw : bytes
            output from RGA measurements, usually from ion current readings. Should be 4-bytes, little-endian, signed.

        Returns
        -------
        int
            base 10
        """
        int_10 = int.from_bytes(raw, 'little', signed=True)
        return int_10

    def get_status_byte(self):
        """
        Status byte indicates what type of error has occurred. To see details about error, query the appropriate
        error type, or use self.get_error_message_all() to look for an error across all types.

        ----------------------------------------------------------------------------------------------------------------
          bit index  |       internal check       |  Error type  |  query  |  name for class methods
        ----------------------------------------------------------------------------------------------------------------
              7      | not used                   |  n/a         |  n/a    |  n/a
              6      | 24V External power supply  |  PS_ERR      |  EP?    |  supply
              5      | Electrometer / detector    |  DET_ERR     |  ED?    |  electrometer
              4      | Quadrupole mass filter     |  QMF_ERR     |  EQ?    |  mass_filter
              3      | Electron multiplier        |  CEM_ERR     |  EM?    |  electron_multiplier
              2      | not used                   |  n/a         |  n/a    |  n/a
              1      | Filament                   |  FIL_ERR     |  EF?    |  filament
              0      | Communications             |  RS232_ERR   |  EC?    |  communications
        ----------------------------------------------------------------------------------------------------------------

        Returns
        -------
        int
            should be interpreted as an 8-digit binary byte. Each bit in the byte gives information of a specific
            error type.
        """
        return int(self._query_('ER?'))

    def get_error_byte_communications(self):
        """
        Analogous to the status byte.

        Returns
        -------
        int
            should be interpreted as an 8-digit binary byte. Each bit in the byte gives information of a specific
            error type.
        """
        return int(self._query_('EC?'))

    def get_error_byte_filament(self):
        """
        Analogous to the status byte.

        Returns
        -------
        int
            should be interpreted as an 8-digit binary byte. Each bit in the byte gives information of a specific
            error type.
        """
        return int(self._query_('EF?'))

    def get_error_byte_electron_multiplier(self):
        """
        Analogous to the status byte.

        Returns
        -------
        int
            should be interpreted as an 8-digit binary byte. Each bit in the byte gives information of a specific
            error type.
        """
        return int(self._query_('EM?'))

    def get_error_byte_mass_filter(self):
        """
        Analogous to the status byte.

        Returns
        -------
        int
            should be interpreted as an 8-digit binary byte. Each bit in the byte gives information of a specific
            error type.
        """
        return int(self._query_('EQ?'))

    def get_error_byte_electrometer(self):
        """
        Analogous to the status byte.

        Returns
        -------
        int
            should be interpreted as an 8-digit binary byte. Each bit in the byte gives information of a specific
            error type.
        """
        return int(self._query_('ED?'))

    def get_error_byte_supply(self):
        """
        Analogous to the status byte.

        Returns
        -------
        int
            should be interpreted as an 8-digit binary byte. Each bit in the byte gives information of a specific
            error type.
        """
        return int(self._query_('EP?'))

    def get_error_message_communications(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_communications()
        errors_lst = [  # error message if the bit corresponding to the index is True.
            'Bad command received',
            'Bad parameter received',
            'Command-too-long',
            'OVERWROTE in receiving',
            'Transmit buffer overwrite',
            'Jumper protection violation',
            'Parameter conflict',
            'bit not used'
        ]
        return self._create_error_msg(error_byte, errors_lst)

    def get_error_message_filament(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_filament()
        errors_lst = [  # error message if the bit corresponding to the index is True.
            'Single filament operation',
            'bit not used',
            'bit not used',
            'bit not used',
            'bit not used',
            'Vacuum chamber pressure too high',
            'unable to set the requested emission current',
            'no filament detected'
        ]
        return self._create_error_msg(error_byte, errors_lst)

    def get_error_message_electron_multiplier(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_electron_multiplier()
        errors_lst = [  # error message if the bit corresponding to the index is True.
            'bit not used',
            'bit not used',
            'bit not used',
            'bit not used',
            'bit not used',
            'bit not used',
            'bit not used',
            'No electron multiplier option installed'
        ]
        return self._create_error_msg(error_byte, errors_lst)

    def get_error_message_mass_filter(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_mass_filter()
        errors_lst = [  # error message if the bit corresponding to the index is True.
            'bit not used',
            'bit not used',
            'bit not used',
            'bit not used',
            'Power supply in current limited mode',
            'bit not used',
            'Primary current exceeds 2.0 A',
            'RF_CT exceeds (V_ext - 2V) at M_MAX'
        ]
        return self._create_error_msg(error_byte, errors_lst)

    def get_error_message_electrometer(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_electrometer()
        errors_lst = [  # error message if the bit corresponding to the index is True.
            'bit not used',
            'Op-amp input offset voltage out of range',
            'bit not used',
            'COMPENSATE fails to read -5nA input current',
            'COMPENSATE fails to read +5nA input current',
            'DETECT fails to read -5nA input current',
            'DETECT fails to read +5nA input current',
            'ADC16 test failure'
        ]
        return self._create_error_msg(error_byte, errors_lst)

    def get_error_message_supply(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_supply()
        errors_lst = [  # error message if the bit corresponding to the index is True.
            'bit not used',
            'bit not used',
            'bit not used',
            'bit not used',
            'bit not used',
            'bit not used',
            'External 20V power supply error: Voltage > 26V',
            'External 20V power supply error: Voltage < 22V'
        ]
        return self._create_error_msg(error_byte, errors_lst)

    def get_error_message_all(self, status=None):
        """
        Looks for any error across any error type and creates an error string.

        Parameters
        ----------
        status : int, optional.
            should be the status byte. If none is given, the status byte will be queried from the RGA at the
            beginning of the command.

        Returns
        -------
        str
            error string
        """
        if status is None:
            status = int(self._query_('ER?'))
        if status == 0:
            return
        else:
            status_lst = [  # error message if the bit corresponding to the index is True.
                'communications',
                'filament',
                None,
                'electron_multiplier',
                'mass_filter',
                'electrometer',
                'supply',
                None
            ]

            err_lst = [
                self.get_error_message_communications(),
                self.get_error_message_filament(),
                None,
                self.get_error_message_electron_multiplier(),
                self.get_error_message_mass_filter(),
                self.get_error_message_electrometer(),
                self.get_error_message_supply(),
                None
            ]

            error_msg_all = ''
            # error_msg_all = '\n' \
            #                 '####################\n' \
            #                 '      ERROR         \n' \
            #                 '####################\n'

            for i in range(8):
                if i == 2 or i == 7:
                    pass
                elif status & int(2**i):
                    error_msg_all += 'ERROR in:' + str(status_lst[i]) + '\n' \
                                    + str(err_lst[i])

            return error_msg_all

    # Ionizer
    # -------
    def set_ionizer_electron_energy(self, e_volts):
        return self._command_('EE' + str(e_volts))

    def set_ionizer_ion_energy(self, e_volts):
        return self._command_('IE' + str(e_volts))

    def set_ionizer_focus_voltage(self, e_volts):
        return self._command_('VF' + str(e_volts))

    def set_ionizer_filament_state(self, state):
        if type(state) is not bool:
            return 'ERROR: input must be bool'
        self._filament_state = state
        if state:
            return self._command_('FL*')
        else:
            return self._command_('FL0')

    def get_ionizer_filament_state(self):
        return self._filament_state

    def set_ionizer_filament_current(self, miliamps):
        err = self._command_('FL' + str(miliamps))
        if err is None:
            self._filament_state = bool(miliamps)
        return err

    def get_ionizer_filament_current(self):
        return self._query_('FL?')

    def degas_ionizer_filament(self, minutes):
        self._serial_port.timeout = minutes*60 + 5
        out = self._command_('DG' + str(minutes))
        self._serial_port.timeout = self._read_timeout
        return out

    # Detector
    # --------
    def calibrate_detector(self):
        """
        manual recommends doing this every couple months.
        :return:
        """
        return self._command_('CL')

    def zero_detector(self):
        """
        use this after changing the scan speed, changing detector type (either Faraday Cage or Electron Multiplier),
        or calibrating the detector using 'CL'
        :return: STATUS byte
        """
        return self._command_('CA')

    def set_detector_scan_speed(self, speed):
        """
        set scan speed using the Noise Floor function.
        :param int speed: noise floor parameter, also a measure of speed. Accepted integers are between 0 and 7.
        NOTE: manual says it maximum speed is 7, but in reality, values up to 10 are valid.
        Increasing speed also increases noise.
        :return:
        """
        err = self._command_noresponse_('NF' + str(speed))
        if err is None:
            self._noise_floor = speed
            return self.zero_detector()
        else:
            return err

    def get_detector_scan_speed(self):
        return self._query_('NF?')

    def set_detector_cdem_state(self, state):
        """
        For on, sets the default voltage value. For off, sets voltage to 0.

        Parameters
        ----------
        state : bool
            True for on, False for off.

        Returns
        -------
        None
            if successful, return None
        str
            else, return an error string
        """
        self._cdem_state = state
        if state:
            err = self._command_('HV*')
        else:
            err = self._command_('HV0')

        if err is None:
            return self.zero_detector()
        else:
            return err

    def set_detector_cdem_voltage(self, volts):
        err = self._command_('HV' + str(volts))
        if err is None:
            self._cdem_state = bool(volts)
            return self.zero_detector()
        else:
            return err

    def get_detector_cdem_voltage(self):
        return self._query_('HV?')

    # Scans
    def get_partial_sensitivity_factor(self):
        return float(self._query_('SP?'))

    def get_total_sensitivity_factor(self):
        return float(self._query_('ST?'))

    def set_initial_mass(self, m_lo):
        return self._command_noresponse_('MI' + str(m_lo))

    def set_final_mass(self, m_hi):
        return self._command_noresponse_('MF' + str(m_hi))

    def set_steps_per_amu(self, s):
        return self._command_noresponse_('SA' + str(s))

    def get_number_data_points(self):
        out = self._query_('AP?')
        try:
            return int(out)
        except ValueError:
            return out

    def get_analog_scan(self, m_lo=1, m_hi=65, points_per_amu=10, speed=3):
        """
        start an analog scan across an initial to a final mass. Raw output from RGA comes as four-byte signed
        integers representing the ion currents in units of 0.1 femtoAmps.

        Parameters
        ---------
        m_lo : int
            initial mass in amu to start the scan at
        m_hi : int
            final mass in amu to stop the scan at
        points_per_amu : int
            number of datapoints to take per unit mass. The analog scan takes current measurements at equally spaced
            mass intervals. The mass interval is equal to the inverse of points_per_amu
        speed : int
            noise floor or speed. Arbitrary units.

        Returns
        -------
        np.array
           1D array containing the measurement in units of Torr
        """
        err = self.set_initial_mass(m_lo)
        if err is not None:
            return err
        err = self.set_final_mass(m_hi)
        if err is not None:
            return err
        err = self.set_steps_per_amu(points_per_amu)
        if err is not None:
            return err
        err = self.set_detector_scan_speed(speed)
        if err is not None:
            return err
        err = self.set_ionizer_filament_state(True)
        if err is not None:
            return err

        n_points = int(self._query_('AP?')) + 1  # final data point is the total pressure

        self._serial_port.write('SC1\r'.encode('utf-8'))
        time.sleep(0.3)
        out = np.asarray([])
        for i in range(n_points):
            raw = self._serial_port.read(4)
            int_10 = self._translate_to_decimal(raw)
            out = np.append(out, int_10)

        return out*(1e-13)/self.get_partial_sensitivity_factor()  # convert raw units to Torr

    def get_histogram_scan(self, m_lo=1, m_hi=100, speed=3 ):
        """
        start a historgam scan across an initial to a final mass. Raw output from RGA comes as four-byte signed
        integers representing the ion currents in units of 0.1 femtoAmps.

        Parameter
        ---------
        m_lo : int
            initial mass in amu to start the scan at
        m_hi : int
            final mass in amu to stop the scan at
        speed : int
            noise floor or speed. Arbitrary units.

        Returns
        -------
        np.array
           1D array containing the measurement in units of Torr
        """
        err = self.set_initial_mass(m_lo)
        if err is not None:
            return err
        err = self.set_final_mass(m_hi)
        if err is not None:
            return err
        err = self.set_detector_scan_speed(speed)
        if err is not None:
            return err
        err = self.set_ionizer_filament_state(True)
        if err is not None:
            return err

        n_points = int(self._query_('HP?')) + 1  # final data point is the total pressure

        self._serial_port.write('HS1\r'.encode('utf-8'))
        time.sleep(0.3)
        out = np.asarray([])
        for i in range(n_points):
            raw = self._serial_port.read(4)  # receive each data point individually.
            int_10 = self._translate_to_decimal(raw)
            out = np.append(out, int_10)

        return out*(1e-13)/self.get_partial_sensitivity_factor()  # convert raw units to Torr

    def get_single_mass_measurement(self, mass=28, speed=8):
        """
        get a single mass pressure measurement.

        Parameters
        ---------
        mass : int
            mass in amu at which to take the pressure measurement
        speed : int
            noise floor or speed. Arbitrary units.

        Returns
        -------
        int
            pressure measurement. Units of Torr
        """
        err = self.set_detector_scan_speed(speed)
        if err is not None:
            return err

        msg = 'MR' + str(mass) + '\r'
        self._serial_port.write(msg.encode('utf-8'))
        int_10 = self._translate_to_decimal(self._serial_port.read(4))
        self._serial_port.write('MR0\r'.encode('utf-8'))  # deactivate RF/DC voltages
        return int_10*(1e-13)/self.get_partial_sensitivity_factor()  # convert raw units to Torr

    @property
    def idn(self):
        return self._query_('ID?')

    @property
    def status_byte(self):
        return self.get_status_byte()

    @property
    def filament_state(self):
        return self._filament_state

    @filament_state.setter
    def filament_state(self, state):
        self.set_ionizer_filament_state(state)

    @property
    def filament_current(self):
        return self.get_ionizer_filament_current()

    @filament_current.setter
    def filament_current(self, miliamps):
        self.set_ionizer_filament_current(miliamps=miliamps)


# Eliptec motor
class ELL14K:
    pass