"""
Created on Tuesday, April 19, 2022
@author: Sebastian Miki-Silva
"""
import time

import auxiliary
import device_models
import device_type
import simple_pid as pid


def main():
    ps = device_models.SPD3303X(ip4_address='10.176.42.121')
    ps.ch1_state = 'off'
    ps.ch1_set_current = 1
    daq = device_models.Web_Tc()
    pid_func = pid.PID(Kp=3, Ki=0.1, Kd=0, setpoint=100, output_limits=(0, 30))

    # auxiliary.testing_SPD3303X(ps)
    print(daq.temp_ch0)

    heater = device_type.HeaterAssembly(
        power_supply=ps,
        supply_channel=1,
        temperature_daq=daq,
        daq_channel=0,
        set_temperature=50,
        pid_function=pid_func,
        MAX_set_temp=200,
        MIN_set_temp=0,
        configure_on_startup=False,
    )

    heater.live_plot(x_size=50)

    ps.reset_channels()
    time.sleep(2)


if __name__ == '__main__':
    main()
