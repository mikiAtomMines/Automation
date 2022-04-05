# Automation
Classes for autmating experiment. Includes classes for power supplies, gaussmeter, temperature daq, and vturbovacuum pumps. 


## PowerSupplyClass.py
This file includes three classes: EthernetDevice, PowerSupply, and SPD3303X. The last class inherits from the first two. In the future, if more power supplies are used in the experiment, we will add more classes corresponding to their respective power supply model. Currently we only have the SPD3303X model power supply that is being controlled through ethernet. The main function of this file tests this class. 

### EthernetDevice:
Had query, command, connect, and disconnect methods. Might need to modify to make more general in the future. 

### PowerSupply:
Any power supply. Had max voltage and max current limits, number of channels, and an option to reset the power supply on startup. No methods. 

### SPD3303X:
Currently the only power supply we control through ethernet. Has methods to set voltage, current, turn the channels on or off, set limits to the voltage and current, and read all these measurables.


## GaussmeterClass.py
This file has a class for the AlphaLabs Inc GM3 gaussmeter. 

### GM3Gaussmeter:
GM3 Gaussmeter class. Has a query method that is used for data acquisiton methods. 
The query method takes input a string of the desired query using the command name as it appears in the manual. Can use the command name, or the hex command identifyer in the format 'AA'. The method will format the query message according to the input. It will also read the response and return it as a byte object. 
get_instantenous_data queries the gaussmeter for a single reading of all the measurables. It then parses the output into human-readable strings. 


## testing files
All files with names starting with 'testing' are used as preliminary testing of certain libraries and communication protocols. Currently testing SimplePID library, and serial communication with Leybold TurboVac pumps. 
