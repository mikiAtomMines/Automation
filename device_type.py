"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""


import auxiliary
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

import simple_pid

# TODO: Add proper error handling. This includes receiving error from power supply.
# TODO: Finish adding comments


class PowerSupply:
    def __init__(
            self,
            MAX_voltage_limit=None,
            MAX_current_limit=None,
            channel_voltage_limits=None,
            channel_current_limits=None,
            number_of_channels=1,
            reset_on_startup=True
    ):

        """
        A benchtop programmable power supply.

        Parameters
        ----------
        MAX_voltage_limit : float
            Maximum voltage that the power supply can output based on hardware limitations.
        MAX_current_limit : float
            Maximum current that the power supply can output based on hardware limitations.
        channel_voltage_limits : list of float
            list containing the individual channel limits for the set voltage. The set voltage of a channel cannot
            exceed its limit voltage. The 0th item corresponds to the limit of channel 1, 1st item to channel 2,
            and so on.
        channel_current_limits : list of float
            list containing the individual channel limits for the set current. The set current of a channel cannot
            exceed its limit current. The 0th item corresponds to the limit of channel 1, 1st item to channel 2,
            and so on.
        number_of_channels : int
            the number of physical programmable channels in the power supply.
        reset_on_startup : bool
            If set to true, will run a method to set the set voltage and current to 0 and reset the channel limits to
            their full range.
        """

        self._MAX_voltage_limit = MAX_voltage_limit
        self._MAX_current_limit = MAX_current_limit
        self._channel_voltage_limits = channel_voltage_limits
        self._channel_current_limits = channel_current_limits
        self._number_of_channels = number_of_channels
        self._reset_on_startup = reset_on_startup

        if self._channel_voltage_limits is None and self._MAX_voltage_limit is not None:
            self._channel_voltage_limits = [self._MAX_voltage_limit] * self._number_of_channels
        if self._channel_current_limits is None and self._MAX_current_limit is not None:
            self._channel_current_limits = [self._MAX_current_limit] * self._number_of_channels

    def check_channel_syntax(self, channel):
        if type(channel) != int:
            raise TypeError('ERROR: channel should be an int, starting from 1.', type(channel), 'not supported')
        elif channel > self.number_of_channels:
            raise ValueError('ERROR: channel', channel, 'not found. This power supply has',
                             self.number_of_channels, 'channels.')

    @property
    def idn(self):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Return : str
        ------
            identification string
        """
        return None

    @property
    def MAX_voltage_limit(self):
        return self._MAX_voltage_limit

    @MAX_voltage_limit.setter
    def MAX_voltage_limit(self, new_MAX_voltage):
        print('CAUTION: The MAX voltage limit should always match the hardware limitation of the power supply.')
        print('Setting MAX voltage limit to', new_MAX_voltage)
        self._MAX_voltage_limit = new_MAX_voltage

    @property
    def MAX_current_limit(self):
        return self._MAX_current_limit

    @MAX_current_limit.setter
    def MAX_current_limit(self, new_MAX_current):
        print('CAUTION: The MAX current limit should always match the hardware limitation of the power supply.')
        print('Setting MAX voltage limit to', new_MAX_current)
        self._MAX_voltage_limit = new_MAX_current

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

    @number_of_channels.setter
    def number_of_channels(self, n):
        print('CAUTION: The number of channels should always match the hardware')
        print('Setting number of channels to', n)
        self._number_of_channels = n

    def get_set_voltage(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set voltage

        Return : float
        ------
        """
        pass

    def get_actual_voltage(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set voltage

        Return : float
        ------
        """
        pass

    def set_set_voltage(self, channel, volts):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to set the set voltage
        volts : float
            The desired new value for the set voltage in volts.
        """
        pass

    def get_set_current(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set current

        Return : float
        ------
        """
        pass

    def get_actual_current(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set current

        Return : float
        ------
        """
        pass

    def get_channel_voltage_limit(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set current

        Return : float
        ------
        """
        pass

    def get_channel_current_limit(self, channel):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to get the set current

        Return : float
        ------
        """
        pass

    def set_set_current(self, channel, amps):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to set the set current
        amps : float
            The desired new value for the set current in amps.
        """
        pass

    def set_channel_voltage_limit(self, channel, volts):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to set the channel voltage limit
        volts : float
            The desired new value for the voltage limit.
        """
        pass

    def set_channel_current_limit(self, channel, amps):
        """
        This is a placeholder for the real method. For each model of power supply, this method has to be re-writen.

        Parameters
        ----------
        channel : int
            The desired channel to set the channel current limit
        amps : float
            The desired new value for the current limit.
        """
        pass

    def set_all_channels_voltage_limit(self, volts):
        for chan in range(1, self.number_of_channels+1):
            self.set_channel_voltage_limit(chan, volts)

    def set_all_channels_current_limit(self, amps):
        for chan in range(1, self.number_of_channels+1):
            self.set_channel_current_limit(chan, amps)

    def zero_all_channels(self):
        """
        Sets the set voltage and set current of all channels to 0. Then sets all voltage and current channel limits
        to the maximum allowed limits for full range of operation.
        """
        max_v = self.MAX_voltage_limit
        max_c = self.MAX_current_limit
        for chan in range(1, self.number_of_channels+1):
            self.set_set_voltage(channel=chan, volts=0)
            self.set_set_current(channel=chan, amps=0)
            self.set_channel_voltage_limit(channel=chan, volts=max_v)
            self.set_channel_current_limit(channel=chan, amps=max_c)


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
            """

            self._board_number = board_number
            self._ip4_address = ip4_address
            self._port = port
            self._default_units = default_units
            self._is_connected = False

            if self._ip4_address is not None:
                ul.ignore_instacal()
                dscrptr = ul.get_net_device_descriptor(host=self._ip4_address, port=self._port, timeout=2000)
                ul.create_daq_device(board_num=self._board_number, descriptor=dscrptr)
                self._is_connected = True

        # ----------------
        # Connection and board info
        # ----------------
        def connect(self, ip=None, port=54211):
            if self._ip4_address is None and ip is None:
                raise TypeError("ip address is None. Set the attribute ip_address to the device's IPv4 address, "
                                "or input the IPv4 address as an argument and try again.")
            ul.ignore_instacal()
            try:
                dscrptr = ul.get_net_device_descriptor(host=ip, port=port, timeout=2000)
            except AttributeError:
                dscrptr = ul.get_net_device_descriptor(host=self._ip4_address, port=port, timeout=20000)

            ul.create_daq_device(board_num=self._board_number, descriptor=dscrptr)
            self._is_connected = True

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
                raise AttributeError('ERROR: board_number cannot be changed while connection is on.')

        @property
        def ip4_address(self):
            return self._ip4_address

        @ip4_address.setter
        def ip4_address(self, new_ip):
            if not self._is_connected:
                self._ip4_address = new_ip
            else:
                raise AttributeError('ERROR: ip4_address cannot be changed while connection is on.')

        @property
        def port(self):
            return self._port

        @port.setter
        def port(self, new_port):
            if not self._is_connected:
                self._port = new_port
            else:
                raise AttributeError('ERROR: port cannot be changed while connection is on.')

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
                the number of the channel from which to read the temperature. defaults to channel 0 if the channel
                number is not specified.
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
                default_units attribute. Possible values (not case-sensitive):
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
            list of float
                List containing the temperature or voltage values as a float in the specified units. The index of a
                value corresponds to its respective channel. If a channel is not available, its respective place in
                the list will have None.
            """
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
            list of float
                List containing the temperature or voltage values as a float in the specified units. The index of a
                value corresponds to its respective channel. If a channel is not available, its respective place in
                the list will have None.
            """
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
            :param int channel: MCC temp channel
            :return str: TC type.
            """
            if not (0 <= channel <= self.number_temp_channels):
                raise ValueError('channel', channel, 'not found. Check the number of temp channels in the device.')

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

        def set_thermocuple_type(self, channel, new_tc_type):
            """
            :param int channel: MCC temp channel
            :param str new_tc_type: new thermocouple type to set on the desired channel. Not cap sensitive
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

            if not (0 <= channel <= self.number_temp_channels):
                raise ValueError('channel', channel, 'not found. Check the number of temp channels in the device.')
            if new_tc_type not in tc_type_dict.keys():
                raise ValueError('TC type ' + new_tc_type + ' not supported by this device.')

            val = tc_type_dict[new_tc_type.upper()]

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
            new_units : string
                the units in which the channel signal is shown. Valid inputs (not case-sensitive):
                for Celsius                 celsius,               c
                for Fahrenheit              fahrenheit,            f
                for Kelvin                  kelvin,                k
                for calibrated voltage      volts, volt, voltage,  v
                for uncalibrated voltage    raw, none, noscale     r   TODO: figure out what calibrated and uncalibrated is
            """
            if new_units is None:
                new_units = 'celsius'
            new_units = new_units.lower()
            auxiliary.get_TempScale_unit(new_units)
            self._default_units = new_units

        @property
        def thermocouple_type_ch0(self):
            return self.get_thermocouple_type(channel=0)

        @thermocouple_type_ch0.setter
        def thermocouple_type_ch0(self, new_tc_type):
            self.set_thermocuple_type(channel=0, new_tc_type=new_tc_type)

        @property
        def thermocouple_type_ch1(self):
            return self.get_thermocouple_type(channel=1)

        @thermocouple_type_ch1.setter
        def thermocouple_type_ch1(self, new_tc_type):
            self.set_thermocuple_type(channel=1, new_tc_type=new_tc_type)

        @property
        def thermocouple_type_ch2(self):
            return self.get_thermocouple_type(channel=2)

        @thermocouple_type_ch2.setter
        def thermocouple_type_ch2(self, new_tc_type):
            self.set_thermocuple_type(channel=2, new_tc_type=new_tc_type)

        @property
        def thermocouple_type_ch3(self):
            return self.get_thermocouple_type(channel=3)

        @thermocouple_type_ch3.setter
        def thermocouple_type_ch3(self, new_tc_type):
            self.set_thermocuple_type(channel=3, new_tc_type=new_tc_type)

        @property
        def thermocouple_type_ch4(self):
            return self.get_thermocouple_type(channel=4)

        @thermocouple_type_ch4.setter
        def thermocouple_type_ch4(self, new_tc_type):
            self.set_thermocuple_type(channel=4, new_tc_type=new_tc_type)

        @property
        def thermocouple_type_ch5(self):
            return self.get_thermocouple_type(channel=5)

        @thermocouple_type_ch5.setter
        def thermocouple_type_ch5(self, new_tc_type):
            self.set_thermocuple_type(channel=5, new_tc_type=new_tc_type)

        @property
        def thermocouple_type_ch6(self):
            return self.get_thermocouple_type(channel=6)

        @thermocouple_type_ch6.setter
        def thermocouple_type_ch6(self, new_tc_type):
            self.set_thermocuple_type(channel=6, new_tc_type=new_tc_type)

        @property
        def thermocouple_type_ch7(self):
            return self.get_thermocouple_type(channel=7)

        @thermocouple_type_ch7.setter
        def thermocouple_type_ch7(self, new_tc_type):
            self.set_thermocuple_type(channel=7, new_tc_type=new_tc_type)

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
                raise ValueError('ERROR: units ' + str(units) + ' not supported.')

        def get_temp(self, channel_n=0, units=None):
            if units is None:
                units = self._default_units

            return self.get_ai_device().t_in(channel=channel_n, scale=self.get_TempScale_unit(units.lower()))

        def get_temp_scan(self, low_channel=0, high_channel=7, units=None):
            if units is None:
                units = self._default_units

            return self.get_ai_device().t_in_list(low_chan=low_channel, high_chan=high_channel,
                                                  scale=self.get_TempScale_unit(units.lower()))

        def get_thermocouple_type(self, channel):
            return self.get_ai_device().get_config().get_chan_tc_type(channel=channel)

        def set_thermocouple_type(self, channel, new_tc_type):
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
                val = tc_type_dict[new_tc_type.upper()]
            except KeyError:
                raise ValueError('ERROR: TC Type ' + str(new_tc_type) + ' not supported')
            self.get_ai_device().get_config().set_chan_tc_type(channel=channel, tc_type=val)

        @property
        def idn(self):
            return self.get_info().get_product_id()

        @property
        def ip4_address(self):
            return self.get_config().get_host_ip()

        @property
        def number_temp_channels(self):
            return self.get_ai_device().get_info().get_num_chans()

        @property
        def default_units(self):
            return self._default_units

        @default_units.setter
        def default_units(self, new_units):
            self.get_TempScale_unit(new_units)
            self._default_units = new_units

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
    def __init__(self, idn=None, MAX_temp=9999, MAX_volts=9999, MAX_current=9999, resistance=20):
        """
        Parameters
        ----------
        
        MAX_temp : float, None
            The maximum possible value for set temp. Should be based on the physical limitations of the heater.
            Should be used as a safety mechanism so the set temperature is never set higher than what the hardware
            allows. If set to None, the limit is infinity.

        """
        self.idn = idn
        self.MAX_temp = MAX_temp
        self.MAX_volts = MAX_volts
        self.MAX_current = MAX_current
        self.resistance = resistance

