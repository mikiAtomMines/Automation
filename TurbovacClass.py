# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 16:18:50 2022

@author: Pointsman
"""
import serial
from bitarray import bitarray
from bitarray import util

def binary_to_hex_byte(byte):
    hex_string = hex(int(byte, 2))
    # remove 0x and pad with 0

    hex_string = hex_string[2:].zfill(2)

    return bytes.fromhex(hex_string)


def main():
    # turbovac = serial.Serial(port='COM3', baudrate=19200, bytesize=serial.EIGHTBITS, stopbits=1, parity=serial.PARITY_EVEN,  writeTimeout=1, timeout=1)

    bytes_array = []
    for i in range(24):
        a = bitarray()
        bytes_array.append(a)

    bytes_array[0].frombytes(b'\x02')
    bytes_array[1].frombytes(b'\x16')
    bytes_array[2].frombytes(b'\x00')

    qry_designator = bitarray('0001' + '0')  # qry designator plus reserved bit
    param_num = bitarray('00010010110')      # param number. Currently 150
    word0 = qry_designator + param_num
    byte3 = word0[:8]
    byte4 = word0[8:]

    bytes_array[3] = byte3
    bytes_array[4] = byte4
    bytes_array[11].frombytes(b'\x04')

    bit_query = ''
    for byte_i in bytes_array:
        if len(byte_i) < 8:
            byte_i.frombytes(b'\x00')
        byte_i.append(util.parity(byte_i))
        bit_query += byte_i.to01()


    # bytes_array = [b'\x00']*24
    #
    # qry_designator = '0001' + '0'  # qry designator plus reserved bit
    # param_num = '00010010110'      # param number. Currently 150
    # word0 = qry_designator + param_num
    # byte3 = word0[:8]
    # byte4 = word0[8:]
    #
    #
    #
    # bytes_array[0] = (b'\x02')
    # bytes_array[1] = (b'\x16')
    # bytes_array[2] = (b'\x00')     # bus address kept as default 0.
    # bytes_array[3] = binary_to_hex_byte(byte3)
    # bytes_array[4] = binary_to_hex_byte(byte4)
    # bytes_array[11] = b'\x04'

    for byte_i in bytes_array:
        util.pprint(byte_i)

    print()
    print(bit_query + '\n')

    array_query = bitarray(bit_query)

    byte_query = array_query.tobytes()

    print(byte_query)

    # turbovac.write(query)
    # out = turbovac.read(24)

    # turbovac.close()



if __name__ == '__main__':
    main()