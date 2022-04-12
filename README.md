Last updated: April 12, 2022.

Author: Sebastian Miki-Silva

#Automation
Library for automating experiment. The library has a hierarchy in place for the different classes. At the top, there is 
the classes from the file connection_type.py. These classes generalize methods for different connection types used by 
lab equipment such as TCP-IP, Serial, etc. Next in line are the classes from the file device_type.py. These classes 
distinguish between different lab equipment such as power supplies, gaussmeters, temperature daqs, etc. These classes
inherit from connection_type.py. Next are the classes from device_model.py, which are specific models for different lab
equipment such as the SPD3303X power supply, or the GM3 gaussmeter. These classes inherit from connection_type.py and 
from device_type.py. 

## Classes from connection_type.py
    SocketEthernetDevice(ip4_address=None, port=50000)
            
    Parameters
    ----------
    ip4_address : str
        The Ipv4 address of the device to connect. 
    port : int
        Connection port number. The port number is not device-specific and can be chosen to be any number between 49152 
        and 65536. Some manufacturers might recommend some other numbers.

This class connects to a device which uses TCP-IP protocol to communicate. The connection is established via a socket 
object from the socket library. To connect to the device, an IPv4 address must be provided. If provided, the object will 
automatically attempt to establish a connection. If none is provided, a connection must be made manually using the 
connect() method.

## Classes from device_type.py
These classes inherit from connection_type.py.

### PowerSupply
    PowerSupply(MAX_voltage_limit=None, MAX_current_limit=None, number_of_channels=1, 
                      reset_on_startup=True)
    Parameters
    ----------
    MAX_voltage_limit : float
        Maximum voltage in Volts that the power supply can output based on hardware.
    MAX_current_limit : float
        Maximum current in Amps that the power supply can output based on hardware limitations.
    number_of_channels : int
        Specifies the number of programmable physical channels in the power supply. Do not include any non-programmable 
        channel in this number.
    reset_on_startup : bool
        If true, will turn off all channels and set the output voltage to zero immediately after the connection with the
        device is made. 

This class represents any benchtop programmable power supply. It contains the maximum voltage and current values allowed 
by the hardware of the power supply. These attributes should not be used as voltage and current limit setters, as they 
are a property of the hardware and should remain constant unless the hardware is changed. 

### MCC_device

    MCC_Device(board_number=0)
        Parameters
        ----------
        board_number : int
            All MCC devices have a board number which can be configured using instacal. The instance of Web_Tc must
            match the board number of its associated device. Possible values from 0 to 99.
        ip4_address : str
            IPv4 address of the associated MCC device
        port : int
            Communication port to be used. Safely chose any number between 49152 and 65536.

This class represents any MCC device that is supported by the MCC universal library. To connect to the device 
automatically using instacal, a board number must be specified and must match the board number of the associated device. 
To establish a connection to the device using the MCC Universal Library API functions, an IPv4 address and port number
must be specified. Currently, the API functions have not been implemented so only a connection using instacal possible. 

        
## Classes for device_model.py
These classes inherit from connection_type.py and device_type.py.

### GM3
    class GM3(baudrate=115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1):
    def __init__(self, *args, **kwargs):
        super().__init__(baudrate=115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, *args, **kwargs)
        
    Parameters
    ----------
    port : str
        Device port name. Can be found on device manager. Example: COM3
    baudrate : int 
        The baudrate unique to this device.
    bytesize : int
        The size in bits of a single byte. 
    parity : serial.PARITY
        Unique to device. Possible values: PARITY_NONE, PARITY_EVEN, PARITY_ODD PARITY_MARK, PARITY_SPACE
    stopbits : serial.STOPBITS
        Number of stop bits. Possible values: STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
    timeout : int
        read timeout in seconds. Time that read() will wait for response before exiting.

    More parameters in documentation for serial.Serial class.

This class represents the GM3 gaussmeter by AlphaLabInc. Connects to the device using serial communication through USB. 

### SPD3303X
    SPD3303X(ip4_address=None, port=5025, ch1_voltage_limit=32, ch1_current_limit=3.3, ch2_voltage_limit=32, 
             ch2_current_limit=3.3, reset_on_startup=True):
    
    Parameters
    ----------
    ip4_address : str
        IPv4 address of the power supply.
    port : int
        port used for communication. Siglent recommends to use 5025 for the SPD3303X power supply. For other devices,
        can use any between 49152 and 65536.
    ch1_voltage_limit : float
        Set an upper limit on the voltage output of channel 1.
    ch1_current_limit : float
        Set an upper limit on the current output of channel 1.
    ch2_voltage_limit : float
        Set an upper limit on the voltage output of channel 2.
    ch2_current_limit : float
        Set an upper limit on the current output of channel 2.
    reset_on_startup : bool 
        If True, run a routine to set turn off the output of both channels and set the set

This class represents the SPD3303X power supply by Siglent. Implements methods to set and read voltage and current for 
both programmable channels. Note that all channel voltage limits are software-based since the power supply does not have any built-in limit
features. This means that the channel limits are checked before sending a command to the power supply. If the
requested set voltage is higher than the channel voltage limit, the command will not go through.

### Web-Tc
    Web_Tc(ip4_address=None, port=54211, board_number=0, default_units='celsius')
        Parameters
        ----------
        ip4_address : string
            The current IPv4 address of the device. Can be found through instacal. For the Web_TC, the ip4_address is
            unused because the API functions that use it are not supported by this device.
        port : int
            The port number to be used. MCC recommends to use 54211. Port 80 is reserved for the web browser
            application. For the Web_TC, the port number is unused because the API functions that use it are not
            supported by this device.
        board_number : int
            All MCC devices have a board number which can be configured using instacal. The instance of Web_Tc must
            match the board number of its associated device. Possible values from 0 to 99.
        default_units : string
            the units in which the temperature is shown, unless specified otherwise in the method. Possible values
            (not case-sensitive):
            for Celsius                 celsius,               c
            for Fahrenheit              fahrenheit,            f
            for Kelvin                  kelvin,                k
            for calibrated voltage      volts, volt, voltage,  v
            for uncalibrated voltage    raw, none, noscale     r

This class represents the Web-TC temperature DAQ by MCC. Implements methods to read the temperature at the TC channels. 
Will implement I/O configuration methods in the future. 
    
    
