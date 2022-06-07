"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import serial
import time
from serial import Serial
from sys import platform

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
error_count = 0


class GM3():  # TODO: needs work.
    def __init__(self, port, tmout):
        """
        Parameters
        ----------
        port : str
            Device port name. Can be found on device manager. Example: COM3
        timeout : float
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

    def query(self, command):
        """
        query function for gaussmeter. The function sends the appropriate command to the gaussmeter and reads the
        appropiate number of bytes and returns them as a byte string. Currently, the only supported commands are:
        ID_METER_PROP (0x01), ID_METER_SETT (0x02), STREAM_DATA (0x03), and RESET_TIME (0x04).
        
        Parameters
        ----------
        command : str
            the command to send to the gaussmeter. Can be a string with the hex value of the command in the format
            'AA' or '0xAA' or the command name as it appears in the AlphaApp comm protocol manual.

        Returns
        -------
        bytes
            byte object containing the response from the gaussmeter. Has variable length depending on the query
            command used.
        """
        global error_count

        qry_dict = {  # command as appears in manual: hex command identifyer
            'ID_METER_PROP': '01',
            'ID_METER_SETT': '02',
            'STREAM_DATA': '03',
            'RESET_TIME': '04',
            '01': '01',
            '02': '02',
            '03': '03',
            '04': '04',
            '0x01': '01',
            '0x02': '02',
            '0x03': '03',
            '0x04': '04',
        }

        try:
            qry = qry_dict[command]
        except KeyError:
            raise ValueError('ERROR: command', command, 'not found. Possible string commands:',
                             '\nID_METER_PROP    or    01    or    0x01',
                             '\nID_METER_SETT    or    02    or    0x02',
                             '\nSTREAM_DATA      or    03    or    0x03',
                             '\nRESET_TIME       or    04    or    0x04')

        read_length_dict = {  # read message lenght in bytes
            '01': 20,
            '02': 20,
            '03': 30,
            '04': 31,
        }
        read_length = read_length_dict[qry]
        ack = ''
        r = None
        while ack != bytes.fromhex('08'):  # loop to confirm that the message has been received
            self._ser.write(bytes.fromhex(qry * 6))
            r = self._ser.read(read_length)
            ack = self._ser.read(1)

            if ack != bytes.fromhex('08'):  # count the number of times a message is not received succesfully.
                error_count += 1

        if qry == '03' or qry == '04':
            return r

        while ack != bytes.fromhex('07'):
            self._ser.write(bytes.fromhex('08' * 6))
            r += self._ser.read(read_length)
            ack = self._ser.read(1)

        return r

    def command(self, command):
        """
        TODO: Add comments
        """

        cmd_dict = {
            'KILL_ALL_PROCESS': 'FF',
            'FF': 'FF',
            '0xFF': 'FF'
        }
        try:
            cmd = cmd_dict[command]
        except KeyError:
            raise ValueError('ERROR: command', command, 'not found. Possible string commands:',
                             '\nKILL_ALL_PROCESS    or    FF    or    0xFF')

        self._ser.write(bytes.fromhex(cmd * 6))

        return None

    def get_instantenous_data(self):
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

        query_bytes = self.query('STREAM_DATA')
        # ack = query_bytes[-1].hex()
        # print(ack)
        query_string = query_bytes.hex()

        """
        We then divide the string into sections of 12 characters (6 bytes). Each section contains all the information
        for a single measurable. Within ech section, we identify the second (byte_2) and the third, fourth, fifth, 
        and sixth bytes (bytes_3456) from this section. byte_2 gives information on the sign and magnitude of the 
        measured quantity. bytes_3456 give the digits. 
        """
        number_of_measurables = int(len(query_string) / 2 / 6)  # find number of measurable variables
        out = []
        for measurable_i in range(number_of_measurables):
            section_i = measurable_i * 12
            byte_2 = int(query_string[section_i + 2: section_i + 4], 16)
            bytes_3456 = int(query_string[section_i + 4: section_i + 12], 16)

            sign = 1
            if byte_2 & 0x08:  # 0x08 = 00001000 : if 4th bit = 1, sign is negative. Else, sign is positive
                sign = -1
            digits = bytes_3456
            magnitude = 10 ** (
                        -1 * int(byte_2 & 0x07))  # 0x07 = 00000111 : 1st, 2nd, 3rd bits give inverse power of 10.

            out.append(sign * digits * magnitude)

        return out

    def get_instantenous_data_t0(self):
        """
        reset the time coordinate and query the gaussmeter for an instantenous reading of the time stamp in seconds,
        x-axis, y-axis, z-axis, and magnitude in Gauss readings of a magnetic field. Note the time points only serve
        as an index for the data points but do not give meaningful time information.
        :return: list containing the float values for time (s), x-axis (G), y-axis (G), z-axis (G), and magnitude (G).

        The response from the gaussmeter comes as a long byte string containing hex numbers in the format 'AA. The
        data can be thought to be split in sections of 6 bytes. Each section contains the information for each
        measurable that the gaussmeter collects. Currently, there are only 5 measurables, which means that the
        response has a total of 30 bytes.

        The response is then converted into a python string. Since each hex number has two characters, the string is
        60 characters long.
        """

        query_bytes = self.query('RESET_TIME')
        # ack = query_bytes[-1].hex()
        # print(ack)
        query_string = query_bytes.hex()

        """
        We then divide the string into sections of 12 characters (6 bytes). Each section contains all the information
        for a single measurable. Within ech section, we identify the second (byte_2) and the third, fourth, fifth, 
        and sixth bytes (bytes_3456) from this section. byte_2 gives information on the sign and magnitude of the 
        measured quantity. bytes_3456 give the digits. 
        """
        number_of_measurables = int(len(query_string) / 2 / 6)
        out = []
        for measurable_i in range(number_of_measurables):
            section_i = measurable_i * 12
            byte_2 = int(query_string[section_i + 2: section_i + 4], 16)
            bytes_3456 = int(query_string[section_i + 4: section_i + 12], 16)

            sign = 1
            if byte_2 & 0x08:  # 0x08 = 00001000 : if 4th bit = 1, sign is negative. Else, sign is positive
                sign = -1
            digits = bytes_3456
            magnitude = 10 ** (
                        -1 * int(byte_2 & 0x07))  # 0x07 = 00000111 : 1st, 2nd, 3rd bits give inverse power of 10.

            out.append(sign * digits * magnitude)

        return out

    @property
    def properties(self):
        out = self.query('ID_METER_PROP').decode('utf-8')
        out = out.replace(':', '\n')
        return out

    @property
    def settings(self):
        out = self.query('ID_METER_SETT').decode('utf-8')
        out = out.replace(':', '\n')
        return out


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
            MAX_voltage_limit=physical_parameters['MAX_voltage_limit'],
            MAX_current_limit=physical_parameters['MAX_current_limit'],
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
            MAX_voltage_limit=physical_parameters['MAX_voltage_limit'],
            MAX_current_limit=physical_parameters['MAX_current_limit'],
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
    """
    Newport picomotor controller.
    """
    def __init__(
            self,
            ip4_address=None,
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
            self._socket.recv(4096)

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

    def reboot_controller(self):
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

    def motion_done(self, chan):
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

    def get_set_position(self, chan):
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

    def set_set_position(self, chan, position):
        """
        :param int chan:
        :param int position: measured in steps with respect to the home position  # TODO: check home position or origin
        :return:
        """
        self._command_(str(chan) + 'PA' + str(position))
        while not self.motion_done(chan=chan):
            pass

    def displace(self, chan, dis):
        """
        :param int chan:
        :param dis: measured in steps. With respect to the position just before starting to move. # TODO: check
        :return:
        """
        self._command_(str(chan) + 'PR' + str(dis))
        while not self.motion_done(chan=chan):
            pass

    def move_indefinetely(self, chan, direction):
        """
        Moves indefinetely. Need to use hard_stop or other stopping command to stop the motion.
        :param int chan:
        :param str direction: possible values for positive direction: +, pos, or positive. For negative direction: -,
        neg, or negative.
        """
        while not self.motion_done(chan=chan):
            pass

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
    def set_position_ch1(self):
        return self.get_set_position(chan=1)

    @set_position_ch1.setter
    def set_position_ch1(self, new_pos):
        self.set_set_position(chan=1, position=new_pos)

    @property
    def set_position_ch2(self):
        return self.get_set_position(chan=2)

    @set_position_ch2.setter
    def set_position_ch2(self, new_pos):
        self.set_set_position(chan=2, position=new_pos)

    @property
    def set_position_ch3(self):
        return self.get_set_position(chan=3)

    @set_position_ch3.setter
    def set_position_ch3(self, new_pos):
        self.set_set_position(chan=3, position=new_pos)

    @property
    def set_position_ch4(self):
        return self.get_set_position(chan=4)

    @set_position_ch4.setter
    def set_position_ch4(self, new_pos):
        self.set_set_position(chan=4, position=new_pos)

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

    # @property
    # def (self):
    #     return


# ======================================================================================================================
# RGA
# ======================================================================================================================
class Srs100:
    def __init__(
            self,
            port,
            read_timeout=10
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

    def _query_(self, qry):
        """
        :param str qry:
        :return str:
        """
        qry += '\r'
        self._serial_port.write(data=qry.encode('utf-8'))
        return self._serial_port.read_until(expected='\n\r'.encode('utf-8')).decode('utf-8').strip()

    def _command_noresponse_(self, cmd):
        cmd += '\r'
        self._serial_port.write(data=cmd.encode('utf-8'))
        status = self.get_status_byte()
        self.get_error_message_all(status=status)
        return status

    def _command_(self, cmd):
        """
        :param str cmd:
        :return int: returns status byte as a decimal integer.
        """

        status = int(self._query_(cmd))
        self.get_error_message_all(status=status)
        return status

    # General
    # -------
    def initialize(self):
        print(self.idn)
        print('Flushing communication buffers')
        return self.flush_buffers()

    def flush_buffers(self):
        return self._command_('IN0')

    # Error handling
    # --------------
    def _create_error_msg(self, byte, dict):
        final_msg = ''
        for i in range(8):
            if byte & int(2 ** i):
                final_msg += '- ' + dict[i]
                final_msg += '\n'
        return final_msg

    def get_status_byte(self):
        """
        a byte as a decimal int that tells the error types that have occurred or that have not been checked.To
        interpret it, it needs to be turned into an 8-bit binary number first. Possible error types: RS232_ERR,
        FIL_ERR, CEM_ERR, QMF_ERR, DET_ERR, and PS_ERR. Use to following table to determine which error types have
        occurred and what methods to call to see the specific error:
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

        To get an individual error byte for a single error type, use get_error_byte_{name}
        To get all individual error bytes for each error type, use get_error_bytes.
        To get individual error messages per error type, use get_error_message_{name}

        :return int byte: status byte as a decimal int. The position or index of the bit indicates the type of error
        it represents. If the bit is 1, it indicates that its type of error has occurred.
        """
        return int(self._query_('ER?'))

    def get_error_byte_all(self, status=None):
        """
        get the error byte as a decimal int for each error type: RS232_ERR, FIL_ERR, CEM_ERR, QMF_ERR,
        DET_ERR, and PS_ERR.
        :param int status: the status byte returned by most commands of the RGA, or requested by get_status().
        :return tuple of ints:
        """
        if status is None:
            status = self.get_status_byte()
        errors_dict = {
            0: 'EC?',  # Communications, RS232_ERR
            1: 'EF?',  # Filament, FIL_ERR
            2: None,   # not used
            3: 'EM?',  # Electron Multiplier, CEM_ERR
            4: 'EQ?',  # Quadrupole Mass Filter, QMF_ERR
            5: 'ED?',  # Electrometer, DET_ERR
            6: 'EP?',  # 24V External Power Supply, PS_ERR
            7: None    # not used
        }
        errors = []
        for i in range(8):
            if status & int(2**i):
                errors.append(int(self._query_(errors_dict[i])))
            else:
                errors.append(0)

        return tuple(errors)

    def get_error_byte_communications(self):
        return int(self._query_('EC?'))

    def get_error_byte_filament(self):
        return int(self._query_('EF?'))

    def get_error_byte_electron_multiplier(self):
        return int(self._query_('EM?'))

    def get_error_byte_mass_filter(self):
        return int(self._query_('EQ?'))

    def get_error_byte_electrometer(self):
        return int(self._query_('ED?'))

    def get_error_byte_supply(self):
        return int(self._query_('EP?'))

    def get_error_message_communications(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_communications()
        errors_dict = {  # key: bit numer or index. Value: error message if the bit is True.
            0: 'Bad command received',
            1: 'Bad parameter received',
            2: 'Command-too-long',
            3: 'OVERWROTE in receiving',
            4: 'Transmit buffer overwrite',
            5: 'Jumper protection violation',
            6: 'Parameter conflict',
            7: 'bit not used'
        }
        return self._create_error_msg(error_byte, errors_dict)

    def get_error_message_filament(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_filament()
        errors_dict = {  # key: bit numer or index. Value: error message if the bit is True.
            0: 'Single filament operation',
            1: 'bit not used',
            2: 'bit not used',
            3: 'bit not used',
            4: 'bit not used',
            5: 'Vacuum chamber pressure too high',
            6: 'unable to set the requested emission current',
            7: 'no filament detected'
        }
        return self._create_error_msg(error_byte, errors_dict)

    def get_error_message_electron_multiplier(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_electron_multiplier()
        errors_dict = {  # key: bit numer or index. Value: error message if the bit is True.
            0: 'bit not used',
            1: 'bit not used',
            2: 'bit not used',
            3: 'bit not used',
            4: 'bit not used',
            5: 'bit not used',
            6: 'bit not used',
            7: 'No electron multiplier option installed'
        }
        return self._create_error_msg(error_byte, errors_dict)

    def get_error_message_mass_filter(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_mass_filter()
        errors_dict = {  # key: bit numer or index. Value: error message if the bit is True.
            0: 'bit not used',
            1: 'bit not used',
            2: 'bit not used',
            3: 'bit not used',
            4: 'Power supply in current limited mode',
            5: 'bit not used',
            6: 'Primary current exceeds 2.0 A',
            7: 'RF_CT exceeds (V_ext - 2V) at M_MAX'
        }
        return self._create_error_msg(error_byte, errors_dict)

    def get_error_message_electrometer(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_electrometer()
        errors_dict = {  # key: bit numer or index. Value: error message if the bit is True.
            0: 'bit not used',
            1: 'Op-amp input offset voltage out of range',
            2: 'bit not used',
            3: 'COMPENSATE fails to read -5nA input current',
            4: 'COMPENSATE fails to read +5nA input current',
            5: 'DETECT fails to read -5nA input current',
            6: 'DETECT fails to read +5nA input current',
            7: 'ADC16 test failure'
        }
        return self._create_error_msg(error_byte, errors_dict)

    def get_error_message_supply(self, error_byte=None):
        if error_byte is None:
            error_byte = self.get_error_byte_supply()
        errors_dict = {  # key: bit numer or index. Value: error message if the bit is True.
            0: 'bit not used',
            1: 'bit not used',
            2: 'bit not used',
            3: 'bit not used',
            4: 'bit not used',
            5: 'bit not used',
            6: 'External 20V power supply error: Voltage > 26V',
            7: 'External 20V power supply error: Voltage < 22V'
        }
        return self._create_error_msg(error_byte, errors_dict)

    def get_error_message_all(self, status=None):
        if status is None:
            status = int(self._query_('ER?'))
        if status == 0:
            return
        else:
            msg_lst = {  # key: bit numer or index. Value: error message if the bit is True.
                0: 'communications',
                1: 'filament',
                2: None,
                3: 'electron_multiplier',
                4: 'mass_filter',
                5: 'electrometer',
                6: 'supply',
                7: None
            }

            error_msg_all = '\n' \
                            '####################\n' \
                            '      ERROR\n' \
                            '####################\n'
            for i in range(8):
                if i == 2 or i == 7:
                    pass
                elif status & int(2**i):
                    error_msg_all += 'ERROR in:' + str(msg_lst[i]) + '\n'
                    if i == 0:
                        error_msg_all += self.get_error_message_communications()
                    elif i == 1:
                        error_msg_all += self.get_error_message_filament()
                    elif i == 3:
                        error_msg_all += self.get_error_message_electron_multiplier()
                    elif i == 4:
                        error_msg_all += self.get_error_message_mass_filter()
                    elif i == 5:
                        error_msg_all += self.get_error_message_electrometer()
                    elif i == 6:
                        error_msg_all += self.get_error_message_supply()

            print(error_msg_all)
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
        if state.lower() == 'on':
            self._filament_state = True
            return self._command_('FL*')
        elif state.lower() == 'off':
            self._filament_state = False
            return self._command_('FL0')
        else:
            raise ValueError('ERROR: possible states: on or off, not case-sensitive')

    def get_ionizer_filament_state(self):
        return self._filament_state

    def set_ionizer_filament_current(self, miliamps):
        if miliamps == 0:
            self._filament_state = False
            status = self._command_('FL' + str(miliamps))
        else:
            status = self._command_('FL' + str(miliamps))
            if status == 0:
                self._filament_state = True
        return status

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
        Increasing speed also increases noise.
        :return:
        """
        return self._command_noresponse_('NF' + str(speed))

    def get_detector_scan_speed(self):
        return self._query_('NF?')

    def set_detector_cdem_state(self, state):
        if state.lower() == 'on':
            self._cdem_state = True
            return self._command_('HV*')
        elif state.lower() == 'off':
            self._cdem_state = False
            return self._command_('HV0')

    def set_detector_cdem_voltage(self, volts):
        if volts < 1:
            self._cdem_state = False
        return self._command_('HV' + str(volts))

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