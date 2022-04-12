"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

# TODO: Add proper error handling. This includes receiving error from power supply.
# TODO: Finish adding comments

import socket
import sys


class SocketEthernetDevice:
    def __init__(
            self,
            ip4_address=None,
            port=50000,
    ):

        """
        An ethernet-controlled device.

        :param ip4_address: The IPv4 address of the device.
        :param port: The port number used to connect the device. Can be any number between 49152 and 65536.
        """

        self._ip4_address = ip4_address
        self._port = port
        self._socket = None

        if ip4_address is not None:
            self.connect()

    @property
    def ip4_address(self):
        return self._ip4_address

    @property
    def port(self):
        return self._port

    def connect(self):
        try:
            socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_object.connect((self._ip4_address, self._port))
        except socket.error:
            print('ERROR: Could not connect to power supply. Please Check IPv4 address and try again. ')
            sys.exit()

        self._socket = socket_object

    def disconnect(self):
        socket_ps = self._socket
        socket_ps.close()
