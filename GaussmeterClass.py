"""
Created on Fri Mar 24 13:41 2022

@author: Sebastian Miki-Silva
"""

import serial
import sys
import time


class AlphaIncGaussmeter(serial.Serial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        """
        :param port: Device name. Can be found on device manager.
        :param baudrate: Baudrate. Unique to device.
        :param bytesize: Number of data bits. Possible values: FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
        :param parity: Unique to device. Possible values: PARITY_NONE, PARITY_EVEN, PARITY_ODD PARITY_MARK, PARITY_SPACE
        :param stopbits: Number of stop bits. Possible values: STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
        :param timeout: read timeout. Time that read() will wait for response before exiting.
        
        More parameters in documentation for serial.Serial class. 
        """

    def query(self, command):
        """
        query function for gaussmeter. The function sends the appropriate command to the gaussmeter and reads the
        appropiate number of bytes and returns them as a byte string. Currently, the only supported commands are:
        ID_METER_PROP (0x01), ID_METER_SETT (0x02), STREAM_DATA (0x03), and RESET_TIME (0x04).

        :param command: the command to send to the gaussmeter. Can be a string with the hex value of the command in the
        format 'AA' or '0xAA' or the command name as it appears in the AlphaApp comm protocol manual.
        :return: byte string containing the response from the gaussmeter. Has variable length depending on the query
        command used.
        """

        qry_dict = {  # command as appears in manual: hex command identifyer
            'ID_METER_PROP': '01',
            'ID_METER_SETT': '02',
            'STREAM_DATA': '03',
            'RE SET_TIME': '04',
            'KILL_ALL_PROCESS': 'FF',
            '01': '01',
            '02': '02',
            '03': '03',
            '04': '04',
            'FF': 'FF',
            '0x01': '01',
            '0x02': '02',
            '0x03': '03',
            '0x04': '04',
            '0xFF': 'FF'
        }
        qry = qry_dict[command]  # TODO: Add error handling

        number_of_bytes_dict = {  # the acknoledge byte is sent
            '01': 20,
            '02': 20,
            '03': 30,
            '04': 30,
        }
        number_of_bytes = number_of_bytes_dict[qry]

        self.write(bytes.fromhex(qry*6))
        # self.write(bytes.fromhex(qry))       # Send the command to the gaussmeter in bytes format.
        # self.write(bytes.fromhex('00' * 5))  # Padding for command.
        r = self.read(number_of_bytes)       # Read bytes of the response back.
        ack = self.read(1)

        if qry == '03' or qry == '04':
            return r

        while ack != bytes.fromhex('07'):
            self.write(bytes.fromhex('08' * 6))
            r += self.read(number_of_bytes)
            ack = self.read(1)
        return r

    def command(self, command):
        """
        """

        cmd_dict = {
            'KILL_ALL_PROCESS': 'FF',
            'FF': 'FF',
            '0xFF': 'FF'
        }
        cmd = cmd_dict[command]  # TODO: Add error handling

        self.write(bytes.fromhex(cmd*6))
        # self.write(bytes.fromhex(cmd))       # Send the command to the gaussmeter in bytes format.
        # self.write(bytes.fromhex('00' * 5))  # Padding for command.

        return None

    def get_instantenous_data(self):  # TODO: Improve readability, add comments, imporve algorithm for formatting.
        """
        query the gaussmeter for an instantenous reading of the time stamp in seconds, x-axis, y-axis, z-axis,
        and magnitude in Gauss readings of a magnetic field.
        :return: list containing the float values for time (s), x-axis (G), y-axis (G), z-axis (G), and magnitude (G).
        """

        """
        The response from the gaussmeter comes as a long byte string containing hex numbers in the format 'AA. The 
        data can be thought to be split in sections of 6 bytes. Each section contains the information for each 
        measurable that the gaussmeter collects. Currently, there are only 5 measurables, which means that the 
        response has a total of 30 bytes.
        
        The response is then converted into a python string. Since each hex number has two characters, the string is 
        60 characters long. 
        """

        query_bytes = self.query('STREAM_DATA')
        # ack = query_bytes[-1].hex()
        # print(ack)
        query_string = query_bytes.hex()

        """
        We then divide the string into sections of 12 characters (6 bytes) and identify the second  (byte_2) and the 
        third, fourth, fifth, and sixth bytes (bytes_3456) from this section. byte_2 gives information on the sign 
        and magnitude of the measured quantity. bytes_3456 give the digits. 
        """
        number_of_measurables = int(len(query_string)/2 / 6)
        out = []
        for measurable_i in range(number_of_measurables):
            section_i = measurable_i*12
            byte_2 = int(query_string[section_i+2: section_i+4], 16)
            bytes_3456 = int(query_string[section_i+4: section_i+12], 16)

            sign = 1
            if byte_2 & 0x08:               # 0x08 = 00001000 : if 4th bit = 1, sign is negative. Else, sign is positive
                sign = -1
            power = -1*int(byte_2 & 0x07)   # 0x07 = 00000111 : 1st, 2nd, and 3rd bits give inverse power of 10.
            digits = bytes_3456

            out.append(sign*digits*10**power)

        return out

    @property
    def properties(self):
        out = self.query('ID_METER_PROP').decode('utf-8')
        out = out.replace(':', '\n')
        return out

    @property
    def settings(self):
        out = self.query('ID_METER_SETT').decode('utf-8')
        out = out.replace(':', '\n')
        return out


def collect_data(gaussmeter, t):
    time_initial = time.time()

    data = [gaussmeter.get_instantenous_data_t0()]
    while time.time() - time_initial < t:
        point = gaussmeter.get_instantenous_data()
        print(point)
        data.append(point)
        time.sleep(0.5)

    return data


def test_gaussmeter_class():
    a = 3

    gaussmeter = AlphaIncGaussmeter(port='COM3', baudrate=115200, stopbits=1, parity=serial.PARITY_NONE, timeout=5, writeTimeout=5)
    # gaussmeter.command('FF')
    for i in range(30):
        print(gaussmeter.properties)
    # print()
    # print(gaussmeter.settings)
    # print()
    # print(gaussmeter.get_instantenous_data_t0())
    # time.sleep(a)
    # print()
    # print(gaussmeter.get_instantenous_data())
    # print(gaussmeter.get_instantenous_data())
    # print(gaussmeter.get_instantenous_data())
    # print(gaussmeter.get_instantenous_data())
    # print(gaussmeter.get_instantenous_data())
    # print(gaussmeter.get_instantenous_data())
    # print(gaussmeter.get_instantenous_data())
    # print(gaussmeter.get_instantenous_data())
    # print()
    # # print(collect_data(gaussmeter, 3))
    # collect_data(gaussmeter, 10)
    gaussmeter.close()




def main():
    test_gaussmeter_class()


if __name__ == '__main__':
    main()
