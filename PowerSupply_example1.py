import matplotlib.pyplot as plt
import numpy as np
import time
from scipy.stats import linregress

from automation.device_models import Spd3303x

def get_iv_curve(v_lo, v_hi, n_points, i_max):
    """
    measure the current as a function of voltage to calculate resistance. Plot data with linear fit.
    """
    ps = Spd3303x('10.176.42.121', zero_on_startup=True)
    ps_ch = 1

    v = np.linspace(v_lo, v_hi, n_points)
    i = np.asarray([])

    ps.set_voltage_limit(ps_ch, v_hi)
    ps.set_current_limit(ps_ch, i_max)
    ps.set_channel_state(1, True)

    ps.set_current(ps_ch, i_max)
    time.sleep(0.5)
    for v_i in v:
        ps.set_voltage(ps_ch, v_i)
        time.sleep(0.5)
        i = np.append(i, ps.get_actual_current(ps_ch))

    ps.zero_all_channels()
    ps.disconnect()

    model = linregress(v, i)

    print('Slope:', model.slope, ' +- ', model.slope)
    print('Intercept:', model.intercept, ' +- ', model.intercept_stderr)
    if model.slope != 0:
        print('Resistance:', 1/model.slope, ' +- ', model.stderr/(model.slope**2))
    else:
        print('Resistance: inf +- nan')

    v_model = np.linspace(v_lo, v_hi, n_points*10)
    i_model = model.slope*v_model + model.intercept

    plt.figure(figsize=(6,4))
    plt.plot(v, i, '.', label='data')
    plt.plot(v_model, i_model, '-', label='model')
    plt.legend()
    plt.show()


get_iv_curve(0, 10, 40, 3)