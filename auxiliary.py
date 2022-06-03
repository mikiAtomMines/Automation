"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import time
import sys
import matplotlib.pyplot as plt
try:
    from mcculw import enums
except ModuleNotFoundError:
    pass

error_count = 0

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
# def channel_syntax(self, power_supply, channel_num):
#     chan_syntax = {
#         'spd3303x': 'CH'
#     }
#
#     try:
#         return chan_syntax[power_supply] + channel_num
#     except KeyError:
#         print('ERROR: Invalid power supply. ')
#         sys.exit()


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


def test_Mr50040(mr):
    print(mr.get_actual_voltage())
    print(mr.get_actual_current())
    print(mr.set_current(amps=0.2))
    print(mr.set_voltage(volts=2))
    print(mr.set_channel_state(state=True))
    print(mr.get_actual_voltage())
    print(mr.get_actual_current())
    print(mr.get_actual_power())
    print(mr.set_current(amps=0))
    print(mr.set_voltage(volts=0))

# def testing_HeaterAssembly():
#     ps = device_models.SPD3303X(ip4_address='10.176.42.121')
#     ps.ch1_state = 'on'
#     ps.ch1_set_current = 1
#     daq = device_models.Web_Tc()
#     pid_func = pid.PID(Kp=3, Ki=0.1, Kd=0, setpoint=100, output_limits=(0, 30))
#
#     print(daq.temp_ch0)
#
#     heater = device_type.HeaterAssembly(
#         power_supply=ps,
#         supply_channel=1,
#         temperature_daq=daq,
#         daq_channel=0,
#         set_temperature=50,
#         pid_function=pid_func,
#         MAX_set_temp=200,
#         MIN_set_temp=0,
#         configure_on_startup=False,
#     )
#
#     heater.live_plot(x_size=50)
#
#     ps.reset_channels()
#     time.sleep(2)


def testing_model8742(controller):
    """
    :param device_models.Model8742 controller:
    :return:
    """
    print(controller.idn)
    controller.displace(chan=1, dis=1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    controller.displace(chan=1, dis=1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    # controller.set_origin(chan=1)
    # print('set_origin here')
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    controller.displace(chan=1, dis=-1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    controller.displace(chan=1, dis=-1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    controller.set_set_position(chan=1, position=0)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    controller.displace(chan=1, dis=-2000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    # controller.set_origin(chan=1)
    # print('instant', controller.get_instant_position(chan=1))
    # print('set    ', controller.get_set_position(chan=1))

    print()
    print('testing velocity')
    print()
    controller.set_velocity(chan=1, vel=200)
    controller.soft_stop(chan=1)
    controller.set_set_position(chan=1, position=1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    controller.set_set_position(chan=1, position=-1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    controller.set_set_position(chan=1, position=0)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_set_position(chan=1))
    controller.set_velocity(chan=1, vel=1000),


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

    for i in data:
        time_, actual_temp, set_temp, voltage = [float(a) for a in str.split()]

        time_list.append(time_)
        actual_temp_list.append(actual_temp)
        set_temp_list.append(set_temp)
        voltage_list.append(voltage)

    plt.plot(time_list, actual_temp_list)

    plt.show()

