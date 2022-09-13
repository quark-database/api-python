import struct
from socket import socket
from typing import Final


class TcpClient:
    __host: Final[str]
    __port: Final[int]
    __socket: socket

    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__socket = socket()

    def connect(self):
        self.__socket.connect((self.__host, self.__port))

    def send_and_receive(self, text_message: str) -> str:
        text_message_length = len(text_message)
        text_message_bytes = text_message.encode("utf-8")

        message_bytes = struct.pack('>I', text_message_length) + text_message_bytes

        self.__socket.sendall(message_bytes)

        return self.__receive_message().decode("utf-8")

    def __receive_next_bytes(self, byte_count_to_receive: int) -> bytearray or None:
        received_bytes = bytearray()

        while len(received_bytes) < byte_count_to_receive:
            packet = self.__socket.recv(byte_count_to_receive - len(received_bytes))
            if not packet:
                return None

            received_bytes.extend(packet)

        return received_bytes

    def __receive_message(self):
        raw_message_length = self.__receive_next_bytes(4)

        if raw_message_length is None:
            return None

        message_length = struct.unpack('>I', raw_message_length)[0]

        return self.__receive_next_bytes(message_length)
