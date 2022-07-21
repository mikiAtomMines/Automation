import matplotlib.pyplot as plt
import matplotlib.animation as anim
import time

from automation.assemblies import Oven


def live_plot(oven, x_size=10):
    """
    plots current temp and ps_volts
    :param x_size: number of data points per frame
    """
    t = [0.0] * x_size
    temp_asm = {}
    setpoint_asm = {}
    for name in oven.get_assemblies_keys():
        temp_asm[name] = []*x_size
        setpoint_asm[name] = []*x_size

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
    oven = Oven('10.176.42.185')  # connect to BeagleBoneBlack

    print(oven.idn)  # assemblies names with respective power supplies and daqs
    for name in oven.get_assemblies_keys():
        print('   ', name)
        print(oven.get_pid_limits(name))
        print(oven.get_heater_MAX_temp(name))
        print(oven.get_heater_MAX_volts(name))
        print(oven.get_heater_MAX_current(name))

    set_temp = 60
    for name in oven.get_assemblies_keys():
        oven.ready_assembly(name)
        oven.set_pid_setpoint(name, set_temp)
        print(name + ' pid set to ' + str(set_temp))
        oven.set_pid_regulation(name, True)

    for i in range(10):
        print(oven.get_daq_temp(oven.get_assemblies_keys()[0]))
        time.sleep(60)

    oven.disconnect()
    print('oven disconnected. Regulation should still be on and working.')
    time.sleep(2*60)

    oven = Oven('10.176.42.185')
    print('oven connected. Regulation should still be on and working.')

    live_plot(oven)


main()