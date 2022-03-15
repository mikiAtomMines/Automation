"""
Created on Fri Mar 11 12:53:39 2022

@author: Sebastian Miki-Silva
"""

#TODO: fix usbtmc power supply class.

import socket
import usbtmc
import usb
import sys
import time


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


class UsbtmcPowerSupply:
    def __init__(self, id_vendor=None, id_product=None, MAX_voltage=1000, MAX_current=100, reset_channels=True):
        self._id_vendor = id_vendor
        self._id_product = id_product
        # self._MAX_voltage = MAX_voltage
        # self._MAX_current = MAX_current
        # self._ch1_voltage_limit = MAX_voltage
        # self._ch1_current_limit = MAX_current
        # self._ch2_voltage_limit = MAX_voltage
        # self._ch2_current_limit = MAX_current

        self._instrument = usbtmc.Instrument(id_vendor, id_product)

    def __query(self, query):
        reply = self._instrument.ask('*IDN?')
        return reply

    
def testing_EthernetPowerSupply():

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

def testing_UsbtmcPowerSupply():
    SPD3303X = UsbtmcPowerSupply(id_vendor=0xF4EC, id_product=0x1430)

def main():
    USBTMC_bInterfaceClass = 0xFE
    USBTMC_bInterfaceSubClass = 3
    USBTMC_bInterfaceProtocol = 0
    USB488_bInterfaceProtocol = 1

    USBTMC_MSGID_DEV_DEP_MSG_OUT = 1
    USBTMC_MSGID_REQUEST_DEV_DEP_MSG_IN = 2
    USBTMC_MSGID_DEV_DEP_MSG_IN = 2
    USBTMC_MSGID_VENDOR_SPECIFIC_OUT = 126
    USBTMC_MSGID_REQUEST_VENDOR_SPECIFIC_IN = 127
    USBTMC_MSGID_VENDOR_SPECIFIC_IN = 127
    USB488_MSGID_TRIGGER = 128

    USBTMC_STATUS_SUCCESS = 0x01
    USBTMC_STATUS_PENDING = 0x02
    USBTMC_STATUS_FAILED = 0x80
    USBTMC_STATUS_TRANSFER_NOT_IN_PROGRESS = 0x81
    USBTMC_STATUS_SPLIT_NOT_IN_PROGRESS = 0x82
    USBTMC_STATUS_SPLIT_IN_PROGRESS = 0x83
    USB488_STATUS_INTERRUPT_IN_BUSY = 0x20

    USBTMC_REQUEST_INITIATE_ABORT_BULK_OUT = 1
    USBTMC_REQUEST_CHECK_ABORT_BULK_OUT_STATUS = 2
    USBTMC_REQUEST_INITIATE_ABORT_BULK_IN = 3
    USBTMC_REQUEST_CHECK_ABORT_BULK_IN_STATUS = 4
    USBTMC_REQUEST_INITIATE_CLEAR = 5
    USBTMC_REQUEST_CHECK_CLEAR_STATUS = 6
    USBTMC_REQUEST_GET_CAPABILITIES = 7
    USBTMC_REQUEST_INDICATOR_PULSE = 64

    USB488_READ_STATUS_BYTE = 128
    USB488_REN_CONTROL = 160
    USB488_GOTO_LOCAL = 161
    USB488_LOCAL_LOCKOUT = 162

    USBTMC_HEADER_SIZE = 12

    RIGOL_QUIRK_PIDS = [0x04ce, 0x0588]

    def list_devices():
        "List all connected USBTMC devices"

        def is_usbtmc_device(dev):
            for cfg in dev:
                d = usb.util.find_descriptor(cfg, bInterfaceClass=USBTMC_bInterfaceClass,
                                             bInterfaceSubClass=USBTMC_bInterfaceSubClass)
                if d is not None:
                    return True

                if dev.idVendor == 0x1334:
                    # Advantest
                    return True

                if dev.idVendor == 0x0957:
                    # Agilent
                    if dev.idProduct in [0x2818, 0x4218, 0x4418]:
                        # Agilent U27xx modular devices in firmware update mode
                        # 0x2818 for U2701A/U2702A (firmware update mode on power up)
                        # 0x4218 for U2722A (firmware update mode on power up)
                        # 0x4418 for U2723A (firmware update mode on power up)
                        return True

            return False

        print(list(usb.core.find(find_all=True, custom_match=is_usbtmc_device)))

    list_devices()

if __name__ == '__main__':
    main()