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

---

### SocketEthernetDevice
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

#### Properties
    ip4_address
    port

#### Methods
    connect()
    disconnect()

## Classes from device_type.py

---

### PowerSupply
    PowerSupply(
            MAX_voltage_limit=None,
            MAX_current_limit=None,
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
        channel_voltage_limits : list of float
            list containing the individual channel limits for the set voltage. The set voltage of a channel cannot 
            exceed its limit voltage. The 0th item corresponds to the limit of channel 1, 1st item to channel 2, 
            and so on.
        channel_current_limits : list of float
            list containing the individual channel limits for the set current. The set current of a channel cannot 
            exceed its limit current. The 0th item corresponds to the limit of channel 1, 1st item to channel 2, 
            and so on.
        number_of_channels : int
            the number of physical programmable channels in the power supply.
        reset_on_startup : bool
            If set to true, will run a method to set the set voltage and current to 0 and reset the channel limits to 
            their full range. 
        """

This class represents any benchtop programmable power supply. It contains the maximum voltage and current values allowed 
by the hardware of the power supply. These attributes should not be used as voltage and current limit setters, as they 
are a property of the hardware and should remain constant unless the hardware is changed. 

#### Properties
- MAX_voltage_limit  
- MAX_current_limit  
- channel_voltage_limits **(no setter)**
- channel_current_limits **(no setter)** 
- number_of_channels

#### Methods
- set_set_voltage  
- set_set_current   
- set_channel_voltage_limit  
- set_channel_current_limit  
- set_all_channels_voltage_limit  
- set_all_channels_voltage_limit
- zero_call_channels

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

#### Properties

- idn **(no setter)**
- board_number
- ip4_address **(no setter)**
- port **(no setter)**
- model **(no setter)**
- max_address  **(no setter)**
- unique_id **(no setter)**
- serial_number **(no setter)**
- number_temp_channels **(no setter)**
- number_io_channels **(no setter)**
- number_ad_channels **(no setter)** 
- number_da_channels **(no setter)**
- clock_frequency_MHz **(no setter)**

### HeaterAssembly

    HeaterAssembly(
            power_supply=None,
            supply_channel=None,
            temperature_daq=None,
            daq_channel=None,
            pid_function=None,
            set_temperature=None,
            temp_units=None,
            MAX_set_temp=None,
            MIN_set_temp=None,
            configure_on_startup=False,

    ):
        """
        A heater assembly composed of a heater, a temperature measuring device, and a power supply.

        Parameters
        ----------
        power_supply : device_models.PowerSupply
            The power supply model that is being used for controlling the electrical power going into the heater.
        supply_channel : int
            The physical power supply channel connected to the heater for controlling the electrical power.
        temperature_daq : device_models.MCC_device
            The temperature DAQ device that is being used for reading the temperature of the heater.
        daq_channel : int
            The physical DAQ channel used for taking temperature readings of the heater.
        pid_function : simple_pid.PID
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
        MAX_set_temp : float, None
            The maximum possible value for set temp. Should be based on the physical limitations of the heater.
            Should be used as a safety mechanism so the set temperature is never set higher than what the hardware
            allows. If set to None, the limit is infinity.
        MIN_set_temp : float, None
            The minimum possible value for set temp. Analogous to MAX_temp.
        configure_on_startup : bool
            Will configure the PID object's output limits, setpoint, and optionally, the Kp, Ki, and Kd. Set this to
            True if the pid object has not been manually configured.
        """

#### Properties

- power_supply **(no setter)**
- supply_channel 
- temperature_daq **(no setter)**
- daq_channel
- set_temperature
- temp_units
- pid_function **(no setter)**
- MAX_set_temp **(no setter)**
- MIN_set_temp **(no setter)**
- configure_pid_on_startup **(no setter)**
- current_temperature **(no setter)**

#### Methods

- configure_pid
- update_supply
- live_plot
        
## Classes from device_model.py

---

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

#### Properties

- properties
- settings

#### Methods

- query
- command
- get_instantenous_data
- get_instantenous_data_t0

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

#### Properties

- idn **(no setter)**
- ip4_address **(no setter)**
- system_status **(no setter)**
- ch1_state
- ch2_state
- ch1_set_voltage
- ch2_set_voltage
- ch1_actual_voltage **(no setter)**
- ch2_actual_voltage **(no setter)**
- ch1_set_current
- ch2_set_current
- ch1_actual_current **(no setter)**
- ch2_actual_current **(no setter)**
- ch1_voltage_limit
- ch1_current_limit
- ch2_voltage_limit
- ch2_current_limit

#### Methods

- reset_channels()
- get_channel_state(channel)
- get_set_voltage(channel)
- get_actual_voltage(channel)
- get_set_current(channel)
- get_actual_current(channel)
- get_voltage_limit(channel)
- get_current_limit(channel)
- set_channel_state(channel, state)
- set_set_voltage(channel, volts)
- set_set_current(channel, amps)
- set_channel_voltage_limit(channel, volts)
- set_channel_current_limit(channel, amps)


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

#### Properties
- default_units
- thermocouple_type_ch0 **(no setter)**
- thermocouple_type_ch1 **(no setter)**
- thermocouple_type_ch2 **(no setter)**
- thermocouple_type_ch3 **(no setter)**
- thermocouple_type_ch4 **(no setter)**
- thermocouple_type_ch5 **(no setter)**
- thermocouple_type_ch6 **(no setter)**
- thermocouple_type_ch7 **(no setter)**
- temp_ch0 **(no setter)**
- temp_ch1 **(no setter)**
- temp_ch2 **(no setter)**
- temp_ch3 **(no setter)**
- temp_ch4 **(no setter)**
- temp_ch5 **(no setter)**
- temp_ch6 **(no setter)**
- temp_ch7 **(no setter)**

#### Methods
- get_temp(channel_n, units, averaged)
- get_temp_all_channels(units, averaged)
- get_temp_scan(low_channel, high_channel, units, averaged)