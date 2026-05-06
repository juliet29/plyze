from dataclasses import dataclass
from pathlib import Path
from plyze.qoi.xarray_helpers import normalize_xarray_min_max
from typing import Literal, NamedTuple
import polars as pl
from plyze.qoi.data.interfaces import QOIandData
from plyze.qoi.registries.main import QOIRegistry
from plyze.qoi.xarray_helpers import convert_xarray_to_polars
from plyze.flow_graph.interfaces import (
    FlowGraph,
    ZoneNodeData,
    ZoneNodeQOINames,
)
from plyze.qoi_flow_graph.zone_data import create_flow_graph_xarray
from plyze.utils import XArrayNames
import xarray as xr


EnviroQOINames = Literal["mix_norm", "vent_norm", "temp_norm", "temp_norm_no_scale"]


class EnvironmentalComparisons(NamedTuple):
    t_out: xr.DataArray
    wind_speed: xr.DataArray


def make_enviro(sql: Path):
    # NOTE: just need on sql file that matches the weather of the data being studied!
    e = (
        QOIandData(QOIRegistry.site.t_out, sql).original_arr,
        QOIandData(QOIRegistry.site.wind_speed, sql).original_arr,
    )
    return EnvironmentalComparisons(*[i.squeeze(XArrayNames.SPACE) for i in e])


# TODO: pass in fx because may be more complex.. but also, why not use qoi_registries?
def calc_enviro_norm(
    name: str, value: xr.DataArray, enviro: xr.DataArray, norm: bool = True
):
    if norm:
        vn = normalize_xarray_min_max(value)
        en = normalize_xarray_min_max(enviro)
    else:
        vn = value
        en = enviro
    d = vn / en
    d.name = name

    return d


@dataclass()
class EvalDirectQOIs:
    G: FlowGraph

    def zone_inflow(self, zone: ZoneNodeData):
        pass


def make_enviro_norm_data(G: FlowGraph, enviro: EnvironmentalComparisons):
    def make_ds(qoi: ZoneNodeQOINames):
        plan_array = create_flow_graph_xarray(
            lambda x: x.data.get_qoi_array(qoi), G.zone_nodes
        )
        return plan_array

    norm_arrays = [
        calc_enviro_norm("mix_norm", make_ds("mixing_volume"), enviro.wind_speed),
        calc_enviro_norm("vent_norm", make_ds("ventilation_volume"), enviro.wind_speed),
        calc_enviro_norm(
            "temp_norm",
            make_ds("temperature"),
            enviro.t_out,
        ),
        calc_enviro_norm(
            "temp_norm_no_scale", make_ds("temperature"), enviro.t_out, norm=False
        ),
    ]
    return norm_arrays


def create_enviro_df(norm_arrays: list[xr.DataArray]):
    dfs = []
    for arr in norm_arrays:
        df = convert_xarray_to_polars(arr, name=str(arr.name))
        dfs.append(df)

    df_fin = pl.concat(dfs, how="align")
    return df_fin


def extend_zone_data_to_df(G: FlowGraph, enviro: EnvironmentalComparisons):
    norm_arrays = make_enviro_norm_data(G, enviro)
    df = create_enviro_df(norm_arrays)
    return df
