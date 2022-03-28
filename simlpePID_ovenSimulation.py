import simple_pid as pid
import numpy as np
import time
import matplotlib.pyplot as plt

#######################################################################################################################
# Heating and cooling functions
#######################################################################################################################


def heating(P, rh, dt):
    return rh*P*dt


def cooling(T, T_env, rc, dt):
    return rc*(T-T_env)*dt


def testing_class():
    # Simulation parameters
    # ==================================================================================================================

    set_temperature = 200  # Celsius
    duration = 20  # seconds of total calculations
    interval = 0.2  # seconds between data points

    # Physical Constants
    # ==================================================================================================================
    T0 = 30  # Celsius
    T_env = 25  # Celsius
    rc = 0.5
    rh = 1

    # PID controller
    # ==================================================================================================================

    ovenPower = pid.PID(1, 3, 0.10, setpoint=30)
    ovenPower.setpoint = set_temperature
    ovenPower.sample_time = 0.01  # seconds
    ovenPower.output_limits = (0, 500)

    temp_array = np.asarray([])
    setpoints_array = np.asarray([])
    time_array = np.asarray([])
    power_array = np.asarray([])

    # Calculating heating response to PID output
    # ==================================================================================================================
    T = T0
    initial_time = time.time()
    previous_time = time.time() - initial_time
    current_time = previous_time

    while current_time < duration:
        # if current_time > 5:
        #     ovenPower.setpoint = set_temperature

        if current_time > 1.5 and current_time < 10:
            ovenPower.auto_mode = False

        if current_time > 10:
            ovenPower.auto_mode = True

        current_time = time.time() - initial_time
        dt = current_time - previous_time
        previous_time = current_time

        P = ovenPower(T)
        T += heating(P, rh, dt)
        T -= cooling(T, T_env, rc, dt)

        temp_array = np.append(temp_array, T)
        setpoints_array = np.append(setpoints_array, ovenPower.setpoint)
        time_array = np.append(time_array, current_time)
        power_array = np.append(power_array, P)

        time.sleep(interval)

    plt.plot(time_array, setpoints_array)
    plt.plot(time_array, temp_array)
    # plt.show()

    plt.plot(time_array, power_array)
    plt.show()

    print(temp_array)
    print()
    print(power_array)


def testing_dt_parameter():
    """
    For simulations, we can create a "time" array before-hand with an arbitrary dt. We can then use this dt as a
    parameter when calling the PID object. The object will recognize the parameter and will use it for the time
    stamps and calcualtions instead of measuring a real time value. This way we can create 1000 data points in less
    than a second.
    :return:
    """

    tf = 100  # seconds
    n = 1000

    time_array = np.linspace(0, tf, n)
    my_dt = tf / n

    # simulation things
    # ===================================================================================================================

    set_temperature = 200  # Celsius
    # duration = 20  # seconds of total calculations
    # interval = 0.2  # seconds between data points

    # Physical Constants
    # ====================================================================================================================
    T0 = 30  # Celsius
    T_env = 25  # Celsius
    rc = 0.05
    rh = 0.1

    #   PID controller
    #   ==================================================================================================================

    ovenPower = pid.PID(10, 3, 1, setpoint=30)
    ovenPower.setpoint = set_temperature
    ovenPower.sample_time = 0.01  # seconds
    ovenPower.output_limits = (0, 500)

    temp_array = np.asarray([])
    setpoints_array = np.asarray([])
    power_array = np.asarray([])

    #   Calculating heating response to PID output
    #   =================================================================================================================
    T = T0
    current_time = 0
    for t in time_array:
        current_time = t

        if current_time > 5:
            ovenPower.setpoint = set_temperature

        # if t > 1.5 and current_time < 10:
        #     ovenPower.auto_mode = False
        #
        # if t > 10:
        #     ovenPower.auto_mode = True


        previous_time = current_time

        P = ovenPower(T, dt=my_dt)
        T += heating(P, rh, my_dt)
        T -= cooling(T, T_env, rc, my_dt)

        temp_array = np.append(temp_array, T)
        setpoints_array = np.append(setpoints_array, ovenPower.setpoint)
        power_array = np.append(power_array, P)

        # time.sleep(interval)

    plt.plot(time_array, setpoints_array)
    plt.plot(time_array, temp_array)
    # plt.show()

    plt.plot(time_array, power_array)
    plt.show()

    # print(temp_array)
    # print()
    # print(power_array)


def main():
    testing_dt_parameter()

if __name__ == '__main__':
    main()
