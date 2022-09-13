from enum import Enum
from typing import Final, Tuple


class InstructionResultFormatException(Exception):
    pass


class TableViewRow:
    cells: Final[Tuple[str]]

    def __init__(self, *cells: str):
        self.cells = cells

    def __iter__(self):
        return iter(self.cells)


class TableViewHeader:
    column_names: Final[Tuple[str]]

    def __init__(self, *column_names: str):
        self.column_names = column_names

    def __iter__(self):
        return iter(self.column_names)

    def produce_row(self, *cells: str):
        if len(self.column_names) == len(cells):
            return TableViewRow(*cells)

        raise InstructionResultFormatException(f"Cannot produce a new row with {len(cells)} values, because the table "
                                               f"header contains {'more' if len(self.column_names) > len(cells) else 'less'} "
                                               f"columns, exactly {len(self.column_names)}")


class TableView:
    header: Final[TableViewHeader]
    rows: Final[Tuple[TableViewRow]]

    def __init__(self, header: TableViewHeader, *rows: TableViewRow):
        self.header = header
        self.rows = rows

    @staticmethod
    def empty():
        return TableView(TableViewHeader())


class QueryExecutionStatus(Enum):
    __order__ = "OK SYNTAX_ERROR SERVER_ERROR MIDDLEWARE_ERROR"
    OK = 0,
    SYNTAX_ERROR = 1,
    SERVER_ERROR = 2,
    MIDDLEWARE_ERROR = 3


class QueryResult:
    execution_status: QueryExecutionStatus
    exception: str = ""
    message: str = ""
    time: int = 0
    table_view = TableView.empty()

    def __init__(self, result_in_json: dict):
        print(type(result_in_json).__name__)
        if "status" not in result_in_json:
            raise InstructionResultFormatException("Required 'status' field in instruction result is missed")

        if "message" not in result_in_json:
            raise InstructionResultFormatException("Required 'message' field in instruction result is missed")

        if "exception" in result_in_json:
            self.exception = result_in_json['exception']

        if "time" in result_in_json:
            self.time = int(result_in_json['time'])

        if "table" in result_in_json:
            self.table_view = TableView(TableViewHeader(result_in_json["table"]["header"]),
                                        *map(lambda array: TableViewRow(*array), result_in_json["table"]["records"]))

        self.message = result_in_json["message"]
        self.execution_status = QueryExecutionStatus[result_in_json["status"]]

    def has_table(self) -> bool:
        return len(self.table_view.rows) != 0

    def has_exception(self) -> bool:
        return len(self.exception) != 0
