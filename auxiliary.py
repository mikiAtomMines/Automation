"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import time
import sys
import matplotlib.pyplot as plt
import numpy
from mcculw import enums


error_count = 0


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
        'volt': enums.TempScale.VOLTS,
        'voltage': enums.TempScale.VOLTS,
        'v': enums.TempScale.VOLTS,

        'raw': enums.TempScale.NOSCALE,
        'none': enums.TempScale.NOSCALE,
        'noscale': enums.TempScale.NOSCALE,
        'r': enums.TempScale.NOSCALE
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


def test_GM3(gaussmeter):
    # for i in range(100):
    #     a = gaussmeter.properties
    # print()
    # for i in range(100):
    #     a = gaussmeter.settings
    # print()
    # for i in range(100):
    #     a = gaussmeter.get_instantenous_data()

    print(gaussmeter.properties)

    data = [gaussmeter.get_instantenous_data_t0()]

    # print()
    # time_initial = time.time()
    # while time.time() - time_initial < t:
    #     point = gaussmeter.get_instantenous_data()
    #     print(point)
    #     data.append(point)

    for i in range(100):
        point = gaussmeter.get_instantenous_data()
        print(point)
        data.append(point)

    print(error_count)
    gaussmeter.write(bytes.fromhex('04'*6))

    gaussmeter.command('KILL_ALL_PROCESS')
    gaussmeter.close()


# -----------------------------------------------------------------------------------
# Power supplies
# -----------------------------------------------------------------------------------
def channel_syntax(self, power_supply, channel_num):
    chan_syntax = {
        'spd3303x': 'CH'
    }

    try:
        return chan_syntax[power_supply] + channel_num
    except KeyError:
        print('ERROR: Invalid power supply. ')
        sys.exit()


def testing_SPD3303X(power_supply):
    print()
    print(power_supply.idn)
    print(power_supply.ip4_address)
    print(power_supply.system_status)
    print()

    input('Press enter to set ch1 to 3.45V, and ch2 to 1.51V')
    power_supply.ch1_set_voltage = 3.45
    power_supply.ch2_set_voltage = 1.51
    power_supply.ch1_set_current = 0.005
    power_supply.ch2_set_current = 0.005
    print('CH1 and CH2 set voltages are:', power_supply.ch1_set_voltage, power_supply.ch2_set_voltage)
    print('CH1 and CH2 set currents are:', power_supply.ch1_set_current, power_supply.ch2_set_current)
    print('CH1 and CH2 actual voltages are:', power_supply.ch1_actual_voltage, power_supply.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', power_supply.ch1_actual_current, power_supply.ch2_actual_current)
    print()

    input('Press enter to turn ch1 on, wait 5 sec, then off. Repeat for ch2.')
    power_supply.ch1_state = 'ON'
    print('CH1 state is:', str(power_supply.ch1_state))
    time.sleep(5)
    power_supply.ch1_state = 'OFF'
    print('CH1 state is:', str(power_supply.ch1_state))
    power_supply.ch2_state = 'ON'
    print('CH2 state is:', str(power_supply.ch2_state))
    time.sleep(5)
    power_supply.ch2_state = 'OFF'
    print('CH2 state is:', str(power_supply.ch2_state))
    print()

    input('press enter to turn both on for 5 seconds. Then turn both off.')
    power_supply.ch1_state = 'ON'
    power_supply.ch2_state = 'ON'
    print('CH1 and CH2 states are:', str(power_supply.ch1_state), str(power_supply.ch2_state))
    print('CH1 and CH2 set voltages are:', power_supply.ch1_set_voltage, power_supply.ch2_set_voltage)
    print('CH1 and CH2 set currents are:', power_supply.ch1_set_current, power_supply.ch2_set_current)
    print('CH1 and CH2 actual voltages are:', power_supply.ch1_actual_voltage, power_supply.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', power_supply.ch1_actual_current, power_supply.ch2_actual_current)
    time.sleep(5)
    power_supply.ch1_state = 'OFF'
    power_supply.ch2_state = 'OFF'
    print('CH1 and CH2 states are:', str(power_supply.ch1_state), str(power_supply.ch2_state))
    print('CH1 and CH2 set voltages are:', power_supply.ch1_set_voltage, power_supply.ch2_set_voltage)
    print('CH1 and CH2 set currents are:', power_supply.ch1_set_current, power_supply.ch2_set_current)
    print('CH1 and CH2 actual voltages are:', power_supply.ch1_actual_voltage, power_supply.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', power_supply.ch1_actual_current, power_supply.ch2_actual_current)
    print('CH1 and CH2 voltage limits are:', power_supply.ch1_voltage_limit, power_supply.ch2_voltage_limit)
    print('CH1 and CH2 current limits are:', power_supply.ch1_current_limit, power_supply.ch2_current_limit)
    print('MAX voltage and current limits are:', power_supply.MAX_voltage_limit, power_supply.MAX_current_limit)
    power_supply.reset_channels()
    print('CH1 and CH2 actual voltages are:', power_supply.ch1_actual_voltage, power_supply.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', power_supply.ch1_actual_current, power_supply.ch2_actual_current)
    power_supply.disconnect()


def simple_plot(file):
    file = open(file, 'r')
    header_size = 5
    for i in range(header_size):
        file.readline()

    data = file.readlines()
    time_list = []
    actual_temp_list = []
    set_temp_list = []
    voltage_list = []

    for str_ in data:
        time_, actual_temp, set_temp, voltage = [float(a) for a in str.split()]

        time_list.append(time_)
        actual_temp_list.append(actual_temp)
        set_temp_list.append(set_temp)
        voltage_list.append(voltage)

    plt.plot(time_list, actual_temp_list)

    plt.show()




