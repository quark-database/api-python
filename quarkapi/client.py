import json
from typing import Final

from quarkapi.constants import DEFAULT_QUARK_PORT
from quarkapi.entities import QueryResult
from quarkapi.tcp import TcpClient


class Client:
    __token: Final[str]
    __host: Final[str]
    __port: Final[int]
    __tcp: Final[TcpClient]

    def __init__(self, token: str, host: str = "localhost", port: int = DEFAULT_QUARK_PORT):
        self.__token = token
        self.__host = host
        self.__port = port
        self.__tcp = TcpClient(host, port)

    def connect(self):
        self.__tcp.connect()

    def query(self, instruction: str) -> QueryResult:
        request: dict = {"token": self.__token, "query": instruction}
        response = self.__tcp.send_and_receive(json.dumps(request))
        print(response)
        return QueryResult(json.loads(response))
