import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as anim
from connection_type import SocketEthernetDevice
from device_type import Heater
import simple_pid

class HeaterAssembly:
    def __init__(
            self,
            supply_and_channel,
            daq_and_channel,
            heater=None,
    ):
        """
        Pid controller device based on the beaglebone black rev C. The controller connects through a socket TCP/IP
        connection. Essentially a heater assembly.

        A heater assembly composed of a heater, a temperature measuring device, and a power supply.

        Parameters
        ----------
        supply_and_channel : two tuple of device_models.PowerSupply and int
            The power supply model that is being used for controlling the electrical power going into the heater.
        daq_and_channel : two tuple of device_models.MCC_device and int
            The temperature DAQ device that is being used for reading the temperature of the heater.
        simple_pid : simple_pid.PID()
            The PID function used to regulate the heater's temperature to the set point.
        set_temperature : float
            The desired set temperature in the same units as the temperature readings from the temperature DAQ.
        temp_units : str, None
            Set the temperature units for all temperature readings, setpoints, etc. Possible values (not
            case-sensitive):
            for Celsius                 celsius,               c
            for Fahrenheit              fahrenheit,            f
            for Kelvin                  kelvin,                k
            for default units           None
        heater : Heater
            heater type. Should contain the MAX temperature, MAX current, and MAX volts based on the hardware.

        configure_on_startup : bool
            Will configure the PID object's output limits, setpoint, and optionally, the Kp, Ki, and Kd. Set this to
            True if the pid object has not been manually configured.
        """

        self._supply_and_channel = supply_and_channel
        self._daq_and_channel = daq_and_channel
        self._heater = heater
        if self._heater is None:
            self._heater = Heater()
        self._pid = self._get_default_pid()
        self._MAX_voltage_limit = min(self._heater.MAX_volts, self._supply_and_channel[0].MAX_voltage_limit)
        self._MAX_current_limit = min(self._heater.MAX_current, self._supply_and_channel[0].MAX_current_limit)
        self._MAX_temp_limit = self._heater.MAX_temp
        self._regulating = False

    def _get_default_pid(self):
        """
        Sets the output limits, sample time, set point, and the Kp, Ki, and Kd of the PID object.
        """
        pid = simple_pid.PID()
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        out_max = min(self._heater.MAX_volts, ps.get_channel_voltage_limit(ch))

        pid.Kp = 1
        pid.Ki = 0.03
        pid.Kd = 0
        pid.setpoint = 0
        pid.sample_time = 2
        pid.output_limits = (0, out_max)

        return pid

    def reset_pid(self):
        self._pid = self._get_default_pid()

    def reset_pid_limits(self):
        pid = self._pid
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        out_max = min(self.MAX_voltage_limit, ps.get_channel_voltage_limit(ch))

        pid.output_limits = (0, out_max)

    def stop_supply(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_channel_state(ch, False)
        ps.set_set_voltage(ch, 0)
        ps.set_set_current(ch, 0)

    def reset_power_supply(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_channel_state(ch, False)
        ps.set_set_voltage(ch, 0)
        ps.set_set_current(ch, 0)
        ps.set_channel_voltage_limit(ch, ps.MAX_voltage_limit)
        ps.set_channel_current_limit(ch, ps.MAX_current_limit)

    def ready_power_supply(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_set_voltage(ch, 0)
        ps.set_set_current(ch, 0)
        if ps.get_channel_voltage_limit(ch) > self.MAX_voltage_limit:
            ps.set_channel_voltage_limit(ch, self.MAX_voltage_limit)
        if ps.get_channel_current_limit(ch) > self.MAX_current_limit:
            ps.set_channel_voltage_limit(ch, self.MAX_current_limit)
        ps.set_set_current = ps.get_channel_current_limit(ch)
        ps.set_channel_state(ch, True)

    def reset_assembly(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        self.reset_power_supply()
        ps.set_channel_voltage_limit(ch, self.MAX_voltage_limit)
        ps.set_channel_current_limit(ch, self.MAX_current_limit)
        self.reset_pid()

    def ready_assembly(self):
        self.ready_power_supply()
        self.reset_pid_limits()

    def stop(self):
        self.stop_supply()
        self._pid.setpoint = 0

    # -----------------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------------

    # Power supply
    # ------------
    @property
    def power_supply(self):
        out = 'IDN: ' + self._supply_and_channel[0].idn + '\n' \
              + 'IP4 Address: ' + self._supply_and_channel[0].ip4_address
        return out

    @property
    def supply_set_voltage(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_set_voltage(ch)

    @supply_set_voltage.setter
    def supply_set_voltage(self, new_volt):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_set_voltage(ch, new_volt)

    @property
    def supply_set_current(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_set_current(ch)

    @supply_set_current.setter
    def supply_set_current(self, new_curr):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_set_current(ch, new_curr)

    @property
    def supply_actual_voltage(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_actual_voltage(ch)

    @property
    def supply_actual_current(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_actual_current(ch)

    @property
    def supply_voltage_limit(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_channel_voltage_limit(ch)

    @supply_voltage_limit.setter
    def supply_voltage_limit(self, new_lim):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_channel_voltage_limit(ch, new_lim)

    @property
    def supply_current_limit(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_channel_current_limit(ch)

    @supply_current_limit.setter
    def supply_current_limit(self, new_lim):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_channel_current_limit(ch, new_lim)

    @property
    def supply_channel_state(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_channel_state(ch)

    @supply_channel_state.setter
    def supply_channel_state(self, new_state):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_channel_state(ch, new_state)

    @property
    def supply_channel(self):
        return self._supply_and_channel[1]

    @supply_channel.setter
    def supply_channel(self, new_ch):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        if new_ch <= ps.number_of_channels and new_ch != ch:
            ps.zero_all_channels()
            self._supply_and_channel[1] = new_ch

    @property
    def supply_MAX_voltage(self):
        return self._supply_and_channel[0].MAX_voltage_limit

    @property
    def supply_MAX_current(self):
        return self._supply_and_channel[0].MAX_current_limit

    @property
    def MAX_voltage_limit(self):
        return self._MAX_voltage_limit

    @property
    def MAX_current_limit(self):
        return self._MAX_current_limit

    # Temp DAQ
    # --------
    @property
    def daq(self):
        out = 'IDN: ' + self._daq_and_channel[0].idn + '\n' \
              + 'IP4 Address: ' + self._daq_and_channel[0].ip4_address
        return out

    @property
    def temp(self):
        dq = self._daq_and_channel[0]
        ch = self._daq_and_channel[1]
        return dq.get_temp(ch)

    @property
    def daq_channel(self):
        return self._daq_and_channel[1]

    @daq_channel.setter
    def daq_channel(self, new_chan):  # TODO: add syntax checking for mcc device
        if 0 <= new_chan < self._daq_and_channel[0].number_temp_channels:
            self._daq_and_channel[1] = new_chan
        else:
            print('ERROR: channel not found')
            sys.exit()

    @property
    def thermocouple_type(self):
        dq = self._daq_and_channel[0]
        ch = self._daq_and_channel[1]
        return dq.get_thermocouple_type(ch)

    @thermocouple_type.setter
    def thermocouple_type(self, new_tc):
        dq = self._daq_and_channel[0]
        ch = self._daq_and_channel[1]
        dq.set_thermocouple_type(ch, new_tc)

    @property
    def temp_units(self):
        return self._daq_and_channel[0].default_units

    @temp_units.setter
    def temp_units(self, new_units):
        self._daq_and_channel[0].default_units = new_units  # this also checks if input is valid

    # PID settings
    # ------------
    @property
    def pid_function(self):
        return f'kp={self._pid.Kp} ki={self._pid.Ki} kd={self._pid.Kd} setpoint={self._pid.setpoint} sampletime=' \
               f'{self._pid.sample_time}'

    @property
    def pid_kp(self):
        return self._pid.Kp

    @pid_kp.setter
    def pid_kp(self, new_kp):
        self._pid.Kp = new_kp

    @property
    def pid_ki(self):
        return self._pid.Ki

    @pid_ki.setter
    def pid_ki(self, new_ki):
        self._pid.Ki = new_ki

    @property
    def pid_kd(self):
        return self._pid.Kd

    @pid_kd.setter
    def pid_kd(self, new_kd):
        self._pid.Kd = new_kd

    @property
    def set_temperature(self):
        return self._pid.setpoint

    @set_temperature.setter
    def set_temperature(self, new_temp):
        if self._MAX_temp_limit < new_temp:
            raise ValueError('ERROR: new_temp value of', new_temp, 'not allowed. Check temperature limits')
        self._pid.setpoint = new_temp

    @property
    def sample_time(self):
        return self._pid.sample_time

    @sample_time.setter
    def sample_time(self, new_st):
        self._pid.sample_time = new_st

    @property
    def pid_regulating(self):
        return self._regulating

    @pid_regulating.setter
    def pid_regulating(self, regulate):
        if not (type(regulate) is int) and not (type(regulate) is float):
            raise TypeError('ERROR: ' + str(regulate) + ' not valid input')
        self._regulating = bool(regulate)

    @property
    def MAX_set_temp(self):
        return self._MAX_temp_limit

    # -----------------------------------------------------------------------------
    # methods
    # -----------------------------------------------------------------------------
    def update_supply(self):
        """
        Calculates the new power supply voltage using the PID function based on the current temperature from the
        temperature daq channel. It then sets the power supply channel voltage to this new voltage.
        """
        self.ready_assembly()

        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        new_ps_voltage = self._pid(round(self.temp, 2))
        ps.set_set_voltage(channel=ch, volts=new_ps_voltage)

        return new_ps_voltage

    def live_plot(self, x_size=10):
        """
        plots current temp and ps_volts
        :param x_size: number of data points per frame
        """
        temp = [0.0] * x_size
        ps_v = [0.0] * x_size
        time_ = [0.0] * x_size
        fig = plt.figure()
        ax = plt.subplot(111)

        def animate(i):
            ps_volt = self.update_supply()

            temp.pop(0)
            temp.append(self.temp)

            time_.pop(0)
            time_.append(i)

            ps_v.pop(0)
            ps_v.append(ps_volt)

            ax.cla()
            ax.plot(time_, temp)
            ax.plot(time_, ps_v)
            ax.text(time_[-1], temp[-1] + 2, str(temp[-1]))
            ax.text(time_[-1], ps_v[-1] + 2, str(ps_v[-1]))
            ax.set_ylim([0, self._pid.setpoint * 1.3])

        ani = anim.FuncAnimation(fig, animate, interval=2000)
        plt.show()


class PidHeater(SocketEthernetDevice):  # TODO: Error handling for commands.
    def __init__(self, heater_keys, ip4_address, port=65432, ):
        super().__init__(ip4_address, port)

        self._heater_keys = heater_keys

    def _query_(self, asm_key, msg):
        if type(asm_key) is int:
            try:
                asm_key = self._heater_keys[asm_key]
            except IndexError:
                return 'ERROR: index ' + str(asm_key) + ' not valid.'

        qry = asm_key + ' ' + msg + '\r'
        return self._query(qry.encode('utf-8')).decode('utf-8')

    def _command_(self, asm_key, msg, param=''):
        if type(asm_key) is int:
            try:
                asm_key = self._heater_keys[asm_key]
            except IndexError:
                return 'ERROR: index ' + str(asm_key) + ' not valid.'

        cmd = asm_key + ' ' + msg + ' ' + str(param) + '\r'
        self._command(cmd.encode('utf-8'))

    # Power supply
    # ------------
    def get_supply_idn(self, asm_key):
        return self._query_(asm_key, 'PS:IDN')

    def reset_supply(self, asm_key):
        return self._command_(asm_key, 'PS:RSET')

    def stop_supply(self, asm_key):
        return self._command_(asm_key, 'PS:STOP')

    def stop_all_supplies(self):
        for asm_key in self._heater_keys:
            self._command_(asm_key, 'PS:STOP')

    def ready_supply(self, asm_key):
        return self._command_(asm_key, 'PS:REDY')

    def ready_all_supplies(self):
        for asm_key in self._heater_keys:
            self._command_(asm_key, 'PS:REDY')

    def get_supply_actual_voltage(self, asm_key):
        return self._query_(asm_key, 'PS:VOLT ?')

    def get_supply_set_voltage(self, asm_key):
        return self._query_(asm_key, 'PS:VSET ?')

    def set_supply_set_voltage(self, asm_key, volts):
        return self._command_(asm_key, 'PS:VSET', volts)

    def get_supply_actual_current(self, asm_key):
        return self._query_(asm_key, 'PS:AMPS ?')

    def get_supply_set_current(self, asm_key):
        return self._query_(asm_key, 'PS:ASET ?')

    def set_supply_set_current(self, asm_key, amps):
        return self._command_(asm_key, 'PS:ASET', amps)

    def get_supply_limit_voltage(self, asm_key):
        return self._query_(asm_key, 'PS:VLIM ?')

    def set_supply_limit_voltage(self, asm_key, volts):
        return self._command_(asm_key, 'PS:VLIM', volts)

    def get_supply_limit_current(self, asm_key):
        return self._query_(asm_key, 'PS:ALIM ?')

    def set_supply_limit_current(self, asm_key, amps):
        return self._command_(asm_key, 'PS:ALIM', amps)

    def get_supply_channel_state(self, asm_key):
        return self._query_(asm_key, 'PS:CHIO ?')

    def set_supply_channel_state(self, asm_key, state):
        return self._command_(asm_key, 'PS:CHIO', int(state))

    def get_supply_channel(self, asm_key):
        return self._query_(asm_key, 'PS:CHAN ?')

    def set_supply_channel(self, asm_key, new_chan):
        return self._command_(asm_key, 'PS:CHAN', new_chan)

    # DAQ
    # ---
    def get_daq_idn(self, asm_key):
        return self._query_(asm_key, 'DQ:IDN')

    def get_daq_temp(self, asm_key):
        return self._query_(asm_key, 'DQ:TEMP ?')

    def get_daq_channel(self, asm_key):
        return self._query_(asm_key, 'DQ:CHAN ?')

    def set_daq_channel(self, asm_key, new_chan):
        return self._command_(asm_key, 'DQ:CHAN', new_chan)

    def get_daq_tc_type(self, asm_key):
        return self._query_(asm_key, 'DQ:TCTY ?')

    def set_daq_tc_type(self, asm_key, tc_type):
        return self._command_(asm_key, 'DQ:TCTY', tc_type)

    def get_daq_units(self, asm_key):
        return self._query_(asm_key, 'DQ:UNIT ?')

    def set_daq_units(self, asm_key, units):
        return self._command_(asm_key, 'DQ:UNIT', units)

    # PID Settings
    # ------------
    def get_pid_idn(self, asm_key):
        return self._query_(asm_key, 'PD:IDN')

    def reset_pid(self, asm_key):
        return self._command_(asm_key, 'PD:RSET')

    def reset_pid_limits(self, asm_key):
        return self._command_(asm_key, 'PD:RLIM')

    def get_pid_kpro(self, asm_key):
        return self._query_(asm_key, 'PD:KPRO ?')

    def set_pid_kpro(self, asm_key, new_k):
        return self._command_(asm_key, 'PD:KPRO', new_k)

    def get_pid_kint(self, asm_key):
        return self._query_(asm_key, 'PD:KINT ?')

    def set_pid_kint(self, asm_key, new_k):
        return self._command_(asm_key, 'PD:KINT', new_k)

    def get_pid_kder(self, asm_key):
        return self._query_(asm_key, 'PD:KDER ?')

    def set_pid_kder(self, asm_key, new_k):
        return self._command_(asm_key, 'PD:KDER', new_k)

    def get_pid_setpoint(self, asm_key):
        return self._query_(asm_key, 'PD:SETP ?')

    def set_pid_setpoint(self, asm_key, new_temp):
        return self._command_(asm_key, 'PD:SETP', new_temp)

    def get_pid_sample_time(self, asm_key):
        return self._query_(asm_key, 'PD:SAMP ?')

    def set_pid_sample_time(self, asm_key, new_t):
        return self._command_(asm_key, 'PD:SAMP', new_t)

    def get_pid_regulating(self, asm_key):
        return self._query_(asm_key, 'PD:REGT ?')

    def set_pid_regulating(self, asm_key, regt):
        return self._command_(asm_key, 'PD:REGT', int(regt))

    #Assembly
    def stop(self, asm_key):
        return self._command_(asm_key, 'AM:STOP')

    def reset_assembly(self, asm_key):
        return self._command_(asm_key, 'AM:RSET')

    def ready_assembly(self, asm_key):
        return self._command_(asm_key, 'AM:REDY')