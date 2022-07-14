Date created: March 14, 2022.

Author: Sebastian Miki-Silva

#Automation
Library for automating experiment. The library has a hierarchy in place for the different classes. At the top, there is 
the classes from the file connection_type.py. These classes have general methods for different connection types used by 
lab equipment such as TCP-IP. Next in line are the classes from the file device_type.py. These classes 
distinguish between different lab equipment such as power supplies, gaussmeters, temperature daqs, etc. Next are the 
classes from device_model.py, which are specific models for different lab equipment such as the SPD3303X power supply, 
or the GM3 gaussmeter. These classes inherit from connection_type.py and from device_type.py. 

## Classes from connection_type.py

---

### SocketEthernetDevice
    SocketEthernetDevice(ip4_address, port)
            
    Parameters
    ----------
    ip4_address : str
        The Ipv4 address of the device to connect. 
    port : int
        Connection port number. The port number is not device-specific and can be chosen to be any number between 49152 
        and 65536. Some manufacturers might recommend some other numbers.

This class connects to a device through a socket connection to communicate. To connect to the device, an IPv4 address 
must be provided. The object will automatically attempt to establish a connection. If it fails, it will reattempt 10 
times.

#### Properties
- ip4_address : str
- port : int

#### Methods
- _query(qry)
  - :param qry: bytes
  - :returns: bytes or error string
  
  
- _command(cmd)
  - :param cmd: bytes
  - :returns: None or error string


- connect()
  - :returns: None
  - :raises: OSError

- disconnect()
  - :returns: None


## Classes from device_type.py

---

### PowerSupply
    PowerSupply(
            MAX_voltage_limit,
            MAX_current_limit,
            channel_voltage_limits=None,
            channel_current_limits=None,
            number_of_channels=1,
            reset_on_startup=True
    ):

        """
        Parameters
        ----------
        MAX_voltage_limit : float
            Maximum voltage that the power supply can output based on hardware limitations.
        MAX_current_limit : float
            Maximum current that the power supply can output based on hardware limitations.
        channel_voltage_limits : list of float, optional
            list containing the individual channel limits for the set voltage. The set voltage of a channel cannot 
            exceed its limit voltage. The 0th item corresponds to the limit of channel 1, 1st item to channel 2, 
            and so on. If set to None, a list is created with MAX_voltage_limit as the limit for all channels.
        channel_current_limits : list of float
            list containing the individual channel limits for the set current. The set current of a channel cannot 
            exceed its limit current. The 0th item corresponds to the limit of channel 1, 1st item to channel 2, 
            and so on.If set to None, a list is created with MAX_voltage_limit as the limit for all channels.
        number_of_channels : int
            the number of physical programmable channels in the power supply.
        reset_on_startup : bool
            If set to true, will run a method to set the set voltage and current to 0.
        """

This class represents any benchtop programmable power supply. It contains the maximum voltage and current values allowed 
by the hardware of the power supply. These attributes should not be used as voltage and current limit setters and should
remain constant unless the hardware is changed. 

#### Properties

##### Getters

- idn : str
- MAX_voltage_limit : float  
- MAX_current_limit : float
- channel_voltage_limits : float
- channel_current_limits : float
- number_of_channels : int


#### Methods

Note that all these methods are placeholders for the actual methods to be used in the device_models.py classes.

- check_valid_channel(channel)
  - :param channel: int >= 1
  - :returns: None or error string
  

- get_channel_state(channel)
  - :param channel: int >= 1
  - :returns: bool or error string


- set_channel_state(channel, state)
  - :param channel: int >= 1
  - :param state: bool
  - :returns: None or error string

- get_setpoint_voltage(channel)
  - :param channel: int >= 1
  - :returns: float or error string


- set_voltage(channel, volts)
  - :param channel: int >= 1
  - :param volts: float
  - :returns: None or error string


- get_actual_voltage(channel)
  - :param channel: int >= 1
  - :returns: float or error string

- get_setpoint_current(channel)
  - :param channel: int >= 1
  - :returns: float or error string

- set_current(channel, amps)
  - :param channel: int >= 1
  - :param amps: float
  - :returns: None or error string


- get_actual_current(channel)
  - :param channel: int >= 1
  - :returns: float or error string


- get_voltage_limit(channel)
  - :param channel: int >= 1
  - :returns: float or error string
  

- set_voltage_limit(channel, volts)
  - :param channel: int >= 1
  - :param volts: float
  - :returns: None or error string


- get_current_limit(channel)
  - :param channel: int >= 1
  - :returns: float or error string

    
- set_current_limit(channel, amps)
  - :param channel: int >= 1
  - :param amps: float
  - :returns: None or error string


- set_all_channels_voltage_limit(volts)
  - :param volts: float
  - :returns: None or error string


- set_all_channels_current_limit(amps)
  - :param amps: float
  - :returns: None or error string


- zero_all_channels
  - :returns: None or error string


### MccDeviceWindows

    MccDeviceWindows(board_number, ip4_address=None, port=None, default_units='celsius')
        Parameters
        ----------
        board_number : int
            All MCC devices have a board number which can be configured using instacal. The instance of Web_Tc must
            match the board number of its associated device. Possible values from 0 to 99.
        ip4_address : str, optional
            IPv4 address of the associated MCC device
        port : int, optional
            Communication port to be used. Safely chose any number between 49152 and 65536.
        default_units : str
            units used for temperature readings. Possible values: celsius or c, fahrenheit or f, and kelvin or k.

This class represents any MCC device that is supported by the MCC universal library in Windows. To connect to the device 
without using an IP address, instacal needs to be installed and the board number must match the board number of the 
according device. If an IPv4 address and port number are given, the class will try to establish a connection to the 
device using the MCC Universal Library API functions automatically which do not require instalcal.  


#### Properties

##### Getters

- idn : str
- board_number : int
- ip4_address : str
- port : int
- model : str
- mac_address : str
- unique_id : str
- serial_number : str
- number_temp_channels : int
- number_io_channels : int
- number_ad_channels : int
- number_da_channels : int
- clock_frequency_MHz : int
- default_units : str
- thermocouple_type_ch<n> : str
- temp_ch\<n> : float
  - 0 <= n <= 7

##### Setters

- board_number : int
- ip4_address : str
- port : int
- default_units : str
- thermocouple_type_ch\<n> : str
  - 0 <= n <= 7


#### Methods

- get_TempScale_units(units)
  - :param units: str
  - :returns: mcculw.enums.TempScale


- check_valid_units(units)
  - :param units: str
  - :returns: None or error string

- check_valid_temp_channel(channel)
  - :param channel: int
  - :returns: None or error string


- connect(ip=None, port=None)
  - :param ip: str
  - :param port: int
  - :returns: None or error string


- disconnect()


- get_temp(channel_n=0, units=None, averaged=True)
  - :param channel_n: int
  - :param units: str or None
  - :param averaged: bool
  - :returns: float or error string


- get_temp_all_channels(units=None, averaged=True)
  - :param units: str
  - :param averaged: bool
  - :returns: list of (floats or None) or error string


- get_temp_scan(low_channel=0, high_channel=7, units=None, averaged=True)
  - :param low_channel: int <= high_channel
  - :param high_channel: int >= low_channel
  - :param units: str or None
  - :param averaged: bool
  - :returns: list of (floats or None) or error string


- get_thermocouple_type(channel)
  - :param channel: int
  - :returns: str or error string


- set_thermocouple_type(channel, new_tc_type)
  - :param channel: int
  - :param new_tc_type: str
  - :returns: None or error string


### MccDeviceLinux

    MccDeviceLinux(
                ip4_address,
                port=54211,
                default_units='celsius'
    ):
        """
        Class for an MCC Device. Use only on Linux machines.

        Parameters
        ----------
        ip4_address : str
            IPv4 address of device in format '255.255.255.255'
        port : int
            communications port number.
        default_units : {'c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin', 'v', 'volts', 'r', 'raw'}
            default units to use for temperature measurements
        """

Similar to MccDeviceWindows, but for Linux machines. This class connects only through a TCP/IP connection. There is no 
instalcal for Linux.

#### Properties

##### Getters

- idn : str
- ip4_addres : str
- number_temp_channels : int
- default_units : str
- temp_ch\<n>
  - 0 <= n <= 7

##### Getters
- default_units : str


#### Methods

- get_TempScale_units(units)
  - :param units: str
  - :returns: int or None


- check_valid_units(units)
  - :param units: str
  - :returns: None or error string


- check_valid_temp_channel(channel)
  - :param channel: int
  - :returns: None or error string


- get_temp(channel_n=0, units=None)
  - :param channel_n: int
  - :param units: str or None
  - :returns: float or error string


- get_temp_scan(low_channel=0, high_channel=7, units=None)
  - :param low_channel: int <= high_channel
  - :param high_channel: int >= low_channel
  - :returns: list of float or error string
  

- get_thermocouple_type(channel)
  - :param channel: int
  - :returns: str or error string


- set_thermocouple_type(channel, new_tc)
  - :param channel: int
  - :param new_tc: str
  - :returns: None or str
  

### Heater

    Heater( 
            idn=None, 
            MAX_temp=float('inf'), 
            MAX_volts=float('inf'), 
            MAX_current=float('inf'), 
    ):
        """
        Parameters
        ----------
        idn : str
            Identification string. 
        MAX_temp : float
            The maximum possible value for set temp. Should be based on the physical limitations of the heater.
            Should be used as a safety mechanism so the set temperature is never set higher than what the hardware
            allows. Default is set to infinity. 
        MAX_volts : float
            The maximum allowed value for voltage across the heater. Analogous to MAX_temp.
        MAX_current : float
            The maximum allowed value for the current going through the heater. Analogous to MAX_temp and MAX_voltage.
        """

This class stores the physical parameters of a heater. Used in the HeaterAssembly and the Oven class to set voltage, 
current, and temperature limits. 
        

## Classes from device_model.py

---

These classes inherit from connection_type.py and device_type.py.

### GM3
    GM3(port, tmout):
        
    Parameters
    ----------
    port : str
        Device port name. Can be found on device manager. Example: COM3
    tmout : float
        read timeout in seconds. Time that read() will wait for response before exiting.
    

This class represents the GM3 gaussmeter by AlphaLabInc. Connects to the device using serial communication through USB. 

#### Properties

- properties
- settings

#### Methods

- query
- command
- get_instantenous_data
- get_instantenous_data_t0

### SPD3303X
    SPD3303X(ip4_address, port=5025, ch1_voltage_limit=32, ch1_current_limit=3.3, ch2_voltage_limit=32, 
             ch2_current_limit=3.3, reset_on_startup=True):

        Parameters
        ----------
        ip4_address : str
            IPv4 address of the power supply.
        port : int
            port used for communication. Siglent recommends to use 5025 for the SPD3303X power supply. For other
            devices, can use any between 49152 and 65536.
        channel_voltage_limits : list
            Set an upper limit on the set voltage of the channels. Entry 0 represents channel 1, entry 1 represents 
            channel 2, and so on.
        channel_current_limits : list
            Set an upper limit on the set current of the channels. Entry 0 represents channel 1, entry 1 represents 
            channel 2, and so on.
        zero_on_startup : bool
            If True, run a routine to set turn off the output of both channels and set the set

This class represents the SPD3303X power supply by Siglent. This class inherits from SocketEthernetDevice and from 
PowerSupply classes. Implements methods to set and read voltage and current for both programmable channels. Note that 
all channel voltage limits are software-based since the power supply does not have any built-in limit features. This 
means that the channel limits are checked before sending a command to the power supply. If the requested set voltage is 
higher than the channel voltage limit, the command will not go through.

#### Properties

##### Getters

- idn : str
- ip4_address : str 
- system_status : str
- ch1_state : bool
- ch2_state : bool
- ch1_set_voltage : float
- ch2_set_voltage : float
- ch1_actual_voltage : float
- ch2_actual_voltage : float
- ch1_set_current : float
- ch2_set_current : float
- ch1_actual_current : float
- ch2_actual_current : float
- ch1_voltage_limit : float
- ch1_current_limit : float
- ch2_voltage_limit : float
- ch2_current_limit : float

##### Setters

- ch1_state : bool
- ch2_state : bool
- ch1_set_voltage : float
- ch2_set_voltage : float
- ch1_set_current : float
- ch2_set_current : float
- ch1_voltage_limit : float
- ch1_current_limit : float
- ch2_voltage_limit : float
- ch2_current_limit : float

#### Methods

These are the methods that are explicitly defined under the class. More methods can be found under the PowerSupply 
class.


- get_channel_state(channel)
  - :param channel: int
  - :returns: bool or error string

  
- set_channel_state(channel, state)
  - :param channel: int
  - :param state: bool
  - :returns: None or error string


- get_setpoint_voltage(channel)
  - :param channel: int
  - :returns: float or error string


- set_voltage(channel, volts)
  - :param channel: int
  - :param volts: float
  - :returns: None or error string

  
- get_actual_voltage(channel)
  - :param channel: int
  - :returns: float or error string

  
- get_setpoint_current(channel)
  - :param channel: int
  - :returns: float or error string

  
- set_current(channel, amps)
  - :param channel: int
  - :param amps: float
  - :returns: None or error string


- get_actual_current(channel)
  - :param channel: int
  - :returns: float or error string

  

### Mr50040

    Mr50040(
            ip4_address=None,
            port=5025,
            zero_on_startup=True
    ):

        Parameters
        ----------
        ip4_address : str
            IPv4 address of the power supply.
        port : int
            port used for communication. Siglent recommends to use 5025 for the SPD3303X power supply. For other
            devices, can use any between 49152 and 65536.
        zero_on_startup : bool
            If True, run a routine to set turn off the output of both channels and set the set

This class represents the B&K Precision MR50040 power supply. This class inherits from the SocketEthernetDevice and 
PowerSupply classes. 

#### Properties

##### Getters

- idn : str
- is_current_limited : bool
- is_voltage_limited : bool
- error_code : int
- error_message : str
- voltage : float
- current : float
- power : float

#### Methods

- get_error_code()
  - :returns: int


- get_error()
  - :returns: str


- get_status_byte()
  - :returns: int or error string


- get_cc_to_cv_protection_state()
  - :returns: bool or error string


- set_cc_to_cv_protection_state(state)
  - :param state: bool 
  - :returns: None or error string


- get_cv_to_cc_protection_state()
  - :returns: bool or error string


- set_cv_to_cc_protection_state(state)
  - :param state: bool 
  - :returns: None or error string


- get_channel_state(channel=1)
  - :param channel: int=1, must be equal to 1
  - :returns: bool or error string


- set_channel_state(channel=1, state=None)
  - :param channel: int=1, must be equal to 1
  - :param state: bool
  - :returns: None or error string


- get_setpoint_voltage(channel=1)
  - :param channel: int=1, must be equal to 1
  - :returns: float or error string


- set_voltage(channel=1, volts=None)
  - :param channel: int=1, must be equal to 1
  - :param volts: float
  - :returns: None or error string


- get_actual_voltage(channel=1)
  - :param channel: int=1, must be equal to 1
  - :returns: float or error string


- get_setpoint_current(channel=1)
  - :param channel: int=1, must be equal to 1
  - :returns: float or error string


- set_current(channel=1, amps)
  - :param channel: int=1, must be equal to 1
  - :param amps: float
  - :returns: None or error string


- get_actual_current(channel=1)
  - :param channel: int=1, must be equal to 1
  - :returns: float or error string


- get_setpoint_power()
  - :returns: float or error string


- get_actual_power()
  - :returns: float or error string


- get_voltage_limit(channel=1)
  - :param channel: int=1, must be equal to 1
  - :returns: float or error string


- set_voltage_limit(channel=1, volts)
  - :param channel: int=1, must be equal to 1
  - :param volts: float
  - :returns: None or error string


- get_current_limit(channel=1)
  - :param channel: int=1, must be equal to 1
  - :returns: float or error string

  
- set_current_limit(channel=1, amps)
  - :param channel: int=1, must be equal to 1
  - :param amps: float
  - :returns: None or error string
  

### ETcWindows

      ETcWindows(board_number, ip4_address=None, port=54211, default_units='celsius'):

            Parameters
            ----------
            ip4_address : string
                The current IPv4 address of the device. Can be found through instacal. For the Web_TC,
                the ip4_address is unused because the API functions that use it are not supported by this device.
            port : int
                The port number to be used. MCC recommends to use 54211. Port 80 is reserved for the web browser
                application. For the Web_TC, the port number is unused because the API functions that use it are not
                supported by this device.
            board_number : int
                All MCC devices have a board number which can be configured using instacal. The instance of Web_Tc must
                match the board number of its associated device. Possible values from 0 to 99.
            default_units : string
                the units in which the temperature is shown, unless specified otherwise in the method. Possible values
                (not
                case-sensitive):
                for Celsius                 celsius,               c
                for Fahrenheit              fahrenheit,            f
                for Kelvin                  kelvin,                k
                for calibrated voltage      volts, volt, voltage,  v
                for uncalibrated voltage    raw, none, noscale     r
            
Inherits from MccDeviceWindows. 

#### Methods

- config_io_channel(chan, direction)
  - :param chan: 0 <= int <= 7
  - :param direction: str {'in', 'i', 'out', 'o'}


- get_bit(chan)
  - :param chan: 0 <= int <= 7


- set_bit(chan, out)
  - :param chan: 0 <= int <= 7
  - :param out: int {1, 0}


- config_io_byte(direction)
  - :param direction: str {'in', 'i', 'out', 'o'}


- get_byte()


- set_byte(val)
  - :param val: int



### EtcLinux

     ETcLinux(ip4_address, port=54211, default_units='celsius')

         Parameters
         ----------
         ip4_address : str
             IPv4 address of device in format '255.255.255.255'
         port : int
             communications port number.
         default_units : {'c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin', 'v', 'volts', 'r', 'raw'}
             default units to use for temperature measurements
        """
Inherits everything from MccDeviceLinux


### WebTc
    WebTc(ip4_address=None, port=54211, board_number=0, default_units='celsius')
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

This class represents the Web-TC temperature DAQ by MCC. Inherits from MccDeviceWindows. 


### Model8742
    Model8742(ip4_address=None, port=23, number_of_channels=4)
        """
        Parameters
        ----------
        ip4_address : str
        port : int
            Model8742 uses Telnet therefore need to use port 23.
        number_of_channels : int
            number of physical motor channels

        """

Inherits from SocketEthernetDevice. Represents the Newport Model8742 picomotor. 
#### Properties

##### Getters

- idn : str
- mac_address : str
- hostname : str
- position_ch\<n> : int
  - 1 <= n <= 4
- setpoint_position_ch\<n> : int
  - 1 <= n <= 4
- velocity_ch\<n> : int
  - 1 <= n <= 4

##### Setters

- setpoint_position_ch\<n> : int
  - 1 <= n <= 4
- velocity_ch\<n> : int
  - 1 <= n <= 4


#### Methods
- restart_controller()


- save_settings()


- load_settings()


- _reset_factory_settings()


- motion_done(chan)
  - :param chan: 1 <= int <= 4
  - :returns: bool. True for motion stopped. False for motion is ongoing. 


- get_instant_position(chan)
  - :param chan: 1 <= int <= 4
  - :returns: int


- get_set_position(chan)
  - :param chan: 1 <= int <= 4
  - :returns: int


- get_velocity(chan)
  - :param chan: 1 <= int <= 4
  - :returns: int

  
- get_acceleration(chan)
  - :param chan: 1 <= int <= 4
  - :returns: int


- hard_stop_all()


- soft_stop(chan)
  - :param chan: 1 <= int <= 4. Optional


- set_origin(chan)
  - :param chan: 1 <= int <= 4

  
- set_set_position(chan, position)
  - :param chan: 1 <= int <= 4
  - :param position: int


- displace(chan, dis)
  - :param chan: 1 <= int <= 4
  - :param dis: int


- move_indefinetely(chan)
  - :param chan: 1 <= int <= 4


- set_velocity(chan, vel)
  - :param chan: 1 <= int <= 4
  - :param vel: int


- set_acceleration(chan, acc)
  - :param chan: 1 <= int <= 4
  - :param acc: int


### Srs100


### Ell14k






## Classes from assemblies.py

### HeaterAssembly

    HeaterAssembly(
            supply_and_channel,
            daq_and_channel,
            heater=None,
    ):
        """
        A heater assembly composed of a heater, a temperature measuring device, and a power supply. This assembly
        should only need to be used by the pid_controller_server.py file running on a BeagleBone Black. This represents
        the "body" of an Oven object, while the BeagleBoneBlack is the "brain". 

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

#### Properties

##### Getters
- Assembly:
  - MAX_voltage : float
  - MAX_current : float
  - MAX_set_temp : float
  - is_regulating : bool


- Power supply:
  - power_supply : str
  - supply_setpoint_voltage : float
  - supply_setpoint_current : float
  - supply_actual_voltage : float
  - supply_actual_current : float
  - supply_voltage : float
  - supply_current : float
  - supply_voltage_limit : float
  - supply_current_limit : float
  - supply_channel_state : bool
  - supply_channel : int
  - supply_number_of_channels : int
  - supply_MAX_voltage : float
  - supply_MAX_current : float


- Temperature DAQ:
  - daq : str
  - temp : float
  - daq_channel : int
  - tc_type : str
  - temp_units : str
  - daq_number_of_temp_channels : int


- PID settings:
  - pid_settings : str
  - pid_setpoint : float
  - pid_limits : tuple of floats
  - pid_sample_time : float
  - pid_kp : float
  - pid_ki : float
  - pid_kd : float

##### Setters
- PID Settigns:
  - pid_kp : float
  - pid_ki : float
  - pid_kd : float


#### Methods

###### Assembly
- reset_pid()
  

- reset_pid_limits()

  
- stop_supply()

  
- reset_power_supply()

  
- ready_power_supply()


- reset_assembly()


- ready_assembly()


- stop()


- update_supply()
  - :returns: float


- disconnect_assembly()

###### Power supply

- get_supply_channel()
  - :returns: int


- set_supply_channel(new_ch)
  - :param new_ch: int
  - :returns: None or error string
  

- get_supply_channel_state()
  - :returns: bool


- set_supply_channel_state(state)
  - :param state: bool
  - :returns: None or error string


- get_supply_setpoint_voltage()
  - :returns: float


- set_supply_voltage(volts)
  - :param volts: float
  - :returns: None or error string


- get_supply_actual_voltage()
  - :returns: float


- get_supply_setpoint_current()
  - :returns: float


- set_supply_current(amps)
  - :param amps: float
  - :returns: None or error string


- get_supply_actual_current()
  - :returns: float
  

- get_supply_voltage_limit()
  - :returns: float


- set_supply_voltage_limit(volts)
  - :param volts: float
  - :returns: None or error string


- get_supply_current_limit()
  - :returns: float


- set_supply_current_limit(amps)
  - :param amps: float
  - :returns: None or str

###### Temperature DAQ

- get_daq_temp()
  - :returns: float


- get_daq_channel()
  - :returns: int


- set_daq_channel(new_ch)
  - :param new_ch: int
  - :returns: None or error string
  
  
- get_daq_tc_type()
  - :returns: str


- set_daq_tc_type(new_tc)
  - :param new_tc: str
  - :returns: None or error string


- get_daq_temp_units()
  :returns: str


- set_daq_temp_units(new_units)
  - :param new_units: str
  - :returns: None or error string

###### PID Settings

- get_pid_setpoint()
  - :returns: float


- set_pid_setpoint?(new_set)
  - :param new_set: float
  - :returns: None or error string


- get_pid_limits()
  - :returns: tuple of floats


- get_pid_sample_time()
  - :returns: float


- set_pid_sample_time(seconds)
  - :param seconds: float
  - :returns: None or error string


- get_pid_regulation()
  - :returns: bool


- set_pid_regulation(reg)
  - :param reg: bool
  - :returns: None or error string


### Oven
    Oven(ip4_address, port=65432)
      
    """
    The Oven class refers to the combination of a BeagleBoneBlack rev C and a number of HeaterAssembly objects. A single
    HeaterAssembly object is composed of a power supply, a temperature daq, and a physical heater. The
    BeagleBoneBlack acts as the "brain" of the oven, commanding the different HeaterAssembly objects.
    
    Parameters
    ----------
    ip4_address : str
        IP v4 address of the BeagleBoneBlack that is controlling the HeaterAssembly objects part of the 
        physical oven.
    port : int
        port number. Default to 65432
    """

#### Methods

###### Oven
- get_assemblies_keyes()
  - :returns: list of str
  
###### Power Supply
- get_supply_idn(asm_key):
  - :param asm_key: str 
  - :returns: str


- reset_supply(asm_key):
  - :param asm_key: str
  - :returns: None or error string


- stop_supply(asm_key):
  - :param asm_key: str
  - :returns: None or error string


- stop_all_supplies():


- ready_supply(asm_key):
  - :param asm_key: str
  - :returns: None or error string


- ready_all_supplies():
  - :returns: None 
  

- get_supply_actual_voltage(asm_key):
  - :param asm_key: str
  - :returns: float or error string


- get_supply_setpoint_voltage(asm_key):
  - :param asm_key: str
  - :returns: float or error string


- set_supply_voltage(asm_key, volts):
  - :param asm_key: str
  - :param volts: float
  - :returns: None or error string


- get_supply_actual_current(asm_key):
  - :param asm_key: str
  - :returns: float or error string


- get_supply_setpoint_current(asm_key):
  - :param asm_key: str
  - :returns: float or error string
  

- set_supply_current(asm_key, amps):
  - :param asm_key: str
  - :param amps: float
  - :returns: None or error string


- get_supply_voltage_limit(asm_key):
  - :param asm_key: str
  - :returns: float or error string 


- set_supply_voltage_limit(asm_key, volts):
  - :param asm_key: str
  - :param volts: float
  - :returns: None or error string


- get_supply_current_limit(asm_key):
  - :param asm_key: str
  - :returns: float or error string

  
- set_supply_current_limit(asm_key, amps):
  - :param asm_key: str
  - :param amps: float
  - :returns: None or error string
  

- get_supply_channel_state(asm_key):
  - :param asm_key: str
  - :returns: bool or error string


- set_supply_channel_state(self, asm_key, state):
  - :param asm_key: str
  - :param state: bool
  - :returns: None or error string
  

- get_supply_channel(self, asm_key):
  - :param asm_key: str
  - :returns: int or error string
  

- set_supply_channel(self, asm_key, new_chan):
  - :param asm_key: str
  - :param new_chan: int
  - :returns: None or error string


###### Temperature DAQ
- get_daq_idn(asm_key)
  - :param asm_key: str
  - :returns: str 


- get_daq_temp(asm_key)
  - :param asm_key: str
  - :returns: float or error string


- get_daq_channel(asm_key)
  - :param asm_key: str
  - :returns: int or error string


- set_daq_channel(asm_key, new_ch)
  - :param asm_key: str
  - :param new_ch: int
  - :returns: None or error string
  
  
- get_daq_tc_type(asm_key)
  - :param asm_key: str
  - :returns: str or error string


- set_daq_tc_type(asm_key, new_tc)
  - :param asm_key: str
  - :param new_tc: str
  - :returns: None or error string


- get_daq_temp_units(asm_key)
  - :param asm_key: str
  - :returns: str


- set_daq_temp_units(asm_key, new_units)
  - :param asm_key: str
  - :param new_units: str
  - :returns: None or error string


###### PID settings
- get_pid_idn(asm_key):
  - :param asm_key: str
  - :returns: str


- reset_pid(asm_key):
  - :param asm_key: str
  - :returns: None or error string


- get_pid_limits(asm_key):
  - :param asm_key: str
  - :returns: str


- reset_pid_limits(asm_key):
  - :param asm_key: str
  - :returns: None or error string
 

- get_pid_kpro(asm_key):
  - :returns: float or error string
  

- set_pid_kpro(asm_key, new_k):
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