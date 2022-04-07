"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import time
import sys
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
    enums.TepmScale
        This object is used by the mcc universal library. Possbile values: enums.TepmScale.CELSIUS,
        enums.TepmScale.FAHRENHEIT, enums.TepmScale.KELVIN, enums.TepmScale.VOLTS, and enums.TepmScale.NOSCALE.

    """

    TempScale_dict = {
        'celsius': enums.TepmScale.CELSIUS,
        'c': enums.TepmScale.CELSIUS,

        'fahrenheit': enums.TepmScale.FAHRENHEIT,
        'f': enums.TepmScale.FAHRENHEIT,

        'kelvin': enums.TepmScale.KELVIN,
        'k': enums.TepmScale.KELVIN,

        'volts': enums.TepmScale.VOLTS,
        'volt': enums.TepmScale.VOLTS,
        'voltage': enums.TepmScale.VOLTS,
        'v': enums.TepmScale.VOLTS,

        'raw': enums.TepmScale.NOSCALE,
        'none': enums.TepmScale.NOSCALE,
        'noscale': enums.TepmScale.NOSCALE,
        'r': enums.TepmScale.NOSCALE
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


def testing_SPD3303X(power_supply):
    print(power_supply.idn)
    print(power_supply.ip4_address)
    print(power_supply.system_status)
    print()

    input('Press enter to set ch1 to 3.45V, and ch2 to 1.51V')
    power_supply.ch1_set_voltage = 3.45
    power_supply.ch2_set_voltage = 1.51
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
    time.sleep(5)
    print()

    input('press enter to turn both on for 5 seconds. Then turn both off.')
    power_supply.ch1_state = 'ON'
    power_supply.ch2_state = 'ON'
    time.sleep(5)
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
    power_supply.disconnect()
