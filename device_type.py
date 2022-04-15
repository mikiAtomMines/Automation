"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import sys
import time

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
            number_of_channels=1,
            reset_on_startup=True
    ):

        """
        A benchtop programmable power supply.

        :param MAX_voltage_limit: -- Maximum voltage that the power supply can output based on hardware limitations.
        :param MAX_current_limit: -- Maximum current that the power supply can output based on hardware limitations.
        :param number_of_channels: - Specifies the number of programmable physical channels in the power supply.
        :param reset_on_startup: --- If true, will turn channels off and set the output voltage to zero.
        """

        self._MAX_voltage_limit = MAX_voltage_limit
        self._MAX_current_limit = MAX_current_limit
        self.number_of_channels = number_of_channels
        self._reset_on_startup = reset_on_startup

    @property
    def MAX_voltage_limit(self):
        return self._MAX_voltage_limit

    @property
    def MAX_current_limit(self):
        return self._MAX_current_limit

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
        return self.model +', ' + str(self._board_number)

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

        if self._configure_on_startup:
            self.configure_pid()

        self._temperature_daq.default_units = self._temp_units

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

    # -----------------------------------------------------------------------------
    # Set methods
    # -----------------------------------------------------------------------------
    @supply_channel.setter
    def supply_channel(self, new_chan):
        if 1 <= new_chan <= self._power_supply.number_of_channels:
            self._supply_channel = new_chan
        else:
            print('ERROR: channel not found')
            sys.exit()

    @daq_channel.setter
    def daq_channel(self, new_chan):
        if 1 <= new_chan <= self._temperature_daq.number_temp_channels:
            self._daq_channel = new_chan
        else:
            print('ERROR: channel not found')
            sys.exit()

    @temp_units.setter
    def temp_units(self, new_units):
        self._temperature_daq.default_units = new_units  # this also checks if input is valid
        self._temp_units = new_units

    def configure_pid(self, *args, **kwargs):
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
        current_temp = self._temperature_daq.get_temp(channel_n=self._daq_channel)
        new_ps_voltage = self._pid_function(current_temp)
        self._power_supply.set_set_voltage(channel=self._supply_channel, volts=new_ps_voltage)



