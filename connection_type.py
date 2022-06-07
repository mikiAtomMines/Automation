"""
Created on Thursday, April 7, 2022
@author: Sebastian Miki-Silva
"""


import socket
import time


class SocketEthernetDevice:
    def __init__(
            self,
            ip4_address,
            port,
    ):

        """
        An ethernet-controlled device.

        Parameters
        ----------
        ip4_address : str
            The IPv4 address of the device.
        port : int
            The port number used to connect the device. Can be any number between 49152 and 65536.
        """

        self._ip4_address = ip4_address
        self._port = port
        self._socket = None
        self._is_connected = False

        self.connect()

    def _query(self, qry):
        """
        send a query to the ethernet device and receive a response.

        Parameters
        ----------
        qry : bytes
            The message to send through the socket connection.

        Returns
        -------
        bytes
            Returns the raw reply of the ethernet device as bytes.

        Raises
        ------
        OSError
            If there is an error with the socket object, raise OSError. Might be fixed by using self.connect()
        """

        try:
            self._socket.sendall(qry)
            time.sleep(0.3)
            self._socket.settimeout(15)
            reply = self._socket.recv(4096)
            time.sleep(0.3)
        except TimeoutError:
            return 'ERROR: No response from device for query ' + str(qry)
        except OSError:
            return 'ERROR: Query not sent. Try using the connect() method first.'


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
            time.sleep(0.3)
        except OSError:
            return 'ERROR: Socket not found. Command not sent. Try using the connect() method first.'

        return out

    @property
    def ip4_address(self):
        return self._ip4_address

    # @ip4_address.setter
    # def ip4_address(self, new_ip):
    #     if not self._is_connected:
    #         self._ip4_address = new_ip
    #     else:
    #         raise AttributeError('ERROR: ip4_address cannot be changed while conenction is on.')

    @property
    def port(self):
        return self._port

    # @port.setter
    # def port(self, new_port):
    #     if not self._is_connected:
    #         self._port = new_port
    #     else:
    #         raise AttributeError('ERROR: port cannot be changed while connection is on.')

    @property
    def idn(self):
        """
        Placeholder

        Returns
        -------
        str
            Identification string.
        """
        pass

    def connect(self):
        """
        Establish socket connection to the ip address of the current SocketEthernetDevice. Attempt to connect 10
        times before raising an error.

        Returns
        -------
        None
            If succesful, returns None

        Raises
        ------
        OSError
            If 10 attempts to connect fail, raise OSError.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self._ip4_address, self._port))
            self._socket = sock
            self._is_connected = True
            print('Connection to', self._ip4_address, 'was succesful.')
            return
        except OSError:
            print('Failed to connect. Reattempting...')
            for i in range(10):
                try:
                    sock.connect((self._ip4_address, self._port))
                    self._socket = sock
                    self._is_connected = True
                    print('Connection to', self._ip4_address, 'was succesful.')
                    return
                except OSError:
                    print('attempt', i+1, 'failed')
                    continue
        raise OSError('ERROR: Could not connect to' + str(self._ip4_address))

    def disconnect(self):
        """
        Close socket connection.
        """
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
