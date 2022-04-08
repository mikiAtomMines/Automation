import matplotlib.pyplot as plt
import numpy


def main():
    file = open('data.txt', 'r')
    header_size = 5
    for i in range(header_size):
        file.readline()

    data = file.readlines()
    time_list = []
    actual_temp_list = []
    set_temp_list = []
    voltage_list = []
    time_i = 0
    time_list = []

    for str in data:
        time, actual_temp, set_temp, voltage = [float(a) for a in str.split()]

        time_list.append(time)
        actual_temp_list.append(actual_temp)
        set_temp_list.append(set_temp)
        voltage_list.append(voltage)


    plt.plot(time_list, actual_temp_list)

    plt.show()

main()