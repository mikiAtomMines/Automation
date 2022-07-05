import numpy as np
import time
from datetime import date
from datetime import datetime
from scipy.stats import linregress
import matplotlib.pyplot as plt

from device_models import Spd3303x
from device_models import Gm3
from device_models import Series9550
from device_models import Vxm


def get_pos_b(ps, gm, vx, v, n, st_incr):
    # vx.displace(1, -16000)
    gm.autozero()
    ps.set_current_limit(1, 3)
    ps.set_current(1, 3.0)
    ps.set_voltage(1, 0)
    ps.set_voltage(1, v)
    ps.set_channel_state(1, True)
    time.sleep(1)

    vx.set_speed(1, 1000)
    vx.set_acceleration(1, 1)

    pos = np.arange(0, 16000, st_incr)
    bout = np.asarray([])
    for i in pos:
        bout = np.append(bout, gm.get_avg_zfield(n))
        vx.displace(1, st_incr)
        time.sleep(0.3)

    ps.zero_all_channels()
    gm.disconnect()
    vx.disconnect()

    return pos, bout


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

def process_file(file_):
    v, i, b = [], [], []
    with open(file_, 'r') as file:
        file.readline()
        data = file.readline()
        while data != '\n':
            v_i, i_i, b_i = data.split(',')
            v.append(float(v_i))
            i.append(float(i_i))
            b.append(float(b_i))
            data = file.readline()

    return v, i, b


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


def measure_b_vs_z():
    ps = Spd3303x('10.176.42.171')
    # gm = Gm3('COM3', tmout=3)
    gm = Series9550(15)
    vx = Vxm('COM4')
    n = 10
    incr = 100
    pos, b = get_pos_b(ps, gm, vx, 8, n, incr)
    coilname = 'small2'
    time_now = datetime.now().strftime('%y_%m_%d__%H_%M_%S')
    filename = 'data_coils/' + coilname + '/' + time_now + '.txt'

    with open(filename, 'w') as file:
        file.write(gm.idn + ', average for ' + str(n) + ' datapoints' + '\n')
        file.write('V = ' + str(ps.get_actual_voltage(1)) + ', A = ' + str(ps.get_actual_current(1)) + '\n')
        file.write('deltaX = ' + str(incr) + ' steps.' + '\n')
        file.write('Starting position: tip of probe is touching table surface.')
        for k in range(len(pos)):
            file.write(str(pos[k]) + ',' + str(b[k]) + '\n')
        file.write('\n')

    plt.figure(figsize=[6, 8])
    plt.plot(pos, b, 'o-', label='data')
    plt.legend()
    plt.show()


measure_b_vs_z()
