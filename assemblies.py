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
        A heater assembly composed of a heater, a temperature measuring device, and a power supply. This assembly
        should only need to be used by the pid_controller_server.py file running on a BeagleBone Black.

        Parameters
        ----------
        supply_and_channel : two tuple of device_models.PowerSupply and int
            First item in the tuple is the power supply that is being used for controlling the electrical power going
            into the heater. The second item is the supply channel that is being used. If the power supply has only
            one channel, use 1.
        daq_and_channel : two tuple of device_models.MCC_device and int
            First item in the tuple is the temperature DAQ device that is being used for reading the temperature of the
            heater. The second item is the channel to use.
        heater : Heater
            Object that contains the MAX temperature, MAX current, and MAX volts based on the physical heater
            hardware. If none is provided, the class will create an instance of the Heater class to use.
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
        Sets the output limits based on heater and power supply limits. Sets default values to sample time, set point,
        and the Kp, Ki, and Kd of the PID object.

        Returns
        -------
        simple_pid.PID()
            PID object with default values.
        """
        pid = simple_pid.PID()
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        out_max = min(self._heater.MAX_volts, ps.get_voltage_limit(ch))

        pid.Kp = 1
        pid.Ki = 0.03
        pid.Kd = 0
        pid.setpoint = 0
        pid.sample_time = 2
        pid.output_limits = (0, out_max)

        return pid

    def reset_pid(self):
        """
        Resets the pid settings to their default values. Output limits set based on power supply and heater limit
        voltage.
        """
        self._pid = self._get_default_pid()

    def reset_pid_limits(self):
        """
        Reset PID output limits based on heater and power supply limit voltage.
        """
        pid = self._pid
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        out_max = min(self.MAX_voltage_limit, ps.get_voltage_limit(ch))

        pid.output_limits = (0, out_max)

    def stop_supply(self):
        """
        Turn off supply channel, set voltage and current to 0.
        """
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_channel_state(ch, False)
        ps.set_voltage(ch, 0)
        ps.set_current(ch, 0)

    def reset_power_supply(self):
        """
        Turn off supply channel, set voltage and current to 0, and reset voltage and current limits based on power
        supply max limits.
        """
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_channel_state(ch, False)
        ps.set_voltage(ch, 0)
        ps.set_current(ch, 0)
        ps.set_voltage_limit(ch, ps.MAX_voltage_limit)
        ps.set_current_limit(ch, ps.MAX_current_limit)

    def ready_power_supply(self):
        """
        set voltage and current limits based on heater and power supply limits, set the setpoint current to the
        channel current limit, and turn on the supply channel.
        """
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        ps.set_voltage(ch, 0)
        ps.set_current(ch, 0)
        if ps.get_voltage_limit(ch) > self.MAX_voltage_limit:
            ps.set_voltage_limit(ch, self.MAX_voltage_limit)
        if ps.get_current_limit(ch) > self.MAX_current_limit:
            ps.set_current_limit(ch, self.MAX_current_limit)
        ps.set_current(ch, ps.get_current_limit(ch))
        ps.set_channel_state(ch, True)

    def reset_assembly(self):
        """
        Turn off supply channel, set voltage and current to 0, and reset voltage and current limits based on supply
        and heater limits.
        Reset PID to default values.
        """
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        self.reset_power_supply()
        ps.set_voltage_limit(ch, self.MAX_voltage_limit)
        ps.set_current_limit(ch, self.MAX_current_limit)
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
    def get_supply_channel(self):
        return self._supply_and_channel[1]

    def set_supply_channel(self, new_ch):
        ps = self._supply_and_channel[0]

        err = ps.check_valid_channel(new_ch)
        if err is None:
            ps.zero_all_channels()
            self._supply_and_channel[1] = new_ch
        else:
            return err

    def get_supply_channel_state(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_channel_state(ch)

    def set_supply_channel_state(self, state):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.set_channel_state(ch, state)

    def get_supply_setpoint_voltage(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_setpoint_voltage(ch)

    def set_supply_voltage(self, volts):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.set_voltage(ch, volts)

    def get_supply_actual_voltage(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_actual_voltage(ch)

    def get_supply_setpoint_current(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_setpoint_current(ch)

    def set_supply_current(self, amps):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.set_current(ch, amps)

    def get_supply_actual_current(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_actual_current(ch)

    def get_supply_voltage_limit(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_voltage_limit(ch)

    def set_supply_voltage_limit(self, volts):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.set_voltage_limit(ch, volts)

    def get_supply_current_limit(self):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.get_current_limit(ch)

    def set_supply_current_limit(self, amps):
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        return ps.set_current_limit(ch, amps)

    @property
    def power_supply(self):
        out = 'IDN: ' + self._supply_and_channel[0].idn + '\n' \
              + 'IP4 Address: ' + self._supply_and_channel[0].ip4_address
        return out

    @property
    def supply_setpoint_voltage(self):
        return self.get_supply_setpoint_voltage()

    @property
    def supply_setpoint_current(self):
        return self.get_supply_setpoint_current()

    @property
    def supply_actual_voltage(self):
        return self.get_supply_actual_voltage()

    @property
    def supply_actual_current(self):
        return self.get_supply_actual_current()

    @property
    def supply_voltage(self):
        return self.get_supply_actual_voltage()

    @property
    def supply_current(self):
        return self.get_supply_actual_current()

    @property
    def supply_voltage_limit(self):
        return self.get_supply_voltage_limit()

    @property
    def supply_current_limit(self):
        return self.get_supply_current_limit()

    @property
    def supply_channel_state(self):
        return self.get_supply_channel_state()

    @property
    def supply_channel(self):
        return self._supply_and_channel[1]

    @property
    def supply_number_of_channels(self):
        return self._supply_and_channel[0].number_of_channels

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
    def get_daq_temp(self):
        dq = self._daq_and_channel[0]
        ch = self._daq_and_channel[1]
        return dq.get_temp(ch)

    def get_daq_channel(self):
        return self._daq_and_channel[1]

    def set_daq_channel(self, new_ch):
        dq = self._daq_and_channel[0]
        err = dq.check_valid_temp_channel(new_ch)
        if err is None:
            self._daq_and_channel[1] = new_ch
        else:
            return 'ERROR: channel not found'

    def get_daq_tc_type(self):
        dq = self._daq_and_channel[0]
        ch = self._daq_and_channel[1]
        return dq.get_thermocouple_type(ch)

    def set_daq_tc_type(self, new_tc):
        dq = self._daq_and_channel[0]
        ch = self._daq_and_channel[1]
        return dq.set_thermocouple_type(ch, new_tc)

    def get_daq_temp_units(self):
        return self._daq_and_channel[0].default_units

    def set_daq_temp_units(self, new_units):
        dq = self._daq_and_channel[0]
        err = dq.check_valid_units(new_units)
        if err is None:
            dq.default_units = new_units
        else:
            return 'ERROR: temp units not valid'

    @property
    def daq(self):
        out = 'IDN: ' + self._daq_and_channel[0].idn + '\n' \
              + 'IP4 Address: ' + self._daq_and_channel[0].ip4_address
        return out

    @property
    def temp(self):
        return self.get_daq_temp()

    @property
    def daq_channel(self):
        return self._daq_and_channel[1]

    @property
    def tc_type(self):
        dq = self._daq_and_channel[0]
        ch = self._daq_and_channel[1]
        return dq.get_thermocouple_type(ch)

    @property
    def temp_units(self):
        return self._daq_and_channel[0].default_units

    @property
    def daq_number_of_temp_channels(self):
        return self._daq_and_channel[0].number_temp_channels

    # PID settings
    # ------------
    def get_pid_setpoint(self):
        return self._pid.setpoint

    def set_pid_setpoint(self, new_set):
        if self._MAX_temp_limit < new_set:
            return 'ERROR: new_temp value of', new_set, 'not allowed. Check temperature limits'
        self._pid.setpoint = new_set

    def get_pid_limits(self):
        return self._pid.output_limits

    def get_pid_sample_time(self):
        return self._pid.sample_time

    def set_pid_sample_time(self, seconds):
        if seconds < 1:
            return 'ERROR: sample time of ' + str(seconds) + ' is invalid. Use larger or equal to 1 second.'
        self._pid.sample_time = seconds

    def get_pid_regulation(self):
        return self._regulating

    def set_pid_regulation(self, reg):
        if type(reg) is not int and type(reg) is not bool:
            return 'ERROR: type ' + str(type(reg)) + ' not supported'
        self._regulating = bool(reg)

    @property
    def pid_function(self):
        return f'kp={self._pid.Kp} ki={self._pid.Ki} kd={self._pid.Kd} setpoint={self._pid.setpoint} sampletime=' \
               f'{self._pid.sample_time}'

    @property
    def pid_setpoint(self):
        return self.get_pid_setpoint()

    @property
    def pid_limits(self):
        return self.get_pid_limits()

    @property
    def pid_sample_time(self):
        return self.get_pid_sample_time()

    @property
    def is_regulating(self):
        return self.get_pid_regulation()

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
    def pid_is_regulating(self):
        return self._regulating

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
        ps = self._supply_and_channel[0]
        ch = self._supply_and_channel[1]
        new_ps_voltage = self._pid(round(self.temp, 2))
        ps.set_voltage(channel=ch, volts=new_ps_voltage)

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


class Oven(SocketEthernetDevice):
    def __init__(self, ip4_address, port=65432, ):
        super().__init__(ip4_address, port)

    def _query_(self, asm_key, msg):
        """
        Send a query to the ethernet device and receives response.

        Parameters
        ----------
        asm_key : str or int
            the name of the assembly to send the command. Can also be an int, which will interpret it as an index in
            the list of assemblies in the oven.
        msg : str
            command from custom communications protocol.

        Returns
        -------
        str
            Returns response as string or error string.
        """
        if type(asm_key) is int:
            try:
                asm_key = self.get_assemblies_keys()[asm_key]
            except IndexError:
                return 'ERROR: index ' + str(asm_key) + ' not valid.'

        qry = asm_key + ' ' + msg + '\r'
        return self._query(qry.encode('utf-8')).decode('utf-8').strip('\r')

    def _command_(self, asm_key, msg, param=''):
        """
        Send a command to the ethernet device.

        Parameters
        ----------
        asm_key : str or int
            the name of the assembly to send the command. Can also be an int, which will interpret it as an index in
            the list of assemblies in the oven.
        msg : str
            command from custom communications protocol.
        param : str, int, float
            Required by setters.

        Returns
        -------
        None
            If command was sent and executed succesfully, return None
        str
            Else, return error string.
        """
        if type(asm_key) is int:
            try:
                asm_key = self.get_assemblies_keys()[asm_key]
            except IndexError:
                return 'ERROR: index ' + str(asm_key) + ' not valid.'

        cmd = asm_key + ' ' + msg + ' ' + str(param) + '\r'
        err = self._query(cmd.encode('utf-8')).decode('utf-8')
        if err != 'NOERROR\r':
            return err

    # Oven
    def get_assemblies_keys(self):
        """
        :return list of str: keys of all the heater assemblies used by the oven.
        """
        return self._query_('OVEN', 'OV:KEYS').split()

    # Power supply
    # ------------
    def get_supply_idn(self, asm_key):
        return self._query_(asm_key, 'PS:IDN')

    def reset_supply(self, asm_key):
        return self._command_(asm_key, 'PS:RSET')

    def stop_supply(self, asm_key):
        return self._command_(asm_key, 'PS:STOP')

    def stop_all_supplies(self):
        for asm_key in self.get_assemblies_keys():
            self._command_(asm_key, 'PS:STOP')

    def ready_supply(self, asm_key):
        return self._command_(asm_key, 'PS:REDY')

    def ready_all_supplies(self):
        for asm_key in self.get_assemblies_keys():
            self._command_(asm_key, 'PS:REDY')

    def get_supply_actual_voltage(self, asm_key):
        qry = self._query_(asm_key, 'PS:VOLT ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def get_supply_setpoint_voltage(self, asm_key):
        qry = self._query_(asm_key, 'PS:VSET ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def set_supply_voltage(self, asm_key, volts):
        return self._command_(asm_key, 'PS:VSET', volts)

    def get_supply_actual_current(self, asm_key):
        qry = self._query_(asm_key, 'PS:AMPS ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def get_supply_setpoint_current(self, asm_key):
        qry = self._query_(asm_key, 'PS:ASET ?')
        try:
            return float(qry)
        except ValueError:
            return

    def set_supply_current(self, asm_key, amps):
        return self._command_(asm_key, 'PS:ASET', amps)

    def get_supply_voltage_limit(self, asm_key):
        qry = self._query_(asm_key, 'PS:VLIM ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def set_supply_voltage_limit(self, asm_key, volts):
        return self._command_(asm_key, 'PS:VLIM', volts)

    def get_supply_current_limit(self, asm_key):
        qry = self._query_(asm_key, 'PS:ALIM ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def set_supply_current_limit(self, asm_key, amps):
        return self._command_(asm_key, 'PS:ALIM', amps)

    def get_supply_channel_state(self, asm_key):
        qry = self._query_(asm_key, 'PS:CHIO ?')
        if qry == 'False':
            return False
        elif qry == 'True':
            return True
        else:
            return qry

    def set_supply_channel_state(self, asm_key, state):
        return self._command_(asm_key, 'PS:CHIO', int(state))

    def get_supply_channel(self, asm_key):
        qry = self._query_(asm_key, 'PS:CHAN ?')
        try:
            return int(qry)
        except ValueError:
            return qry

    def set_supply_channel(self, asm_key, new_chan):
        return self._command_(asm_key, 'PS:CHAN', new_chan)

    # DAQ
    # ---
    def get_daq_idn(self, asm_key):
        return self._query_(asm_key, 'DQ:IDN')

    def get_daq_temp(self, asm_key):
        qry = self._query_(asm_key, 'DQ:TEMP ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def get_daq_channel(self, asm_key):
        qry = self._query_(asm_key, 'DQ:CHAN ?')
        try:
            return int(qry)
        except ValueError:
            return qry

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

    def get_pid_limits(self, asm_key):
        return self._query_(asm_key, 'PD:LIMS ?')

    def reset_pid_limits(self, asm_key):
        return self._command_(asm_key, 'PD:RLIM')

    def get_pid_kpro(self, asm_key):
        qry = self._query_(asm_key, 'PD:KPRO ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def set_pid_kpro(self, asm_key, new_k):
        return self._command_(asm_key, 'PD:KPRO', new_k)

    def get_pid_kint(self, asm_key):
        qry = self._query_(asm_key, 'PD:KINT ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def set_pid_kint(self, asm_key, new_k):
        return self._command_(asm_key, 'PD:KINT', new_k)

    def get_pid_kder(self, asm_key):
        qry = self._query_(asm_key, 'PD:KDER ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def set_pid_kder(self, asm_key, new_k):
        return self._command_(asm_key, 'PD:KDER', new_k)

    def get_pid_setpoint(self, asm_key):
        qry = self._query_(asm_key, 'PD:SETP ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def set_pid_setpoint(self, asm_key, new_temp):
        return self._command_(asm_key, 'PD:SETP', new_temp)

    def get_pid_sample_time(self, asm_key):
        qry = self._query_(asm_key, 'PD:SAMP ?')
        try:
            return float(qry)
        except ValueError:
            return qry

    def set_pid_sample_time(self, asm_key, new_t):
        return self._command_(asm_key, 'PD:SAMP', new_t)

    def get_pid_regulation(self, asm_key):
        qry = self._query_(asm_key, 'PD:REGT ?')
        if qry == 'False':
            return False
        elif qry == 'True':
            return True
        else:
            return qry

    def set_pid_regulation(self, asm_key, regt):
        return self._command_(asm_key, 'PD:REGT', int(regt))

    # Assembly
    def get_assembly_MAX_voltage(self, asm_key):
        qry = self._query_(asm_key, 'AM:MAXV')
        try:
            return float(qry)
        except ValueError:
            return qry

    def get_assembly_MAX_current(self, asm_key):
        qry = self._query_(asm_key, 'AM:MAXA')
        try:
            return float(qry)
        except ValueError:
            return qry

    def stop(self, asm_key):
        return self._command_(asm_key, 'AM:STOP')

    def reset_assembly(self, asm_key):
        return self._command_(asm_key, 'AM:RSET')

    def ready_assembly(self, asm_key):
        return self._command_(asm_key, 'AM:REDY')
