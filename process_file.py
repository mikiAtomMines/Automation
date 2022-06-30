from scipy.stats import linregress
import numpy as np
import matplotlib.pyplot as plt


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


def main():

    files = ['22_06_30__15_53_07.txt', '22_06_30__16_03_24.txt', '22_06_30__16_13_52.txt']
    coilname = 'small1'

    for filename in files:
        v, i, b = process_file('data_coils/' + coilname + '/' + filename)

        model = linregress(i, v)
        x_model = np.asarray(i)
        y_model = model.slope*x_model + model.intercept

        with open('data_coils/resistance_meaurements.txt', 'a') as file:
            file.write(coilname + ',' + str(model.slope) + ',' + str(model.stderr) + '\n')

        plt.figure(figsize=[6, 8])
        plt.plot(i, v, 'o', label='data')
        plt.plot(x_model, y_model, label='model')
        plt.legend()
        plt.show()

        model2 = linregress(v, b)
        x_model2 = np.asarray(v)
        y_model2 = model2.slope*x_model2 + model2.intercept

        with open('data_coils/field_meaurements.txt', 'a') as file:
            file.write(coilname + ',' + str(model2.slope) + ',' + str(model2.stderr) + '\n')

        plt.figure(figsize=[6, 8])
        plt.plot(v, b, 'o', label='data')
        plt.plot(x_model2, y_model2, label='model')
        plt.legend()
        plt.show()


main()