import time

import panel as pn
from panel.interact import interact
import simple_pid
# from device_models import SPD3303X
# from device_type import HeaterAssembly
# from device_type import Heater
# from device_models import E_Tc

pn.extension()


pid = simple_pid.PID()
pid.setpoint = 10

# ps = SPD3303X(ip4_address='10.176.42.121')
# ht = Heater(MAX_volts=25, MAX_temp=75)
# etc = E_Tc(ip4_address='10.176.42.200', board_number=0)
#
#
# pid_controller = HeaterAssembly(power_supply=ps, supply_channel=1, temperature_daq=etc, daq_channel=0,
#                                 simple_pid=pid, configure_on_startup=True)




toggle_regulate_pid = pn.widgets.Checkbox(name='Regulate On/Off')
toggle_regulate_pid2 = pn.widgets.Checkbox(name='Regulate On/Off 2')
# def toggle_value(button):
#     regulate_pid_show = 'Regulating'
#     if button == False:
#         regulate_pid_show = 'Not regulating'
#     return regulate_pid_show
#
# button_widget, button_value = interact(toggle_value, button=toggle_regulate_pid)

@interact(button=toggle_regulate_pid)
def toggle_value(button):
    if button == True:
        regulate_pid_show = 'Regulating'
        pid.auto_mode = True
    else:
        regulate_pid_show = 'Not regulating'
        pid.auto_mode = False

    return regulate_pid_show

@interact(button=toggle_regulate_pid2)
def toggle_value2(button):
    if button == True:
        regulate_pid_show = 'Regulating'
        pid.auto_mode = True
    else:
        regulate_pid_show = 'Not regulating'
        pid.auto_mode = False

    return regulate_pid_show


current_temp = 'current_temp'
set_temp = 'set_temp'
supply_ip = 'supply_ip'
set_volts = 'set_volts'
set_amps = 'set_amps'
actual_volts = 'actual_volts'
actual_amps = 'actual_amps'
volts_limit = 'volts_limit'
amps_limit = 'amps_limit'


app = pn.Column(
    pn.Row(toggle_value, toggle_value2),
    # pn.Row(button_widget, button_value),
    pn.Row(current_temp, set_temp),
    pn.Row(pid(1), actual_volts, volts_limit),
    pn.Row(set_amps, actual_amps, amps_limit)
)


app.show(threaded=True)

