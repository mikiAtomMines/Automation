"""
Created on Fri Mar 24 13:41 2022

@author: Sebastian Miki-Silva
"""

import serial
import sys
import time


class AlphaIncGaussmeter(serial.Serial):
    def __init__(self, *args, **kwargs):
        super().__init__(baudrate=115200, stopbits=1, parity=serial.PARITY_NONE, *args, **kwargs)

        """
        :param port: Device name. Can be found on device manager.
        :param baudrate: Baudrate. Unique to device.
        :param bytesize: Number of data bits. Possible values: FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
        :param parity: Unique to device. Possible values: PARITY_NONE, PARITY_EVEN, PARITY_ODD PARITY_MARK, PARITY_SPACE
        :param stopbits: Number of stop bits. Possible values: STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
        :param timeout: read timeout. Time that read() will wait for response before exiting.
        
        More parameters in documentation for serial.Serial class. 
        """

    def query(self, qry):  # TODO: Make more general for other commands. Improve algorithm.
        number_bytes = {
            '01': 20,
            '02': 20,
            '03': 30,
            '04': 30
        }

        self.write(bytes.fromhex(qry))  # Send the command to the gaussmeter in bytes format.
        self.write(bytes.fromhex('00' * 5))  # Padding for command.

        r = self.read(number_bytes[qry])  # Read 20 bytes of the response back.
        ack = self.read(1)  # Get acknoledge byte.

        if qry == '03':
            return r

        out = ''
        out += r.decode('utf-8')

        while ack != bytes.fromhex('07'):
            self.write(bytes.fromhex('08' * 6))
            r = self.read(20)
            ack = self.read(1)

            out += r.decode('utf-8')

        return out

    def get_data(self):  # TODO: Improve readability, add comments, imporve algorithm for formatting.
        # self.write(bytes.fromhex('03'))  # Send the command to the gaussmeter in bytes format.
        # self.write(bytes.fromhex('00' * 5))  # Padding for command.
        #
        # measurables = []
        # for measurable in range(5):
        #     byte_table = []
        #     for byte in range(6):
        #         single_byte = self.read(1).hex()
        #         single_byte_bin = f'{int(single_byte, 16):0>8b}'
        #         byte_table.append(single_byte_bin)
        #
        #     measurables.append(byte_table)
        #
        # time_list = measurables[4]
        # x_axis_list = measurables[1]
        # y_axis_list = measurables[2]
        # z_axis_list = measurables[3]
        # magnitude_list = measurables[0]
        #
        # print(time_list)
        # exp =
        # print(int(time_list[-2] + time_list[-1], 2))
        # # print(int(time_list[-3], 2))
        # # print(int(time_list[-2], 2))
        # # print(int(time_list[-1], 2))

        bytes_data = self.query('03').hex()
        bits_data = []
        for i in range(0, len(bytes_data), 2):
            bits_i = f'{int(bytes_data[i:i+2], 16):0>8b}'
            bits_data.append(bits_i)

        time_list = bits_data[0:6]
        x_axis_list = bits_data[6:12]
        y_axis_list = bits_data[12:18]
        z_axis_list = bits_data[18:24]
        magnitude_list = bits_data[24:30]

        measurables_lists = [
            time_list,
            x_axis_list,
            y_axis_list,
            z_axis_list,
            magnitude_list
        ]

        print(time_list)
        out = []
        for i in range(len(measurables_lists)):
            measurable = measurables_lists[i]
            measurable_power = -1 * int(measurable[1][5:8], 2)
            measurable_digits = int(measurable[2] + measurable[3] + measurable[4] + measurable[5], 2)
            measurable_sign = 1
            if measurable[1][4] == 1:
                measurable_sign = -1

            measurable_value = measurable_digits * measurable_sign * 10**measurable_power
            out.append(measurable_value)

        return out

    @property
    def properties(self):
        out = self.query('01')

        out = out.replace(':', '\n')
        return out

    @property
    def settings(self):
        out = self.query('02')

        out = out.replace(':', '\n')
        return out


def test_gaussmeter_class():
    gaussmeter = AlphaIncGaussmeter(port='COM3', timeout=5, writeTimeout=1)
    print(gaussmeter.properties)
    print()
    print(gaussmeter.settings)
    print()
    print(gaussmeter.get_data())
    gaussmeter.close()


def main():
    test_gaussmeter_class()


if __name__ == '__main__':
    main()
