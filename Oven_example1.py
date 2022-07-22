import matplotlib.pyplot as plt
import matplotlib.animation as anim
import time

from automation.assemblies import Oven


def live_plot(oven, x_size=10):
    """
    plots current temp and ps_volts
    :param Oven oven: Oven object to control.
    :param int x_size: number of data points per frame
    """
    t = [0.0] * x_size
    temp_asm = {}
    setpoint_asm = {}
    for name in oven.get_assemblies_keys():
        temp_asm[name] = [0.0]*x_size
        setpoint_asm[name] = [0.0]*x_size

    fig = plt.figure()
    ax = plt.subplot(111)

    def animate(i):
        for name in oven.get_assemblies_keys():
            temp = temp_asm[name]
            setpoint = setpoint_asm[name]
            temp.pop(0)
            temp.append(oven.get_daq_temp(name))
            setpoint.pop(0)
            setpoint.append(oven.get_pid_setpoint(name))

        t.pop(0)
        t.append(i)

        ax.cla()
        for name in oven.get_assemblies_keys():
            temp = temp_asm[name]
            setpoint = setpoint_asm[name]
            ax.plot(t, temp, '.-', label=name)
            ax.plot(t, setpoint, '--', label=name)


    ani = anim.FuncAnimation(fig, animate, interval=2000)
    plt.show()


def main():
    o_ip = '10.176.42.185'  # connect to BeagleBoneBlack
    oven = Oven(o_ip)

    print(oven.idn)  # assemblies names with respective power supplies and daqs
    assemblies = oven.get_assemblies_keys()
    for name in assemblies:
        print('   ', name)
        print('pid limits: ', oven.get_pid_limits(name))
        print('heater MAX temp: ', oven.get_heater_MAX_temp(name))
        print('heater MAX volts: ', oven.get_heater_MAX_volts(name))
        print('heater MAX amps: ', oven.get_heater_MAX_current(name))

    set_temp = 60
    for name in assemblies:  # set the set temp, start oven regulation.
        oven.ready_assembly(name)
        oven.set_pid_setpoint(name, set_temp)
        print(name + ' pid set to ' + str(set_temp))
        oven.set_pid_regulation(name, True)

    for i in range(10):  # for 10 minutes, print temp, volts, and amps.
        print('temp: ', oven.get_daq_temp(assemblies[0]))
        print('volts: ', oven.get_supply_actual_voltage(assemblies[0]))
        print('amps: ', oven.get_supply_actual_current(assemblies[0]))
        time.sleep(10)

    oven.disconnect()  # disconnect from BBB.
    print('oven disconnected. Regulation should still be on and working.')
    time.sleep(2*60)

    oven = Oven(o_ip)  # connect to BBB.
    print('oven connected. Regulation should still be on and working.')

    set_temp = 45
    for name in assemblies:
        oven.set_pid_setpoint(name, set_temp)
        oven.set_pid_kpro(name, 0.2)
        print(name + ' pid set to ' + str(set_temp))
        oven.set_pid_regulation(name, True)

    live_plot(oven)

    for name in assemblies:
        oven.set_pid_regulation(name, False)

main()