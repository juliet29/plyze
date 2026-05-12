from itertools import product
from typing import Sequence
from dataclasses import dataclass
import xarray as xr
from pathlib import Path
from plyze.qoi.data.interfaces import QOIandData
from plyze.utils import XArrayNames
from plyze.qoi.registries.interfaces import QOIType
from plyze.qoi.xarray_helpers import convert_xarray_to_polars, select_time
from datetime import datetime

from plyze.qoi.data.spaces import create_space_df
from typing import Annotated
from cyclopts import Parameter


@dataclass
class TimeSelection:
    year: int
    month: Annotated[list[int], Parameter(consume_multiple=True)]
    days: Annotated[list[int], Parameter(consume_multiple=True)]
    hours: Annotated[list[int], Parameter(consume_multiple=True)]
    listwise: bool = False

    def __post_init__(self):
        if not self.hours:
            self.hours = list(range(0, 24))

    def calc_datetimes(self):
        if self.listwise:
            assert isinstance(self.month, list)
            assert len(self.month) == len(self.hours) == len(self.days)
            datetimes = [
                datetime(year=self.year, month=m, day=d, hour=h)
                for m, d, h in zip(self.month, self.days, self.hours)
            ]
        else:
            assert len(self.month) == 1

            datetimes = [
                datetime(year=self.year, month=self.month[0], day=i, hour=j)
                for i, j in product(self.days, self.hours)
            ]

        return datetimes


def select_custom_times(qoidata: QOIandData, ts: TimeSelection):
    arr = select_time(qoidata.original_arr, ts.calc_datetimes())
    qoidata.set_array(arr)
    return qoidata


def to_dataframe(qoidata: QOIandData):
    assert isinstance(qoidata.arr, xr.DataArray)
    df = convert_xarray_to_polars(qoidata.arr, qoidata.qoi.nickname)
    return df


def to_dataframe_with_spaces(qoi: QOIType, idf: Path, sql: Path, ts: TimeSelection):
    qoid = select_custom_times(QOIandData(qoi, sql), ts)
    df = to_dataframe(qoid)
    space_df = create_space_df(idf)

    dd = df.join(space_df, on=XArrayNames.SPACE)
    qoid.set_dataframe(dd)
    return qoid


def to_multi_data(qois: Sequence[QOIType], idf: Path, sql: Path, ts: TimeSelection):

    def to_df(qoi: QOIType):
        qoid = select_custom_times(QOIandData(qoi, sql), ts)
        return to_dataframe(qoid)

    # TODO: add utils4plans as set_unique function
    space_types = [i.space_type for i in qois]
    assert (
        len(set(space_types)) == 1
    ), f"Expected the space_types to all be the same, but got: {space_types}"

    dfs = [to_df(i) for i in qois]

    d0 = dfs[0]
    for df in dfs[1:]:
        d0 = d0.join(df, on=[XArrayNames.DATETIME, XArrayNames.SPACE])

    space_df = create_space_df(idf)
    return d0.join(space_df, on=XArrayNames.SPACE)
