"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import serial
import sys
import time

import auxiliary
from connection_type import SocketEthernetDevice
from device_type import PowerSupply
from device_type import MCC_Device

from mcculw import ul
from mcculw import enums


# ======================================================================================================================
# Gaussmeters
# ======================================================================================================================
error_count = 0


class GM3(serial.Serial):  # TODO: needs work.
    def __init__(self, *args, **kwargs):
        super().__init__(baudrate=115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, *args, **kwargs)

        """
        Parameters
        ----------
        port : str
            Device port name. Can be found on device manager. Example: COM3
        baudrate : int 
            The baudrate unique to this device.
        bytesize : int
            The size in bits of a single byte. 
        parity : serial.PARITY
            Unique to device. Possible values: PARITY_NONE, PARITY_EVEN, PARITY_ODD PARITY_MARK, PARITY_SPACE
        stopbits : serial.STOPBITS
            Number of stop bits. Possible values: STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
        timeout : int
            read timeout in seconds. Time that read() will wait for response before exiting.
    
        More parameters in documentation for serial.Serial class.
        """

    def query(self, command):
        global error_count
        """
        query function for gaussmeter. The function sends the appropriate command to the gaussmeter and reads the
        appropiate number of bytes and returns them as a byte string. Currently, the only supported commands are:
        ID_METER_PROP (0x01), ID_METER_SETT (0x02), STREAM_DATA (0x03), and RESET_TIME (0x04).
        
        Parameters
        ----------
        command : str
            
        
        :param command: the command to send to the gaussmeter. Can be a string with the hex value of the command 
        in the
        format 'AA' or '0xAA' or the command name as it appears in the AlphaApp comm protocol manual.
        :return: byte object containing the response from the gaussmeter. Has variable length depending on the query
        command used.
        """

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
            self.write(bytes.fromhex(qry * 6))
            r = self.read(read_length)
            ack = self.read(1)

            if ack != bytes.fromhex('08'):  # count the number of times a message is not received succesfully.
                error_count += 1

        if qry == '03' or qry == '04':
            return r

        while ack != bytes.fromhex('07'):
            self.write(bytes.fromhex('08' * 6))
            r += self.read(read_length)
            ack = self.read(1)

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

        self.write(bytes.fromhex(cmd * 6))

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
class SPD3303X(SocketEthernetDevice, PowerSupply):
    """
    An ethernet-controlled power supply. Querys and commands based on manual for Siglent SPD3303X power supply.
    All voltages and currents are in Volts and Amps unless specified otherwise.
    """

    def __init__(
            self,
            ip4_address=None,
            port=5025,
            channel_voltage_limits=None,
            channel_current_limits=None,
            reset_on_startup=True
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
        reset_on_startup : bool
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
            reset_on_startup=reset_on_startup,
        )

        if self._reset_on_startup is True and ip4_address is not None:
            self.reset_channels()

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
        out = self._query(qry.encode('utf-8'))
        return out.decode('utf-8').strip()
    
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
        out = self._command(cmd.encode('utf-8'))
        return out

    def reset_channels(self):
        self.ch1_state = 'OFF'
        self.ch2_state = 'OFF'
        self.zero_all_channels()
        print('Both channels turned off and set to 0. Channel limits are reset to MAX.')

    # =============================================================================
    #       Get methods
    # =============================================================================
    def get_channel_state(self, channel):
        """
        The 5th digit from right to left of the binary output from the system status query gives the state of channel 1,
        1 for on and 0 for off.

        Parameters
        ----------
        channel : int
            channel to get the state from. Number is from 1 up to the number of channels of the power supply.
        Return
        ------
        bool
            True for on, False for off.
        """
        self.check_channel_syntax(channel)
        one_or_zero = int(self.system_status[-4-channel])
        return bool(one_or_zero)

    def get_set_voltage(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        qry = 'CH' + str(channel) + ':voltage?'
        return float(self._query_(qry))

    def get_actual_voltage(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        qry = 'measure:voltage? ' + 'CH' + str(channel)
        return float(self._query_(qry))

    def get_set_current(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        qry = 'CH' + str(channel) + ':current?'
        return float(self._query_(qry))

    def get_actual_current(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        qry = 'measure:current? ' + 'CH' + str(channel)
        return float(self._query_(qry))

    def get_voltage_limit(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        return self._channel_voltage_limits[channel - 1]

    def get_current_limit(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        return self._channel_current_limits[channel - 1]

    # =============================================================================
    #       Set methods
    # =============================================================================
    def set_channel_state(self, channel, state):
        """
        :param channel: int
        :param state: str valid inputs (not case sensitive): on, off.
        """
        self.check_channel_syntax(channel)
        cmd = 'Output CH' + str(channel) + ',' + state.upper()
        self._command_(cmd)

    def set_set_voltage(self, channel, volts):
        """
        :param channel: int
        :param volts: float
        """
        self.check_channel_syntax(channel)
        volts = round(volts, 3)

        limit = self.get_voltage_limit(channel)
        chan = 'CH' + str(channel)
        if volts <= limit:
            cmd = chan + ':voltage ' + str(volts)
            self._command_(cmd)
        else:
            raise ValueError(chan + ' voltage not set. New voltage is higher than ' + chan + ' voltage limit.')

    def set_set_current(self, channel, amps):
        """
        :param channel: int
        :param amps: float
        """
        self.check_channel_syntax(channel)
        amps = round(amps, 3)

        limit = self.get_current_limit(channel)
        chan = 'CH' + str(channel)
        if amps <= limit:
            cmd = chan + ':current ' + str(amps)
            self._command_(cmd)
        else:
            raise ValueError(chan + ' current not set. New current is higher than ' + chan + ' current limit')

    def set_channel_voltage_limit(self, channel, volts):
        """
        :param channel: int
        :param volts: float
        """
        self.check_channel_syntax(channel)

        if volts > self._MAX_voltage_limit or volts <= 0:
            print('Voltage limit not set. New voltage limit is not allowed by the power supply.')
        elif volts < self.ch1_set_voltage:
            print('Voltage limit not set. New voltage limit is lower than present channel set voltage.')
        else: 
            self._channel_voltage_limits[channel - 1] = volts
            
    def set_channel_current_limit(self, channel, amps):
        """
        :param channel: int
        :param amps: float
        """
        self.check_channel_syntax(channel)

        if amps > self._MAX_current_limit or amps <= 0:
            print('Current limit not set. New current limit is not allowed by the power supply.')
        elif amps < self.ch1_set_current:
            print('Current limit not set. New current limit is lower than present channel set current.')
        else: 
            self._channel_current_limits[channel - 1] = amps

    # =============================================================================
    #       Properties
    # =============================================================================
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
        return self.get_channel_state(1)

    @ch1_state.setter
    def ch1_state(self, state):
        """
        :param state: str valid inputs (not case sensitive): on, off.
        """
        self.set_channel_state(1, state)

    @property
    def ch2_state(self):
        return self.get_channel_state(2)

    @ch2_state.setter
    def ch2_state(self, state):
        """
        :param state: str valid inputs (not case sensitive): on, off.
        """
        self.set_channel_state(2, state)

    @property
    def ch1_set_voltage(self):
        return self.get_set_voltage(1)

    @ch1_set_voltage.setter
    def ch1_set_voltage(self, volts):
        self.set_set_voltage(1, volts)

    @property
    def ch2_set_voltage(self):
        return self.get_set_voltage(2)

    @ch2_set_voltage.setter
    def ch2_set_voltage(self, volts):
        self.set_set_voltage(2, volts)

    @property
    def ch1_actual_voltage(self):
        return self.get_actual_voltage(1)

    @property
    def ch2_actual_voltage(self):
        return self.get_actual_voltage(2)

    @property
    def ch1_set_current(self):
        return self.get_set_current(1)

    @ch1_set_current.setter
    def ch1_set_current(self, amps):
        self.set_set_current(1, amps)

    @property
    def ch2_set_current(self):
        return self.get_set_current(2)

    @ch2_set_current.setter
    def ch2_set_current(self, amps):
        self.set_set_current(2, amps)

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
        self.set_channel_voltage_limit(1, volts)

    @property
    def ch1_current_limit(self):
        return self._channel_current_limits[0]

    @ch1_current_limit.setter
    def ch1_current_limit(self, amps):
        self.set_channel_current_limit(1, amps)

    @property
    def ch2_voltage_limit(self):
        return self._channel_voltage_limits[1]

    @ch2_voltage_limit.setter
    def ch2_voltage_limit(self, volts):
        self.set_channel_voltage_limit(2, volts)

    @property
    def ch2_current_limit(self):
        return self._channel_current_limits[1]

    @ch2_current_limit.setter
    def ch2_current_limit(self, amps):
        self.set_channel_current_limit(2, amps)


# ======================================================================================================================
# Temperature DAQs
# ======================================================================================================================
class Web_Tc(MCC_Device):
    def __init__(self, board_number, ip4_address=None, port=54211, default_units='celsius'):
        """
        Class for a Web_Tc device from MCC. Might make a master class for temperature daq

        Parameters
        ----------
        ip4_address : string
            The current IPv4 address of the device. Can be found through instacal. For the Web_TC, the ip4_address is
            unused because the API functions that use it are not supported by this device.
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


class E_Tc(MCC_Device):
    def __init__(self, board_number, ip4_address=None, port=54211, default_units='celsius'):
        """
        Class for a Web_Tc device from MCC. Might make a master class for temperature daq

        Parameters
        ----------
        ip4_address : string
            The current IPv4 address of the device. Can be found through instacal. For the Web_TC, the ip4_address is
            unused because the API functions that use it are not supported by this device.
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
            'positivre': '+',
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
class SRS100:
    def __init__(
            self,
            port
    ):
        s = serial.Serial(port=port, baudrate=28800, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=2)
        self._port = port
        self._serial_port = s
        self._filament_state = False
        self._CDEM_state = False

    def _query_(self, qry):
        """
        :param str qry:
        :return str:
        """
        qry += '\r'
        self._serial_port.write(data=qry.encode('utf-8'))
        return self._serial_port.read_until(expected='\n\r'.encode('utf-8')).decode('utf-8')

    def initialize(self):
        print(self.idn)
        print('Flushing communication buffers')
        status = self.flush_buffers()
        return status

    def flush_buffers(self):
        return self._query_('IN0')

    # Ionizer
    # -------
    def set_ionizer_electron_energy(self, e_volts):
        return self._query_('EE' + str(e_volts))

    def set_ionizer_ion_energy(self, e_volts):
        return self._query_('IE' + str(e_volts))

    def set_ionizer_focus_voltage(self, e_volts):
        return self._query_('VF' + str(e_volts))

    def set_ionizer_filament_state(self, state):
        if state.lower() == 'on':
            self._filament_state = True
            return self._query_('FL*')
        elif state.lower() == 'off':
            self._filament_state = False
            return self._query_('FL0.00')

    def set_ionizer_filament_current(self, mAmps):
        if mAmps < 0.02:
            self._filament_state = False
        return self._query_('FL' + str(mAmps))

    def degas(self, minutes):
        out = self._query_('DG' + str(minutes))
        time.sleep(minutes * 60)
        return out

    # Detector
    # --------
    def calibrate_detector(self):
        return self._query_('CL')

    def zero_detector(self):
        """
        use this after changing the scan speed, changing detector type (either Faraday Cage or Electron Multiplier),
        or calibrating the detector using 'CL'
        :return: STATUS byte
        """
        return self._query_('CA')

    def set_detector_scan_speed(self, speed):
        """
        set scan speed using the Noise Floor function.
        :param int speed: noise floor parameter, also a measure of speed. Accepted integers are between 0 and 7.
        Increasing speed also increases noise.
        :return:
        """
        return self._query_('NF' + str(speed))

    def set_detector_CDEM_state(self, state):
        if state.lower() == 'on':
            self._CDEM_state = True
            return self._query_('HV*')
        elif state.lower() == 'off':
            self._CDEM_state = False
            return self._query_('HV0')

    def set_detector_CDEM_voltage(self, volts):
        if volts < 1:
            self._CDEM_state = False
        return self._query_('HV' + str(volts))

    @property
    def idn(self):
        return self._query_('ID?')

    @property
    def filament_state(self):
        return self._filament_state

    @filament_state.setter
    def filament_state(self, state):
        self.set_ionizer_filament_state(state)

