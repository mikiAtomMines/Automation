"""
Created on Fri Mar 11 12:53:39 2022

@author: Sebastian Miki-Silva
"""

import socket # for sockets
import sys # for exit
import time # for sleep


class EthernetPowerSupply:
    def __init__(self, ip4_address=None, port=50000, MAX_voltage=1000, MAX_current=100, reset_channels=True):
        self._ip4_address = ip4_address
        self._port = port
        self._MAX_voltage_limit = MAX_voltage
        self._MAX_current_limit = MAX_current
        self._ch1_voltage_limit = MAX_voltage
        self._ch1_current_limit = MAX_current
        self._ch2_voltage_limit = MAX_voltage
        self._ch2_current_limit = MAX_current
        
        try:
            socket_ps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_ps.connect((self._ip4_address, self._port))
        except socket.error:
            print('ERROR: Could not connect to power supply')
            sys.exit()
            
        self._socket = socket_ps
        
        if reset_channels:
            self.reset_channels()
        
    def __query(self, query):
        query_bytes = query.encode('utf-8')
        socket_ps = self._socket
        socket_ps.sendall(query_bytes)
        reply_bytes = socket_ps.recv(4096)
        reply = reply_bytes.decode('utf-8').strip()
        time.sleep(0.3)
        return reply
    
    def __command(self, cmd):
        cmd_bytes = cmd.encode('utf-8')
        socket_ps = self._socket
        out = socket_ps.sendall(cmd_bytes)  # return None if successful
        time.sleep(0.3)
        return out
    
    def reset_channels(self):
        self.ch1_state='OFF'
        self.ch2_state='OFF'
        self.ch1_set_voltage = 0
        self.ch2_set_voltage = 0
        print('Both channels set to 0 and turned off')
        
    def disconnect(self):
        socket_ps = self._socket
        socket_ps.close()
    
# =============================================================================
#       Get methods
# =============================================================================    
    
    @property
    def idn(self):
        qry = '*IDN?'
        return self.__query(qry)
    
    @property
    def ip4_address(self):
        qry = 'IP?'
        return self.__query(qry)
    
    @property    
    def system_status_binary(self):
        qry = 'system:status?'
        reply_hex_str = self.__query(qry)  #bytes representing hex number
        reply_bin_str = f'{int(reply_hex_str, 16):0>10b}'  # binary num as string
        return reply_bin_str
    
    @property
    def ch1_state(self):
        one_zero = int(self.system_status_binary[-5])
        return bool(one_zero)
    
    @property
    def ch2_state(self):
        one_zero = int(self.system_status_binary[-6])
        return bool(one_zero)
        
    @property
    def ch1_set_voltage(self):
        qry = 'CH1:voltage?'
        return self.__query(qry)
            
    @property       
    def ch2_set_voltage(self):
        qry = 'CH2:voltage?'
        return self.__query(qry)
        
    def get_set_voltage(self, channel):
        qry = channel.upper() + ':voltage?'
        return self.__query(qry)
    
    @property
    def ch1_actual_voltage(self):
        qry = 'measure:voltage? CH1'
        return self.__query(qry)
            
    @property       
    def ch2_actual_voltage(self):
        qry = 'measure:voltage? CH2'
        return self.__query(qry)
        
    def get_actual_voltage(self, channel):
        qry = 'measure:voltage? ' + channel.upper()
        return self.__query(qry)
        
    @property
    def ch1_set_current(self):
        qry = 'CH1:current?'
        return self.__query(qry)
        
    @property
    def ch2_set_current(self):
        qry = 'CH2:current?'
        return self.__query(qry)
        
    def get_set_current(self, channel):
        qry = channel.upper() + ':current?'
        return self.__query(qry)
    
    @property
    def ch1_actual_current(self):
        qry = 'measure:current? CH1'
        return self.__query(qry)
            
    @property       
    def ch2_actual_current(self):
        qry = 'measure:current? CH2'
        return self.__query(qry)
        
    def get_actual_current(self, channel):
        qry = 'measure:current? ' + channel.upper()
        return self.__query(qry)  
    
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

    @ch1_state.setter
    def ch1_state(self, state):
        cmd = 'Output CH1,' + state.upper()
        return self.__command(cmd)
        
    @ch2_state.setter
    def ch2_state(self, state):
        cmd = 'Output CH2,' + state.upper()
        return self.__command(cmd)
    
    @ch1_set_voltage.setter
    def ch1_set_voltage(self, volts):
        cmd = 'CH1:voltage ' + str(volts)
        return self.__command(cmd)

    @ch2_set_voltage.setter
    def ch2_set_voltage(self, volts):
        cmd = 'CH2:voltage ' + str(volts)
        return self.__command(cmd)
    
    def set_voltage(self, channel, volts):
        cmd = channel.upper() + ':voltage ' + str(volts)
        return self.__command(cmd)
    
    @ch1_set_current.setter
    def ch1_set_current(self, amps):
        cmd = 'CH1:current ' + str(amps)
        return self.__command(cmd)
    
    @ch2_set_current.setter
    def ch2_set_current(self, amps):
        cmd = 'CH2:current ' + str(amps)
        return self.__command(cmd)
    
    def set_current(self, channel, amps):
        cmd = channel.upper() + ':current ' + str(amps)
        return self.__command(cmd)

    @ch1_voltage_limit.setter
    def ch1_voltage_limit(self, volts):
        if volts > self._MAX_voltage_limit or volts <= 0:
            print('Voltage limit not set. \
                  New voltage limit is not allowed by the power supply')                  
        elif volts < self.ch1_set_voltage:
            print('Voltage limit not set. \
                  New voltage limit is lower than present ch1 voltage')
        else:    
            self.ch1_voltage_limit = volts
    
    @ch1_current_limit.setter
    def ch1_current_limit(self, amps):
        if amps > self._MAX_current_limit or amps <= 0:
            print('Current limit not set. \
                  New voltage limit is not allowed by the power supply')                  
        elif amps < self.ch1_set_current:
            print('Current limit not set. \
                  New current limit is lower than present ch1 current')
        else:    
            self.ch1_current_limit = amps
            
    @ch2_voltage_limit.setter
    def ch2_voltage_limit(self, volts):
        if volts > self._MAX_voltage_limit or volts <= 0:
            print('Voltage limit not set. New voltage limit is not \
                   allowed by the power supply')
        elif volts < self.ch2_set_voltage:
            print('Voltage limit not set. New voltage limit is lower \
                  than present ch2 voltage')
        else:    
            self.ch1_voltage_limit = volts
    
    @ch2_current_limit.setter
    def ch2_current_limit(self, amps):
        if amps > self._MAX_current_limit or amps <= 0:
            print('Current limit not set. New voltage limit is not \
                  allowed by the power supply')
        elif amps < self.ch1_set_current:
            print('Current limit not set. New current limit is lower \
                  than present ch2 current')
        else:    
            self.ch2_current_limit = amps
    
    
def main():
    SPD3303X = EthernetPowerSupply('10.176.42.121', 5025, MAX_voltage=32, MAX_current=3.2)
    print(SPD3303X.idn)
    print(SPD3303X.ip4_address)
    print(SPD3303X.system_status_binary)
    print()
    
    input('Press enter to set ch1 to 3.45V, and ch2 to 1.51V')
    SPD3303X.ch1_set_voltage=3.45
    SPD3303X.ch2_set_voltage=1.51
    print('CH1 and CH2 set voltages are:', SPD3303X.ch1_set_voltage, SPD3303X.ch2_set_voltage)
    print('CH1 and CH2 set currents are:', SPD3303X.ch1_set_current, SPD3303X.ch2_set_current)
    print('CH1 and CH2 actual voltages are:', SPD3303X.ch1_actual_voltage, SPD3303X.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', SPD3303X.ch1_actual_current, SPD3303X.ch2_actual_current)
    print()
    
    input('Press enter to turn ch1 on, wait 5 sec, then off. Repeat for ch2.')
    SPD3303X.ch1_state='ON'
    print('CH1 state is:', str(SPD3303X.ch1_state))
    time.sleep(5)
    SPD3303X.ch1_state='OFF'
    print('CH1 state is:', str(SPD3303X.ch1_state))
    SPD3303X.ch2_state='ON'
    print('CH2 state is:', str(SPD3303X.ch2_state))
    time.sleep(5)
    SPD3303X.ch2_state='OFF'
    print('CH2 state is:', str(SPD3303X.ch2_state))
    time.sleep(5)
    print()
    
    input('press enter to turn both on for 5 seconds. Then turn both off.')
    SPD3303X.ch1_state='ON'
    SPD3303X.ch2_state='ON'
    time.sleep(5)
    print('CH1 and CH2 states are:', str(SPD3303X.ch1_state), str(SPD3303X.ch2_state))
    print('CH1 and CH2 set voltages are:', SPD3303X.ch1_set_voltage, SPD3303X.ch2_set_voltage)
    print('CH1 and CH2 set currents are:', SPD3303X.ch1_set_current, SPD3303X.ch2_set_current)
    print('CH1 and CH2 actual voltages are:', SPD3303X.ch1_actual_voltage, SPD3303X.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', SPD3303X.ch1_actual_current, SPD3303X.ch2_actual_current)
    time.sleep(5)
    SPD3303X.ch1_state='OFF'
    SPD3303X.ch2_state='OFF'
    print('CH1 and CH2 states are:', str(SPD3303X.ch1_state), str(SPD3303X.ch2_state))
    print('CH1 and CH2 set voltages are:', SPD3303X.ch1_set_voltage, SPD3303X.ch2_set_voltage)
    print('CH1 and CH2 set currents are:', SPD3303X.ch1_set_current, SPD3303X.ch2_set_current)
    print('CH1 and CH2 actual voltages are:', SPD3303X.ch1_actual_voltage, SPD3303X.ch2_actual_voltage)
    print('CH1 and CH2 actual currents are:', SPD3303X.ch1_actual_current, SPD3303X.ch2_actual_current)
    
    SPD3303X.reset_channels()
    SPD3303X.disconnect()


if __name__ == '__main__':
    main()