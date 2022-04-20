"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import serial
import sys
import time
import device_type
import connection_type
import auxiliary
from mcculw import ul
from mcculw import enums


# ======================================================================================================================
# Gaussmeters
# ======================================================================================================================
error_count = 0


class GM3(serial.Serial):
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

        :param command: the command to send to the gaussmeter. Can be a string with the hex value of the command in the
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
        qry = qry_dict[command]  # TODO: Add error handling

        number_of_bytes_dict = {  # the acknoledge byte is sent
            '01': 20,
            '02': 20,
            '03': 30,
            '04': 31,
        }
        number_of_bytes = number_of_bytes_dict[qry]
        ack = ''
        r = None
        while ack != bytes.fromhex('08'):  # loop to confirm that the message has been received
            self.write(bytes.fromhex(qry * 6))
            r = self.read(number_of_bytes)
            ack = self.read(1)

            if ack != bytes.fromhex('08'):  # count the number of times a message is not received succesfully.
                error_count += 1

        if qry == '03' or qry == '04':
            return r

        while ack != bytes.fromhex('07'):
            self.write(bytes.fromhex('08' * 6))
            r += self.read(number_of_bytes)
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
        cmd = cmd_dict[command]  # TODO: Add error handling

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
class SPD3303X(connection_type.SocketEthernetDevice, device_type.PowerSupply):
    """
    An ethernet-controlled power supply. Querys and commands based on manual for Siglent SPD3303X power supply.
    All voltages and currents are in Volts and Amps unless specified otherwise.
    """

    def __init__(
            self,
            ip4_address=None,
            port=5025,
            voltage_limits=None,
            current_limits=None,
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
        voltage_limits : list
            Set an upper limit on the set voltage of the channels. Entry 0 represents channel 1, entry 1 represents 
            channel 2, and so on.
        current_limits : list
            Set an upper limit on the set current of the channels. Entry 0 represents channel 1, entry 1 represents 
            channel 2, and so on.
        reset_on_startup : bool
            If True, run a routine to set turn off the output of both channels and set the set


        Note that all channel voltage limits are software-based since the power supply does not have any built-in limit
        features. This means that the channel limits are checked before sending a command to the power supply. If the
        requested set voltage is higher than the channel voltage limit, the command will not go through.
        """
        if voltage_limits is None:
            voltage_limits = [32, 32]
        if current_limits is None:
            current_limits = [3.3, 3.2]
            
        physical_parameters = {
            'MAX_voltage_limit': 32,
            'MAX_current_limit': 3.3,
            'number_of_channels': 2,
        }

        connection_type.SocketEthernetDevice.__init__(
            self,
            ip4_address=ip4_address,
            port=port
        )
        device_type.PowerSupply.__init__(
            self,
            MAX_voltage_limit=physical_parameters['MAX_voltage_limit'],
            MAX_current_limit=physical_parameters['MAX_current_limit'],
            number_of_channels=physical_parameters['number_of_channels'],
            voltage_limits=voltage_limits,
            current_limits=current_limits,
            reset_on_startup=reset_on_startup,
        )

        if self._reset_on_startup is True and ip4_address is not None:
            self.reset_channels()

    def _query(self, query):  # TODO: Make more general. Take bytes as input, return bytes as output.
        """
        send a query to the ethernet device and receive a response.

        Parameters
        ----------
        query : string
            Python string containing the query command. Dependent on each individual device.
        Returns
        -------
        string
            Returns the reply of the ethernet device as a string. The output of the ethernet device is received as
            bytes, which is then decoded with utf-8.
        """

        try:
            query_bytes = query.encode('utf-8')
            socket_ps = self._socket
            socket_ps.sendall(query_bytes)
            reply_bytes = socket_ps.recv(4096)
        except OSError:
            print('ERROR: Socket not found. Query not sent.')
            sys.exit()

        reply = reply_bytes.decode('utf-8').strip()
        time.sleep(0.3)
        return reply

    def _command(self, cmd):  # TODO: make more general.
        """
        send a command to the ethernet device. Does not receive any response.
        
        Parameters
        ----------
        cmd : string
            Python string containing the command. Dependent on each individual device.
        Returns
        -------
        None
            Returns None if the command is succesfully sent.
        """

        try:
            cmd_bytes = cmd.encode('utf-8')
            socket_ps = self._socket
        except OSError:
            raise OSError('ERROR: Socket not found. Command not sent.')

        out = socket_ps.sendall(cmd_bytes)  # return None if successful
        time.sleep(0.3)
        return out

    def reset_channels(self):
        self.ch1_state = 'OFF'
        self.ch2_state = 'OFF'
        self.zero_all_channels()
        print('Both channels turned off and set to 0. Channel limits are reset to MAX.')

    # =============================================================================
    #       Get methods
    # =============================================================================

    # System
    # =============================================================================
    @property
    def idn(self):
        qry = '*IDN?'
        return self._query(qry)

    @property
    def ip4_address(self):
        qry = 'IP?'
        return self._query(qry)

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
        reply_hex_str = self._query(qry)  # hex number represented in bytes
        reply_bin_str = f'{int(reply_hex_str, 16):0>10b}'  # 10 digit binary num, padded with 0, as string
        return reply_bin_str

    # Channel properties
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
        return float(self._query(qry))

    def get_actual_voltage(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        qry = 'measure:voltage? ' + 'CH' + str(channel)
        return float(self._query(qry))

    def get_set_current(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        qry = 'CH' + str(channel) + ':current?'
        return float(self._query(qry))

    def get_actual_current(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        qry = 'measure:current? ' + 'CH' + str(channel)
        return float(self._query(qry))

    @property
    def ch1_state(self):
        return self.get_channel_state(1)

    @property
    def ch2_state(self):
        return self.get_channel_state(2)

    @property
    def ch1_set_voltage(self):
        return self.get_set_voltage(1)

    @property
    def ch2_set_voltage(self):
        return self.get_set_voltage(2)

    @property
    def ch1_actual_voltage(self):
        return self.get_actual_voltage(1)

    @property
    def ch2_actual_voltage(self):
        return self.get_actual_voltage(2)

    @property
    def ch1_set_current(self):
        return self.get_set_current(1)

    @property
    def ch2_set_current(self):
        return self.get_set_current(2)

    @property
    def ch1_actual_current(self):
        return self.get_actual_current(1)

    @property
    def ch2_actual_current(self):
        return self.get_actual_current(2)

    # channel limits
    # =============================================================================
    def get_voltage_limit(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        return self._voltage_limits[channel-1]

    def get_current_limit(self, channel):
        """
        :param channel: int
        """
        self.check_channel_syntax(channel)
        return self._current_limits[channel-1]

    @property
    def ch1_voltage_limit(self):
        return self._voltage_limits[0]

    @property
    def ch1_current_limit(self):
        return self._current_limits[0]

    @property
    def ch2_voltage_limit(self):
        return self._voltage_limits[1]

    @property
    def ch2_current_limit(self):
        return self._current_limits[1]

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
        self._command(cmd)

    @ch1_state.setter
    def ch1_state(self, state):
        """
        :param state: str valid inputs (not case sensitive): on, off.
        """
        self.set_channel_state(1, state)

    @ch2_state.setter
    def ch2_state(self, state):
        """
        :param state: str valid inputs (not case sensitive): on, off.
        """
        self.set_channel_state(2, state)

    # voltage and current setters
    # =============================================================================
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
            self._command(cmd)
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
            self._command(cmd)
        else:
            raise ValueError(chan + ' current not set. New current is higher than ' + chan + ' current limit')

    @ch1_set_voltage.setter
    def ch1_set_voltage(self, volts):
        self.set_set_voltage(1, volts)

    @ch1_set_current.setter
    def ch1_set_current(self, amps):
        self.set_set_current(1, amps)

    @ch2_set_voltage.setter
    def ch2_set_voltage(self, volts):
        self.set_set_voltage(2, volts)

    @ch2_set_current.setter
    def ch2_set_current(self, amps):
        self.set_set_current(2, amps)

    # channel limits
    # =============================================================================
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
            self._voltage_limits[channel-1] = volts
            
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
            self._current_limits[channel-1] = amps
    
    @ch1_voltage_limit.setter
    def ch1_voltage_limit(self, volts):
        self.set_channel_voltage_limit(1, volts)

    @ch1_current_limit.setter
    def ch1_current_limit(self, amps):
        self.set_channel_current_limit(1, amps)

    @ch2_voltage_limit.setter
    def ch2_voltage_limit(self, volts):
        self.set_channel_voltage_limit(2, volts)

    @ch2_current_limit.setter
    def ch2_current_limit(self, amps):
        self.set_channel_current_limit(2, amps)


# ======================================================================================================================
# Temperature DAQs
# ======================================================================================================================
class Web_Tc(device_type.MCC_Device):
    def __init__(self, ip4_address=None, port=54211, board_number=0, default_units='celsius'):
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

        super().__init__(board_number)
        self._ip4_address = ip4_address
        self._port = port
        self._default_units = default_units

    # ==================================================================================================================
    # Get methods and properties
    # ==================================================================================================================
    def get_temp(self, channel_n=0, units=None, averaged=True):
        """
        Reads the analog signal out of a channel and returns the value in the desired units.

        Parameters
        ----------
        channel_n : int
            the number of the channel from which to read the temperature. defaults to channel 0 if the channel number
            is not specified.
        units : string or None
            the units in which the temperature is shown. Defaults to None which uses the default units set by the
            instance. Possible values (not case-sensitive):
            for Celsius                 celsius,               c
            for Fahrenheit              fahrenheit,            f
            for Kelvin                  kelvin,                k
            for calibrated voltage      volts, volt, voltage,  v
            for uncalibrated voltage    raw, none, noscale     r   TODO: figure out what calibrated and uncalibrated is
            for default units           bool : None
        averaged : bool
            When selected, 10 samples are read from the specified channel and averaged. The average is the reading
            returned. The maximum acquisiton frequency doesn't change regardless of this parameter.

        Returns
        -------
        float
            Temperature or voltage value as a float in the specified units.
        """

        filter_on_off = enums.TInOptions.FILTER
        if not averaged:
            filter_on_off = enums.TInOptions.NOFILTER

        if units is None:
            units = self._default_units

        out = ul.t_in(
            board_num=self._board_number,
            channel=channel_n,
            scale=auxiliary.get_TempScale_unit(units.lower()),
            options=filter_on_off
        )

        return out

    def get_temp_all_channels(self, units=None, averaged=True):
        """
        Reads the analog signal out of all available channels. The read values are returned inside a list.

        Parameters
        ----------
        units : string or None
            the units in which the temperature is shown. Defaults to None which uses the default units set by the
            instance. Possible values (not case-sensitive):
            for Celsius                 celsius,               c
            for Fahrenheit              fahrenheit,            f
            for Kelvin                  kelvin,                k
            for calibrated voltage      volts, volt, voltage,  v
            for uncalibrated voltage    raw, none, noscale     r   TODO: figure out what calibrated and uncalibrated is
            for default units           bool : None
        averaged : bool
            When selected, 10 samples are read from the specified channel and averaged. The average is the reading
            returned. The maximum acquisiton frequency doesn't change regardless of this parameter.

        Returns
        -------
        list of floats
            List containing the temperature or voltage values as a float in the specified units. The index of a value
            corresponds to its respective channel. If a channel is not available, its respective place in the list
            will have None.
        """

        out = []
        for channel in range(self.number_temp_channels):
            try:
                out.append(self.get_temp(channel_n=channel, units=units, averaged=averaged))
            except ul.ULError:
                print('ERROR: Could not read from channel ' + str(channel) + '. Appending None.')
                out.append(None)
                continue

        return out

    def get_temp_scan(self, low_channel=0, high_channel=7, units=None, averaged=True):
        """
        Reads the analog signal out of a range of channels delimited by the low_channel and the high_channel
        (inclusive). The read values are returned inside a list.

        Parameters
        ----------
        low_channel : int
            the number of the channel from which to start the scan. Defaults to channel 0 if the channel number
            is not specified.
        high_channel : int
            the number of the channel on which to stop the scan. Defaults to channel 7 if the channel number
            is not specified. The range is inclusive, therefore the signal from this channel is included in the output
        units : string or None
            the units in which the temperature is shown. Defaults to None which uses the default units set by the
            instance. Possible values (not case-sensitive):
            for Celsius                 celsius,               c
            for Fahrenheit              fahrenheit,            f
            for Kelvin                  kelvin,                k
            for calibrated voltage      volts, volt, voltage,  v
            for uncalibrated voltage    raw, none, noscale     r   TODO: figure out what calibrated and uncalibrated is
            for default units           bool : None
        averaged : bool
            When selected, 10 samples are read from the specified channel and averaged. The average is the reading
            returned. The maximum acquisiton frequency doesn't change regardless of this parameter.

        Returns
        -------
        list of floats
            List containing the temperature or voltage values as a float in the specified units. The index of a value
            corresponds to its respective channel. If a channel is not available, its respective place in the list
            will have None.
        """

        out = []
        for channel in range(low_channel, high_channel+1):
            try:
                out.append(self.get_temp(channel_n=channel, units=units, averaged=averaged))
            except ul.ULError:
                print('ERROR: Could not read from channel ' + str(channel) + '. Appending None.')
                out.append(None)
                continue

        return out

    @property
    def default_units(self):
        return self._default_units

    @property
    def thermocouple_type_ch0(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=0,
            config_item=enums.BoardInfo.CHANTCTYPE
        )

    @property
    def thermocouple_type_ch1(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=1,
            config_item=enums.BoardInfo.CHANTCTYPE
        )

    @property
    def thermocouple_type_ch2(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=2,
            config_item=enums.BoardInfo.CHANTCTYPE
        )

    @property
    def thermocouple_type_ch3(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=3,
            config_item=enums.BoardInfo.CHANTCTYPE
        )

    @property
    def thermocouple_type_ch4(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=4,
            config_item=enums.BoardInfo.CHANTCTYPE
        )

    @property
    def thermocouple_type_ch5(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=5,
            config_item=enums.BoardInfo.CHANTCTYPE
        )

    @property
    def thermocouple_type_ch6(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=6,
            config_item=enums.BoardInfo.CHANTCTYPE
        )

    @property
    def thermocouple_type_ch7(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=7,
            config_item=enums.BoardInfo.CHANTCTYPE
        )

    @property
    def temp_ch0(self):
        return self.get_temp(channel_n=0)

    @property
    def temp_ch1(self):
        return self.get_temp(channel_n=1)

    @property
    def temp_ch2(self):
        return self.get_temp(channel_n=2)

    @property
    def temp_ch3(self):
        return self.get_temp(channel_n=3)

    @property
    def temp_ch4(self):
        return self.get_temp(channel_n=4)

    @property
    def temp_ch5(self):
        return self.get_temp(channel_n=5)

    @property
    def temp_ch6(self):
        return self.get_temp(channel_n=6)

    @property
    def temp_ch7(self):
        return self.get_temp(channel_n=7)

    # ==================================================================================================================
    # Set methods and setters
    # ==================================================================================================================
    @default_units.setter
    def default_units(self, new_units):
        """
        Set the default units as the new_units. First use get_TempScale_unit() to error check the new_units. If no
        exception is raised, then the default units are set using new_units.

        Parameters
        ----------
        new_units : string
            the units in which the channel signal is shown. Valid inputs (not case-sensitive):
            for Celsius                 celsius,               c
            for Fahrenheit              fahrenheit,            f
            for Kelvin                  kelvin,                k
            for calibrated voltage      volts, volt, voltage,  v
            for uncalibrated voltage    raw, none, noscale     r   TODO: figure out what calibrated and uncalibrated is
        """
        if new_units is None:
            self._default_units = self._temp
        auxiliary.get_TempScale_unit(new_units)
        self._default_units = new_units
