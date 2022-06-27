import numpy as np
import time
from scipy.stats import linregress
import matplotlib.pyplot as plt

from device_models import Spd3303x
from device_models import GM3


def get_ivb(ps, gm):
    """
    :param Spd3303x ps:
    :param GM3 gm:
    :return:
    """
    ps.set_current_limit(1, 2.3)
    ps.set_current(1, 2.0)
    ps.set_voltage(1, 0)
    ps.set_channel_state(1, True)

    vmax = 8
    increment = 0.2
    v = 0
    vout = []
    iout = []
    bout = []
    while v < vmax:
        ps.set_voltage(1, v)
        time.sleep(1)
        v += increment
        vout.append(ps.get_actual_voltage(1))
        iout.append(ps.get_actual_current(1))
        bout.append(get_avg_field(gm, t=3))

    ps.zero_all_channels()

    return vout, iout, bout


def get_avg_field(gm, t):
    ti = time.time()
    sum_ = 0
    i = 0
    while time.time() - ti <= t:
        sum_ += gm.get_field()[4]
        time.sleep(0.3)
        i += 1

    return sum_/i


def process_file(file_):
    v, i, b = [], [], []
    with open(file_, 'r') as file:
        data = file.readline()
        while data != '\n':
            v_i, i_i, b_i = data.split(',')
            v.append(float(v_i))
            i.append(float(i_i))
            b.append(float(b_i))
            data = file.readline()

    return i, v, b


def main():
    ps = Spd3303x('10.176.42.121')
    gm = GM3('COM3', tmout=3)
    v, i, b = get_ivb(ps, gm)
    coilname = 'large1'
    filename = 'data_coils/' + coilname + '.txt'

    with open(filename, 'w') as file:
        for k in range(len(v)):
            file.write(str(v[k]) + ',' + str(i[k]) + ',' + str(b[k]) + '\n')

        file.write('\n')

    i, v, b = process_file(filename)

    model = linregress(i, v)
    x_model = np.asarray(i)
    y_model = model.slope*x_model + model.intercept

    with open('resistance_meaurements.txt', 'a') as file:
        file.write(coilname + ',' + str(model.slope) + ',' + str(model.stderr) + '\n')

    plt.figure(figsize=[6, 8])
    plt.plot(i, v, 'o', label='data')
    plt.plot(x_model, y_model, label='model')
    plt.legend()
    plt.show()

    model2 = linregress(i, b)
    x_model2 = np.asarray(i)
    y_model2 = model2.slope*x_model2 + model2.intercept

    plt.figure(figsize=[6, 8])
    plt.plot(i, b, 'o', label='data')
    plt.plot(x_model2, y_model2, label='model')
    plt.legend()
    plt.show()


main()
