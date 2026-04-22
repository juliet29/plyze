from pathlib import Path
from typing import Callable, NamedTuple, TypeVar, get_args
import polars as pl
from plyze.qoi.data.interfaces import QOIandData
from plyze.qoi.registries.main import QOIRegistry
from plyze.qoi.xarray_helpers import convert_xarray_to_polars
from plyze.flow_graph.interfaces import (
    Edge,
    ExternalNode,
    FlowGraph,
    ZoneNode,
    ZoneNodeQOINames,
)
from plyze.utils import XArrayNames
import xarray as xr


GraphVal = TypeVar("GraphVal", ZoneNode, ExternalNode, Edge)


def create_flow_graph_xarray(
    fx: Callable[[GraphVal], xr.DataArray], graph_vals: list[GraphVal]
):
    plan_data = xr.concat(
        [fx(i) for i in graph_vals],
        dim=XArrayNames.SPACE,
    )

    return plan_data


def collate_zone_data_to_df(G: FlowGraph, afn_nodes_only: bool = True):
    def make_df(qoi: ZoneNodeQOINames):
        if afn_nodes_only:
            nodes = [i for i in G.zone_nodes if i.data.is_in_afn]
        else:
            nodes = G.zone_nodes

        plan_array = create_flow_graph_xarray(
            lambda x: x.data.get_qoi_array(qoi), nodes
        )
        return convert_xarray_to_polars(plan_array, name=qoi)

    # basically concat and turn into dataframe..

    dfs = [make_df(i) for i in get_args(ZoneNodeQOINames)]
    df = pl.concat(dfs, how="align")

    return df


# More QOIS -> not stored on the nodes # TODO: add to QOI registry?
#
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


def norm_da(da: xr.DataArray):
    da_min = da.min()
    da_max = da.max()

    da_norm = (da - da_min) / (da_max - da_min)
    return da_norm


def calc_enviro_norm(
    name: str, value: xr.DataArray, enviro: xr.DataArray, norm: bool = True
):
    if norm:
        vn = norm_da(value)
        en = norm_da(enviro)
    else:
        vn = value
        en = enviro
    d = vn / en
    d.name = name

    print(d)

    return d


def extend_zone_data_df(G: FlowGraph, enviro: EnvironmentalComparisons):
    # t_in_t_out = df.select(pl.col(QOIRegistry.temp.nickname)) / enviro.pl_t_out

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
    dfs = []
    for arr in norm_arrays:
        df = convert_xarray_to_polars(arr, name=str(arr.name))
        dfs.append(df)

    df_fin = pl.concat(dfs, how="align")
    return df_fin
