"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import time
import auxiliary
import device_type
import device_models
import simple_pid as pid
import numpy as np

# TODO: Make a PID_controller class that has power supplies and web_tc as attributes.
def test_TC():
    web_tc = device_models.Web_Tc()
    data = []

    file = open('data.txt', 'w')
    file.write('Created on Thursday, April 7, 2022\n')
    file.write('@author: Sebastian Miki-Silva\n')
    file.write('\n')
    file.write('Temperature (C)')

    while True:
        point = web_tc.temp_ch0
        file.write(str(point) + '\n')
        print(point)
        time.sleep(1)


def main():
    web_tc = device_models.Web_Tc(board_number=0)
    supply = device_models.SPD3303X(ip4_address='10.176.42.121', port=5025, reset_on_startup=True)
    supply.set_both_channels_current_limit(0.25)
    supply.set_both_channels_voltage_limit(25)
    supply.ch1_state = 'on'
    supply.ch1_set_current = 0.205

    set_temp = 45  # Celsius

    pid_voltage = pid.PID(3, 0.2, 0, setpoint=0)
    pid_voltage.output_limits = (0, supply.ch1_voltage_limit)

    duration = 0  # seconds

    file = open('data.txt', 'w')
    file.write('Created on Thursday, April 7, 2022\n')
    file.write('@author: Sebastian Miki-Silva\n')
    file.write('\n')
    file.write(f'{"Time (s)":<25}{"Actual temperature (C)":<25}{"Set temperature (V)":<25}{"PID voltage (V)":<25}')
    file.write('\n')

    time_i = time.time()
    current_time = time.time() - time_i
    while True:
        if current_time > duration:
            pid_voltage.setpoint = set_temp

        current_time = time.time() - time_i

        actual_temp = web_tc.temp_ch0
        oven_set_voltage = pid_voltage(actual_temp)

        supply.ch1_set_voltage = oven_set_voltage

        print(f'{str(current_time):<25}'
              + f'{str(actual_temp):<25}'
              + f'{str(pid_voltage.setpoint):<25}'
              + f'{str(oven_set_voltage):<25}'
              )

        file.write(f'{str(current_time):<25}'
                   + f'{str(actual_temp):<25}'
                   + f'{str(pid_voltage.setpoint):<25}'
                   + f'{str(oven_set_voltage):<25}'
                   + '\n'
                   )

        time.sleep(1)

    file.close()


if __name__ == '__main__':
    main()
