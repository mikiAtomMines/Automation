import numpy as np
import time
from datetime import date
from datetime import datetime
from scipy.stats import linregress
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

from device_models import Spd3303x
from device_models import Gm3
from device_models import Series9550
from device_models import Vxm


def get_pos_b(coilname, ps, gm, vx, a, n, delta_step):
    # vx.displace(1, -16000)
    gm.autozero()
    ps.set_current_limit(1, 3)
    ps.set_current(1, a)
    ps.set_voltage(1, 20)
    ps.set_channel_state(1, True)
    time.sleep(1)

    vx.set_speed(1, 1000)
    vx.set_acceleration(1, 1)

    time_now = datetime.now().strftime('%y_%m_%d__%H_%M_%S')
    filename = 'data_coils/' + coilname + '/' + time_now + '.txt'

    file = open(filename, 'w')
    file.write(str(gm.idn) + ', average for ' + str(n) + ' data points' + '\n')
    file.write('V = ' + str(ps.get_actual_voltage(1)) + ', A = ' + str(ps.get_actual_current(1)) + '\n')
    file.write('deltaX = ' + str(delta_step) + ' steps.' + '\n')
    file.write('Starting position: tip of probe is 1.8 inches below resting surface of magnetic coil.' + '\n')

    pos = np.arange(0, 16000, delta_step)
    bout = np.asarray([])
    berr = np.asarray([])
    for pos_i in pos:
        f, sterror = gm.get_avg_zfield(n)
        bout = np.append(bout, f)
        berr = np.append(berr, sterror)
        vx.displace(1, delta_step)
        time.sleep(0.3)
        file.write(str(pos_i) + ',' + str(f) + ',' + str(sterror) + '\n')
    file.write('\n')
    file.close()

    ps.zero_all_channels()
    gm.disconnect()
    vx.disconnect()

    return pos, bout, berr


def get_ivb(ps, gm, vmax, vmin, incr, avg_t):
    """
    :param avg_t:
    :param incr:
    :param vmin:
    :param vmax:
    :param Spd3303x ps:
    :param Gm3, Series9550 gm:
    :return:
    """
    ps.set_current_limit(1, 3)
    ps.set_current(1, 3.0)
    ps.set_voltage(1, 0)
    ps.set_channel_state(1, True)

    increment = incr
    v = vmin
    vout = []
    iout = []
    bout = []
    while v <= vmax:
        ps.set_voltage(1, v)
        time.sleep(1)
        v += increment
        vout.append(ps.get_actual_voltage(1))
        iout.append(ps.get_actual_current(1))
        bout.append(gm.get_avg_zfield(t=avg_t))

    ps.zero_all_channels()

    return vout, iout, bout

def process_file(file_, n_cols):
    out = []
    for i in range(n_cols):
        out.append(np.asarray([]))

    with open(file_, 'r') as file:
        data = file.readline()
        while data != '\n':
            try:
                cols = data.split(',')
                for i in range(n_cols):
                    out[i] = np.append(out[i], float(cols[i]))
            except (ValueError, IndexError):
                pass

            data = file.readline()

    return out


def measure_v_vs_i_and_b_vs_v():
    ps = Spd3303x('10.176.42.171')
    # gm = Gm3('COM3', tmout=3)
    gm = Series9550(15)
    v, i, b = get_ivb(ps, gm, 8, 0, 0.2, 10)
    coilname = 'small1'
    time_now = datetime.now().strftime('%y_%m_%d__%H_%M_%S')
    filename = 'data_coils/' + coilname + '/' + time_now + '.txt'


    with open(filename, 'w') as file:
        file.write(gm.idn + '\n')
        for k in range(len(v)):
            file.write(str(v[k]) + ',' + str(i[k]) + ',' + str(b[k]) + '\n')
        file.write('\n')

    v, i, b = process_file(filename)

    model = linregress(i, v)
    x_model = np.asarray(i)
    y_model = model.slope*x_model + model.intercept

    with open('data_coils/officeMeasurements/resistance_meaurements.txt', 'a') as file:
        file.write(coilname + ',' + str(model.slope) + ',' + str(model.stderr) + '\n')

    plt.figure(figsize=[6, 8])
    plt.plot(i, v, 'o', label='data')
    plt.plot(x_model, y_model, label='model')
    plt.legend()
    plt.show()

    model2 = linregress(v, b)
    x_model2 = np.asarray(v)
    y_model2 = model2.slope*x_model2 + model2.intercept

    with open('data_coils/officeMeasurements/field_meaurements.txt', 'a') as file:
        file.write(coilname + ',' + str(model2.slope) + ',' + str(model2.stderr) + '\n')

    plt.figure(figsize=[6, 8])
    plt.plot(v, b, 'o', label='data')
    plt.plot(x_model2, y_model2, label='model')
    plt.legend()
    plt.show()


def get_field_fit(pos, b, berr):
    def coil_field_z_axis(z, N, B, F):
        """

        :param z: steps
        :param A: scale mu_0 / 2pi
        :param N: center position of coils in meter
        :param C: side length of coil in meters
        :param D: current in amps
        :return:
        """

        # C = 0.667893  # meters for small coil
        C = 0.7028942  # meters for medium coil
        # C = 0.7378954  # meters for large coil

        D = 2.3 * N  # amps
        meters = (z - F) * B  # convert steps to meters

        x = meters
        f = 2e-7*D*C**2
        s = 1 / (x**2 + (C**2)/4)
        t = 1 / np.sqrt(x**2 + (C**2)/2)

        return f*s*t*10000  # tesla to gauss

    popt, pcov = curve_fit(coil_field_z_axis, pos, b, p0=[60, 6.35e-6, 6260], bounds=([58, 0, 5500], [62, 1e-5, 6500]))
    pos_model = np.linspace(pos[0], pos[-1], 1000)
    b_model = coil_field_z_axis(pos_model, *popt)

    print(popt)

    residuals = b - coil_field_z_axis(pos, *popt)
    return pos_model, b_model, residuals

def main():
    # ps = Spd3303x('10.176.42.171')
    # # gm = Gm3('COM3', tmout=3)
    # gm = Series9550(15)
    # vx = Vxm('COM4')

    coilname = 'medium1'
    file_name = '22_07_06__18_11_05.txt'

    # pos, b, berr = get_pos_b(coilname, ps, gm, vx, 2.3, 10, 100)

    file_full = 'data_coils/' + coilname + '/' + file_name
    pos, b, berr = process_file(file_full, 3)
    pos_model, b_model, residuals = get_field_fit(pos, b, berr)

    coilname2 = 'medium2'
    file_name2 = '22_07_06__18_33_37.txt'
    file_full2 = 'data_coils/' + coilname2 + '/' + file_name2
    pos2, b2, berr2 = process_file(file_full2, 3)
    pos_model2, b_model2, residuals2 = get_field_fit(pos2, b2, berr2)

    plt.figure(figsize=[6, 8])
    plt.plot(pos, b, '.-', label='data')
    plt.plot(pos_model, b_model, '-', label='model')

    plt.plot(pos2, b2, '.-', label='data2')
    plt.plot(pos_model2, b_model2, '-', label='model2')
    plt.legend()
    plt.show()

    plt.figure(figsize=[6, 8])
    plt.plot(pos, residuals, '.-', label='data')

    plt.plot(pos2, residuals2, '.-', label='data2')
    plt.legend()
    plt.show()


main()
