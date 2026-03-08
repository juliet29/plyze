from itertools import product
from typing import Sequence
import xarray as xr
from pathlib import Path
from plys.qoi.data.interfaces import QOIandData
from plys.qoi.registries.interfaces import QOIType
from plys.qoi.xarray_helpers import convert_xarray_to_polars
from datetime import datetime

from plys.qoi.data.spaces import create_space_df


def select_times(qoidata: QOIandData):
    days = [1]  # 2
    times = [9, 12, 15, 18, 21, 0]
    datetimes = [
        datetime(year=2017, month=7, day=i, hour=j) for i, j in product(days, times)
    ]
    arr = qoidata.original_arr.sel(datetimes=datetimes)
    qoidata.set_array(arr)
    return qoidata


def to_dataframe(qoidata: QOIandData):
    assert isinstance(qoidata.arr, xr.DataArray)
    df = convert_xarray_to_polars(qoidata.arr, qoidata.qoi.nickname)
    return df


def to_dataframe_with_spaces(qoi: QOIType, idf: Path, sql: Path):
    qoid = select_times(QOIandData(qoi, sql))
    df = to_dataframe(qoid)
    space_df = create_space_df(idf)

    dd = df.join(space_df, on="space_names")
    qoid.set_dataframe(dd)
    return qoid


def to_multi_data(qois: Sequence[QOIType], idf: Path, sql: Path):

    def to_df(qoi: QOIType):
        qoid = select_times(QOIandData(qoi, sql))
        return to_dataframe(qoid)

    # TODO: add utils4plans as set_unique function
    space_types = [i.space_type for i in qois]
    assert (
        len(set(space_types)) == 1
    ), f"Expected the space_types to all be the same, but got: {space_types}"

    dfs = [to_df(i) for i in qois]
    d0 = dfs[0]
    for df in dfs[1:]:
        d0 = d0.join(df, on=["datetimes", "space_names"])

    space_df = create_space_df(idf)
    return d0.join(space_df, on="space_names")
