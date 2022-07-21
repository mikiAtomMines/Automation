"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""


from sys import platform

try:
    import mcculw  # Python MCC library for windows
    from mcculw import ul
    from mcculw import enums
except ModuleNotFoundError:
    pass

try:
    import uldaq  # Python MCC library for Linux
    from uldaq import DaqDevice
    from uldaq import AiDevice
except ModuleNotFoundError:
    pass


# TODO: Add proper error handling. This includes receiving error from power supply.
# TODO: Finish adding comments


class PowerSupply:
    def __init__(
            self,
            MAX_voltage,
            MAX_current,
            channel_voltage_limits=None,
            channel_current_limits=None,
            number_of_channels=1,
            zero_on_startup=True
    ):

        """
        A benchtop programmable power supply.

        Parameters
        ----------
        MAX_voltage : float
            Maximum voltage that the power supply can output based on hardware limitations.
        MAX_current : float
            Maximum current that the power supply can output based on hardware limitations.
        channel_voltage_limits : list of float, None
            list containing the individual channel limits for the set voltage. The set voltage of a channel cannot
            exceed its limit voltage. The 0th item corresponds to the limit of channel 1, 1st item to channel 2,
            and so on.
        channel_current_limits : list of float, None
            list containing the individual channel limits for the set current. The set current of a channel cannot
            exceed its limit current. The 0th item corresponds to the limit of channel 1, 1st item to channel 2,
            and so on.
        number_of_channels : int
            the number of physical programmable channels in the power supply.
        zero_on_startup : bool
            If set to true, will run a method to set the set voltage and current to 0.
        """

        self._MAX_voltage = MAX_voltage
        self._MAX_current = MAX_current
        self._channel_voltage_limits = channel_voltage_limits
        self._channel_current_limits = channel_current_limits
        self._number_of_channels = number_of_channels
        self._zero_on_startup = zero_on_startup

        if self._channel_voltage_limits is None and self._MAX_voltage is not None:
            self._channel_voltage_limits = [self._MAX_voltage] * self._number_of_channels
        if self._channel_current_limits is None and self._MAX_current is not None:
            self._channel_current_limits = [self._MAX_current] * self._number_of_channels

    def check_valid_channel(self, channel):
        if type(channel) != int:
            return 'ERROR: channel should be an int, starting from 1.', type(channel), 'not supported'
        elif channel > self.number_of_channels:
            return 'ERROR: channel' + str(channel) + 'not found. This power supply has' + str(self.number_of_channels)\
                   + 'channels. '
        else:
            return None

    def get_channel_state(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the state

        Returns
        -------
        bool
            If succesful, return a bool. True for ON, False for OFF.
        str
            Else, return an error string.
        """
        pass

    def set_channel_state(self, channel, state):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to set the state, True for ON, False for OFF

        Returns
        -------
        None
            If succesful, returns None.
        str
            Else, return an error string.
        """
        pass

    def get_setpoint_voltage(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set voltage

        Returns
        -------
        float
            If succesful, return a float.
        str
            Else, return an error string.
        """
        pass

    def set_voltage(self, channel, volts):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to set the set voltage
        volts : float
            The desired new value for the set voltage in volts.

        Returns
        -------
        None
            If succesful, returns None.
        str
            Else, return an error string.
        """
        pass

    def get_actual_voltage(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set voltage

        Returns
        -------
        float
            If succesful, return a float.
        str
            Else, return an error string.
        """
        pass

    def get_setpoint_current(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set current

        Returns
        -------
        float
            If succesful, return a float.
        str
            Else, return an error string.
        """
        pass

    def set_current(self, channel, amps):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to set the set current
        amps : float
            The desired new value for the set current in amps.

        Returns
        -------
        None
            If succesful, returns None.
        str
            Else, return an error string.
        """
        pass

    def get_actual_current(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set current

        Return
        float
            If succesful, return a float.
        str
            Else, return an error string.
        ------
        """
        pass

    def get_voltage_limit(self, channel):
        """
        Get the software voltage limit of the power supply. The setpoint voltage of the power supply cannot be set
        higher than this value. This value cannot be set higher than the hardware power supply MAX voltage limit.

        Parameters
        ----------
        channel : int
            The desired channel to get the channel voltage limit

        Returns
        -------
        float
            If succesful, return a float.
        str
            Else, return an error string.
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        return self._channel_voltage_limits[channel - 1]

    def set_voltage_limit(self, channel, volts):
        """
        Set the software voltage limit of the power supply. The setpoint voltage of the power supply cannot be set
        higher than this value. This value cannot be set higher than the hardware power supply MAX voltage limit.

        Parameters
        ----------
        channel : int
            The desired channel to set the channel voltage limit
        volts : float
            The desired new value for the voltage limit.

        Returns
        -------
        None
            If succesful, returns None.
        str
            Else, return an error string.
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        if volts > self._MAX_voltage or volts <= 0:
            return 'Voltage limit not set. New voltage limit is not allowed by the power supply.'
        elif volts < self.get_setpoint_voltage(channel):
            return 'Voltage limit not set. New voltage limit is lower than present channel setpoint voltage.'
        else:
            self._channel_voltage_limits[channel - 1] = volts

    def get_current_limit(self, channel):
        """
        Get the software current limit of the power supply. The setpoint current of the power supply cannot be set
        higher than this value. This value cannot be set higher than the hardware power supply MAX current limit.

        Parameters
        ----------
        channel : int
            The desired channel to get the channel current limit

        Returns
        -------
        float
            If succesful, return a float.
        str
            Else, return an error string.
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        return self._channel_current_limits[channel - 1]

    def set_current_limit(self, channel, amps):
        """
        Set the software current limit of the power supply. The setpoint current of the power supply cannot be set
        higher than this value. This value cannot be set higher than the hardware power supply MAX current limit.

        Parameters
        ----------
        channel : int
            The desired channel to set the channel current limit
        amps : float
            The desired new value for the current limit.

        Returns
        -------
        None
            If succesful, returns None.
        str
            Else, return an error string.
        """
        err = self.check_valid_channel(channel)
        if err is not None:
            return err

        if amps > self._MAX_current or amps <= 0:
            return 'Current limit not set. New current limit is not allowed by the power supply.'
        elif amps < self.get_setpoint_current(channel):
            return 'Current limit not set. New current limit is lower than present channel setpoint current.'
        else:
            self._channel_current_limits[channel - 1] = amps

    def set_all_channels_voltage_limit(self, volts):
        """
        Set the software voltage limit of the power supply for all channels. The setpoint voltage of the power supply
        cannot be set higher than this value. This value cannot be set higher than the hardware power supply MAX
        voltage limit.

        Parameters
        ----------
        volts : float
            The desired new value for the voltage limit.

        Returns
        -------
        None
            If succesful, returns None.
        str
            Else, return an error string.
        """
        for chan in range(1, self.number_of_channels+1):
            err = self.set_voltage_limit(chan, volts)
            if err is not None:
                return err

    def set_all_channels_current_limit(self, amps):
        """
        Set the software current limit of the power supply for all channels. The setpoint current of the power supply
        cannot be set higher than this value. This value cannot be set higher than the hardware power supply MAX
        current limit.

        Parameters
        ----------
        amps : float
            The desired new value for the current limit.

        Returns
        -------
        None
            If succesful, returns None.
        str
            Else, return an error string.
        """
        for chan in range(1, self.number_of_channels+1):
            err = self.set_current_limit(chan, amps)
            if err is not None:
                return err

    def zero_all_channels(self):
        """
        Sets the set voltage and set current of all channels to 0.

        Returns
        -------
        None
            If succesful, returns None.
        str
            Else, return an error string.
        """
        for chan in range(1, self.number_of_channels+1):
            err1 = self.set_voltage(channel=chan, volts=0)
            if err1 is not None:
                return err1
            err2 = self.set_current(channel=chan, amps=0)
            if err2 is not None:
                return err2
            err3 = self.set_channel_state(channel=chan, state=False)
            if err3 is not None:
                return err3
            print('Channel', chan, 'zeroed.')

    # Properties
    # ----------
    @property
    def idn(self):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Returns
        -------
        str
            identification string
        """
        pass

    @property
    def MAX_voltage(self):
        return self._MAX_voltage

    # @MAX_voltage_limit.setter
    # def MAX_voltage_limit(self, new_MAX_voltage):
    #     print('CAUTION: The MAX voltage limit should always match the hardware limitation of the power supply.')
    #     print('Setting MAX voltage limit to', new_MAX_voltage)
    #     self._MAX_voltage_limit = new_MAX_voltage

    @property
    def MAX_current(self):
        return self._MAX_current

    # @MAX_current_limit.setter
    # def MAX_current_limit(self, new_MAX_current):
    #     print('CAUTION: The MAX current limit should always match the hardware limitation of the power supply.')
    #     print('Setting MAX voltage limit to', new_MAX_current)
    #     self._MAX_voltage_limit = new_MAX_current

    @property
    def channel_voltage_limits(self):
        out = ''
        for i, lim in enumerate(self._channel_voltage_limits):
            out += 'chan' + str(i+1) + ': ' + str(lim) + '\n'

        return out

    @property
    def channel_current_limits(self):
        out = ''
        for i, lim in enumerate(self._channel_current_limits):
            out += 'chan' + str(i + 1) + ': ' + str(lim) + '\n'

        return out

    @property
    def number_of_channels(self):
        return self._number_of_channels

    # @number_of_channels.setter
    # def number_of_channels(self, n):
    #     print('CAUTION: The number of channels should always match the hardware')
    #     print('Setting number of channels to', n)
    #     self._number_of_channels = n


# ======================================================================================================================
if platform == 'win32':
    class MccDeviceWindows:
        def __init__(
                self,
                # Connection stuff
                board_number,
                ip4_address=None,
                port=None,

                # For Temperature DAQs:
                default_units='celsius',
        ):
            """
            Class for an MCC device supported by their Universal Library.

            Parameters
            ----------
            board_number : int
                All MCC devices must have a board number assigned to them either with instacal or with
                ul.create_daq_descriptor. If using instacal, board_number must match the board number of its associated
                device. If using IP address, board_number is the number to assign the device and must not be already in
                use. Can be any int from 0 to 99.
            ip4_address : str
                IPv4 address of the associated MCC device
            port : int
                Communication port to be used. Safely chose any number between 49152 and 65536.
            default_units : str
                Temperature units to use for temp measurements. Possible values: celsius or c, fahrenheit or f,
                and kelvin or k.
            """

            self._board_number = board_number
            self._ip4_address = ip4_address
            self._port = port
            self._default_units = default_units
            self._is_connected = False

            if self._ip4_address is not None and self._port is not None:
                self.connect()

        def get_TempScale_units(self, units):
            """
            Returns the associated mcculw.enums.TempScale object with the desired temperature unit.

            Parameters
            ----------
            units : {'c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin', 'v', 'volts', 'voltage', 'r', 'raw'}, None
                the units in which the temperature is shown. Defaults to None, which uses the default units set by the
                instance. Possible values (not case-sensitive):
                for Celsius                 'celsius',          'c'
                for Fahrenheit              'fahrenheit',       'f'
                for Kelvin                  'kelvin',           'k'
                for calibrated voltage      'volts', 'voltage', 'v'
                for uncalibrated voltage    'raw',              'r'
                for default units           None

            Returns
            -------
            enums.TempScale
                This object is used by the mcc universal library. Possbile values: enums.TempScale.CELSIUS,
                enums.TempScale.FAHRENHEIT, enums.TempScale.KELVIN, enums.TempScale.VOLTS, and enums.TempScale.NOSCALE.

            """

            TempScale_dict = {
                'celsius': enums.TempScale.CELSIUS,
                'c': enums.TempScale.CELSIUS,

                'fahrenheit': enums.TempScale.FAHRENHEIT,
                'f': enums.TempScale.FAHRENHEIT,

                'kelvin': enums.TempScale.KELVIN,
                'k': enums.TempScale.KELVIN,

                'volts': enums.TempScale.VOLTS,
                'voltage': enums.TempScale.VOLTS,
                'v': enums.TempScale.VOLTS,

                'raw': enums.TempScale.NOSCALE,
                'r': enums.TempScale.NOSCALE
            }

            try:
                out = TempScale_dict[units.lower()]
            except KeyError:
                print('\nERROR: input string "', units, '" for units is not a valid input. Possible inputs:')
                print('    "celsius"                    or    "c"    ')
                print('    "fahrenheit"                 or    "f"    ')
                print('    "kelvin"                     or    "k"    ')
                print('    "volts", "voltage"           or    "v"    ')
                print('    "raw",                       or    "r"    ')
                out = None
            return out

        def check_valid_units(self, units):  # TODO: figure out what calibrated and uncalibrated is
            """
            Check input units for valid format

            Parameters
            ----------
            units : {'c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin', 'v', 'volts', 'voltage', 'r', 'raw'}, None
                the units in which the temperature is shown. Defaults to None, which uses the default units set by the
                instance. Possible values (not case-sensitive):
                for Celsius                 'celsius',          'c'
                for Fahrenheit              'fahrenheit',       'f'
                for Kelvin                  'kelvin',           'k'
                for calibrated voltage      'volts', 'voltage', 'v'
                for uncalibrated voltage    'raw',              'r'
                for default units           None

            Returns
            -------
            None
                If units are valid
            str
                Else, return error string
            """
            if units is None:
                return
            elif type(units) is not str:
                return 'ERROR: input type should be string. Type ' + str(type(units)) + ' not supported.'

            units_set = {None, 'c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin', 'r', 'raw', 'none', 'noscale', 'v',
                         'volts', 'volt', 'voltage'}

            if units.lower() not in units_set:
                return 'ERROR: units ' + str(units) + ' not supported'

        def check_valid_temp_channel(self, channel):
            """
            Compares the input temperature channel with the number of temperature channels in the device to determine
            if the input channel is valid.

            Parameters
            ----------
            channel : int
                the channel to check. Valid from 0 to the number of temp channels in the device.

            Returns
            -------
            None
                If channel is valid, return None.
            str
                Else, return error string.
            """
            if type(channel) is not int:
                return 'ERROR: channel input must be int. type ' + str(type(channel)) + ' not supported.'

            if not (0 <= channel < self.number_temp_channels):
                return 'ERROR: channel ' + str(channel) + ' not valid. This unit has ' + str(
                    self.number_temp_channels) + ' channels, starting from channel 0.'

        # ----------------
        # Connection and board info
        # ----------------
        def connect(self, ip=None, port=None):
            if (self._ip4_address is None and ip is None) or (self._port is None and port is None) :
                return "ERROR: need to give an IP address and port first."

            ul.ignore_instacal()
            if ip is None:
                ip = self._ip4_address
            if port is None:
                port = self._port

            dscrptr = ul.get_net_device_descriptor(host=ip, port=port, timeout=2000)
            ul.create_daq_device(board_num=self._board_number, descriptor=dscrptr)
            self._is_connected = True
            print('Connection to', self._ip4_address, 'was succesful')

        def disconnect(self):
            ul.release_daq_device(self._board_number)
            self._is_connected = False

        @property
        def idn(self):
            return self.model + ', ' + str(self._board_number)

        @property
        def board_number(self):
            return self._board_number

        @board_number.setter
        def board_number(self, new_num):
            if not self._is_connected:
                self._board_number = new_num
            else:
                print('ERROR: board_number cannot be changed while device is connected.')

        @property
        def ip4_address(self):
            return self._ip4_address

        @ip4_address.setter
        def ip4_address(self, new_ip):
            if not self._is_connected:
                self._ip4_address = new_ip
            else:
                print('ERROR: ip4_address cannot be changed while device is connected')

        @property
        def port(self):
            return self._port

        @port.setter
        def port(self, new_port):
            if not self._is_connected:
                self._port = new_port
            else:
                print('ERROR: port cannot be changed while connection is on.')

        @property
        def model(self):
            return ul.get_board_name(self._board_number)

        @property
        def mac_address(self):
            return ul.get_config_string(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=0,
                config_item=enums.BoardInfo.DEVMACADDR,
                max_config_len=255
            )

        @property
        def unique_id(self):
            return ul.get_config_string(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=0,
                config_item=enums.BoardInfo.DEVUNIQUEID,
                max_config_len=255
            )

        @property
        def serial_number(self):
            return ul.get_config_string(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=0,
                config_item=enums.BoardInfo.DEVSERIALNUM,
                max_config_len=255
            )

        @property
        def number_temp_channels(self):
            """
            :return : int
            """
            return ul.get_config(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=0,
                config_item=enums.BoardInfo.NUMTEMPCHANS
            )

        @property
        def number_io_channels(self):
            """
            :return : int
            """
            return ul.get_config(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=0,
                config_item=enums.BoardInfo.NUMIOPORTS
            )

        @property
        def number_ad_channels(self):
            """
            :return : int
            """
            return ul.get_config(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=0,
                config_item=enums.BoardInfo.NUMADCHANS
            )

        @property
        def number_da_channels(self):
            """
            :return : int
            """
            return ul.get_config(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=0,
                config_item=enums.BoardInfo.NUMDACHANS
            )

        @property
        def clock_frequency_MHz(self):
            """
            :return : int
            """
            return ul.get_config(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=0,
                config_item=enums.BoardInfo.CLOCK
            )

        # -----------------
        # Temperature DAQ's
        # -----------------
        def get_temp(self, channel_n=0, units=None, averaged=True):
            """
            Reads the analog signal out of a channel and returns the value in the desired units.

            Parameters
            ----------
            channel_n : int
                the number of the channel from which to read the temperature. defaults to channel 0.
            units : str, None
                check docstring for self.check_valid_units for valid input units.
            averaged : bool
                When selected, 10 samples are read from the specified channel and averaged. The average is the reading
                returned. The maximum acquisiton frequency doesn't change regardless of this parameter.

            Returns
            -------
            float
                If succesful, reading as a float in the specified units.
            str
                Else, return error string
            """
            err1 = self.check_valid_units(units)
            err2 = self.check_valid_temp_channel(channel_n)
            if err1 is not None:
                return err1
            if err2 is not None:
                return err2

            if averaged:
                filter_on_off = enums.TInOptions.FILTER
            else:
                filter_on_off = enums.TInOptions.NOFILTER

            if units is None:
                units = self._default_units

            out = ul.t_in(
                board_num=self._board_number,
                channel=channel_n,
                scale=self.get_TempScale_units(units.lower()),
                options=filter_on_off
            )

            return out

        def get_temp_all_channels(self, units=None, averaged=True):
            """
            Reads the analog signal out of all available channels. The read values are returned inside a list.

            Parameters
            ----------
            units : str, None
                check docstring for self.check_valid_units for valid input units.
            averaged : bool
                When selected, 10 samples are read from the specified channel and averaged. The average is the reading
                returned. The maximum acquisiton frequency doesn't change regardless of this parameter.

            Returns
            -------
            list of float
                List containing the readings as a float in the specified units. The index of a
                value corresponds to its respective channel. If a channel is not available, its respective place in
                the list will have None.
            str
                If an error occurs, return error string
            """
            err = self.check_valid_units(units)
            if err is not None:
                return err

            if units is None:
                units = self._default_units

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
                is not specified. The range is inclusive, therefore the signal from this channel is included in the
                output
            units : str, None
                check docstring for self.check_valid_units for valid input units.
            averaged : bool
                When selected, 10 samples are read from the specified channel and averaged. The average is the reading
                returned. The maximum acquisiton frequency doesn't change regardless of this parameter.

            Returns
            -------
            list of float
                List containing the temperature or voltage values as a float in the specified units. The index of a
                value corresponds to its respective channel. If a channel is not available, its respective place in
                the list will have None.
            str
                If an error occurs, return error string
            """
            err1 = self.check_valid_units(units)
            err2 = self.check_valid_temp_channel(low_channel)
            err3 = self.check_valid_temp_channel(high_channel)
            if err1 is not None:
                return err1
            if err2 is not None:
                return err2
            if err3 is not None:
                return err3

            if units is None:
                units = self._default_units

            out = []
            for channel in range(low_channel, high_channel + 1):
                try:
                    out.append(self.get_temp(channel_n=channel, units=units, averaged=averaged))
                except ul.ULError:
                    print('ERROR: Could not read from channel ' + str(channel) + '. Appending None.')
                    out.append(None)
                    continue

            return out

        def get_thermocouple_type(self, channel):
            """
            Parameters:
            -----------
            channel : int
                temperature channel to get TC-type

            Returns
            -------
            str
                If succesful, return TC-type as a string. Else, return an error string.
            """
            err = self.check_valid_temp_channel(channel)
            if err is not None:
                return err

            tc_type_dict = {
                1: 'J',
                2: 'K',
                3: 'T',
                4: 'E',
                5: 'R',
                6: 'S',
                7: 'B',
                8: 'N'
            }

            tc_int = ul.get_config(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=channel,
                config_item=enums.BoardInfo.CHANTCTYPE
            )

            return tc_type_dict[tc_int]

        def set_thermocuple_type(self, channel, new_tc):
            """
            Parameters
            ----------
            channel : int
                temperature channel to set the TC-type
            new_tc : {'j', 'k', 't', 'e', 'r', 's', 'b', 'n'}
                Not case-sensitive.

            Returns
            -------
            None
                If succesful, return None
            str
                Else, return an error string
            """
            err = self.check_valid_temp_channel(channel)
            if err is not None:
                return err

            tc_type_dict = {
                'J': 1,
                'K': 2,
                'T': 3,
                'E': 4,
                'R': 5,
                'S': 6,
                'B': 7,
                'N': 8
            }

            try:
                val = tc_type_dict[new_tc.upper()]
            except KeyError:
                return 'TC type ' + new_tc + ' not supported by this device.'

            ul.set_config(
                info_type=enums.InfoType.BOARDINFO,
                board_num=self._board_number,
                dev_num=channel,
                config_item=enums.BoardInfo.CHANTCTYPE,
                config_val=val
            )

        @property
        def default_units(self):
            return self._default_units

        @default_units.setter
        def default_units(self, new_units=None):
            """
            Set the default units as the new_units. First use get_TempScale_unit() to error check the new_units. If no
            exception is raised, then the default units are set using new_units.

            Parameters
            ----------
            new_units : string, None
                see docstring for self.check_valid_units for valid units.
            """
            err = self.check_valid_units(new_units)
            if err is not None:
                print(err)
            else:
                if new_units is None:
                    new_units = 'celsius'

                self._default_units = new_units.lower()

        @property
        def thermocouple_type_ch0(self):
            return self.get_thermocouple_type(channel=0)

        @thermocouple_type_ch0.setter
        def thermocouple_type_ch0(self, new_tc_type):
            self.set_thermocuple_type(channel=0, new_tc=new_tc_type)

        @property
        def thermocouple_type_ch1(self):
            return self.get_thermocouple_type(channel=1)

        @thermocouple_type_ch1.setter
        def thermocouple_type_ch1(self, new_tc_type):
            self.set_thermocuple_type(channel=1, new_tc=new_tc_type)

        @property
        def thermocouple_type_ch2(self):
            return self.get_thermocouple_type(channel=2)

        @thermocouple_type_ch2.setter
        def thermocouple_type_ch2(self, new_tc_type):
            self.set_thermocuple_type(channel=2, new_tc=new_tc_type)

        @property
        def thermocouple_type_ch3(self):
            return self.get_thermocouple_type(channel=3)

        @thermocouple_type_ch3.setter
        def thermocouple_type_ch3(self, new_tc_type):
            self.set_thermocuple_type(channel=3, new_tc=new_tc_type)

        @property
        def thermocouple_type_ch4(self):
            return self.get_thermocouple_type(channel=4)

        @thermocouple_type_ch4.setter
        def thermocouple_type_ch4(self, new_tc_type):
            self.set_thermocuple_type(channel=4, new_tc=new_tc_type)

        @property
        def thermocouple_type_ch5(self):
            return self.get_thermocouple_type(channel=5)

        @thermocouple_type_ch5.setter
        def thermocouple_type_ch5(self, new_tc_type):
            self.set_thermocuple_type(channel=5, new_tc=new_tc_type)

        @property
        def thermocouple_type_ch6(self):
            return self.get_thermocouple_type(channel=6)

        @thermocouple_type_ch6.setter
        def thermocouple_type_ch6(self, new_tc_type):
            self.set_thermocuple_type(channel=6, new_tc=new_tc_type)

        @property
        def thermocouple_type_ch7(self):
            return self.get_thermocouple_type(channel=7)

        @thermocouple_type_ch7.setter
        def thermocouple_type_ch7(self, new_tc_type):
            self.set_thermocuple_type(channel=7, new_tc=new_tc_type)

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


if platform == 'linux' or platform == 'linux2':
    class MccDeviceLinux(DaqDevice):
        def __init__(
                self,
                ip4_address,
                port=54211,
                default_units='celsius'
        ):
            """
            Class for an MCC Device. Use only on Linux machines.

            Parameters
            ----------
            ip4_address : str
                IPv4 address of device in format '255.255.255.255'
            port : int
                communications port number.
            default_units : {'c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin', 'v', 'volts', 'r', 'raw'}
                default units to use for temperature measurements
            """
            d = uldaq.get_net_daq_device_descriptor(ip4_address, port, ifc_name=None, timeout=2)
            super().__init__(d)
            self._default_units = default_units

            self.connect()

        def get_TempScale_unit(self, units):
            units_dict = {
                'celsius': 1,
                'c': 1,
                'fahrenheit': 2,
                'f': 2,
                'kelvin': 3,
                'k': 3,
                'volts': 4,
                'v': 4,
                'raw': 5,
                'r': 5
            }
            try:
                return units_dict[units.lower()]
            except KeyError:
                return None

        def check_valid_units(self, units):  # TODO: figure out what calibrated and uncalibrated is
            """
            Check input units for valid format

            Parameters
            ----------
            units : {'c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin', 'v', 'volts', 'voltage', 'r', 'raw'}, None
                the units in which the temperature is shown. Defaults to None, which uses the default units set by the
                instance. Possible values (not case-sensitive):
                for Celsius                 'celsius',          'c'
                for Fahrenheit              'fahrenheit',       'f'
                for Kelvin                  'kelvin',           'k'
                for calibrated voltage      'volts',            'v'
                for uncalibrated voltage    'raw',              'r'
                for default units           None

            Returns
            -------
            None
                If units are valid
            str
                Else, return error string
            """
            if units is None:
                return
            elif type(units) is not str:
                return 'ERROR: input type should be string. Type ' + str(type(units)) + ' not supported.'

            units_set = {None, 'c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin', 'r', 'raw', 'v', 'volts'}

            if units.lower() not in units_set:
                return 'ERROR: units ' + str(units) + ' not supported'

        def check_valid_temp_channel(self, channel):
            """
            Compares the input temperature channel with the number of temperature channels in the device to determine
            if the input channel is valid.

            Parameters
            ----------
            channel : int
                the channel to check. Valid from 0 to the number of temp channels in the device.

            Returns
            -------
            None
                If channel is valid, return None.
            str
                Else, return error string.
            """
            if type(channel) is not int:
                return 'ERROR: channel input must be int. type ' + str(type(channel)) + ' not supported.'

            if not (0 <= channel < self.number_temp_channels):
                return 'ERROR: channel ' + str(channel) + ' not valid. This unit has ' + str(
                    self.number_temp_channels) + ' channels, starting from channel 0.'

        def get_temp(self, channel_n=0, units=None):
            """
            Reads the analog signal out of a channel and returns the value in the desired units.

            Parameters
            ----------
            channel_n : int
                the number of the channel from which to read the temperature. defaults to channel 0.
            units : str, None
                check docstring for self.check_valid_units for valid input units.

            Returns
            -------
            float
                If succesful, reading as a float in the specified units.
            str
                Else, return error string
            """
            err1 = self.check_valid_units(units)
            if err1 is not None:
                return err1
            err2 = self.check_valid_temp_channel(channel_n)
            if err2 is not None:
                return err2

            if units is None:
                units = self._default_units

            return self.get_ai_device().t_in(channel=channel_n, scale=self.get_TempScale_unit(units.lower()))

        def get_temp_scan(self, low_channel=0, high_channel=7, units=None):
            """
            Reads the analog signal out of a range of channels delimited by the low_channel and the high_channel
            (inclusive). The read values are returned inside a list.

            Parameters
            ----------
            low_channel : int
                the channel from which to start the scan. Defaults to channel 0.
            high_channel : int
                the channel on which to stop the scan. Defaults to channel 7.
            units : str, None
                check docstring for self.check_valid_units for valid input units.

            Returns
            -------
            list of float
                List containing the temperature or voltage values as a float in the specified units. The index of a
                value corresponds to its respective channel. If a channel is not available, its respective place in
                the list will have None.
            str
                If an error occurs, return error string
            """
            err1 = self.check_valid_units(units)
            err2 = self.check_valid_temp_channel(low_channel)
            err3 = self.check_valid_temp_channel(high_channel)
            if err1 is not None:
                return err1
            if err2 is not None:
                return err2
            if err3 is not None:
                return err3

            if units is None:
                units = self._default_units

            return self.get_ai_device().t_in_list(low_chan=low_channel, high_chan=high_channel,
                                                  scale=self.get_TempScale_unit(units.lower()))

        def get_thermocouple_type(self, channel):
            """
            Parameters:
            -----------
            channel : int
                temperature channel to get TC-type

            Returns
            -------
            str
                If succesful, return TC-type as a string. Else, return an error string.
            """
            err = self.check_valid_temp_channel(channel)
            if err is not None:
                return err

            tc_type_dict = {
                1: 'J',
                2: 'K',
                3: 'T',
                4: 'E',
                5: 'R',
                6: 'S',
                7: 'B',
                8: 'N'
            }

            tc_int = self.get_ai_device().get_config().get_chan_tc_type(channel=channel)
            return tc_type_dict[tc_int]

        def set_thermocouple_type(self, channel, new_tc):
            """
            Parameters
            ----------
            channel : int
                temperature channel to set the TC-type
            new_tc : {'j', 'k', 't', 'e', 'r', 's', 'b', 'n'}
                Not case-sensitive.

            Returns
            -------
            None
                If succesful, return None
            str
                Else, return an error string
            """
            tc_type_dict = {
                'J': 1,
                'K': 2,
                'T': 3,
                'E': 4,
                'R': 5,
                'S': 6,
                'B': 7,
                'N': 8
            }

            try:
                val = tc_type_dict[new_tc.upper()]
            except KeyError:
                return 'ERROR: TC Type ' + str(new_tc) + ' not supported'

            self.get_ai_device().get_config().set_chan_tc_type(channel=channel, tc_type=val)

        @property
        def idn(self):
            return str(self.get_info().get_product_id())

        @property
        def ip4_address(self):
            return str(self.get_config().get_host_ip())

        @property
        def number_temp_channels(self):
            return self.get_ai_device().get_info().get_num_chans()

        @property
        def default_units(self):
            return self._default_units

        @default_units.setter
        def default_units(self, new_units):
            err = self.check_valid_units(new_units)
            if err is None:
                self._default_units = new_units
            else:
                print(err)

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


# =====================================================================================================================
class Heater:
    def __init__(
            self,
            idn=None,
            MAX_temp=float('inf'),
            MAX_volts=float('inf'),
            MAX_current=float('inf'),
    ):
        """
        Parameters
        ----------
        idn : str
            Identification string.
        MAX_temp : float
            The maximum possible value for set temp. Should be based on the physical limitations of the heater.
            Should be used as a safety mechanism so the set temperature is never set higher than what the hardware
            allows. Default is set to infinity.
        MAX_volts : float
            The maximum allowed value for voltage across the heater. Analogous to MAX_temp.
        MAX_current : float
            The maximum allowed value for the current going through the heater. Analogous to MAX_temp and MAX_voltage.
        """
        self.idn = idn
        self.MAX_temp = MAX_temp
        self.MAX_volts = MAX_volts
        self.MAX_current = MAX_current

