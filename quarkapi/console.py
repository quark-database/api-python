import json
from dataclasses import dataclass
from os.path import exists
from typing import List

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from quarkapi.client import Client
from quarkapi.constants import QUARK_VERSION, DEFAULT_QUARK_PORT, RECENT_SERVERS_FILE_NAME
from quarkapi.dataclass_json_encoder import DataclassJSONEncoder
from quarkapi.entities import QueryExecutionStatus

console = Console()


@dataclass
class ServerInfo:
    host: str
    port: int
    token: str

    def __eq__(self, other):
        return self.port == other.port and self.host == other.host


def try_connect_and_read_queries(server_info: ServerInfo) -> None:
    client = Client(host=server_info.host, port=server_info.port, token=server_info.token)
    try:
        with console.status("[gray]Trying to connect to the server...", spinner="earth"):
            client.connect()

        query = ""
        while query != "exit":
            with console.status("[gray]Sending a query...", spinner="earth") as status:
                result = client.query(query)
                status.stop()

                match result.execution_status:
                    case QueryExecutionStatus.OK:
                        console.print(f":checkmark:  Query is executed successfully.")
                        console.print(f":envelope:  Message: {result.message}")
                        console.print(f":clock:  Execution time {'>' if result.time == 0 else ''}{1 if result.time == 0 else result.time } milliseconds")
                        if result.has_table():
                            table = Table(header_style="bold")
                            for column_name in result.table_view.header:
                                table.add_column(column_name)

                            for row in result.table_view.rows:
                                table.add_row(row.cells)

                            console.print(table)
                        else:
                            console.print("<no table returned>", style="gray", justify="center")
                    case QueryExecutionStatus.SYNTAX_ERROR:
                        console.print(f":no entry:  Your query contains a syntax error.")
                        console.print(f":envelope:  Message: {result.message}")
                    case QueryExecutionStatus.SERVER_ERROR:
                        console.print(f":no entry:  Server got an error.")
                        console.print(f":envelope:  Message: {result.message}")
                        if result.has_exception():
                            console.print(f":no entry: Exception message: {result.exception}")
                    case QueryExecutionStatus.MIDDLEWARE_ERROR:
                        console.print(f":no entry:  Your query cannot be handled.")
                        console.print(f":envelope:  Message: {result.message}")

                console.print("")
    except Exception as exception:
        console.print(f":no entry: Connection to {server_info.host}:{server_info.port} failed, "
                      f"because of {type(exception.__name__)}: {str(exception)}")


def load_recent_servers() -> List[ServerInfo]:
    recent_servers: List[ServerInfo] = []

    if exists(RECENT_SERVERS_FILE_NAME):
        with open(RECENT_SERVERS_FILE_NAME, "r") as recent_servers_json_file:
            for recent_server_json_object in json.load(recent_servers_json_file):
                recent_servers.append(ServerInfo(recent_server_json_object["host"], int(recent_server_json_object["port"]), recent_server_json_object["token"]))

    return recent_servers


def save_server_to_recent_servers_file(server_to_save: ServerInfo) -> None:
    recent_servers_to_save = load_recent_servers()

    existing_recent_server = next((server_to_save == recent_server for recent_server in recent_servers_to_save), None)

    if existing_recent_server is None:
        recent_servers_to_save.append(server_to_save)
    else:
        existing_recent_server.token = server_to_save.token

    with open(RECENT_SERVERS_FILE_NAME, "w+") as recent_servers_json_file:
        json.dump(recent_servers_to_save, recent_servers_json_file, ensure_ascii=False, indent=4, cls=DataclassJSONEncoder)


def run_console() -> None:
    recent_servers = load_recent_servers()
    console.print(f":comet: [bold #00AAFF]Quark Console {QUARK_VERSION}[bold #00AAFF] :comet:", justify="center")

    for index, recent_server in enumerate(recent_servers):
        console.print(f":computer:  Recent server #{index + 1} '{recent_server.host}:[gray]{recent_server.port}[/gray]'")

    host = Prompt.ask(":package:  Enter the host name or a number of one of the recent server listed above to connect", default="localhost")

    try:
        index_of_recent_server = int(host)
        while index_of_recent_server <= 0 or index_of_recent_server > len(recent_servers):
            console.print(f":no entry:  There is no recent server with number {index_of_recent_server}. Enter a "
                          f"number between 1 and {len(recent_servers)}")
            index_of_recent_server = int(Prompt.ask(":package:  Please, try to enter again the host name or a number "
                                                    "of one of the recent server listed above to connect"))
        try_connect_and_read_queries(recent_servers[index_of_recent_server + 1])
    except ValueError:
        port = int(Prompt.ask(f":package:  Enter the port of the server {host}", default=DEFAULT_QUARK_PORT))
        token = Prompt.ask(f":lock:  Enter an access token of the server")
        server_info = ServerInfo(host, port, token)
        save_server_to_recent_servers_file(server_info)
        try_connect_and_read_queries(server_info)
