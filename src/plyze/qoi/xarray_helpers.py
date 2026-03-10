import polars as pl
from datetime import datetime
import xarray as xr
import re


def find_drn_in_name(space_name: str):
    pattern = re.compile("(NORTH)|(SOUTH)|(EAST)|(WEST)")
    res = pattern.search(space_name.upper())
    if res:
        return res.group()
    else:
        raise ValueError(
            f"External node name {space_name} does not contain a direction!"
        )


def select_time(arr: xr.DataArray, dt: datetime | list[datetime]):
    assert "datetimes" in arr.dims
    return arr.sel(datetimes=dt)


def convert_xarray_to_polars(data: xr.DataArray | xr.Dataset, name=""):
    if name:
        data.name = name
    return pl.from_pandas(data.to_dataframe(), include_index=True)


def get_data(arr: xr.DataArray):
    return arr.to_dict()["data"]
