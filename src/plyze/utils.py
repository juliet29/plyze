from pathlib import Path
from typing import NamedTuple


class XArrayNames:
    SPACE = "space_names"
    DATETIME = "datetimes"


class CaseData(NamedTuple):
    idf: Path
    sql: Path
