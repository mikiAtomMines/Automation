"""
Created on Fri Mar 18, 2022

@author: Sebastian Miki-Silva
"""

import serial
import sys
import time


def main():
    gaussmeter = serial.Serial(port='COM3', baudrate=115200, stopbits=1, parity=serial.PARITY_NONE)
    print(gaussmeter.name)
    print(gaussmeter.isOpen())

    w = gaussmeter.write(b'ID_METER_PROP')
    r = gaussmeter.read()

    print(r)

    gaussmeter.close()


if __name__ == '__main__':
    main()
