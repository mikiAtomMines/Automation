"""
Created on Fri Mar 18, 2022

@author: Sebastian Miki-Silva
"""

import serial
import sys
import time
# import bytes


def main():
    gaussmeter = serial.Serial(port='COM3', baudrate=115200, timeout=5, stopbits=1, parity=serial.PARITY_NONE,
                               writeTimeout=5)

    output = ''
    w = gaussmeter.write(bytes.fromhex('01'))  # Send the command to the gaussmeter in bytes format.
    w2 = gaussmeter.write(bytes.fromhex('00'*5))

    r = gaussmeter.read(20)  # Read 20 bytes of the response back.
    ack = gaussmeter.read(1)

    output += r.decode('utf-8')

    count = 0
    while ack != bytes.fromhex('07'):
        print(count)
        gaussmeter.write(bytes.fromhex('08'*6))
        r = gaussmeter.read(20)
        ack = gaussmeter.read(1)

        output += r.decode('utf-8')
        count += 1

    print(output)

    gaussmeter.close()


if __name__ == '__main__':
    main()
