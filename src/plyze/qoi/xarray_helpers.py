from plan2eplus.ezcase.ez import logger
import numpy as np
import polars as pl
from datetime import datetime
import xarray as xr
import re
from plyze.utils import XArrayNames


def normalize_xarray_min_max(da: xr.DataArray):
    da_min = da.min()
    da_max = da.max()

    da_norm = (da - da_min) / (da_max - da_min)
    return da_norm


def find_drn_in_name(space_name: str):
    pattern = re.compile("(NORTH)|(SOUTH)|(EAST)|(WEST)")
    res = pattern.search(space_name.upper())
    if res:
        return res.group()
    else:
        raise ValueError(
            f"External node name {space_name} does not contain a direction!"
        )


def get_data_by_space_name(arr: xr.DataArray, name: str):
    try:
        return arr.sel(space_names=name.upper())
    except KeyError:
        raise Exception(f"Could not find data for {name} in {arr}")


def make_dt_str(val: datetime | np.datetime64):
    FORMAT = "%m/%d/%y - %H"
    if isinstance(val, datetime):
        res = datetime.strftime(val, FORMAT)
    else:
        res = datetime.strftime(
            val.item(), FORMAT  # pyright: ignore[reportArgumentType]
        )
    return res


def log_datetimes(dt: list[datetime] | list[np.datetime64]):
    final = [make_dt_str(i) for i in dt]
    logger.debug(final)


def select_time(arr: xr.DataArray, dt: datetime | list[datetime]):
    assert XArrayNames.DATETIME in arr.dims

    # curr_times = [i for i in arr[XArrayNames.DATETIME].data]
    # if isinstance(dt, list):
    #     log_datetimes([curr_times[0], curr_times[-1]])
    #     log_datetimes(dt)
    #
    #     time_overlap = set_intersection(curr_times, dt)
    #     diff = set_difference(curr_times, dt)
    #     logger.debug((len(curr_times), len(dt)))
    #     logger.debug(len(time_overlap))
    #     logger.debug(len(diff))
    #
    # log_datetimes(time_overlap)
    # log_datetimes(diff)
    return arr.sel(datetimes=dt)


def convert_xarray_to_polars(data: xr.DataArray | xr.Dataset, name=""):
    if name:
        data.name = name
    return pl.from_pandas(data.to_dataframe(), include_index=True).with_columns(
        pl.col(XArrayNames.DATETIME).dt.cast_time_unit("us")
    )


def get_data(arr: xr.DataArray):
    return arr.to_dict()["data"]


def get_single_value(arr: xr.DataArray):
    assert arr.size == 1
    return float(arr.data)


def calc_median(arr: xr.DataArray):
    return arr.median()
