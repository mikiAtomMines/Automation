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


class MCC_instrument:  # TODO: add API functions
    def __init__(self, board_number=0):
        """
        Class for an MCC device supported by their Universal Library.

        Parameters
        ----------
        board_number : int
            All MCC devices have a board number which can be configured using instacal. The instance of Web_Tc must
            match the board number of its associated device. Possible values from 0 to 99.
        """

        self._board_number = board_number
        # self._model = self.model
        # self._mac_address = self.mac_address
        # self._unique_id = self.unique_id
        # self._serial_number = self.serial_number
        # self._number_temp_channels = self.number_temp_channels
        # self._number_io_cahnnels = self.number_io_channels
        # self._number_ad_channels = self.number_ad_channels
        # self._number_da_channels = self.number_da_channels

    @property
    def board_number(self):
        return self._board_number

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

    """
    Plan for API functions:

    First get device Descriptor object using 

    """
