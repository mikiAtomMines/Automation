"""
Created on Tuesday, April 5, 2022

@author: Sebastian Miki-Silva
"""

import sys
import time

import mcculw.ul
from mcculw import ul
from mcculw.enums import TempScale
from mcculw.enums import TInOptions
from mcculw.enums import FunctionType
from mcculw.enums import InfoType
from mcculw.enums import BoardInfo
from mcculw.device_info import DaqDeviceInfo


def get_TempScale_unit(units):
    """
    Returns the associated mcculw.enums.TempScale object with the desired temperature unit.

    Parameters
    ----------
    units : string
        the units in which the temperature is shown. Possible values (not case-sensitive):
        for Celsius                 celsius,               c
        for Fahrenheit              fahrenheit,            f
        for Kelvin                  kelvin,                k
        for calibrated voltage      volts, volt, voltage,  v
        for uncalibrated voltage    raw, none, noscale     r

    Returns
    -------
    TempScale
        This object is used by the mcc universal library. Possbile values: TempScale.CELSIUS,
        TempScale.FAHRENHEIT, TempScale.KELVIN, TempScale.VOLTS, and TempScale.NOSCALE.

    """

    TempScale_dict = {
        'celsius': TempScale.CELSIUS,
        'c': TempScale.CELSIUS,

        'fahrenheit': TempScale.FAHRENHEIT,
        'f': TempScale.FAHRENHEIT,

        'kelvin': TempScale.KELVIN,
        'k': TempScale.KELVIN,

        'volts': TempScale.VOLTS,
        'volt': TempScale.VOLTS,
        'voltage': TempScale.VOLTS,
        'v': TempScale.VOLTS,

        'raw': TempScale.NOSCALE,
        'none': TempScale.NOSCALE,
        'noscale': TempScale.NOSCALE,
        'r': TempScale.NOSCALE
    }

    try:
        out = TempScale_dict[units.lower()]
        return out
    except KeyError:
        print('\nERROR: input string "', units, '" for units is not a valid input. Possible inputs:')
        print('    "celsius"                    or    "c"    ')
        print('    "fahrenheit"                 or    "f"    ')
        print('    "kelvin"                     or    "k"    ')
        print('    "volts", volt", "voltage"    or    "v"    ')
        print('    "raw", "none", "noscale"     or    "r"    ')

        sys.exit()


class Web_Tc:
    def __init__(
            self,
            ip4_address=None,
            port=54211,
            board_number=0,
            io_number_of_channels=8,
            default_units='celsius'
    ):
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
        io_number_of_channels : int
            The number of physical digital input/output channels. Currently unused. TODO: CHECK for this model.
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

        self._ip4_address = ip4_address
        self._port = port
        self._board_number = board_number
        self._number_temp_channels = self.number_temp_chanels
        self._number_io_channels = io_number_of_channels
        self._default_units = default_units

    @property
    def model(self):
        return ul.get_board_name(self._board_number)

    @property
    def mac_address(self):
        return ul.get_config_string(
            info_type=InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=0,
            config_item=BoardInfo.DEVMACADDR,
            max_config_len=255
        )

    @property
    def serial_number(self):
        return ul.get_config_string(
            info_type=InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=0,
            config_item=BoardInfo.DEVSERIALNUM,
            max_config_len=255
        )

    @property
    def number_temp_chanels(self):
        return ul.get_config(
            info_type=InfoType.BOARDINFO,
            board_num=self._board_number,
            dev_num=0,
            config_item=BoardInfo.NUMTEMPCHANS
        )

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

        filter_on_off = TInOptions.FILTER
        if not averaged:
            filter_on_off = TInOptions.NOFILTER

        if units is None:
            units = self._default_units

        out = ul.t_in(
            board_num=self._board_number,
            channel=channel_n,
            scale=get_TempScale_unit(units.lower()),
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
        for channel in range(self._ai_number_of_channels):
            try:
                out.append(self.get_temp(channel_n=channel))
            except mcculw.ul.ULError:
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
                out.append(self.get_temp(channel_n=channel))
            except mcculw.ul.ULError:
                print('ERROR: Could not read from channel ' + str(channel) + '. Appending None.')
                out.append(None)
                continue

        return out


def main():
    """
    main

    Parameters
    ----------
    input : type
        Python string containing the query command. Dependent on each individual device.

    Returns
    -------
    type
        Descrition.

    """
    print()
    web_tc_1 = Web_Tc(board_number=0)
    print()
    print(web_tc_1.info)
    print(web_tc_1.get_temp_scan(high_channel=4))
    print(web_tc_1.get_temp_all_channels())


    # for i in range(100):
    #     print(web_tc_1.get_temp(averaged=True))
    #     time.sleep(1)


if __name__ == '__main__':
    main()
