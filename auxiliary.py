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


def process_file(file_, n_cols):
    out = []
    for i in range(n_cols):
        out.append([])

    with open(file_, 'r') as file:
        data = file.readline()
        while data != '\n':
            try:
                cols = data.split(',')
                for i in range(n_cols):
                    out[i].append(float(cols[i]))
            except (ValueError, IndexError):
                pass

            data = file.readline()

    return out


def main():


    pass


if __name__ == '__main__':
    main()