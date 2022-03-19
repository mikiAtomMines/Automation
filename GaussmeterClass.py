"""
Created on Fri Mar 18, 2022

@author: Sebastian Miki-Silva
"""

import serial
import sys
import time

# TODO: why does the read method take so long? about 20 seconds per byte. Why?

def main():
    gaussmeter = serial.Serial(port='COM3', baudrate=115200, stopbits=1, parity=serial.PARITY_NONE)
    print(gaussmeter.name)
    print(gaussmeter.isOpen())

    for i in range(6):
        write = gaussmeter.write(b'ID_METER_PROP')
        time.sleep(0.2)

    out = ''


    print('write:', write)
    print('out:', out)


    gaussmeter.close()


if __name__ == '__main__':
    main()
