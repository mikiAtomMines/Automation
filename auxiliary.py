"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

import time
import sys
import matplotlib.pyplot as plt
try:
    from mcculw import enums
except ModuleNotFoundError:
    pass


# -----------------------------------------------------------------------------------
# Power supplies
# -----------------------------------------------------------------------------------

def simple_plot(file):
    file = open(file, 'r')
    header_size = 5
    for i in range(header_size):
        file.readline()

    data = file.readlines()
    time_list = []
    actual_temp_list = []
    set_temp_list = []
    voltage_list = []

    for i in data:
        time_, actual_temp, set_temp, voltage = [float(a) for a in str.split()]

        time_list.append(time_)
        actual_temp_list.append(actual_temp)
        set_temp_list.append(set_temp)
        voltage_list.append(voltage)

    plt.plot(time_list, actual_temp_list)

    plt.show()


def main():
    # v = Vxm('COM6')
    # v.disconnect()

    gm = Series9550(15)
    testing_Series9550(gm)


if __name__ == '__main__':
    main()