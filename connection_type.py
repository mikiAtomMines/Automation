"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""

# TODO: Add proper error handling. This includes receiving error from power supply.
# TODO: Finish adding comments

import socket
import time
import sys

import serial


class SocketEthernetDevice:
    def __init__(
            self,
            ip4_address=None,
            port=None,
    ):

        """
        An ethernet-controlled device.

        :param ip4_address: The IPv4 address of the device.
        :param port: The port number used to connect the device. Can be any number between 49152 and 65536.
        """

        self._ip4_address = ip4_address
        self._port = port
        self._socket = None
        self._is_connected = False

        if ip4_address is not None:
            self.connect()

    def _query(self, query):
        """
        send a query to the ethernet device and receive a response.

        Parameters
        ----------
        query : bytes
            Python bytes containing the query command. Dependent on each individual device.
        Returns
        -------
        bytes
            Returns the reply of the ethernet device as bytes.
        """

        try:
            self._socket.sendall(query)
            reply = self._socket.recv(4096)
        except OSError:
            raise OSError('ERROR: Socket not found. Query not sent. Try using the connect() method first.')

        time.sleep(0.3)
        return reply

    def _command(self, cmd):
        """
        send a command to the ethernet device. Does not receive any response.

        Parameters
        ----------
        cmd : bytes
            Python btyes containing the command. Dependent on each individual device.
        Returns
        -------
        None
            Returns None if the command is succesfully sent.
        """

        try:
            out = self._socket.sendall(cmd)
        except OSError:
            raise OSError('ERROR: Socket not found. Command not sent. Try using the connect() method first.')

        time.sleep(0.3)
        return out

    @property
    def ip4_address(self):
        return self._ip4_address

    @ip4_address.setter
    def ip4_address(self, new_ip):
        if not self._is_connected:
            self._ip4_address = new_ip
        else:
            raise AttributeError('ERROR: ip4_address cannot be changed while conenction is on.')

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, new_port):
        if not self._is_connected:
            self._port = new_port
        else:
            raise AttributeError('ERROR: port cannot be changed while connection is on.')

    def connect(self):
        try:
            socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_object.connect((self._ip4_address, self._port))
        except OSError:
            raise OSError('ERROR: Could not connect to ethernet device. Please Check IPv4 address and try again. ')

        self._socket = socket_object
        self._is_connected = True

    def disconnect(self):
        self._socket.close()
        self._is_connected = False

#
# class SerialConnection:
#     def __int__(
#             self,
#             baudrate=None,
#             bytesize=None,
#             parity=None,
#             stopbits=0,
#             read_timeout=None,
#             write_timeout=None,
#     ):
#         """
#
#         Parameters
#         ----------
#         baudrate : int
#         bytesize : int
#             number of data bits.
#         parity : str
#             defines the parity of the communication. Possible values: serial.PARITY_NONE or 'N', serial.PARITY_EVEN
#             or 'E', serial.PARITY_ODD or 'O', and others.
#         stopbits : int
#             number of stop bits to be used in the communication.
#         read_timeout : float
#             read timeout in seconds. If set to None, will wait forever or until the number of requested bytes are
#             received.
#         write_timeout : float
#             write timeout in seconds. Analogous to read_timeout. Is blocking by default.
#         """
#
#         self._baudrate = baudrate
#         self._bytesize = bytesize
#         self._parity = parity
#         self._stopbits = stopbits
#         self._read_timeout = read_timeout
#         self._write_timeout = write_timeout
#         self._serial_com = serial.Serial(
#             baudrate=self._baudrate,
#             bytesize=self._bytesize,
#             parity=self._parity,
#             stopbits=self._stopbits,
#             timeout=self._read_timeout,
#             write_timeout=self._write_timeout
#         )
#
