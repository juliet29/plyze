from typing import Callable, TypeVar, get_args
import polars as pl
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


#
