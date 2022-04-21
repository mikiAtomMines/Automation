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


class MCC_Device:  # TODO: add API functions
    def __init__(self, board_number=None, ip4_address=None, port=50000):
        """
        Class for an MCC device supported by their Universal Library.

        Parameters
        ----------
        board_number : int
            All MCC devices have a board number which can be configured using instacal. The instance of Web_Tc must
            match the board number of its associated device. Possible values from 0 to 99.
        ip4_address : str
            IPv4 address of the associated MCC device
        port : int
            Communication port to be used. Safely chose any number between 49152 and 65536.
        """

        self._board_number = board_number
        self._ip4_address = ip4_address
        self._port = port
        # self._model = self.model
        # self._mac_address = self.mac_address
        # self._unique_id = self.unique_id
        # self._serial_number = self.serial_number
        # self._number_temp_channels = self.number_temp_channels
        # self._number_io_cahnnels = self.number_io_channels
        # self._number_ad_channels = self.number_ad_channels
        # self._number_da_channels = self.number_da_channels

    @property
    def idn(self):
        return self.model + ', ' + str(self._board_number)

    @property
    def board_number(self):
        return self._board_number

    @property
    def ip4_address(self):
        return self._ip4_address

    @property
    def port(self):
        return self._port

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
        Return
        ------
        int
            number of channels
        """
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=0,
            config_item=enums.BoardInfo.NUMTEMPCHANS
        )

    @property
    def number_io_channels(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=0,
            config_item=enums.BoardInfo.NUMIOPORTS
        )

    @property
    def number_ad_channels(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=0,
            config_item=enums.BoardInfo.NUMADCHANS
        )

    @property
    def number_da_channels(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=0,
            config_item=enums.BoardInfo.NUMDACHANS
        )

    @property
    def clock_frequency_MHz(self):
        return ul.get_config(
            info_type=enums.InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=0,
            config_item=enums.BoardInfo.CLOCK
        )

    @board_number.setter
    def board_number(self, new_number):
        if not (0 <= new_number <= 99):
            print('ERROR: new board number must be a number between 0 and 99, inclusive.')
            sys.exit()

        self._board_number = new_number

    """
    Plan for API functions:

    First get device Descriptor object using 

    """

# TODO: add heater object with physical parmeters as safety, like max temp, max current, max voltage. USe this object
#  in the heater class.


class HeaterAssembly:  # TODO: ass
    def __init__(
            self,
            power_supply=None,
            supply_channel=None,
            temperature_daq=None,
            daq_channel=None,
            pid_function=None,
            set_temperature=None,
            temp_units=None,
            MAX_set_temp=None,
            MIN_set_temp=None,
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
        MAX_set_temp : float, None
            The maximum possible value for set temp. Should be based on the physical limitations of the heater.
            Should be used as a safety mechanism so the set temperature is never set higher than what the hardware
            allows. If set to None, the limit is infinity.
        MIN_set_temp : float, None
            The minimum possible value for set temp. Analogous to MAX_temp.
        configure_on_startup : bool
            Will configure the PID object's output limits, setpoint, and optionally, the Kp, Ki, and Kd. Set this to
            True if the pid object has not been manually configured.
        """
        if MIN_set_temp is None:
            MIN_set_temp = 0
        if MAX_set_temp is None:
            MAX_set_temp = 0

        self._power_supply = power_supply
        self._supply_channel = supply_channel
        self._temperature_daq = temperature_daq
        self._daq_channel = daq_channel
        self._set_temperature = set_temperature
        self._temp_units = temp_units
        self._pid_function = pid_function
        self._MAX_set_temp = MAX_set_temp
        self._MIN_set_temp = MIN_set_temp
        self._configure_on_startup = configure_on_startup

        self._pid_function.setpoint = self._set_temperature
        if self._configure_on_startup:
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
        return self._MAX_set_temp

    @property
    def MIN_set_temp(self):
        return self.MIN_set_temp

    @property
    def configure_on_startup(self):
        return self._configure_on_startup

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
        if self._MAX_set_temp < new_temp < self._MIN_set_temp:
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

        # pid.output_limits((self._MIN_set_temp, self._MAX_set_temp))
        # pid.setpoint = self._set_temperature

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
        :param x_size:
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
