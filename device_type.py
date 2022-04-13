"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import sys
import time

from mcculw import ul
from mcculw import enums

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
        self.reset_on_startup = reset_on_startup

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
            MAX_set_temp=None,
            MIN_set__temp=None
    ):
        """
        A heater object.

        Parameter
        ----------
        power_supply : device_models.PowerSupply
            The power supply model that is being used for controlling the electrical power going into the heater.
        supply_channel : int
            The physical power supply channel connected to the heater for controlling the electrical power.
        temperature_probe : device_models.MCC_device
            The temperature DAQ device that is being used for reading the temperature of the heater.
        daq_channel : int
            The physical DAQ channel used for taking temperature readings of the heater.
        pid : simple_pid.PID
            The PID function used to regulate the heater's temperature to the set point.
        set_temperature : float
            The desired set temperature in the same units as the temperature readings from the temperature DAQ.
        MAX_set_temp : float
            The maximum possible value for set temp. Should be based on the physical limitations of the heater.
            Should be used as a safety mechanism so the set temperature is never set higher than what the hardware
            allows.
        MIN_set_temp : float
            The minimum possible value for set temp. Analogous to MAX_temp.
        """

        self._power_supply = power_supply
        self._supply_channel = supply_channel
        self._temperature_daq = temperature_daq
        self._daq_channel = daq_channel
        self._set_temperature = set_temperature
        self._pid_function = pid_function

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

    @property  # TODO: finish later
    def pid_function(self):
        return ''

    def update_supply(self):

