import simple_pid as pid
import numpy as np
import time
import matplotlib.pyplot as plt


#######################################################################################################################
# Physical Constants
#######################################################################################################################

T0 = 30  # Celsius
T_env = 25  # Celsius
rc = 0.5
rh = 1



#######################################################################################################################
# Simulation parameters
#######################################################################################################################

set_temperature = 200  # Celsius
duration = 20  # seconds of total calculations
interval = 0.2  # seconds between data points



#######################################################################################################################
# Heating and cooling functions
#######################################################################################################################

def heating(P, dt):
    return rh*P*dt


def cooling(T, T_env, rc, dt):
    return rc*(T-T_env)*dt



#######################################################################################################################
# Setting PID output and arrays. Interpret it as oven power
#######################################################################################################################

ovenPower = pid.PID(1, 3, 0.10, setpoint=30)
ovenPower.setpoint = 0
ovenPower.sample_time = 0.01  # seconds
ovenPower.output_limits = (0, 100)

temp_array = np.asarray([])
setpoints_array = np.asarray([])
time_array = np.asarray([])
power_array = np.asarray([])



#######################################################################################################################
# Calculating heating response to PID output
#######################################################################################################################
T = T0
initial_time = time.time()
previous_time = time.time() - initial_time
current_time = previous_time

while current_time < duration:
    if current_time > 5:
        ovenPower.setpoint = 200

    current_time = time.time() - initial_time
    dt = current_time - previous_time
    previous_time = current_time

    P = ovenPower(T)
    T += heating(P, dt)
    T -= cooling(T, T_env, rc, dt)


    temp_array = np.append(temp_array, T)
    setpoints_array = np.append(setpoints_array, ovenPower.setpoint)
    time_array = np.append(time_array, current_time)
    power_array = np.append(power_array, P)

    time.sleep(interval)



#######################################################################################################################
# Plot and print output
#######################################################################################################################
plt.plot(time_array, setpoints_array)
plt.plot(time_array, temp_array)
plt.show()

print(temp_array)
print()
print(power_array)
