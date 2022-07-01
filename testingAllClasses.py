"""
Created on Tuesday, April 19, 2022
@author: Sebastian Miki-Silva
"""
import time

import auxiliary
import device_models
from device_models import Mr50040
from device_models import Series9550
from device_models import Spd3303x
from device_models import Vxm

def testing_GM3(gaussmeter):
    # for i in range(100):
    #     a = gaussmeter.properties
    # print()
    # for i in range(100):
    #     a = gaussmeter.settings
    # print()
    # for i in range(100):
    #     a = gaussmeter.get_instantenous_data()

    print(gaussmeter.idn)

    data = [gaussmeter.get_instantenous_data_t0()]

    # print()
    # time_initial = time.time()
    # while time.time() - time_initial < t:
    #     point = gaussmeter.get_instantenous_data()
    #     print(point)
    #     data.append(point)

    for i in range(100):
        point = gaussmeter.get_datapoint()
        print(point)
        data.append(point)

    print(error_count)
    gaussmeter.write(bytes.fromhex('04'*6))

    gaussmeter.command('KILL_ALL_PROCESS')
    gaussmeter.close()


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
    power_supply.zero_all_channels()
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
    print('set    ', controller.get_setpoint_position(chan=1))
    controller.displace(chan=1, dis=1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_setpoint_position(chan=1))
    # controller.set_origin(chan=1)
    # print('set_origin here')
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_setpoint_position(chan=1))
    controller.displace(chan=1, dis=-1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_setpoint_position(chan=1))
    controller.displace(chan=1, dis=-1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_setpoint_position(chan=1))
    controller.set_position(chan=1, position=0)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_setpoint_position(chan=1))
    controller.displace(chan=1, dis=-2000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_setpoint_position(chan=1))
    # controller.set_origin(chan=1)
    # print('instant', controller.get_instant_position(chan=1))
    # print('set    ', controller.get_set_position(chan=1))

    print()
    print('testing velocity')
    print()
    controller.set_velocity(chan=1, vel=200)
    controller.soft_stop(chan=1)
    controller.set_position(chan=1, position=1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_setpoint_position(chan=1))
    controller.set_position(chan=1, position=-1000)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_setpoint_position(chan=1))
    controller.set_position(chan=1, position=0)
    print('instant', controller.get_instant_position(chan=1))
    print('set    ', controller.get_setpoint_position(chan=1))
    controller.set_velocity(chan=1, vel=1000),


def testing_ETc(daq):
    print(daq.temp_ch0)
    print(daq.number_temp_channels)
    print(daq.number_da_channels)
    print(daq.number_ad_channels)
    print(daq.number_io_channels)
    daq.set_thermocuple_type(channel=0, new_tc_type='K')
    print(daq.get_thermocouple_type(channel=0))
    daq.set_thermocuple_type(channel=0, new_tc_type='K')
    print(daq.get_thermocouple_type(channel=0))

    # daq.config_io_channel(0, 'out')
    # daq.set_bit(chan=0, out=0)
    # time.sleep(2)
    # daq.set_bit(chan=0, out=1)
    # time.sleep(5)
    # daq.set_bit(chan=0, out=0)

    daq.config_io_byte(direction='out')
    daq.set_byte(val=0)
    print(daq.get_byte())


def testing_Series9550(gm):
    print(gm.get_zfield())
    gm.autozero()
    gm.disconnect()


def testing_Vxm(v):
    v.set_origin(1)
    v.set_speed(1, 1000)
    v.set_acceleration(1, 1)
    v.displace(1, 1000)
    # v.set_position(1, 0)

    v.disconnect()

def testing_RGA(rga):
    rga.flush_buffers()
    print(rga.idn)
    rga.flush_buffers()

    print(rga._query_('EC?'))
    print(rga._query_('EF?'))
    print('0\n\r')
    print(rga._query_('EM?'))
    print(rga._query_('EQ?'))
    print(rga._query_('ED?'))
    print(rga._query_('EP?'))
    print('0\n\r')

    print('setting RGA filament on')
    print(rga.set_ionizer_filament_state(state='on'))
    print('RGA filament is on')
    print('filament current:')
    print(rga.get_ionizer_filament_current())
    time.sleep(5)
    print()

    print('setting RGA filament off')
    print(rga.set_ionizer_filament_state(state='off'))
    print('RGA filament is off')
    print('filament current:')
    print(rga.get_ionizer_filament_current())
    print(rga.get_status())

    print(rga._command_(cmd='FL'))
    print(rga.status_byte)


def main():
    gm = Series9550(15)
    ps = Spd3303x('10.176.42.171', zero_on_startup=False)
    vx = Vxm('COM4')

    testing_Vxm(vx)

    pass


if __name__ == '__main__':
    main()
