import numpy as np
import time
from datetime import datetime
from scipy.stats import linregress
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

from device_models import Spd3303x
from device_models import Gm3
from device_models import Series9550
from device_models import Vxm


def get_pos_b(coilname, ps, gm, vx, a, n, delta_step, notes=''):
    """
    collects data on the position and magnetic field, writes it to a file, and then returns the data

    Paramters
    ---------
    coilname : {'small1', 'small2', 'medium1', 'medium2', 'large1', 'large2'}
        name of the coil. Before running, there must be a directory inside data_coils with the name of the coil.
    ps : Spd3303x
        power supply to power coils
    gm : Gm3, Series9550
        gaussmeter to be used
    vx : Vxm
        motor controller
    a : float
        current to put through the coil wire
    n : int
        number of gaussmeter measurements to average. The measured field is the average of these n measurements
    delta_step : int
        the number of steps to displace the probe between datapoints
    notes : str
        notes to write in the header of the file

    Returns
    -------
    tuple of numpy arrays
        tuple containing the position array, magnetic field array, and the standard error array.
    """
    # vx.displace(1, -16000)
    gm.autozero()
    ps.set_current_limit(1, 3)
    ps.set_voltage(1, 20)
    ps.set_current(1, a)
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
    file.write(notes)
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


def process_file(file_, n_cols):
    """
    Reads n_cols from a file and outputs every column as a numpy array. Will also attempt to ignore a header.

    Parameters
    ----------
    file_ : str
        path to the file to process
    n_cols : int
        number of columns of file and number of arrays to output. Must match or else output will not be correct.

    Returns
    -------
    list of numpy arrays
        a list containing as many numpy arrays as specified by n_cols.
    """
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


def get_field_fit(pos, b, berr, coilname, amps):
    """
    model for magnetic field.

    Parameters
    ----------
    pos : numpy array
        position data
    b : numpy array
        magnetic field data
    berr : numpy array
        standard error of data points. Not used currently
    coilname : {'small1', 'small2', 'medium1', 'medium2', 'large1', 'large2'}
        name of the coil that was used to get the data
    amps : float
        current through the coil at the moment of taking data

    """
    def coil_field_z_axis(z, n, z0):
        """
        :param z: steps
        :param n: number of turns of wire in the coil
        :param z0: center position of coils in meter
        """
        coil_side = {
            'small': 0.667893,  # meters
            'medium': 0.7028942,
            'large': 0.7378954
        }

        side = coil_side[coilname[:-1]]

        meters = (z - z0) * 6.8E-6  # convert steps to meters

        x = meters
        f = 2e-7*amps*n*side**2
        s = 1 / (x**2 + (side**2)/4)
        t = 1 / np.sqrt(x**2 + (side**2)/2)

        return f*s*t*10000  # tesla to gauss

    popt, pcov = curve_fit(coil_field_z_axis, pos, b, p0=[60, 6260], bounds=([58, 5500], [62, 6500]))
    pos_model = np.linspace(pos[0], pos[-1], 1000)
    b_model = coil_field_z_axis(pos_model, *popt)

    print(popt, pcov)

    residuals = b - coil_field_z_axis(pos, *popt)
    return pos_model, b_model, residuals


def collect_field_data():
    ps = Spd3303x('10.176.42.171')
    # gm = Gm3('COM3', tmout=3)
    gm = Series9550(15)
    vx = Vxm('COM4')

    coilname = 'large1'
    amps = 2.3

    pos, b, berr = get_pos_b(coilname, ps, gm, vx, amps, 10, 100, notes='Removed one turn of wire to the coil.\n')
    pos_model, b_model, residuals = get_field_fit(pos, b, berr, coilname, amps)

    plt.figure(figsize=[6, 8])
    plt.plot(pos, b, '.-', label='data')
    plt.plot(pos_model, b_model, '-', label='model')
    plt.legend()
    plt.show()


def plot_data_from_file():
    amps = 2.3

    coilname = 'large1'
    file_name = '22_07_08__12_31_18.txt'
    file_full = 'data_coils/' + coilname + '/' + file_name
    pos, b, berr = process_file(file_full, 3)
    pos_model, b_model, residuals = get_field_fit(pos, b, berr, coilname, amps)

    coilname2 = 'large2'
    file_name2 = '22_07_08__11_40_12.txt'
    file_full2 = 'data_coils/' + coilname2 + '/' + file_name2
    pos2, b2, berr2 = process_file(file_full2, 3)
    pos_model2, b_model2, residuals2 = get_field_fit(pos2, b2, berr2, coilname, amps)

    plt.figure(figsize=[6, 8])
    plt.title('Coil field vs position')
    plt.ylabel('Magnetic field (gauss)')
    plt.xlabel('Probe position (steps)')
    plt.plot(pos, b, '.-', label=coilname + ' data')
    plt.plot(pos_model, b_model, '-', label=coilname + 'model')

    plt.plot(pos2, b2, '.-', label=coilname2 + ' data')
    plt.plot(pos_model2, b_model2, '-', label=coilname2 + 'model')
    plt.legend()
    plt.show()

    plt.figure(figsize=[6, 8])
    plt.title('Residuals')
    plt.xlabel('Probe position (steps)')
    plt.plot(pos, residuals, '.-', label=coilname)

    plt.plot(pos2, residuals2, '.-', label=coilname2)
    plt.legend()
    plt.show()


def main():
    plot_data_from_file()


main()
