# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 16:18:50 2022

@author: Pointsman
"""
import serial


def binary_to_hex_byte(byte):
    hex_string = hex(int(byte, 2))
    # remove 0x and pad with 0

    hex_string = hex_string[2:].zfill(2)

    return bytes.fromhex(hex_string)


def main():
    turbovac = serial.Serial(port='COM3', baudrate=19200, bytesize=serial.EIGHTBITS, stopbits=1, parity=serial.PARITY_EVEN,  writeTimeout=1, timeout=1)

    bytes_array = [b'\x00']*24

    qry_designator = '0001' + '0'  # qry designator plus reserved bit
    param_num = '00010010110'      # param number. Currently 150
    word0 = qry_designator + param_num
    byte3 = word0[:8]
    byte4 = word0[8:]

    bytes_array[0] = (b'\x02')
    bytes_array[1] = (b'\x16')
    bytes_array[2] = (b'\x00')     # bus address kept as default 0.
    bytes_array[3] = binary_to_hex_byte(byte3)
    bytes_array[4] = binary_to_hex_byte(byte4)
    bytes_array[11] = b'\x04'

    query = b''
    for byte_i in bytes_array:
        query += byte_i

    turbovac.write(query)
    out = turbovac.read(24)


    turbovac.close()



if __name__ == '__main__':
    main()