"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as anim
from mcculw import ul
from mcculw import enums
import auxiliary

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
    def MAX_voltage_limit(self):
        return self._MAX_voltage_limit

    @property
    def MAX_current_limit(self):
        return self._MAX_current_limit

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

    @MAX_voltage_limit.setter
    def MAX_voltage_limit(self, new_MAX_voltage):
        print('CAUTION: The MAX voltage limit should always match the hardware limitation of the power supply.')
        print('Setting MAX voltage limit to', new_MAX_voltage)
        self._MAX_voltage_limit = new_MAX_voltage

    @MAX_current_limit.setter
    def MAX_current_limit(self, new_MAX_current):
        print('CAUTION: The MAX current limit should always match the hardware limitation of the power supply.')
        print('Setting MAX voltage limit to', new_MAX_current)
        self._MAX_voltage_limit = new_MAX_current

    @number_of_channels.setter
    def number_of_channels(self, n):
        print('CAUTION: The number of channels should always match the hardware')
        print('Setting number of channels to', n)
        self._number_of_channels = n

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
        Sets the set voltage and set current of all chanles to 0. Then sets all voltage and current channel limits
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
class MCC_Device:
    def __init__(
            self,
            # Connection stuff
            board_number,
            ip4_address=None,
            port=None,

            # For Temperature DAQs:
            default_units='celsius'

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
        list of float
            List containing the temperature or voltage values as a float in the specified units. The index of a value
            corresponds to its respective channel. If a channel is not available, its respective place in the list
            will have None.
        """

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


# =====================================================================================================================
class Heater:
    def __init__(self, idn=None, MAX_temp=None, MAX_volts=None, MAX_current=None):
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


class HeaterAssembly:
    def __init__(
            self,
            power_supply=None,
            supply_channel=None,
            temperature_daq=None,
            daq_channel=None,
            pid_function=None,
            set_temperature=None,
            temp_units=None,
            heater=None,
            configure_on_startup=False,

    ):
        """
        A heater assembly composed of a heater, a temperature measuring device, and a power supply.

        Parameters
        ----------
        power_supply : device_models.PowerSupply
            The power supply model that is being used for controlling the electrical power going into the heater.
        supply_channel : int
            The physical power supply channel connected to the heater for controlling the electrical power.
        temperature_daq : device_models.MCC_device
            The temperature DAQ device that is being used for reading the temperature of the heater.
        daq_channel : int
            The physical DAQ channel used for taking temperature readings of the heater.
        pid_function : simple_pid.PID
            The PID function used to regulate the heater's temperature to the set point.
        set_temperature : float
            The desired set temperature in the same units as the temperature readings from the temperature DAQ.
        temp_units : str, None
            Set the temperature units for all temperature readings, setpoints, etc. Possible values (not
            case-sensitive):
            for Celsius                 celsius,               c
            for Fahrenheit              fahrenheit,            f
            for Kelvin                  kelvin,                k
            for default units           None
        heater : Heater
            heater type. Should contain the MAX temperature, MAX current, and MAX volts based on the hardware.
        
        configure_on_startup : bool
            Will configure the PID object's output limits, setpoint, and optionally, the Kp, Ki, and Kd. Set this to
            True if the pid object has not been manually configured.
        """

        self._power_supply = power_supply
        self._supply_channel = supply_channel
        self._temperature_daq = temperature_daq
        self._daq_channel = daq_channel
        self._pid_function = pid_function
        self._set_temperature = set_temperature
        self._temp_units = temp_units
        self._heater = heater
        self._configure_pid_on_startup = configure_on_startup

        self._pid_function.setpoint = self._set_temperature
        if self._configure_pid_on_startup:
            self.configure_pid()

        self._temp_units = self._temperature_daq.default_units  # If None, default units are Celsius

    # -----------------------------------------------------------------------------
    # Get methods
    # -----------------------------------------------------------------------------
    @property
    def power_supply(self):
        out = 'IDN: ' + self._power_supply.idn + '\n'\
            + 'IP4 Address: ' + self._power_supply.ip4_address

        return out

    @property
    def supply_channel(self):
        return self._supply_channel

    @property
    def temperature_daq(self):
        out = 'IDN: ' + self._temperature_daq.idn + '\n'\
            + 'IP4 Address: ' + self._temperature_daq.ip4_address

        return out

    @property
    def daq_channel(self):
        return self._daq_channel

    @property
    def set_temperature(self):
        return self._set_temperature

    @property
    def temp_units(self):
        return self._temp_units

    @property  # TODO: finish later
    def pid_function(self):
        return ''

    @property
    def MAX_set_temp(self):
        return self.heater.MAX_temp

    @property
    def MIN_set_temp(self):
        return self.MIN_set_temp

    @property
    def configure_pid_on_startup(self):
        return self._configure_pid_on_startup

    @property
    def current_temperature(self):
        return self._temperature_daq.get_temp(channel_n=self._daq_channel)

    # -----------------------------------------------------------------------------
    # Set methods
    # -----------------------------------------------------------------------------
    @supply_channel.setter
    def supply_channel(self, new_chan):
        self._power_supply.check_channel_syntax()

        if 1 <= new_chan <= self._power_supply.number_of_channels:
            self._supply_channel = new_chan
        else:
            print('ERROR: channel not found')
            sys.exit()

    @daq_channel.setter
    def daq_channel(self, new_chan):  # TODO: add syntax checking for mcc device
        if 1 <= new_chan <= self._temperature_daq.number_temp_channels:
            self._daq_channel = new_chan
        else:
            print('ERROR: channel not found')
            sys.exit()

    @set_temperature.setter
    def set_temperature(self, new_temp):
        if self._heater.MAX_temp < new_temp:
            raise ValueError('ERROR: new_temp value of', new_temp, 'not allowed. Check the MAX and MIN set '
                                                                   'temperature limits')
        self._set_temperature = new_temp
        self._pid_function.setpoint = new_temp

    @temp_units.setter
    def temp_units(self, new_units):
        self._temperature_daq.default_units = new_units  # this also checks if input is valid
        self._temp_units = new_units

    def configure_pid(self, *args, **kwargs):  # TODO: Finish. Currently not working
        """
        Sets the output limits, set point, and optionally, the Kp, Ki, and Kd of the PID object. Any number of K
        parameters can be set. The function will only set If no arguments are given, the K parameters of the PID object
        will not change.

        Parameters
        ----------
        *args : float
            Proportional (Kp), integration (Ki), and differentiation (Kd) terms in the PID function. The order is Kp,
            Ki, and Kd.
        *kwargs : float
            Same as *args. Keywords are Kp, Ki, or Kd.

        """

        pid = self._pid_function
        out_min = 0
        out_max = min(self._heater.MAX_volts, self._power_supply.get_voltage_limit(self._supply_channel))
        pid.output_limits =(out_min, out_max)
        pid.setpoint = self._set_temperature

        try:
            pid.Kp = args[0]
            pid.Kp = kwargs['Kp']
            pid.Ki = args[1]
            pid.Ki = kwargs['Ki']
            pid.Kd = args[2]
            pid.Kd = kwargs['Kd']
        except IndexError:
            pass
        except KeyError:
            pass

    def update_supply(self):
        """
        Calculates the new power supply voltage using the PID function based on the current temperature from the
        temperature daq channel. It then sets the power supply channel voltage to this new voltage.
        """
        current_temp = self.current_temperature
        print(current_temp)
        new_ps_voltage = self._pid_function(current_temp)
        # print(new_ps_voltage)
        self._power_supply.set_set_voltage(channel=self._supply_channel, volts=new_ps_voltage)

        return new_ps_voltage

    def live_plot(self, x_size=10):
        """
        plots current temp and ps_volts
        :param x_size: number of data points per frame
        """
        temp = [0.0]*x_size
        ps_v = [0.0]*x_size
        time_ = [0.0]*x_size
        fig = plt.figure()
        ax = plt.subplot(111)

        def animate(i):
            ps_volt = self.update_supply()

            temp.pop(0)
            temp.append(self.current_temperature)

            time_.pop(0)
            time_.append(i)

            ps_v.pop(0)
            ps_v.append(ps_volt)

            ax.cla()
            ax.plot(time_, temp)
            ax.plot(time_, ps_v)
            ax.text(time_[-1], temp[-1]+2, str(temp[-1]))
            ax.text(time_[-1], ps_v[-1]+2, str(ps_v[-1]))
            ax.set_ylim([0, self._set_temperature*1.3])

        ani = anim.FuncAnimation(fig, animate, interval=2000)
        plt.show()
