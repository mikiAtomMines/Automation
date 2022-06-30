import numpy as np
import time
from datetime import date
from datetime import datetime
from scipy.stats import linregress
import matplotlib.pyplot as plt

from device_models import Spd3303x
from device_models import Gm3


def get_ivb(ps, gm, vm, incr):
    """
    :param Spd3303x ps:
    :param Gm3 gm:
    :return:
    """
    ps.set_current_limit(1, 3)
    ps.set_current(1, 3.0)
    ps.set_voltage(1, 0)
    ps.set_channel_state(1, True)

    vmax = vm
    increment = incr
    v = 2
    vout = []
    iout = []
    bout = []
    while v <= vmax:
        ps.set_voltage(1, v)
        time.sleep(1)
        v += increment
        vout.append(ps.get_actual_voltage(1))
        iout.append(ps.get_actual_current(1))
        bout.append(get_avg_field(gm, t=10))

    ps.zero_all_channels()

    return vout, iout, bout


def get_avg_field(gm, t):
    ti = time.time()
    sum_ = 0
    i = 0
    while time.time() - ti <= t:
        sum_ += gm.get_datapoint()[3]
        time.sleep(0.3)
        i += 1

    return abs(sum_/i)


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

    return v, i, b


def main():
    ps = Spd3303x('10.176.42.121')
    gm = Gm3('COM3', tmout=3)
    v, i, b = get_ivb(ps, gm, 8, 0.2)
    coilname = 'small2'
    time_now = datetime.now().strftime('%y_%m_%d__%H_%M_%S')
    filename = 'data_coils/' + coilname + '/' + time_now + '.txt'


    with open(filename, 'w') as file:
        for k in range(len(v)):
            file.write(str(v[k]) + ',' + str(i[k]) + ',' + str(b[k]) + '\n')
        file.write('\n')

    v, i, b = process_file(filename)

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

    model2 = linregress(v, b)
    x_model2 = np.asarray(v)
    y_model2 = model2.slope*x_model2 + model2.intercept

    with open('field_meaurements.txt', 'a') as file:
        file.write(coilname + ',' + str(model2.slope) + ',' + str(model2.stderr) + '\n')

    plt.figure(figsize=[6, 8])
    plt.plot(v, b, 'o', label='data')
    plt.plot(x_model2, y_model2, label='model')
    plt.legend()
    plt.show()


for i in range(10):
    main()
