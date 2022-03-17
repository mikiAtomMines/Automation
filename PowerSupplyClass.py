"""
Created on Fri Mar 11 12:53:39 2022

@author: Sebastian Miki-Silva
"""

# TODO: Add proper error handling. This includes receiving error from power supply.
# TODO: Finish adding comments

import socket
import sys
import time


class EthernetDevice:
    def __init__(
            self,
            ip4_address=None,
            port=50000,
    ):

        """
        An ethernet-controlled device.

        :param ip4_address: The IPv4 address of the device.
        :param port: The port number used to connect the device. Can be any number between 49152 and 65536.
        """

        self._ip4_address = ip4_address
        self._port = port
        self._socket = None


    @property
    def ip4_address(self):
        return self._ip4_address

    @property
    def port(self):
        return self._port

    def _query(self, query):
        query_bytes = query.encode('utf-8')
        socket_ps = self._socket
        socket_ps.sendall(query_bytes)
        reply_bytes = socket_ps.recv(4096)
        reply = reply_bytes.decode('utf-8').strip()
        time.sleep(0.3)
        return reply

    def _command(self, cmd):
        cmd_bytes = cmd.encode('utf-8')
        socket_ps = self._socket
        out = socket_ps.sendall(cmd_bytes)  # return None if successful
        time.sleep(0.3)
        return out

    def connect(self):
        try:
            socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_object.connect((self._ip4_address, self._port))
        except socket.error:
            print('ERROR: Could not connect to power supply. Please Check IPv4 address and try again. ')
            sys.exit()

        self._socket = socket_object

    def disconnect(self):
        socket_ps = self._socket
        socket_ps.close()


class PowerSupply:
    def __init__(
            self,
            MAX_voltage_limit=None,
            MAX_current_limit=None,
            number_of_channels=1,
            reset_on_startup=True
    ):

        """
        A benchtop programmable power supply.

        :param MAX_voltage_limit: -- Maximum voltage that the power supply can output based on hardware limitations.
        :param MAX_current_limit: -- Maximum current that the power supply can output based on hardware limitations.
        :param number_of_channels: - Specifies the number of programmable physical channels in the power supply.
        :param reset_on_startup: --- If true, will turn channels off and set the output voltage to zero.
        """

        self._MAX_voltage_limit = MAX_voltage_limit
        self._MAX_current_limit = MAX_current_limit
        self.number_of_channels = number_of_channels
        self.reset_on_startup = reset_on_startup

    @property
    def MAX_voltage_limit(self):
        return self._MAX_voltage_limit

    @property
    def MAX_current_limit(self):
        return self._MAX_current_limit


class SPD3303X(EthernetDevice, PowerSupply):
    """
    An ethernet-controlled power supply. Querys and commands based on manual for Siglent SPD3303X power supply.
    All voltages and currents are in Volts and Amps unless specified otherwise.
    """

    def __init__(
            self,
            ip4_address=None,
            port=5025,
            ch1_voltage_limit=32,
            ch1_current_limit=3.3,
            ch2_voltage_limit=32,
            ch2_current_limit=3.3,
            reset_on_startup=True
    ):

        """
        Initialize a new SPD3303X power supply.

        :param ip4_address: IPv4 address of the power supply.
        :param port: port used for communication. Siglent recommends to use 5025 for the SPD3303X power
            supply. For other devices, can use any between 49152 and 65536.
        :param ch1_voltage_limit: Set an upper limit on the voltage output of channel 1.
        :param ch1_current_limit: Set an upper limit on the current output of channel 1.
        :param ch2_voltage_limit: Set an upper limit on the voltage output of channel 2.
        :param ch2_current_limit: Set an upper limit on the current output of channel 2.
        :param reset_on_startup: If True, run a routine to set turn off the output of both channels and set the set


        Note that all channel voltage limits are software-based since the power supply does not have any built-in limit
        features. This means that the channel limits are checked before sending a command to the power supply. If the
        requested set voltage is higher than the channel voltage limit, the command will not go through.
        """

        self._ip4_address = ip4_address
        self._port = port
        self.number_of_channels = 2

        self._ch1_voltage_limit = ch1_voltage_limit
        self._ch1_current_limit = ch1_current_limit
        self._ch2_voltage_limit = ch2_voltage_limit
        self._ch2_current_limit = ch2_current_limit

        self._MAX_voltage_limit = 32
        self._MAX_current_limit = 3.3
        self.reset_on_startup = reset_on_startup

        self.connect()
        
        if self.reset_on_startup is True:
            self.reset_channels()

    def reset_channels(self):
        self.ch1_state = 'OFF'
        self.ch2_state = 'OFF'
        self.ch1_set_voltage = 0
        self.ch2_set_voltage = 0
        print('Both channels set to 0 and turned off')
    
# =============================================================================
#       Get methods
# =============================================================================    

# System
# =============================================================================
    @property
    def idn(self):
        qry = '*IDN?'
        return self._query(qry)
    
    @property
    def ip4_address(self):
        qry = 'IP?'
        return self._query(qry)
    
    @property    
    def system_status(self):
        """
        Query the power supply for its status. The output is a hex number represented in bytes. To be interpreted, it
        needs to be converted into a 10-digit binary number. Each digit in the binary number represents a state for
        some physical attribute of the power supply. Refer to the manual for the meaning of each digit.
        :return: 10-digit binary number as a string representing the status of the system
        """
        qry = 'system:status?'
        reply_hex_str = self._query(qry)   # hex number represented in bytes
        reply_bin_str = f'{int(reply_hex_str, 16):0>10b}'  # binary num as string
        return reply_bin_str

# Channel properties
# =============================================================================

    @property
    def ch1_state(self):
        """
        The 5th digit from right to left of the binary output from the system status query gives the state of channel 1,
        1 for on and 0 for off.
        :return:
        """
        one_zero = int(self.system_status[-5])
        return bool(one_zero)
    
    @property
    def ch2_state(self):
        one_or_zero = int(self.system_status_binary[-6])
        return bool(one_or_zero)
        
    @property
    def ch1_set_voltage(self):
        qry = 'CH1:voltage?'
        return self._query(qry)
            
    @property       
    def ch2_set_voltage(self):
        qry = 'CH2:voltage?'
        return self._query(qry)
        
    # def get_set_voltage(self, channel):  # TODO: Add format check for parameter channel
    #     qry = channel.upper() + ':voltage?'
    #     return self._query(qry)
    
    @property
    def ch1_actual_voltage(self):
        qry = 'measure:voltage? CH1'
        return self._query(qry)
            
    @property       
    def ch2_actual_voltage(self):
        qry = 'measure:voltage? CH2'
        return self._query(qry)
        
    # def get_actual_voltage(self, channel):  # TODO: Add format check for parameter channel
    #     qry = 'measure:voltage? ' + channel.upper()
    #     return self._query(qry)
        
    @property
    def ch1_set_current(self):
        qry = 'CH1:current?'
        return self._query(qry)
        
    @property
    def ch2_set_current(self):
        qry = 'CH2:current?'
        return self._query(qry)
        
    # def get_set_current(self, channel):  # TODO: Add format check for parameter channel
    #     qry = channel.upper() + ':current?'
    #     return self._query(qry)
    
    @property
    def ch1_actual_current(self):
        qry = 'measure:current? CH1'
        return self._query(qry)
            
    @property       
    def ch2_actual_current(self):
        qry = 'measure:current? CH2'
        return self._query(qry)
        
    # def get_actual_current(self, channel):  # TODO: Add format check for parameter channel
    #     qry = 'measure:current? ' + channel.upper()
    #     return self._query(qry)

# channel limits
# =============================================================================

    @property     
    def ch1_voltage_limit(self):
        return self._ch1_voltage_limit
        
    @property
    def ch1_current_limit(self):
        return self._ch1_current_limit
    
    @property     
    def ch2_voltage_limit(self):
        return self._ch2_voltage_limit
        
    @property
    def ch2_current_limit(self):
        return self._ch2_current_limit
        
# =============================================================================
#       Set methods
# =============================================================================

# Channel properties
# =============================================================================

    @ch1_state.setter
    def ch1_state(self, state):
        cmd = 'Output CH1,' + state.upper()
        self._command(cmd)
        
    @ch2_state.setter
    def ch2_state(self, state):
        cmd = 'Output CH2,' + state.upper()
        self._command(cmd)
    
    @ch1_set_voltage.setter
    def ch1_set_voltage(self, volts):
        if volts <= self._ch1_voltage_limit:
            cmd = 'CH1:voltage ' + str(volts)
            self._command(cmd)
        else:
            print('CH1 voltage not set. \
                  New voltage is higher than ch1 voltage limit.')

    @ch2_set_voltage.setter
    def ch2_set_voltage(self, volts):
        if volts <= self._ch2_voltage_limit:
            cmd = 'CH2:voltage ' + str(volts)
            self._command(cmd)
        else:
            print('CH2 voltage not set. \
                  New voltage is higher than ch1 voltage limit.')

    # def set_voltage(self, channel, volts):  # TODO: Add voltage limiter based on the current channel's voltage limit
    #     cmd = channel.upper() + ':voltage ' + str(volts)
    #     self._command(cmd)
    
    @ch1_set_current.setter
    def ch1_set_current(self, amps):
        if amps <= self._ch1_current_limit:
            cmd = 'CH1:current ' + str(amps)
            self._command(cmd)
        else:
            print('CH1 current not set. \
                  New voltage is higher than ch1 voltage limit.')

    @ch2_set_current.setter
    def ch2_set_current(self, amps):
        if amps <= self._ch2_current_limit:
            cmd = 'CH2:current ' + str(amps)
            self._command(cmd)
        else:
            print('CH2 current not set. \
                  New voltage is higher than ch1 voltage limit.')
    
    # def set_current(self, channel, amps):  # TODO: Add current limiter based on the current channel's current limit
    #     cmd = channel.upper() + ':current ' + str(amps)
    #     self._command(cmd)

# channel limits
# =============================================================================

    @ch1_voltage_limit.setter
    def ch1_voltage_limit(self, volts):
        if volts > self._MAX_voltage_limit or volts <= 0:
            print('Voltage limit not set. \
                  New voltage limit is not allowed by the power supply')                  
        elif volts < self.ch1_set_voltage:
            print('Voltage limit not set. \
                  New voltage limit is lower than present ch1 voltage')
        else:    
            self._ch1_voltage_limit = volts
    
    @ch1_current_limit.setter
    def ch1_current_limit(self, amps):
        if amps > self._MAX_current_limit or amps <= 0:
            print('Current limit not set. \
                  New voltage limit is not allowed by the power supply')                  
        elif amps < self.ch1_set_current:
            print('Current limit not set. \
                  New current limit is lower than present ch1 current')
        else:    
            self._ch1_current_limit = amps
            
    @ch2_voltage_limit.setter
    def ch2_voltage_limit(self, volts):
        if volts > self._MAX_voltage_limit or volts <= 0:
            print('Voltage limit not set. New voltage limit is not \
                   allowed by the power supply')
        elif volts < self.ch2_set_voltage:
            print('Voltage limit not set. New voltage limit is lower \
                  than present ch2 voltage')
        else:    
            self._ch1_voltage_limit = volts
    
    @ch2_current_limit.setter
    def ch2_current_limit(self, amps):
        if amps > self._MAX_current_limit or amps <= 0:
            print('Current limit not set. New voltage limit is not \
                  allowed by the power supply')
        elif amps < self.ch1_set_current:
            print('Current limit not set. New current limit is lower \
                  than present ch2 current')
        else:    
            self._ch2_current_limit = amps

    
def testing_EthernetPowerSupply():

    SPD3303X_1 = SPD3303X('10.176.42.121', 5025)
    print(SPD3303X_1.idn)
    print(SPD3303X_1.ip4_address)
    print(SPD3303X_1.system_status_binary)
    print()
    
    input('Press enter to set ch1 to 3.45V, and ch2 to 1.51V')
    SPD3303X_1.ch1_set_voltage = 3.45
    SPD3303X_1.ch2_set_voltage = 1.51
    print('CH1 and CH2 set voltages are:', SPD3303X_1.ch1_set_voltage, SPD3303X_1.ch2_set_voltage)
    print('CH1 and CH2 set currents are:', SPD3303X_1.ch1_set_current, SPD3303X_1.ch2_set_current)
    print('CH1 and CH2 actual voltages are:', SPD3303X_1.ch1_actual_voltage, SPD3303X_1.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', SPD3303X_1.ch1_actual_current, SPD3303X_1.ch2_actual_current)
    print()
    
    input('Press enter to turn ch1 on, wait 5 sec, then off. Repeat for ch2.')
    SPD3303X_1.ch1_state = 'ON'
    print('CH1 state is:', str(SPD3303X_1.ch1_state))
    time.sleep(5)
    SPD3303X_1.ch1_state = 'OFF'
    print('CH1 state is:', str(SPD3303X_1.ch1_state))
    SPD3303X_1.ch2_state = 'ON'
    print('CH2 state is:', str(SPD3303X_1.ch2_state))
    time.sleep(5)
    SPD3303X_1.ch2_state = 'OFF'
    print('CH2 state is:', str(SPD3303X_1.ch2_state))
    time.sleep(5)
    print()
    
    input('press enter to turn both on for 5 seconds. Then turn both off.')
    SPD3303X_1.ch1_state = 'ON'
    SPD3303X_1.ch2_state = 'ON'
    time.sleep(5)
    print('CH1 and CH2 states are:', str(SPD3303X_1.ch1_state), str(SPD3303X_1.ch2_state))
    print('CH1 and CH2 set voltages are:', SPD3303X_1.ch1_set_voltage, SPD3303X_1.ch2_set_voltage)
    print('CH1 and CH2 set currents are:', SPD3303X_1.ch1_set_current, SPD3303X_1.ch2_set_current)
    print('CH1 and CH2 actual voltages are:', SPD3303X_1.ch1_actual_voltage, SPD3303X_1.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', SPD3303X_1.ch1_actual_current, SPD3303X_1.ch2_actual_current)
    time.sleep(5)
    SPD3303X_1.ch1_state = 'OFF'
    SPD3303X_1.ch2_state = 'OFF'
    print('CH1 and CH2 states are:', str(SPD3303X_1.ch1_state), str(SPD3303X_1.ch2_state))
    print('CH1 and CH2 set voltages are:', SPD3303X_1.ch1_set_voltage, SPD3303X_1.ch2_set_voltage)
    print('CH1 and CH2 set currents are:', SPD3303X_1.ch1_set_current, SPD3303X_1.ch2_set_current)
    print('CH1 and CH2 actual voltages are:', SPD3303X_1.ch1_actual_voltage, SPD3303X_1.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', SPD3303X_1.ch1_actual_current, SPD3303X_1.ch2_actual_current)
    print('CH1 and CH2 voltage limits are:', SPD3303X_1.ch1_voltage_limit, SPD3303X_1.ch2_voltage_limit)
    print('CH1 and CH2 current limits are:', SPD3303X_1.ch1_current_limit, SPD3303X_1.ch2_current_limit)
    print('MAX voltage and current limits are:', SPD3303X_1.MAX_voltage_limit, SPD3303X_1.MAX_current_limit)
    SPD3303X_1.reset_channels()
    SPD3303X_1.disconnect()


def main():
    testing_EthernetPowerSupply()


if __name__ == '__main__':
    main()
